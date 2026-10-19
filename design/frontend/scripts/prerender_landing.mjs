import { readFile, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { createElement } from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { createServer } from 'vite';

const dist = resolve('dist');
const indexPath = resolve(dist, 'index.html');
const html = await readFile(indexPath, 'utf8');
const root = '<div id="root"></div>';
if (!html.includes(root)) throw new Error('Built index.html has no empty app root');

// Other app routes use the normal client shell; the public homepage has
// meaningful HTML available to visitors and compliance crawlers without JS.
await writeFile(resolve(dist, 'app-shell.html'), html);

const vite = await createServer({
  server: { middlewareMode: true },
  appType: 'custom',
});
try {
  const { LandingContent } = await vite.ssrLoadModule('/src/screens/landing/landing_content.tsx');
  const landing = renderToStaticMarkup(createElement(LandingContent));
  const page = html
    .replace(root, `<div id="root">${landing}</div>`)
    .replace('<title>Riffy</title>', '<title>Riffy | Practice humour and conversation</title>')
    .replace('</head>', '    <link rel="canonical" href="https://riffy.pro/" />\n  </head>');
  await writeFile(indexPath, page);
  console.log('Prerendered public landing page');
} finally {
  await vite.close();
}
