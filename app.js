document.documentElement.classList.remove('no-js');

(function () {
  "use strict";

  var plane = document.getElementById('plane');
  var stage = document.getElementById('stage');
  var ctrl  = document.getElementById('ctrl');
  var rule  = document.getElementById('rule');
  var body  = document.getElementById('audit-body');
  if (!plane || !stage || !ctrl || !rule || !body) return;

  var spans = Array.prototype.slice.call(stage.querySelectorAll('.pii'));
  var total = spans.length;

  // Timestamp fixo, capturado uma vez: a linha de auditoria não deve tremer
  // enquanto o leitor arrasta o plano.
  var t = new Date();
  function pad(n) { return (n < 10 ? '0' : '') + n; }
  var stamp = pad(t.getHours()) + ':' + pad(t.getMinutes()) + ':' + pad(t.getSeconds());

  // Oito caracteres em qualquer estado: a linha de auditoria é monoespaçada, e
  // um resumo mais curto antes do envio faria o bloco inteiro requebrar de
  // largura na hora em que a mensagem sai.
  var hashes = ['————————', '3b81e4c0', '7d40af19', '9f2c1a7e'];
  var enviado = false;

  function render() {
    var frac = ctrl.value / ctrl.max;
    var planeX = frac * stage.clientWidth;
    var done = 0;

    for (var i = 0; i < total; i++) {
      var s = spans[i];
      var w = s.offsetWidth;
      var cut = planeX - s.offsetLeft;
      if (cut < 0) cut = 0;
      if (cut > w) cut = w;
      s.style.setProperty('--cut', cut + 'px');
      // Antes do envio a mensagem ainda não está no layout e w vale zero, o
      // que faria `cut >= w/2` valer para os três de uma vez e a cena nascer
      // já respondida.
      if (w > 0 && cut >= w / 2) done++;
    }

    rule.style.left = (frac * 100) + '%';
    ctrl.setAttribute('aria-valuetext',
      total + ' dados pessoais detectados, ' + done + ' já transformados em token');

    plane.classList.toggle('is-answered', done === total);

    // A detecção não depende da posição do plano: são sempre três achados. O
    // que a trilha registra progressivamente é quantos foram transformados.
    // Antes do envio nada foi classificado ainda — a linha existe, com os
    // mesmos campos e a mesma largura, mas sem afirmar achado nenhum.
    body.innerHTML =
      '<span>' + (enviado ? stamp : '--:--:--') + '</span>' +
      '<span>politica=<b>tokenizar</b></span>' +
      '<span>' + (enviado ? total : '—') + ' achados</span>' +
      '<span><b>' + (enviado ? done : '—') + '</b> transformados</span>' +
      '<span>destino=anthropic</span>' +
      '<span>sha256:' + hashes[done] + '…</span>';
  }

  // ── o usuário escrevendo ─────────────────────────────────────────
  // O leitor precisa ver o vazamento acontecer antes de ver o controle. A
  // digitação é só encenação: nada depende dela, e qualquer interação com o
  // plano corta para o fim.

  var alvo   = document.getElementById('typed');
  var caixa  = document.getElementById('composer-box');

  // A frase digitada é o prompt sem os tokens — eles são o estado de saída,
  // não existem no momento em que a pessoa escreve.
  var cru = stage.querySelector('.payload').cloneNode(true);
  Array.prototype.forEach.call(cru.querySelectorAll('.pii i'), function (el) {
    el.parentNode.removeChild(el);
  });
  var frase = cru.textContent.replace(/\s+/g, ' ').trim();

  function enviar() {
    if (enviado) return;
    enviado = true;
    if (alvo) alvo.textContent = '';
    plane.classList.remove('is-typing');
    plane.classList.add('is-sent');
    render(); // a mensagem só agora entra no layout: remede os trechos
  }

  function digitar() {
    if (!alvo || !caixa) { enviar(); return; }
    plane.classList.add('is-typing');
    var i = 0;
    (function passo() {
      if (enviado) return;
      if (i >= frase.length) { setTimeout(enviar, 420); return; }
      var c = frase.charAt(i++);
      alvo.textContent += c;
      caixa.scrollTop = caixa.scrollHeight;
      setTimeout(passo, c === ',' || c === '.' ? 150 : 16);
    })();
  }

  // Sem movimento pedido, ou sem IntersectionObserver, a cena já começa
  // enviada: a encenação é acessório, o plano é o conteúdo.
  var calmo = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (calmo || !window.IntersectionObserver) {
    enviar();
  } else {
    // Margem negativa em vez de threshold: o painel é alto, e uma fração fixa
    // dele pode nunca caber numa janela baixa. Assim dispara quando o painel
    // cruza a faixa central da tela, seja qual for a altura dos dois.
    new IntersectionObserver(function (entradas, obs) {
      if (!entradas[0].isIntersecting) return;
      obs.disconnect();
      setTimeout(digitar, 500);
    }, { rootMargin: '-20% 0px -20% 0px' }).observe(plane);
  }

  // O controle nunca sai do fluxo, para continuar alcançável pelo Tab durante
  // a digitação. Receber o foco já envia a mensagem: senão o anel de foco, que
  // é desenhado pela linha do plano, apontaria para um elemento ainda oculto.
  ctrl.addEventListener('focus', enviar);
  ctrl.addEventListener('pointerdown', enviar);
  ctrl.addEventListener('input', function () { enviar(); render(); });

  // O range tem mil passos para o arrasto não ficar serrilhado, mas isso
  // deixaria a travessia a quinhentos toques de seta. No teclado o passo é
  // 5% — vinte toques de ponta a ponta. Home e End continuam nativos.
  ctrl.addEventListener('keydown', function (ev) {
    enviar();
    var d = ev.key === 'ArrowRight' || ev.key === 'ArrowUp' ? 50
          : ev.key === 'ArrowLeft'  || ev.key === 'ArrowDown' ? -50 : 0;
    if (!d) return;
    ev.preventDefault();
    var v = Math.min(+ctrl.max, Math.max(+ctrl.min, +ctrl.value + d));
    if (v === +ctrl.value) return;
    ctrl.value = v;
    render();
  });

  // offsetLeft/offsetWidth mudam quando o texto reflui; recalcula na mudança
  // de tamanho, sem observar durante o arrasto.
  if (window.ResizeObserver) {
    new ResizeObserver(render).observe(stage);
  } else {
    window.addEventListener('resize', render);
  }

  render();
})();

