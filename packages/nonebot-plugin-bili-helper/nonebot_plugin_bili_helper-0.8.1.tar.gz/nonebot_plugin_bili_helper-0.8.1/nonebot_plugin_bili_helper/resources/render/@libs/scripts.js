const renderTemplates = [];

const { origin } = window.location;

export function cleanupBeforeRender() {
  const bodyChildren = Array.from(document.body.children);
  bodyChildren.forEach((child) => {
    document.body.removeChild(child);
  });
}

async function loadTemplate(src = '') {
  const text = await fetch(src).then((res) => res.text());
  const script = document.createElement('script');
  script.id = `${origin}${src}`;
  script.type = 'text/html';
  script.innerHTML = text;
  document.body.appendChild(script);
  renderTemplates.push(script);
}

export async function loadTemplates(list = [], cb = null) {
  await list.reduce((p, src) => p.then(() => loadTemplate(src)), Promise.resolve());
  cb?.();
}

export function cleanupAfterRender() {
  renderTemplates.forEach((script) => {
    if (script.parentNode) {
      script.parentNode.removeChild(script);
    }
  });
  renderTemplates.length = 0;
}
