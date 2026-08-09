document.documentElement.classList.remove('no-js');

(function () {
  "use strict";

  var stage = document.getElementById('stage');
  var ctrl  = document.getElementById('ctrl');
  var rule  = document.getElementById('rule');
  var body  = document.getElementById('audit-body');
  if (!stage || !ctrl || !rule || !body) return;

  var spans = Array.prototype.slice.call(stage.querySelectorAll('.pii'));
  var total = spans.length;

  // Timestamp fixo, capturado uma vez: a linha de auditoria não deve tremer
  // enquanto o leitor arrasta o plano.
  var t = new Date();
  function pad(n) { return (n < 10 ? '0' : '') + n; }
  var stamp = pad(t.getHours()) + ':' + pad(t.getMinutes()) + ':' + pad(t.getSeconds());

  var hashes = ['—', '3b81e4c0', '7d40af19', '9f2c1a7e'];

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
      if (cut >= w / 2) done++;
    }

    rule.style.left = (frac * 100) + '%';
    ctrl.setAttribute('aria-valuetext',
      total + ' dados pessoais detectados, ' + done + ' já transformados em token');

    // A detecção não depende da posição do plano: são sempre 3 achados.
    // O que a trilha registra progressivamente é quantos foram transformados.
    if (done === 0) {
      body.innerHTML = '<span>aguardando tráfego</span>';
    } else {
      body.innerHTML =
        '<span>' + stamp + '</span>' +
        '<span>politica=<b>tokenizar</b></span>' +
        '<span>' + total + ' achados</span>' +
        '<span><b>' + done + '</b> transformados</span>' +
        '<span>destino=anthropic</span>' +
        '<span>sha256:' + hashes[done] + '…</span>';
    }
  }

  ctrl.addEventListener('input', render);

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
