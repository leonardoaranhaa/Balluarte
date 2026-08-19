-- 001 — trilha de auditoria: tabela append-only com encadeamento por hash.
--
-- Append-only aqui não é convenção de uso, é o que o banco permite. UPDATE e
-- DELETE levantam exceção por gatilho, e o papel da aplicação nem recebe o
-- privilégio. Os dois juntos de propósito: o GRANT protege do código, o
-- gatilho protege de quem entra com psql e privilégio demais — que é a mão
-- que de fato altera trilha quando alguém quer alterar trilha.
--
-- Sobre o que NÃO existe nesta tabela: nenhuma coluna para valor de dado
-- pessoal. Não é que a aplicação evite preencher; é que não há onde. A regra 2
-- do CLAUDE.md fica sendo propriedade do esquema, e não disciplina de quem
-- escreve o INSERT.

CREATE TABLE trilha_auditoria (
    -- Ordem da cadeia dentro do tenant. BIGSERIAL para não depender do relógio
    -- para ordenar: dois registros no mesmo milissegundo precisam de ordem
    -- definida, senão a verificação da cadeia fica ambígua.
    sequencia          BIGSERIAL   PRIMARY KEY,

    requisicao_id      UUID        NOT NULL,
    registrado_em      TIMESTAMPTZ NOT NULL,

    tenant             TEXT        NOT NULL,

    -- Identificador da chave, nunca a chave. Quem investiga precisa saber
    -- qual credencial chamou; ninguém precisa da credencial.
    chave_origem       TEXT        NOT NULL,

    provedor_destino   TEXT        NOT NULL,

    -- Qual política decidiu, com o sha256 do texto do arquivo. Sem o hash,
    -- "estava vigente a v2" é afirmação; com ele, é conferível contra o
    -- repositório.
    politica_nome      TEXT        NOT NULL,
    politica_versao    INTEGER     NOT NULL,
    politica_sha256    CHAR(64)    NOT NULL,

    acao_global        TEXT        NOT NULL,

    -- [{"entidade": "BR_CPF", "quantidade": 2, "acao": "tokenizar"}, ...]
    -- Tipo, quantidade e ação. Nunca valor.
    achados            JSONB       NOT NULL,

    hash_anterior      CHAR(64)    NOT NULL,
    hash_registro      CHAR(64)    NOT NULL,

    CONSTRAINT trilha_hash_unico UNIQUE (hash_registro),

    CONSTRAINT trilha_acao_conhecida
        CHECK (acao_global IN ('permitir', 'tokenizar', 'mascarar', 'bloquear')),

    CONSTRAINT trilha_hash_formato
        CHECK (hash_registro ~ '^[0-9a-f]{64}$' AND hash_anterior ~ '^[0-9a-f]{64}$'),

    CONSTRAINT trilha_achados_e_lista
        CHECK (jsonb_typeof(achados) = 'array')
);

-- A cadeia é POR TENANT, não global.
--
-- Uma cadeia única para todos os clientes obrigaria o tenant A a ler o hash de
-- registros do tenant B para verificar a própria integridade — o que colide
-- de frente com a segregação. Com uma cadeia por tenant, verificar a própria
-- trilha não exige enxergar a de ninguém.
CREATE UNIQUE INDEX trilha_encadeamento ON trilha_auditoria (tenant, sequencia);
CREATE INDEX trilha_por_tenant_e_data ON trilha_auditoria (tenant, registrado_em);
CREATE INDEX trilha_por_requisicao ON trilha_auditoria (tenant, requisicao_id);

CREATE OR REPLACE FUNCTION trilha_e_append_only() RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION
        'trilha_auditoria é append-only: % recusado no registro %',
        TG_OP, COALESCE(OLD.sequencia, -1)
        USING ERRCODE = 'integrity_constraint_violation';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trilha_sem_update
    BEFORE UPDATE ON trilha_auditoria
    FOR EACH ROW EXECUTE FUNCTION trilha_e_append_only();

CREATE TRIGGER trilha_sem_delete
    BEFORE DELETE ON trilha_auditoria
    FOR EACH ROW EXECUTE FUNCTION trilha_e_append_only();

-- TRUNCATE não passa por gatilho de linha; precisa do seu próprio.
CREATE TRIGGER trilha_sem_truncate
    BEFORE TRUNCATE ON trilha_auditoria
    FOR EACH STATEMENT EXECUTE FUNCTION trilha_e_append_only();
