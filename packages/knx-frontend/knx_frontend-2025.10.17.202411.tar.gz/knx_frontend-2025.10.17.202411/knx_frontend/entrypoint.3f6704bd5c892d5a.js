
function loadES5() {
  var el = document.createElement('script');
  el.src = '/knx_static/frontend_es5/entrypoint.73d17dca01bd94bd.js';
  document.body.appendChild(el);
}
if (/.*Version\/(?:11|12)(?:\.\d+)*.*Safari\//.test(navigator.userAgent)) {
    loadES5();
} else {
  try {
    new Function("import('/knx_static/frontend_latest/entrypoint.3f6704bd5c892d5a.js')")();
  } catch (err) {
    loadES5();
  }
}
  