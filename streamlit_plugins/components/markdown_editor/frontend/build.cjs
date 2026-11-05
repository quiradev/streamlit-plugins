const path = require('node:path');
const fs = require('node:fs');
const esbuild = require('esbuild');

const buildDir = path.join(__dirname, 'build');
fs.mkdirSync(buildDir, { recursive: true });

const editor = fs.readFileSync(path.join(buildDir, 'editor.js'), 'utf8');
esbuild.transformSync(editor, { loader: 'js', target: 'es2022' });

const result = esbuild.buildSync({
  entryPoints: [path.join(__dirname, 'renderers.js')],
  outfile: path.join(buildDir, 'renderers.bundle.js'),
  bundle: true,
  format: 'iife',
  globalName: 'MarkdownEditorRenderers',
  platform: 'browser',
  target: 'es2022',
  minify: true,
  legalComments: 'eof',
  metafile: true,
});

const licenses = new Map();
for (const input of Object.keys(result.metafile.inputs)) {
  if (!path.resolve(input).includes(`${path.sep}node_modules${path.sep}`)) continue;
  let directory = path.dirname(path.resolve(input));
  while (directory !== path.dirname(directory)) {
    const manifest = path.join(directory, 'package.json');
    if (fs.existsSync(manifest)) {
      const pkg = JSON.parse(fs.readFileSync(manifest, 'utf8'));
      if (pkg.name) {
        const key = `${pkg.name}@${pkg.version}`;
        const files = fs.readdirSync(directory).filter((file) => /^licen[sc]e(?:[._-]|$)/i.test(file));
        if (files.length) {
          licenses.set(key, files.map((file) => fs.readFileSync(path.join(directory, file), 'utf8')).join('\n'));
        } else {
          const readme = fs.readdirSync(directory).find((file) => /^readme\.md$/i.test(file));
          const section = readme && fs.readFileSync(path.join(directory, readme), 'utf8')
            .match(/^#{1,3}\s+licen[sc]e\b[\s\S]*$/im)?.[0];
          if (!section) throw new Error(`Missing license text for bundled dependency ${key}`);
          licenses.set(key, section);
        }
        break;
      }
    }
    directory = path.dirname(directory);
  }
}
fs.writeFileSync(path.join(buildDir, 'THIRD_PARTY_LICENSES.txt'),
  [...licenses].sort(([a], [b]) => a.localeCompare(b))
    .map(([name, license]) => `${name}\n${'='.repeat(72)}\n${license}`).join('\n\n'));
