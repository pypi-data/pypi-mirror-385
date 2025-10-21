{
  window.ScriptsModule = {};
  module = { exports: window.ScriptsModule };

  const {
    fetchJsonP,
  } = window.JsonPModule;

  const renderTemplates = [];

  // const { origin } = window.location;

  module.exports.cleanupBeforeRender = function cleanupBeforeRender() {
    const bodyChildren = Array.from(document.body.children);
    bodyChildren.forEach((child) => {
      document.body.removeChild(child);
    });
  }

  async function loadTemplate(src = '') {
    // const text = await fetch(src).then((res) => res.text());
    const url = src.replace(/^\/resources\/template\//, '../../mocks/template-p/').concat('.js');
    const text = await fetchJsonP(url);
    const script = document.createElement('script');
    // script.id = `${origin}${src}`;
    script.id = src;
    script.type = 'text/html';
    script.innerHTML = text;
    document.body.appendChild(script);
    renderTemplates.push(script);
  }

  module.exports.loadTemplates = async function loadTemplates(list = [], cb = null) {
    await list.reduce((p, src) => p.then(() => loadTemplate(src)), Promise.resolve());
    cb?.();
  }

  module.exports.cleanupAfterRender = function cleanupAfterRender() {
    renderTemplates.forEach((script) => {
      if (script.parentNode) {
        script.parentNode.removeChild(script);
      }
    });
    renderTemplates.length = 0;
  }
}
