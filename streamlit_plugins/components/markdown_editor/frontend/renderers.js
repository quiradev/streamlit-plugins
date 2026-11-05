import katex from 'katex';
import hljs from 'highlight.js/lib/core';
import python from 'highlight.js/lib/languages/python';
import javascript from 'highlight.js/lib/languages/javascript';
import typescript from 'highlight.js/lib/languages/typescript';
import json from 'highlight.js/lib/languages/json';
import yaml from 'highlight.js/lib/languages/yaml';
import sql from 'highlight.js/lib/languages/sql';
import bash from 'highlight.js/lib/languages/bash';
import xml from 'highlight.js/lib/languages/xml';
import css from 'highlight.js/lib/languages/css';
import mermaid from 'mermaid';
export { diffArrays, diffLines, diffWordsWithSpace } from 'diff';

for (const [name, language] of Object.entries({
  python, javascript, typescript, json, yaml, sql, bash, xml, css,
})) {
  hljs.registerLanguage(name, language);
}

mermaid.initialize({ startOnLoad: false, securityLevel: 'strict' });

export function renderMath(source, displayMode) {
  return katex.renderToString(source, {
    displayMode,
    output: 'mathml',
    throwOnError: true,
    trust: false,
  });
}

export function highlightCode(source, language) {
  if (hljs.getLanguage(language)) {
    return { html: hljs.highlight(source, { language }).value, supported: true };
  }
  return {
    html: source.replace(/[&<>]/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' })[char]),
    supported: language === 'text' || language === 'plaintext' || language === '',
  };
}

export async function renderDiagram(source) {
  const { svg } = await mermaid.render(`md-diagram-${crypto.randomUUID()}`, source);
  return svg;
}