// ── Envio do formulário ─────────────────────────────────────────────
// Sem biblioteca e sem CDN: o guia AJAX do Formspree carrega um script de
// unpkg.com, o que quebraria a regra de não depender de rede de terceiro e
// exigiria afrouxar o script-src da CSP. Isto aqui é aprimoramento
// progressivo: sem JS (ou sem fetch), o POST normal do <form> acontece e o
// _next devolve o visitante para /obrigado.html.
(function () {
  "use strict";

  var form = document.getElementById('form-agendar');
  if (!form || !window.fetch || !window.FormData) return;

  var status = document.getElementById('form-status');
  var btn = form.querySelector('button[type="submit"]');

  form.addEventListener('submit', function (ev) {
    ev.preventDefault();
    status.textContent = 'enviando…';
    btn.disabled = true;

    fetch(form.action, {
      method: 'POST',
      body: new FormData(form),
      headers: { 'Accept': 'application/json' }
    }).then(function (res) {
      if (res.ok) {
        form.reset();
        status.textContent =
          'Recebido. Respondo em até um dia útil, com dois ou três horários.';
        return;
      }
      return res.json().then(function (data) {
        var msg = (data && data.errors || []).map(function (e) { return e.message; }).join('; ');
        throw new Error(msg || 'o formulário não aceitou o envio');
      });
    }).catch(function (err) {
      // textContent, nunca innerHTML: a mensagem vem de fora.
      status.textContent =
        'Não consegui enviar — ' + err.message +
        '. Escreva direto para contato@baluarte.com.br.';
    }).then(function () {
      btn.disabled = false;
    });
  });
})();
