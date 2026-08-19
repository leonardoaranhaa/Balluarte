-- 002 — segregação por tenant, imposta pelo banco.
--
-- A segregação podia viver no repositório, com um WHERE tenant = %s em toda
-- consulta. Não vive, porque um WHERE esquecido é um vazamento entre clientes
-- e nada avisa. Aqui a linha só é visível se a sessão declarou de quem ela é;
-- consulta sem tenant declarado devolve zero linhas em vez de devolver tudo.
--
-- O papel da aplicação não é dono da tabela nem tem BYPASSRLS, então a
-- política vale para ele mesmo quando o código erra.

CREATE ROLE baluarte_app NOLOGIN;

-- Nem UPDATE nem DELETE são concedidos. O gatilho da 001 já recusaria, mas
-- privilégio que não existe não depende de gatilho continuar existindo.
GRANT SELECT, INSERT ON trilha_auditoria TO baluarte_app;
GRANT USAGE, SELECT ON SEQUENCE trilha_auditoria_sequencia_seq TO baluarte_app;

ALTER TABLE trilha_auditoria ENABLE ROW LEVEL SECURITY;
ALTER TABLE trilha_auditoria FORCE ROW LEVEL SECURITY;

-- current_setting(..., true) devolve NULL quando a variável não foi definida.
-- Comparar com NULL dá NULL, que a política trata como falso: sessão que não
-- declarou tenant não enxerga nada. É o comportamento que se quer — falhar
-- fechado, e não devolver a base inteira.
CREATE POLICY trilha_le_so_o_proprio_tenant ON trilha_auditoria
    FOR SELECT TO baluarte_app
    USING (tenant = current_setting('baluarte.tenant', true));

CREATE POLICY trilha_grava_so_no_proprio_tenant ON trilha_auditoria
    FOR INSERT TO baluarte_app
    WITH CHECK (tenant = current_setting('baluarte.tenant', true));
