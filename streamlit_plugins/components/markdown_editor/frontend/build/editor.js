export default function ({ parentElement, data, setStateValue }) {
  const root = parentElement.querySelector('.md-editor');
  if (!root) return;

  const canvas = root.querySelector('.md-canvas');
  const toolbar = root.querySelector('.md-toolbar');
  const status = root.querySelector('.md-status');
  const modeSelector = root.querySelector('.md-editor-mode');
  const typeSelector = root.querySelector('.md-block-type');
  const syncModeButtons = () => modeSelector.querySelectorAll('[data-mode]').forEach((button) => {
    button.hidden = !runtime.options.editorModes.includes(button.dataset.mode);
    button.dataset.single = String(runtime.options.editorModes.length === 1);
    button.setAttribute('aria-pressed', String(button.dataset.mode === runtime.mode));
  });
  const saveButton = root.querySelector('.md-save');
  const reviewButton = root.querySelector('.md-review-button');
  const reviewToolbar = root.querySelector('.md-review-toolbar');
  const reviewContent = root.querySelector('.md-review-content');
  const floatingMenu = root.querySelector('.md-floating-menu');
  const floatingActions = floatingMenu.querySelector('.md-floating-actions');
  const help = root.querySelector('.md-help');
  const helpToggle = root.querySelector('.md-help-toggle');
  const feedback = root.querySelector('.md-feedback');
  root.dataset.debug = String(Boolean(data?.debug_blocks));
  root.style.height = typeof data?.height === 'number' ? `${data.height}px`
    : data?.height === 'stretch' ? '100%' : data?.height === 'content' ? 'auto' : '760px';
  const inputFingerprint = JSON.stringify({
    blocks: data?.blocks ?? [],
    onlyView: data?.only_view ?? false,
    diff: data?.diff ?? null,
    mode: data?.mode ?? 'raw_visual',
    saveMode: data?.save_mode ?? 'auto',
  });
  const blocksFingerprint = JSON.stringify(data?.blocks ?? []);
  const diffFingerprint = JSON.stringify(data?.diff ?? null);
  const revision = String(data?.revision ?? 0);
  const runtime = root.__markdownEditorRuntime ?? {
    activeBlock: null,
    timer: null,
    historyTimer: null,
    lastPublished: '',
    setStateValue,
    history: [],
    redo: [],
    mode: data?.mode ?? 'raw_visual',
    saveMode: data?.save_mode ?? 'auto',
    savedFingerprint: '',
    draggedBlock: null,
    dragSnapshot: '',
    bookmark: null,
    menuBlock: null,
    onlyView: Boolean(data?.only_view),
    reviewing: false,
    savedBlocks: [],
    reviewMode: 'visual',
    reviewLayout: 'split',
  };
  runtime.setStateValue = setStateValue;
  runtime.mode = runtime.mode ?? data?.mode ?? 'raw_visual';
  runtime.saveMode = data?.save_mode ?? runtime.saveMode ?? 'auto';
  runtime.onlyView = Boolean(data?.only_view) || runtime.reviewing;
  runtime.externalDiff = data?.diff ?? null;
  runtime.inputBlocks = data?.blocks ?? [];
  runtime.options = {
    editorModes: data?.editor_modes ?? ['raw_visual', 'visual'],
    reviewModes: data?.review_modes ?? ['visual', 'markdown'],
    reviewLayouts: data?.review_layouts ?? ['before', 'after', 'split', 'blocks'],
    blockDiffStyle: data?.block_diff_style ?? 'content',
    placeholder: data?.placeholder ?? 'Escribe aquí…',
    showCopy: data?.show_copy_button ?? true,
    showStatus: data?.show_status_bar ?? true,
    toolbarSections: data?.toolbar_sections ?? ['view', 'format', 'block', 'history', 'changes'],
  };
  const optionsFingerprint = JSON.stringify(runtime.options);
  const optionsChanged = root.dataset.optionsFingerprint !== optionsFingerprint;
  if (!runtime.options.reviewModes.includes(runtime.reviewMode)) runtime.reviewMode = runtime.options.reviewModes[0];
  if (!runtime.options.reviewLayouts.includes(runtime.reviewLayout)) runtime.reviewLayout = runtime.options.reviewLayouts[0];
  root.__markdownEditorRuntime = runtime;

  const blockType = (markdown) => {
    if (/^#{1,6}\s/.test(markdown)) return `h${markdown.match(/^#+/)[0].length}`;
    if (/^```mermaid\b/i.test(markdown)) return 'mermaid';
    if (/^```/.test(markdown)) return 'code';
    if (/^\$\$[\s\S]*\$\$\s*$/.test(markdown)) return 'math';
    if (/^>\s?/.test(markdown)) return 'quote';
    if (/^\s*\|/.test(markdown)) return 'table';
    if (/^\s*(?:[-*+]|\d+[.)])\s+\[[ xX]\](?:\s|$)/.test(markdown)) return 'task_list';
    if (/^\s*[-*+]\s/.test(markdown)) return 'list';
    if (/^\s*\d+[.)]\s/.test(markdown)) return 'ordered_list';
    if (/^!\[[^\]]*\]\(/.test(markdown)) return 'image';
    if (/^\[[^\]]+\]\(/.test(markdown)) return 'link';
    if (/^(---+|\*\*\*+|___+)\s*$/.test(markdown)) return 'rule';
    return 'paragraph';
  };

  const typeLabel = (type) => ({
    paragraph: 'Párrafo', h1: 'Título 1', h2: 'Título 2', h3: 'Título 3',
    h4: 'Título 4', h5: 'Título 5', h6: 'Título 6',
    quote: 'Cita', list: 'Lista', ordered_list: 'Lista numerada', task_list: 'Lista de tareas', code: 'Código',
    table: 'Tabla', image: 'Imagen', link: 'Enlace', mermaid: 'Mermaid', math: 'LaTeX', rule: 'Separador',
  })[type] ?? 'Párrafo';

  const isListType = (type) => ['list', 'ordered_list', 'task_list'].includes(type);
  const escapeHtml = (value) => String(value).replace(/[&<>"']/g, (char) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  })[char]);

  const safeUrl = (value) => /^(https?:|mailto:)/i.test(value) ? value : '';

  const inlineHtml = (source) => {
    const tokens = [];
    const token = (html) => {
      tokens.push(html);
      return `\uE000${tokens.length - 1}\uE001`;
    };
    let raw = source.replace(/`([^`\n]+)`/g, (_, code) => token(`<code>${escapeHtml(code)}</code>`));
    raw = raw.replace(/(?<!\\)\$(?!\$)([^$\n]+)(?<!\\)\$(?!\$)/g, (_, formula) => {
      try {
        return token(`<span class="md-inline-math" data-md-math="${escapeHtml(formula)}" contenteditable="false">${MarkdownEditorRenderers.renderMath(formula, false)}</span>`);
      } catch (error) {
        return token(`<span class="md-render-error" data-md-math="${escapeHtml(formula)}" title="${escapeHtml(error.message)}">LaTeX: ${escapeHtml(error.message)}</span>`);
      }
    });
    let html = escapeHtml(raw);
    html = html.replace(/!\[([^\]]*)\]\((https?:\/\/[^)\s]+)\)/g, (_, alt, src) =>
      `<img class="md-visual-image" alt="${alt}" src="${src}">`);
    html = html.replace(/\[([^\]]+)\]\((https?:\/\/[^)\s]+|mailto:[^)\s]+)\)/g, (_, label, href) =>
      `<a href="${safeUrl(href)}">${label}</a>`);
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/~~(.+?)~~/g, '<del>$1</del>');
    html = html.replace(/(^|[^*])\*([^*\n]+)\*/g, '$1<em>$2</em>');
    return html.replace(/\n/g, '<br>').replace(/\uE000(\d+)\uE001/g, (_, index) => tokens[Number(index)]);
  };

  const inlineMarkdown = (node) => {
    if (node.nodeType === Node.TEXT_NODE) return node.nodeValue ?? '';
    if (node.nodeType !== Node.ELEMENT_NODE) return '';
    const element = node;
    if (element.dataset.mdFiller) return '';
    if (element.dataset.mdMath !== undefined) return `$${element.dataset.mdMath}$`;
    if (element.tagName === 'BR') return '\n';
    if (element.tagName === 'IMG') {
      return `![${element.getAttribute('alt') ?? ''}](${element.getAttribute('src') ?? ''})`;
    }
    const content = Array.from(element.childNodes).map(inlineMarkdown).join('');
    if (!content && ['STRONG', 'B', 'EM', 'I', 'DEL', 'S', 'STRIKE', 'CODE', 'A'].includes(element.tagName)) return '';
    if (element.tagName === 'STRONG' || element.tagName === 'B') return `**${content}**`;
    if (element.tagName === 'EM' || element.tagName === 'I') return `*${content}*`;
    if (element.tagName === 'DEL' || element.tagName === 'S' || element.tagName === 'STRIKE') return `~~${content}~~`;
    if (element.tagName === 'CODE') return `\`${content}\``;
    if (element.tagName === 'A') {
      const href = safeUrl(element.getAttribute('href') ?? '');
      return href ? `[${content}](${href})` : content;
    }
    return content;
  };

  const ensureTrailingLine = (editable) => {
    editable.querySelectorAll(':scope > [data-md-filler]').forEach((node) => node.remove());
    if (editable.textContent.endsWith('\n') || editable.lastChild?.nodeName === 'BR') {
      // A final empty line needs a rendered caret stop in contenteditable.
      const filler = document.createElement('br');
      filler.dataset.mdFiller = 'true';
      editable.append(filler);
    }
  };

  const tableCells = (line) => line.trim().replace(/^\|/, '').replace(/\|$/, '')
    .split(/(?<!\\)\|/).map((cell) => cell.trim().replace(/\\\|/g, '|'));

  const parseTable = (markdown) => {
    const lines = markdown.split(/\r?\n/).filter((line) => line.trim().startsWith('|'));
    if (lines.length < 2) return [['Columna 1', 'Columna 2'], ['Dato', 'Dato']];
    const rows = lines.map(tableCells);
    const body = rows.slice(1).filter((row) => !row.every((cell) => /^:?-{3,}:?$/.test(cell)));
    const width = Math.max(1, ...rows.map((row) => row.length));
    return [rows[0], ...body].map((row) =>
      Array.from({ length: width }, (_, index) => row[index] ?? ''));
  };

  const tableAlignments = (markdown, width) => {
    const separator = markdown.split(/\r?\n/).filter((line) => line.trim().startsWith('|'))[1];
    if (!separator) return Array(width).fill('---');
    const cells = tableCells(separator);
    return Array.from({ length: width }, (_, index) => {
      const cell = cells[index] ?? '---';
      return /^:-+:$/.test(cell) ? ':---:' : /^-+:$/.test(cell) ? '---:' : /^:-+$/.test(cell) ? ':---' : '---';
    });
  };

  const listMarker = (line) => line.match(/^([ \t]*)([-+*]|\d+[.)])([ \t]+)(.*)$/);
  const indentation = (text) => text.replace(/\t/g, '    ').length;
  const listTextOffset = (item) => item.marker.length + 1 + (item.checked == null ? 0 : 4);
  const parseList = (markdown) => {
    const roots = [];
    const stack = [];
    let current = null;
    const lines = markdown.split(/\r?\n/);
    lines.forEach((line, lineIndex) => {
      const match = listMarker(line);
      if (!match) {
        const next = listMarker(lines[lineIndex + 1] ?? '');
        if (!line.trim() && current && next && indentation(next[1]) > current.indent
          && /^\d/.test(next[2]) && parseInt(next[2], 10) !== 1) return;
        const leading = indentation(line.match(/^[ \t]*/)?.[0] ?? '');
        const owner = [...stack].reverse().find((item) => leading >= item.indent + item.marker.length + 1);
        if (line.trim() && owner) current = owner;
        if (current) {
          const prefix = ' '.repeat(current.indent + listTextOffset(current));
          const fallback = ' '.repeat(current.indent + current.marker.length + 1);
          current.text += '\n' + (line.startsWith(prefix) ? line.slice(prefix.length)
            : line.startsWith(fallback) ? line.slice(fallback.length) : line.trimStart());
          current.lastLine = lineIndex;
        }
        return;
      }
      const indent = indentation(match[1]);
      while (stack.length && indent < stack.at(-1).indent + stack.at(-1).marker.length + 1) stack.pop();
      const parent = stack.at(-1) ?? null;
      const siblings = parent ? parent.children : roots;
      const task = match[4].match(/^\[([ xX])\](?:[ \t]+(.*)|$)/);
      const item = {
        marker: match[2], text: task ? task[2] ?? '' : match[4], checked: task ? /x/i.test(task[1]) : null, children: [],
        indent, line: lineIndex, lastLine: lineIndex,
      };
      siblings.push(item);
      stack.push(item);
      current = item;
    });
    return roots;
  };

  const listPathEntries = (items, prefix = []) => items.flatMap((item, index) => {
    const path = [...prefix, index];
    return [{ item, path }, ...listPathEntries(item.children, path)];
  });

  const listLocation = (items, path) => {
    let siblings = items;
    let parent = null;
    for (const index of path.slice(0, -1)) {
      parent = siblings[index];
      if (!parent) return null;
      siblings = parent.children;
    }
    const index = path.at(-1) ?? 0;
    return siblings[index] ? { item: siblings[index], siblings, index, parent } : null;
  };

  const numbered = (item) => /^\d/.test(item.marker);
  const listLines = (items, indent = 0, renumber = false) => {
    let nextNumber = null;
    return items.flatMap((item) => {
      if (numbered(item)) {
        if (nextNumber === null) nextNumber = parseInt(item.marker, 10);
        if (renumber) item.marker = `${nextNumber}${item.marker.at(-1)}`;
        nextNumber = parseInt(item.marker, 10) + 1;
      } else nextNumber = null;
      const prefix = ' '.repeat(indent);
      const [first, ...continuations] = item.text.split('\n');
      return [
        `${prefix}${item.marker} ${item.checked == null ? '' : `[${item.checked ? 'x' : ' '}] `}${first}`,
        ...continuations.map((line) => `${prefix}${' '.repeat(listTextOffset(item))}${line}`),
        ...(item.children.length && numbered(item.children[0])
          && parseInt(item.children[0].marker, 10) !== 1 ? [''] : []),
        ...listLines(item.children, indent + Math.max(4, item.marker.length + 1), renumber),
      ];
    });
  };

  const appendTaskCheckbox = (li, item, path = [], readOnly = false) => {
    if (item.checked == null) return;
    li.classList.add('md-task-item');
    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.className = 'md-task-checkbox';
    checkbox.dataset.path = path.join('.');
    checkbox.checked = item.checked;
    checkbox.defaultChecked = item.checked;
    checkbox.disabled = readOnly;
    checkbox.setAttribute('aria-label', `Tarea: ${item.text.split('\n')[0] || 'sin texto'}`);
    li.append(checkbox);
    return checkbox;
  };

  const renderList = (items, editable, prefix = [], readOnly = false) => {
    let list = null;
    let previousKind = null;
    items.forEach((item, index) => {
      const kind = numbered(item) ? 'ol' : 'ul';
      if (!list || previousKind !== kind) {
        list = document.createElement(kind);
        if (kind === 'ol') list.start = parseInt(item.marker, 10);
        editable.append(list);
      }
      previousKind = kind;
      const li = document.createElement('li');
      li.dataset.marker = item.marker;
      appendTaskCheckbox(li, item, [...prefix, index], readOnly);
      const text = document.createElement('div');
      text.className = 'md-list-text';
      text.dataset.path = [...prefix, index].join('.');
      text.contentEditable = String(!readOnly);
      text.dataset.placeholder = runtime.options.placeholder;
      text.innerHTML = inlineHtml(item.text);
      ensureTrailingLine(text);
      li.append(text);
      renderList(item.children, li, [...prefix, index], readOnly);
      list.append(li);
    });
  };

  const readList = (container) => Array.from(container.children)
    .filter((child) => child.matches('ul,ol'))
    .flatMap((list) => Array.from(list.children).filter((child) => child.tagName === 'LI')
      .map((li, index) => {
        const text = li.querySelector(':scope > .md-list-text');
        return {
          marker: li.dataset.marker ?? (list.tagName === 'OL' ? `${list.start + index}.` : '-'),
          checked: li.querySelector(':scope > .md-task-checkbox')?.checked ?? null,
          text: text ? Array.from(text.childNodes).map(inlineMarkdown).join('') : '',
          children: readList(li),
        };
      }));

  const quoteLines = (markdown) => markdown.split('\n').map((line) => {
    const match = line.match(/^((?:>\s*)+)(.*)$/);
    return { depth: match ? (match[1].match(/>/g) ?? []).length : 1, text: match?.[2] ?? line };
  });

  const formatQuote = (lines) => lines.flatMap((line, index) => {
    const previous = lines[index - 1];
    const separator = previous && previous.depth > line.depth
      && previous.text.trim() && line.text.trim() ? ['> '.repeat(line.depth).trimEnd()] : [];
    return [...separator, line.text ? '> '.repeat(line.depth) + line.text : '> '.repeat(line.depth).trimEnd()];
  }).join('\n');

  const renderQuote = (lines, editable, readOnly) => {
    const stack = [editable];
    lines.forEach((line, index) => {
      while (stack.length - 1 > line.depth) stack.pop();
      while (stack.length - 1 < line.depth) {
        const quote = document.createElement('blockquote');
        stack.at(-1).append(quote);
        stack.push(quote);
      }
      const text = document.createElement('div');
      text.className = 'md-quote-text';
      text.dataset.line = String(index);
      text.dataset.depth = String(line.depth);
      text.contentEditable = String(!readOnly);
      text.dataset.placeholder = runtime.options.placeholder;
      text.innerHTML = inlineHtml(line.text);
      ensureTrailingLine(text);
      stack.at(-1).append(text);
    });
  };

  const codeParts = (markdown) => {
    const match = markdown.match(/^```([^\n]*)\n?([\s\S]*?)\n?```$/);
    return match ? { language: match[1].trim(), body: match[2] } : { language: 'text', body: markdown };
  };

  const bodyForVisual = (markdown, type) => {
    if (type === 'math') return markdown.replace(/^\$\$\s*\n?/, '').replace(/\n?\$\$\s*$/, '');
    if (/^h[1-6]$/.test(type)) return markdown.replace(/^#{1,6}\s*/, '');
    if (type === 'quote') return markdown.split(/\r?\n/).map((line) => line.replace(/^>\s?/, '')).join('\n');
    if (type === 'list') return markdown.split(/\r?\n/).map((line) => line.replace(/^\s*[-*+]\s*/, '')).join('\n');
    if (type === 'ordered_list') return markdown.split(/\r?\n/).map((line) => line.replace(/^\s*\d+\.\s*/, '')).join('\n');
    if (type === 'code' || type === 'mermaid') return codeParts(markdown).body;
    if (type === 'table') return '';
    if (type === 'image') return '';
    if (type === 'link') return '';
    if (type === 'rule') return '';
    return markdown;
  };

  const renderVisualContent = (editable, markdown, type, article) => {
    editable.replaceChildren();
    if (type === 'table') {
      editable.contentEditable = 'false';
      const rows = parseTable(markdown);
      article.dataset.tableAlignments = JSON.stringify(tableAlignments(markdown, rows[0].length));
      const table = document.createElement('table');
      rows.forEach((row, rowIndex) => {
        const tr = document.createElement('tr');
        row.forEach((cell) => {
          const cellElement = document.createElement(rowIndex === 0 ? 'th' : 'td');
          cellElement.contentEditable = String(article.dataset.readonly !== 'true');
          cellElement.innerHTML = inlineHtml(cell).replace(/&lt;br\s*\/?&gt;/gi, '<br>');
          const alignment = tableAlignments(markdown, rows[0].length)[tr.children.length];
          cellElement.style.textAlign = alignment === ':---:' ? 'center' : alignment === '---:' ? 'right' : 'left';
          tr.append(cellElement);
        });
        table.append(tr);
      });
      editable.append(table);
      return;
    }
    if (type === 'image') {
      const match = markdown.match(/^!\[([^\]]*)\]\((https?:\/\/[^)\s]+)\)/);
      if (match) {
        const image = document.createElement('img');
        image.className = 'md-visual-image';
        image.alt = match[1];
        image.src = match[2];
        editable.append(image);
      } else {
        editable.textContent = markdown;
      }
      return;
    }
    if (type === 'link') {
      const match = markdown.match(/^\[([^\]]+)\]\((https?:\/\/[^)\s]+|mailto:[^)\s]+)\)$/);
      if (match) {
        const link = document.createElement('a');
        link.href = safeUrl(match[2]);
        link.innerHTML = inlineHtml(match[1]);
        editable.append(link);
      } else {
        editable.textContent = markdown;
      }
      return;
    }
    if (type === 'rule') {
      const rule = document.createElement('hr');
      rule.className = 'md-visual-rule';
      editable.append(rule);
      return;
    }
    if (isListType(type)) {
      editable.contentEditable = 'false';
      renderList(parseList(markdown), editable, [], article.dataset.readonly === 'true');
      return;
    }
    if (type === 'quote') {
      editable.contentEditable = 'false';
      renderQuote(quoteLines(markdown), editable, article.dataset.readonly === 'true');
      return;
    }
    const body = bodyForVisual(markdown, type);
    const parts = codeParts(markdown);
    if (type === 'code' || type === 'mermaid') article.dataset.language = parts.language || 'text';
    if (type === 'code' || type === 'mermaid' || type === 'math') editable.textContent = body;
    else editable.innerHTML = inlineHtml(body);
  };

  const blockMarkdownFromVisual = (editable, article) => {
    const type = article.dataset.type;
    if (type === 'math') return `$$\n${editable.textContent}\n$$`;
    if (type === 'table') {
      const rows = Array.from(editable.querySelectorAll('tr')).map((row) =>
        Array.from(row.querySelectorAll('th,td')).map((cell) =>
          inlineMarkdown(cell).replace(/\n/g, '<br>').replace(/\|/g, '\\|')));
      if (!rows.length) return '| Columna 1 | Columna 2 |\n| --- | --- |';
      const width = Math.max(1, ...rows.map((row) => row.length));
      const normalized = rows.map((row) => Array.from({ length: width }, (_, index) => row[index] ?? ''));
      const header = `| ${normalized[0].join(' | ')} |`;
      const alignments = JSON.parse(article.dataset.tableAlignments ?? '[]');
      const separator = `| ${normalized[0].map((_, index) => alignments[index] ?? '---').join(' | ')} |`;
      return [header, separator, ...normalized.slice(1).map((row) => `| ${row.join(' | ')} |`)].join('\n');
    }
    if (type === 'image') {
      const image = editable.querySelector('img');
      return image ? `![${image.alt}](${image.getAttribute('src') ?? ''})` : editable.textContent;
    }
    if (isListType(type)) {
      return listLines(readList(editable)).join('\n');
    }
    if (type === 'quote') {
      return formatQuote(Array.from(editable.querySelectorAll('.md-quote-text')).flatMap((text) =>
        Array.from(text.childNodes).map(inlineMarkdown).join('').split('\n').map((line) =>
          ({ depth: Number(text.dataset.depth), text: line }))));
    }
    if (type === 'link') {
      const link = editable.querySelector('a');
      const label = link ? Array.from(link.childNodes).map(inlineMarkdown).join('') : '';
      return link ? `[${label}](${link.getAttribute('href') ?? ''})` : editable.textContent;
    }
    if (type === 'rule') return '---';
    const body = Array.from(editable.childNodes).map(inlineMarkdown).join('');
    if (/^h[1-6]$/.test(type)) return `${'#'.repeat(Number(type.slice(1)))} ${body}`;
    if (type === 'quote') return body.split('\n').map((line) => `> ${line}`).join('\n');
    if (type === 'list') return body.split('\n').map((line) => `- ${line}`).join('\n');
    if (type === 'ordered_list') return body.split('\n').map((line, index) => `${index + 1}. ${line}`).join('\n');
    if (type === 'code' || type === 'mermaid') {
      const language = article.dataset.language || 'text';
      return `\`\`\`${language}\n${editable.textContent}\n\`\`\``;
    }
    return body;
  };

  const makeBlock = (item, { readOnly = false, mode = runtime.mode } = {}) => {
    const markdown = String(item.markdown ?? item.text ?? '');
    const type = blockType(markdown);
    const article = document.createElement('article');
    article.className = 'md-block';
    article.dataset.blockId = String(item.id ?? `block-${crypto.randomUUID()}`);
    article.dataset.type = type;
    article.dataset.mode = mode;
    article.dataset.readonly = String(readOnly);
    article.setAttribute('role', 'listitem');

    const head = document.createElement('div');
    head.className = 'md-block-head';
    const kind = document.createElement('span');
    kind.className = 'md-block-kind';
    kind.textContent = `${typeLabel(type)} · ${article.dataset.blockId}`;
    head.append(kind);

    const editable = document.createElement('div');
    editable.className = 'md-editable';
    editable.dataset.placeholder = runtime.options.placeholder;
    editable.contentEditable = String(!readOnly);
    editable.spellcheck = !readOnly;
    editable.setAttribute('role', 'textbox');
    editable.setAttribute('aria-multiline', 'true');
    if (mode === 'visual') renderVisualContent(editable, markdown, type, article);
    else editable.textContent = markdown;
    if (editable.contentEditable === 'true') ensureTrailingLine(editable);
    article.__source = markdown;
    article.__visualInitial = editable.innerHTML;

    article.append(head);
    if (mode === 'visual' && type === 'code') {
      const surface = document.createElement('div');
      surface.className = 'md-code-surface';
      const highlight = document.createElement('div');
      highlight.className = 'md-code-highlight';
      highlight.setAttribute('aria-hidden', 'true');
      surface.append(highlight, editable);
      article.append(surface);
    } else article.append(editable);
    if (mode === 'visual' && (type === 'math' || type === 'mermaid')) {
      editable.hidden = true;
      article.tabIndex = readOnly ? -1 : 0;
      const preview = document.createElement('div');
      preview.className = 'md-rendered-preview';
      preview.setAttribute('aria-label', type === 'math' ? 'Fórmula LaTeX' : 'Diagrama Mermaid');
      article.append(preview);
    }
    if (mode === 'visual') refreshRender(article);
    if (!readOnly) {
      const tools = document.createElement('div');
      tools.className = 'md-block-tools';
      const handle = document.createElement('button');
      handle.type = 'button';
      handle.className = 'md-drag-handle';
      handle.innerHTML = '<span class="md-icon" aria-hidden="true">drag_indicator</span>';
      handle.title = 'Arrastrar para reordenar';
      handle.setAttribute('aria-label', 'Arrastrar para reordenar bloque');
      handle.draggable = true;
      tools.append(handle);
      article.append(tools);
    }
    return article;
  };

  const refreshRender = (article, defer = false) => {
    const editable = article.querySelector('.md-editable');
    const preview = article.querySelector('.md-rendered-preview');
    const highlight = article.querySelector('.md-code-highlight');
    if (highlight) {
      const result = MarkdownEditorRenderers.highlightCode(editable.textContent, article.dataset.language ?? 'text');
      highlight.innerHTML = result.html;
      article.querySelector('.md-render-note')?.remove();
      if (!result.supported) {
        const note = document.createElement('div');
        note.className = 'md-render-note';
        note.textContent = `Sin resaltador para «${article.dataset.language}»; código en texto plano.`;
        article.append(note);
      }
    }
    if (!preview) return;
    if (defer) {
      if (article.__renderTimer) clearTimeout(article.__renderTimer);
      article.__renderTimer = setTimeout(() => {
        if (article.isConnected) refreshRender(article);
      }, 200);
      return;
    }
    const generation = (article.__renderGeneration ?? 0) + 1;
    article.__renderGeneration = generation;
    const showError = (error) => {
      if (article.__renderGeneration !== generation) return;
      preview.classList.add('md-render-error');
      preview.textContent = `${typeLabel(article.dataset.type)}: ${error.message}`;
    };
    preview.classList.remove('md-render-error');
    if (article.dataset.type === 'math') {
      try {
        preview.innerHTML = MarkdownEditorRenderers.renderMath(editable.textContent, true);
      } catch (error) { showError(error); }
    } else {
      preview.textContent = 'Renderizando Mermaid…';
      article.__renderPromise = MarkdownEditorRenderers.renderDiagram(editable.textContent).then((svg) => {
        if (article.__renderGeneration === generation && article.isConnected) preview.innerHTML = svg;
      }).catch(showError);
    }
  };

  const blockSource = (article) => {
    const editable = article.querySelector('.md-editable');
    if (article.dataset.mode === 'raw_visual') return editable.textContent.replace(/\r/g, '');
    return editable.innerHTML === article.__visualInitial
      ? article.__source : blockMarkdownFromVisual(editable, article);
  };

  const getBlocks = () => Array.from(canvas.querySelectorAll(':scope > .md-block')).map((article) => {
    const markdown = blockSource(article);
    const type = runtime.mode === 'visual' ? article.dataset.type : blockType(markdown);
    article.dataset.type = type;
    article.querySelector('.md-block-kind').textContent = `${typeLabel(type)} · ${article.dataset.blockId}`;
    return { id: article.dataset.blockId, type, markdown };
  });

  const buildValue = () => {
    const blocks = getBlocks();
    return { blocks, markdown: blocks.map((block) => block.markdown).join('\n\n'), mode: runtime.mode };
  };

  const documentFingerprint = (blocks) => JSON.stringify(blocks.map(({ id, markdown }) => ({ id, markdown })));
  const isDirty = () => documentFingerprint(getBlocks()) !== documentFingerprint(runtime.savedBlocks);
  const updateSaveControls = () => {
    const dirty = !runtime.onlyView && isDirty();
    saveButton.hidden = runtime.saveMode !== 'button';
    saveButton.disabled = !dirty;
    reviewButton.hidden = runtime.saveMode !== 'button' || !dirty;
    syncToolbarSections();
    return dirty;
  };

  const publish = (force = false) => {
    const value = buildValue();
    const serialized = JSON.stringify(value);
    const dirty = updateSaveControls();
    if (serialized === runtime.lastPublished) {
      if (force) {
        runtime.savedBlocks = value.blocks.map(({ id, markdown }) => ({ id, markdown }));
        updateSaveControls();
      }
      status.textContent = `${value.blocks.length} bloques · ${value.markdown.length} caracteres · Guardado`;
      return;
    }
    if (!force && runtime.saveMode === 'button') {
      status.textContent = `${value.blocks.length} bloques · ${dirty ? 'Cambios sin guardar' : 'Guardado'}`;
      return;
    }
    runtime.lastPublished = serialized;
    runtime.savedFingerprint = serialized;
    runtime.savedBlocks = value.blocks.map(({ id, markdown }) => ({ id, markdown }));
    updateSaveControls();
    status.textContent = `${value.blocks.length} bloques · ${value.markdown.length} caracteres`;
    runtime.setStateValue('value', value);
  };

  const schedulePublish = () => {
    if (runtime.timer) clearTimeout(runtime.timer);
    runtime.timer = setTimeout(() => publish(), 180);
    const dirty = updateSaveControls();
    if (runtime.saveMode === 'button') status.textContent = dirty ? 'Cambios sin guardar' : 'Guardado';
  };

  const snapshot = () => JSON.stringify(getBlocks().map(({ id, markdown }) => ({ id, markdown })));

  const updateHistoryButtons = () => {
    const undo = toolbar.querySelector('[data-history="undo"]');
    const redo = toolbar.querySelector('[data-history="redo"]');
    undo.disabled = runtime.history.length <= 1;
    redo.disabled = runtime.redo.length === 0;
  };

  const pushHistory = () => {
    const current = snapshot();
    runtime.historySelections ??= new Map();
    runtime.historySelections.set(current, captureBookmark() ?? runtime.bookmark);
    if (runtime.history.at(-1) === current) return;
    runtime.history.push(current);
    if (runtime.history.length > 100) runtime.historySelections.delete(runtime.history.shift());
    runtime.redo.length = 0;
    updateHistoryButtons();
  };

  const scheduleHistory = () => {
    if (runtime.historyTimer) clearTimeout(runtime.historyTimer);
    runtime.historyTimer = setTimeout(() => {
      runtime.historyTimer = null;
      pushHistory();
    }, 350);
  };

  const flushHistory = () => {
    if (runtime.historyTimer) clearTimeout(runtime.historyTimer);
    runtime.historyTimer = null;
    pushHistory();
  };

  const setBlockMarkdown = (block, markdown, caret = null) => {
    floatingMenu.hidden = true;
    runtime.menuBlock = null;
    const replacement = makeBlock({ id: block.dataset.blockId, markdown });
    block.replaceWith(replacement);
    runtime.activeBlock = replacement;
    const editable = replacement.querySelector('.md-editable');
    if (caret !== null) setCaret(editable, caret);
    else if (editable.hidden) replacement.focus();
    else (replacement.querySelector('[contenteditable="true"]') ?? editable).focus();
    return replacement;
  };

  const renderBlocks = (blocks, { resetHistory = false, publishValue = true } = {}) => {
    floatingMenu.hidden = true;
    runtime.menuBlock = null;
    canvas.replaceChildren(...blocks.map((item) => makeBlock(item)));
    runtime.activeBlock = null;
    if (resetHistory) {
      runtime.history = [snapshot()];
      runtime.redo = [];
      runtime.historySelections = new Map();
      updateHistoryButtons();
    }
    if (publishValue) publish(true);
  };

  const performUndo = () => {
    flushHistory();
    if (runtime.history.length <= 1) return;
    runtime.redo.push(runtime.history.pop());
    const previous = JSON.parse(runtime.history.at(-1));
    renderBlocks(previous, { publishValue: false });
    restoreBookmark(runtime.historySelections?.get(runtime.history.at(-1)));
    updateHistoryButtons();
    schedulePublish();
  };

  const performRedo = () => {
    flushHistory();
    if (!runtime.redo.length) return;
    const next = runtime.redo.pop();
    runtime.history.push(next);
    renderBlocks(JSON.parse(next), { publishValue: false });
    restoreBookmark(runtime.historySelections?.get(next));
    updateHistoryButtons();
    schedulePublish();
  };

  const setCaret = (editable, position) => {
    ensureTrailingLine(editable);
    editable.focus();
    const range = document.createRange();
    const walker = document.createTreeWalker(editable, NodeFilter.SHOW_TEXT);
    let node = walker.nextNode();
    let remaining = Math.max(position, 0);
    while (node && remaining > node.textContent.length) {
      remaining -= node.textContent.length;
      node = walker.nextNode();
    }
    if (!node) {
      node = document.createTextNode('');
      editable.append(node);
    }
    range.setStart(node, Math.min(remaining, node.textContent.length));
    range.collapse(true);
    const selection = window.getSelection();
    selection.removeAllRanges();
    selection.addRange(range);
  };

  const selectionOffsets = (editable) => {
    const selection = window.getSelection();
    if (!selection || selection.rangeCount === 0 || !editable.contains(selection.anchorNode)) {
      const end = editable.textContent.length;
      return { start: end, end };
    }
    const range = selection.getRangeAt(0);
    const before = document.createRange();
    before.selectNodeContents(editable);
    before.setEnd(range.startContainer, range.startOffset);
    const selected = range.toString().length;
    return { start: before.toString().length, end: before.toString().length + selected };
  };

  const activate = (block) => {
    canvas.querySelectorAll('.md-block.is-active').forEach((item) => item.classList.remove('is-active'));
    block.classList.add('is-active');
    runtime.activeBlock = block;
    typeSelector.value = blockType(blockSource(block));
  };

  const selectedLeaf = (block) => {
    const checkbox = document.activeElement;
    if (checkbox?.matches('.md-task-checkbox') && block.contains(checkbox)) {
      return checkbox.closest('li').querySelector(':scope > .md-list-text');
    }
    const anchor = window.getSelection()?.anchorNode;
    const element = anchor?.nodeType === Node.ELEMENT_NODE ? anchor : anchor?.parentElement;
    return element && block.contains(element)
      ? element.closest('.md-list-text,.md-quote-text,th,td,.md-editable') : null;
  };

  const captureBookmark = () => {
    const selection = window.getSelection();
    if (!selection?.rangeCount) return null;
    const element = selection.anchorNode?.nodeType === Node.ELEMENT_NODE
      ? selection.anchorNode : selection.anchorNode?.parentElement;
    const block = element?.closest('.md-block');
    if (!block || !canvas.contains(block)) return null;
    const leaf = selectedLeaf(block);
    if (!leaf || !leaf.contains(selection.getRangeAt(0).endContainer)) return null;
    return {
      id: block.dataset.blockId, path: leaf.dataset.path, line: leaf.dataset.line,
      row: leaf.closest('tr')?.rowIndex, column: leaf.cellIndex,
      ...selectionOffsets(leaf),
    };
  };

  const restoreBookmark = (bookmark) => {
    if (!bookmark) return;
    const block = Array.from(canvas.children).find((item) => item.dataset.blockId === bookmark.id);
    if (!block) return;
    const leaf = bookmark.path !== undefined
      ? Array.from(block.querySelectorAll('.md-list-text')).find((text) => text.dataset.path === bookmark.path)
      : bookmark.line !== undefined
        ? Array.from(block.querySelectorAll('.md-quote-text')).find((text) => text.dataset.line === bookmark.line)
        : bookmark.row !== undefined
          ? block.querySelector('table')?.rows[bookmark.row]?.cells[bookmark.column]
          : block.querySelector('.md-editable');
    if (!leaf) return;
    setCaret(leaf, bookmark.start);
    if (bookmark.end !== bookmark.start) {
      const walker = document.createTreeWalker(leaf, NodeFilter.SHOW_TEXT);
      let node;
      let remaining = bookmark.end;
      while ((node = walker.nextNode())) {
        if (remaining <= node.textContent.length) {
          window.getSelection().getRangeAt(0).setEnd(node, remaining);
          break;
        }
        remaining -= node.textContent.length;
      }
    }
    runtime.bookmark = bookmark;
    activate(block);
  };

  const rawContext = (block) => {
    const source = blockSource(block);
    const editable = block.querySelector('.md-editable');
    const { start, end } = selectionOffsets(editable);
    const line = source.slice(0, start).split('\n').length - 1;
    const lineStart = source.lastIndexOf('\n', start - 1) + 1;
    return { source, start, end, line, lineStart, column: start - lineStart };
  };

  const splitLeaf = (leaf) => {
    const selection = window.getSelection();
    if (!selection?.rangeCount || !leaf.contains(selection.anchorNode)) {
      return { before: Array.from(leaf.childNodes).map(inlineMarkdown).join(''), after: '' };
    }
    const selected = selection.getRangeAt(0);
    const before = document.createRange();
    before.selectNodeContents(leaf);
    before.setEnd(selected.startContainer, selected.startOffset);
    const after = document.createRange();
    after.selectNodeContents(leaf);
    after.setStart(selected.endContainer, selected.endOffset);
    return {
      before: Array.from(before.cloneContents().childNodes).map(inlineMarkdown).join(''),
      after: Array.from(after.cloneContents().childNodes).map(inlineMarkdown).join(''),
    };
  };

  const updateText = (editable, value, caret) => {
    if (runtime.mode === 'visual') {
      editable.innerHTML = inlineHtml(value);
    } else {
      editable.textContent = value;
    }
    setCaret(editable, caret);
    if (runtime.mode === 'visual') refreshRender(editable.closest('.md-block'));
    scheduleHistory();
    schedulePublish();
  };

  const insertAtSelection = (editable, insertedText) => {
    if (runtime.mode === 'visual') {
      const selection = window.getSelection();
      if (!selection || !selection.rangeCount || !editable.contains(selection.anchorNode)) return;
      const range = selection.getRangeAt(0);
      range.deleteContents();
      const textNode = document.createTextNode(insertedText);
      range.insertNode(textNode);
      range.setStart(textNode, insertedText.length);
      ensureTrailingLine(editable);
      range.collapse(true);
      selection.removeAllRanges();
      selection.addRange(range);
      refreshRender(editable.closest('.md-block'));
      scheduleHistory();
      schedulePublish();
      return;
    }
    const text = editable.textContent;
    const { start, end } = selectionOffsets(editable);
    updateText(editable, text.slice(0, start) + insertedText + text.slice(end), start + insertedText.length);
  };

  const wrapSelection = (format) => {
    const editable = runtime.activeBlock?.querySelector('.md-editable');
    if (!editable) return;
    flushHistory();
    if (runtime.mode === 'visual') {
      const selection = window.getSelection();
      if (!selection || !selection.rangeCount || !editable.contains(selection.anchorNode)) return;
      const range = selection.getRangeAt(0);
      const tag = format === '**' ? 'strong' : format === '*' ? 'em' : format === '~~' ? 'del' : 'code';
      const wrapper = document.createElement(tag);
      const content = range.collapsed ? document.createTextNode('texto') : range.extractContents();
      wrapper.append(content);
      range.insertNode(wrapper);
      range.selectNodeContents(wrapper);
      selection.removeAllRanges();
      selection.addRange(range);
      flushHistory();
      schedulePublish();
      return;
    }
    const text = editable.textContent;
    const { start, end } = selectionOffsets(editable);
    const selectedText = text.slice(start, end) || 'texto';
    const wrapped = `${format}${selectedText}${format}`;
    const next = text.slice(0, start) + wrapped + text.slice(end);
    updateText(editable, next, start + wrapped.length);
    flushHistory();
  };

  const templates = {
    paragraph: 'Escribe un párrafo…', h1: '# Título', h2: '## Subtítulo', h3: '### Sección',
    h4: '#### Título 4', h5: '##### Título 5', h6: '###### Título 6',
    quote: '> Escribe una cita…', list: '- Nuevo elemento', ordered_list: '1. Nuevo elemento',
    task_list: '- [ ] Nueva tarea',
    code: '```python\n# Escribe código aquí\n```',
    table: '| Columna 1 | Columna 2 |\n| --- | --- |\n| Dato | Dato |',
    image: '![Descripción de la imagen](https://placehold.co/640x360)', link: '[Texto del enlace](https://example.com)',
    mermaid: '```mermaid\nflowchart TD\n    A[Inicio] --> B[Fin]\n```', rule: '---',
    math: '$$\nE = mc^2\n$$',
  };

  const convertBlockMarkdown = (type, markdown) => {
    const currentType = blockType(markdown);
    if (isListType(type) && isListType(currentType)) {
      const items = parseList(markdown);
      listPathEntries(items).forEach(({ item, path }) => {
        item.checked = type === 'task_list' ? item.checked ?? false : null;
        item.marker = type === 'ordered_list' ? `${path.at(-1) + 1}.` : '-';
      });
      return listLines(items, 0, true).join('\n');
    }
    let body = markdown;
    if (/^h[1-6]$/.test(currentType)) body = body.replace(/^#{1,6}\s*/, '');
    else if (currentType === 'quote') body = body.replace(/^(?:>\s*)+/gm, '');
    else if (isListType(currentType)) body = body.replace(/^\s*(?:[-*+]|\d+[.)])\s+(?:\[[ xX]\](?:[ \t]+|$))?/gm, '');
    else if (currentType === 'code' || currentType === 'mermaid') {
      body = body.replace(/^```[^\n]*\n?/, '').replace(/\n?```\s*$/, '');
    }
    else if (currentType === 'math') body = bodyForVisual(body, 'math');

    if (type === 'paragraph') return body;
    if (/^h[1-6]$/.test(type)) return `${'#'.repeat(Number(type.slice(1)))} ${body}`;
    if (type === 'quote') return body.split('\n').map((line) => `> ${line}`).join('\n');
    if (type === 'list') return body.split('\n').map((line) => `- ${line}`).join('\n');
    if (type === 'ordered_list') return body.split('\n').map((line, index) => `${index + 1}. ${line}`).join('\n');
    if (type === 'task_list') return body.split('\n').map((line) => `- [ ] ${line}`).join('\n');
    if (type === 'code') return `\`\`\`text\n${body || 'Escribe código aquí'}\n\`\`\``;
    if (type === 'mermaid') return `\`\`\`mermaid\n${body || 'flowchart TD\n    A[Inicio] --> B[Fin]'}\n\`\`\``;
    if (type === 'math') return `$$\n${body || 'E = mc^2'}\n$$`;
    if (type === 'table') return currentType === 'table' ? markdown : templates.table;
    if (type === 'image' || type === 'link' || type === 'rule') return templates[type];
    return markdown;
  };

  const addBlock = (type, afterBlock, before = false, markdown = null) => {
    flushHistory();
    const item = { id: `block-${crypto.randomUUID()}`, markdown: markdown ?? templates[type] ?? templates.paragraph };
    const block = makeBlock(item);
    if (afterBlock?.parentElement === canvas) {
      if (before) afterBlock.before(block);
      else afterBlock.after(block);
    }
    else canvas.append(block);
    runtime.activeBlock = block;
    block.classList.add('is-active');
    activate(block);
    if (block.querySelector('.md-editable').hidden) block.focus();
    else setCaret(block.querySelector('[contenteditable="true"]') ?? block.querySelector('.md-editable'), 0);
    flushHistory();
    schedulePublish();
    return block;
  };

  const replaceBlocks = (blocks) => {
    if (runtime.timer) clearTimeout(runtime.timer);
    if (runtime.historyTimer) clearTimeout(runtime.historyTimer);
    runtime.timer = null;
    runtime.historyTimer = null;
    runtime.reviewing = false;
    runtime.onlyView = false;
    runtime.requestedMode = null;
    runtime.savedBlocks = [];
    const normalized = Array.isArray(blocks) ? blocks : [];
    renderBlocks(normalized.length ? normalized : [{ markdown: '' }], { resetHistory: true });
  };

  const markdownBlocks = (source) => {
    const lines = String(source ?? '').split(/\r?\n/);
    const blocks = [];
    let current = [];
    let fence = '';
    const flush = () => {
      const markdown = current.join('\n').trim();
      if (markdown) blocks.push({ markdown });
      current = [];
    };
    lines.forEach((line, index) => {
      const marker = /^\s*```/.test(line) ? 'code' : /^\s*\$\$\s*$/.test(line) ? 'math' : '';
      if (marker && (!fence || fence === marker)) {
        if (!fence && current.length) flush();
        current.push(line);
        fence = fence ? '' : marker;
        if (!fence) flush();
      } else if (!fence && !line.trim()) {
        const list = isListType(blockType(current.join('\n')));
        if (list && /^\s{2,}\S/.test(lines[index + 1] ?? '')) current.push(line);
        else flush();
      } else {
        current.push(line);
      }
    });
    flush();
    return blocks;
  };

  const reviewSources = () => {
    if (runtime.reviewing) return runtime.reviewData;
    const diff = runtime.externalDiff;
    if (!diff) return null;
    return {
      before: diff.before,
      after: diff.after,
      beforeBlocks: diff.before_blocks ?? markdownBlocks(diff.before),
      afterBlocks: diff.after_blocks ?? markdownBlocks(diff.after),
    };
  };

  const visualVersion = (title, blocks) => {
    const section = document.createElement('section');
    const heading = document.createElement('h4');
    heading.textContent = title;
    const body = document.createElement('div');
    body.className = 'md-diff-canvas';
    body.append(...blocks.map((item) => makeBlock(item, { readOnly: true, mode: 'visual' })));
    section.append(heading, body);
    return section;
  };

  const renderSourceDiff = (before, after) => {
    const table = document.createElement('table');
    table.className = 'md-source-diff';
    table.setAttribute('aria-label', 'Diff Markdown: eliminaciones e inserciones');
    let oldLine = 1;
    let newLine = 1;
    for (const chunk of MarkdownEditorRenderers.diffLines(before, after)) {
      const lines = chunk.value.split('\n');
      if (lines.at(-1) === '') lines.pop();
      for (const line of lines) {
        const row = document.createElement('tr');
        row.className = chunk.added ? 'md-diff-added' : chunk.removed ? 'md-diff-removed' : '';
        for (const [number, label] of [
          [chunk.added ? '' : oldLine++, 'Línea anterior'],
          [chunk.removed ? '' : newLine++, 'Línea nueva'],
        ]) {
          const cell = document.createElement('td');
          cell.className = 'md-diff-line-number';
          cell.textContent = String(number);
          cell.title = label;
          row.append(cell);
        }
        const marker = document.createElement('td');
        marker.className = 'md-diff-marker';
        marker.textContent = chunk.added ? '+' : chunk.removed ? '−' : ' ';
        const content = document.createElement('td');
        const code = document.createElement('code');
        code.textContent = line || ' ';
        content.append(code);
        row.append(marker, content);
        table.append(row);
      }
    }
    if (!table.childElementCount) {
      const empty = document.createElement('p');
      empty.textContent = 'Ambas versiones están vacías.';
      return empty;
    }
    return table;
  };

  const hashBlock = (value) => {
    let hash = 14695981039346656037n;
    for (let index = 0; index < value.length; index++) {
      hash = BigInt.asUintN(64, (hash ^ BigInt(value.charCodeAt(index))) * 1099511628211n);
    }
    return hash.toString(16);
  };

  const compareBlocks = (beforeBlocks, afterBlocks) => {
    const records = (blocks) => blocks.map((block, index) => {
      const type = blockType(block.markdown);
      const content = `${type}\0${block.markdown}`;
      return { ...block, type, index, content, contentHash: hashBlock(content), orderHash: hashBlock(`${index}\0${content}`) };
    });
    const before = records(beforeBlocks);
    const after = records(afterBlocks);
    const matches = new Map();
    const used = new Set();
    const moveCandidates = new Set();
    const compatibleIds = (old, next) => !old.id || !next.id || old.id === next.id;
    const uniqueContent = (old, next) => before.filter((item) => item.content === old.content).length === 1
      && after.filter((item) => item.content === next.content).length === 1;
    const match = (next, old, canMove = false) => {
      matches.set(next.index, old);
      used.add(old.index);
      if (canMove) moveCandidates.add(next.index);
    };
    for (const next of after) {
      const old = next.id && before.find((item) => item.id === next.id && item.type === next.type);
      if (old) match(next, old, true);
    }
    for (const next of after.filter((item) => !matches.has(item.index))) {
      const old = before[next.index];
      if (old && !used.has(old.index) && compatibleIds(old, next)
        && old.orderHash === next.orderHash && old.content === next.content) match(next, old, uniqueContent(old, next));
    }
    for (const next of after.filter((item) => !matches.has(item.index))) {
      const candidates = before.filter((old) => !used.has(old.index) && compatibleIds(old, next)
        && old.contentHash === next.contentHash && old.content === next.content);
      const occurrences = after.filter((item) => !matches.has(item.index) && item.content === next.content);
      if (candidates.length === 1 && occurrences.length === 1) match(next, candidates[0], uniqueContent(candidates[0], next));
    }
    for (const next of after.filter((item) => !matches.has(item.index))) {
      const old = before[next.index];
      if (old && !used.has(old.index) && old.type === next.type && compatibleIds(old, next)) match(next, old);
    }
    // An insertion shifts indices but does not move the surviving sequence.
    const sequence = [...matches].sort(([a], [b]) => a - b);
    const lengths = sequence.map(() => 1);
    const previous = sequence.map(() => -1);
    for (let index = 0; index < sequence.length; index++) {
      for (let other = 0; other < index; other++) {
        if (sequence[other][1].index < sequence[index][1].index && lengths[other] + 1 > lengths[index]) {
          lengths[index] = lengths[other] + 1;
          previous[index] = other;
        }
      }
    }
    const stable = new Set();
    let position = lengths.indexOf(Math.max(...lengths));
    while (position >= 0) {
      stable.add(sequence[position][0]);
      position = previous[position];
    }
    return {
      before, after, matches, used, stable, moveCandidates,
      ambiguous: before.some((old) => !old.id && before.filter((item) => item.content === old.content).length > 1)
        || after.some((next) => !next.id && after.filter((item) => item.content === next.content).length > 1),
    };
  };

  const plainBlockContent = (item) => {
    if (item.type === 'link' || item.type === 'image') return item.markdown;
    if (item.type === 'code' || item.type === 'mermaid') return codeParts(item.markdown).body;
    if (item.type === 'math') return bodyForVisual(item.markdown, 'math');
    if (item.type === 'table') return parseTable(item.markdown).map((row) => row.join(' | ')).join('\n');
    const source = item.type === 'quote' ? quoteLines(item.markdown).map((line) => line.text).join('\n')
      : isListType(item.type)
        ? listPathEntries(parseList(item.markdown)).map(({ item }) =>
          `${item.checked == null ? '' : `[${item.checked ? 'x' : ' '}] `}${item.text}`).join('\n')
        : bodyForVisual(item.markdown, item.type);
    const element = document.createElement('div');
    element.innerHTML = inlineHtml(source);
    element.querySelectorAll('[data-md-math]').forEach((math) =>
      math.replaceWith(document.createTextNode(`$${math.dataset.mdMath}$`)));
    element.querySelectorAll('br').forEach((line) => line.replaceWith(document.createTextNode('\n')));
    return element.textContent;
  };

  const textPoint = (element, position) => {
    const walker = document.createTreeWalker(element, NodeFilter.SHOW_TEXT);
    let node;
    while ((node = walker.nextNode())) {
      if (position <= node.textContent.length) return [node, position];
      position -= node.textContent.length;
    }
    return [element, element.childNodes.length];
  };

  const annotateText = (target, original) => {
    if (target.innerHTML === original.innerHTML) return;
    if (target.textContent === original.textContent
      || target.querySelector('math,img,svg') || original.querySelector('math,img,svg')
      || [...target.querySelectorAll('a')].map((link) => link.href).join('\n')
        !== [...original.querySelectorAll('a')].map((link) => link.href).join('\n')) {
      const removed = document.createElement('span');
      removed.className = 'md-inline-removed';
      removed.append(...Array.from(original.childNodes, (node) => node.cloneNode(true)));
      const added = document.createElement('span');
      added.className = 'md-inline-added';
      added.append(...target.childNodes);
      target.append(removed, added);
      return;
    }
    const changes = MarkdownEditorRenderers.diffWordsWithSpace(original.textContent, target.textContent);
    const operations = [];
    let offset = 0;
    let oldOffset = 0;
    for (const change of changes) {
      if (change.removed) operations.push({
        start: offset, end: offset, oldStart: oldOffset, oldEnd: oldOffset + change.value.length, removed: true,
      });
      else {
        if (change.added) operations.push({ start: offset, end: offset + change.value.length, removed: false });
        offset += change.value.length;
      }
      if (!change.added) oldOffset += change.value.length;
    }
    for (const operation of operations.reverse()) {
      const range = document.createRange();
      range.setStart(...textPoint(target, operation.start));
      range.setEnd(...textPoint(target, operation.end));
      const span = document.createElement('span');
      span.className = operation.removed ? 'md-inline-removed' : 'md-inline-added';
      if (operation.removed) {
        const oldRange = document.createRange();
        oldRange.setStart(...textPoint(original, operation.oldStart));
        oldRange.setEnd(...textPoint(original, operation.oldEnd));
        let fragment = oldRange.cloneContents();
        let ancestor = oldRange.commonAncestorContainer.nodeType === Node.ELEMENT_NODE
          ? oldRange.commonAncestorContainer : oldRange.commonAncestorContainer.parentElement;
        while (ancestor && ancestor !== original) {
          const wrapper = ancestor.cloneNode(false);
          wrapper.append(fragment);
          fragment = wrapper;
          ancestor = ancestor.parentElement;
        }
        span.append(fragment);
      }
      else span.append(range.extractContents());
      range.insertNode(span);
    }
  };

  const sequenceEntries = (before, after, key = (value) => value) => {
    const chunks = MarkdownEditorRenderers.diffArrays(before, after, {
      comparator: (old, next) => key(old) === key(next),
    });
    const entries = [];
    let oldIndex = 0;
    let newIndex = 0;
    for (let index = 0; index < chunks.length; index++) {
      const chunk = chunks[index];
      const replacement = chunk.removed && chunks[index + 1]?.added ? chunks[++index] : null;
      if (replacement) {
        for (let position = 0; position < Math.max(chunk.count, replacement.count); position++) {
          entries.push({
            before: position < chunk.count ? oldIndex++ : undefined,
            after: position < replacement.count ? newIndex++ : undefined,
          });
        }
      } else for (let position = 0; position < chunk.count; position++) {
        entries.push({ before: chunk.added ? undefined : oldIndex++, after: chunk.removed ? undefined : newIndex++ });
      }
    }
    return entries;
  };

  const markPresence = (element, old, next) => {
    if (!old && next) element.classList.add('md-inline-added');
    else if (old && !next) element.classList.add('md-inline-removed');
  };

  const diffList = (before, after, container) => {
    let list;
    for (const entry of sequenceEntries(before, after, (item) => `${numbered(item)}\0${item.checked}\0${item.text}`)) {
      const old = before[entry.before];
      const next = after[entry.after];
      const item = next ?? old;
      const kind = numbered(item) ? 'ol' : 'ul';
      if (!list || list.localName !== kind) {
        list = document.createElement(kind);
        if (kind === 'ol') list.start = parseInt(item.marker, 10);
        container.append(list);
      }
      const li = document.createElement('li');
      if (kind === 'ol') li.value = parseInt(item.marker, 10);
      const checkbox = appendTaskCheckbox(li, item, [], true);
      const text = document.createElement('div');
      text.className = 'md-list-text';
      text.innerHTML = inlineHtml(item.text);
      li.append(text);
      markPresence(li, old, next);
      if (old && next) {
        const original = document.createElement('div');
        original.innerHTML = inlineHtml(old.text);
        annotateText(text, original);
        if (old.marker !== next.marker) {
          text.title = `Marcador anterior: ${old.marker} · Nuevo: ${next.marker}`;
          li.classList.add('md-list-marker-changed');
        }
        if (old.checked !== next.checked) {
          li.classList.add('md-task-state-changed');
          const describe = (checked) => checked == null ? 'sin checkbox' : checked ? 'completada' : 'pendiente';
          const message = `Estado anterior: ${describe(old.checked)} · Nuevo: ${describe(next.checked)}`;
          text.title = [text.title, message].filter(Boolean).join(' · ');
          if (checkbox) {
            checkbox.classList.add('md-inline-added');
            checkbox.title = message;
          }
          if (old.checked != null) {
            const oldCheckbox = appendTaskCheckbox(document.createElement('li'), old, [], true);
            oldCheckbox.classList.add('md-inline-removed');
            oldCheckbox.title = message;
            if (checkbox) {
              const states = document.createElement('span');
              states.className = 'md-task-diff-controls';
              checkbox.replaceWith(states);
              states.append(oldCheckbox, checkbox);
            } else {
              li.classList.add('md-task-item');
              li.prepend(oldCheckbox);
            }
          }
        }
      }
      diffList(old?.children ?? [], next?.children ?? [], li);
      list.append(li);
    }
  };

  const diffTable = (article, oldArticle) => {
    const editable = article.querySelector('.md-editable');
    const oldRows = [...oldArticle.querySelector('table').rows];
    const newRows = [...editable.querySelector('table').rows];
    const columns = sequenceEntries([...oldRows[0].cells], [...newRows[0].cells], (cell) => cell.textContent);
    const shared = columns.filter((entry) => entry.before !== undefined && entry.after !== undefined);
    const rows = [
      { before: 0, after: 0 },
      ...sequenceEntries(oldRows.slice(1), newRows.slice(1), (row) =>
        shared.map((column) => row.cells[oldRows.includes(row) ? column.before : column.after]?.textContent ?? '').join('\0'))
        .map((entry) => ({
          before: entry.before === undefined ? undefined : entry.before + 1,
          after: entry.after === undefined ? undefined : entry.after + 1,
        })),
    ];
    const table = document.createElement('table');
    for (const row of rows) {
      const old = oldRows[row.before];
      const next = newRows[row.after];
      const tr = document.createElement('tr');
      markPresence(tr, old, next);
      for (const column of columns) {
        const original = old?.cells[column.before];
        const updated = next?.cells[column.after];
        const cell = (updated ?? original)?.cloneNode(true)
          ?? document.createElement(row.after === 0 || row.before === 0 ? 'th' : 'td');
        markPresence(cell, original, updated);
        if (original && updated) annotateText(cell, original);
        tr.append(cell);
      }
      table.append(tr);
    }
    editable.replaceChildren(table);
  };

  const markContentChanges = (article, old, next) => {
    const editable = article.querySelector('.md-editable');
    const inline = runtime.options.blockDiffStyle === 'inline';
    const simple = (next.type === 'paragraph' || /^h[1-6]$/.test(next.type))
      && !editable.querySelector('math,img,br') && !next.markdown.includes('\n');
    if (simple || (inline && ['paragraph', 'link', 'image', 'code', 'list', 'ordered_list', 'task_list', 'quote', 'table'].includes(next.type))) {
      const original = makeBlock(old, { readOnly: true, mode: 'visual' });
      if (next.type === 'table') diffTable(article, original);
      else if (isListType(next.type)) {
        editable.replaceChildren();
        diffList(parseList(old.markdown), parseList(next.markdown), editable);
      } else if (next.type === 'quote') {
        const before = quoteLines(old.markdown);
        const after = quoteLines(next.markdown);
        const entries = sequenceEntries(before, after, (line) => `${line.depth}\0${line.text}`);
        editable.replaceChildren();
        renderQuote(entries.map((entry) => after[entry.after] ?? before[entry.before]), editable, true);
        editable.querySelectorAll('.md-quote-text').forEach((text, index) => {
          const entry = entries[index];
          const oldLine = before[entry.before];
          const newLine = after[entry.after];
          markPresence(text, oldLine, newLine);
          if (oldLine && newLine) {
            const oldText = document.createElement('div');
            oldText.innerHTML = inlineHtml(oldLine.text);
            annotateText(text, oldText);
          }
        });
      } else {
        annotateText(article.querySelector('.md-code-highlight') ?? editable,
          original.querySelector('.md-code-highlight') ?? original.querySelector('.md-editable'));
        if (next.type === 'code') article.querySelector('.md-code-surface').classList.add('md-inline-code-diff');
      }
      return;
    }
    const diff = document.createElement('div');
    diff.className = 'md-inline-content-diff';
    diff.setAttribute('aria-label', 'Cambios en el contenido de este bloque');
    const label = document.createElement('div');
    label.className = 'md-content-diff-label';
    label.textContent = 'Cambios de contenido · comparación separada';
    diff.append(label);
    if (inline) {
      const notice = document.createElement('div');
      notice.className = 'md-render-note';
      notice.textContent = 'Los cambios se muestran aparte para conservar el renderizado del bloque.';
      diff.append(notice);
    }
    for (const change of MarkdownEditorRenderers.diffWordsWithSpace(plainBlockContent(old), plainBlockContent(next))) {
      const span = document.createElement('span');
      span.className = change.added ? 'md-inline-added' : change.removed ? 'md-inline-removed' : '';
      span.textContent = change.value;
      diff.append(span);
    }
    article.append(diff);
  };

  const renderBlockDiff = (sources) => {
    const comparison = compareBlocks(sources.beforeBlocks, sources.afterBlocks);
    const container = document.createElement('div');
    const summary = document.createElement('div');
    summary.className = 'md-diff-summary';
    const removed = comparison.before.filter((item) => !comparison.used.has(item.index));
    const added = comparison.after.filter((item) => !comparison.matches.has(item.index));
    const changed = comparison.after.filter((item) => comparison.matches.get(item.index)?.content !== item.content
      && comparison.matches.has(item.index));
    const moved = comparison.after.filter((item) => comparison.moveCandidates.has(item.index) && !comparison.stable.has(item.index));
    summary.textContent = `${changed.length} modificados · ${moved.length} movidos · ${removed.length} eliminados · ${added.length} añadidos`;
    if (comparison.ambiguous) summary.textContent += ' · Bloques repetidos sin ID: correspondencias ambiguas no se consideran movimientos.';
    container.append(summary);
    const emitted = new Set();
    const addArticle = (item, kind, old = null, moved = false) => {
      const article = makeBlock(item, { readOnly: true, mode: 'visual' });
      if (kind) article.classList.add(`md-diff-${kind}`);
      if (moved) article.classList.add('md-diff-moved');
      const badge = document.createElement('span');
      badge.className = 'md-diff-badge';
      const label = { removed: 'Eliminado', added: 'Añadido', changed: 'Contenido modificado', '': 'Sin cambios' }[kind];
      badge.textContent = `${label}${moved ? ' · Movido' : ''} · ${typeLabel(item.type)} · ${
        old ? `Antes ${old.index + 1} → Después ${item.index + 1}` : `${kind === 'removed' ? 'Antes' : 'Después'} ${item.index + 1}`}`;
      article.prepend(badge);
      if (kind === 'changed') markContentChanges(article, old, item);
      container.append(article);
    };
    for (const next of comparison.after) {
      const old = comparison.matches.get(next.index);
      for (const deleted of removed.filter((item) => item.index <= (old?.index ?? next.index))) {
        if (!emitted.has(deleted.index)) { addArticle(deleted, 'removed'); emitted.add(deleted.index); }
      }
      addArticle(next, old ? old.content === next.content ? '' : 'changed' : 'added', old,
        comparison.moveCandidates.has(next.index) && !comparison.stable.has(next.index));
    }
    for (const deleted of removed.filter((item) => !emitted.has(item.index))) addArticle(deleted, 'removed');
    return container;
  };

  const renderReadOnly = () => {
    floatingMenu.hidden = true;
    runtime.menuBlock = null;
    toolbar.hidden = true;
    closeHelp();
    root.querySelector('.md-status').hidden = true;
    canvas.hidden = true;
    canvas.inert = true;
    const sources = reviewSources();
    const viewAllowed = runtime.options.toolbarSections.includes('view');
    reviewToolbar.hidden = !runtime.reviewing && (!viewAllowed || (!sources && !runtime.options.showCopy));
    reviewContent.hidden = false;
    root.dataset.readonly = 'true';
    if (sources) {
      reviewToolbar.querySelector('.md-back-editor').hidden = !runtime.reviewing;
      reviewToolbar.querySelector('.md-review-caption').textContent =
        runtime.reviewing ? 'Última versión guardada frente al borrador; no se ha guardado.' : 'Comparación de versiones · solo lectura';
      reviewToolbar.querySelector('.md-review-layouts').hidden = runtime.reviewMode === 'markdown';
      reviewToolbar.querySelectorAll('[data-review-mode]').forEach((button) => {
        button.hidden = !runtime.options.reviewModes.includes(button.dataset.reviewMode);
        button.dataset.single = String(runtime.options.reviewModes.length === 1);
        button.setAttribute('aria-pressed', String(button.dataset.reviewMode === runtime.reviewMode));
      });
      reviewToolbar.querySelectorAll('[data-review-layout]').forEach((button) => {
        button.hidden = !runtime.options.reviewLayouts.includes(button.dataset.reviewLayout);
        button.dataset.single = String(runtime.options.reviewLayouts.length === 1);
        button.setAttribute('aria-pressed', String(button.dataset.reviewLayout === runtime.reviewLayout));
      });
      if (runtime.reviewMode === 'markdown') reviewContent.replaceChildren(renderSourceDiff(sources.before, sources.after));
      else if (runtime.reviewLayout === 'blocks') reviewContent.replaceChildren(renderBlockDiff(sources));
      else if (runtime.reviewLayout === 'split') {
        const split = document.createElement('div');
        split.className = 'md-review-split';
        split.append(visualVersion('Antes', sources.beforeBlocks), visualVersion('Después', sources.afterBlocks));
        reviewContent.replaceChildren(split);
      } else reviewContent.replaceChildren(runtime.reviewLayout === 'before'
        ? visualVersion('Antes', sources.beforeBlocks) : visualVersion('Después', sources.afterBlocks));
    } else {
      reviewToolbar.querySelector('.md-review-layouts').hidden = true;
      reviewToolbar.querySelector('.md-back-editor').hidden = true;
      reviewToolbar.querySelector('.md-review-caption').textContent = '';
      reviewContent.replaceChildren(visualVersion('Documento', runtime.pendingBlocks
        ?? (canvas.childElementCount ? getBlocks() : runtime.inputBlocks)));
    }
    const caption = reviewToolbar.querySelector('.md-review-caption');
    caption.title = caption.textContent;
    reviewToolbar.querySelector('[aria-label="Formato de comparación"]').hidden = !sources || !viewAllowed;
    reviewToolbar.querySelector('.md-quickbar-end').hidden = !viewAllowed || (!sources && !runtime.options.showCopy);
    reviewToolbar.querySelector('.md-review-versions').hidden =
      !sources || !viewAllowed || runtime.reviewMode === 'markdown';
    syncRibbonPanel(reviewToolbar.querySelector('.md-ribbon-panel'));
    updateCopyButtons();
  };

  const showEditor = () => {
    root.dataset.readonly = 'false';
    reviewToolbar.hidden = true;
    reviewContent.hidden = true;
    canvas.hidden = false;
    canvas.inert = false;
    toolbar.hidden = false;
    closeHelp();
    status.hidden = !runtime.options.showStatus;
    syncModeButtons();
    updateSaveControls();
    updateCopyButtons();
  };

  const openReview = () => {
    flushHistory();
    if (!isDirty()) return;
    if (runtime.timer) clearTimeout(runtime.timer);
    runtime.timer = null;
    runtime.reviewBookmark = captureBookmark() ?? runtime.bookmark;
    const afterBlocks = getBlocks().map(({ id, markdown }) => ({ id, markdown }));
    const beforeBlocks = runtime.savedBlocks.map((item) => ({ ...item }));
    runtime.reviewData = {
      beforeBlocks, afterBlocks,
      before: beforeBlocks.map((item) => item.markdown).join('\n\n'),
      after: afterBlocks.map((item) => item.markdown).join('\n\n'),
    };
    runtime.reviewing = true;
    runtime.onlyView = true;
    renderReadOnly();
    const focus = runtime.options.toolbarSections.includes('view')
      ? reviewToolbar.querySelector('[data-review-mode]:not([hidden])')
      : reviewToolbar.querySelector('.md-back-editor');
    focus?.focus();
  };

  const closeReview = () => {
    runtime.reviewing = false;
    runtime.onlyView = false;
    showEditor();
    if (runtime.requestedMode) {
      setMode(runtime.requestedMode);
      runtime.requestedMode = null;
    }
    if (!runtime.options.editorModes.includes(runtime.mode)) setMode(runtime.options.editorModes[0]);
    restoreBookmark(runtime.reviewBookmark);
    if (runtime.saveMode === 'auto') schedulePublish();
  };

  const setMode = (mode) => {
    if (!runtime.options.editorModes.includes(mode) || mode === runtime.mode) return;
    flushHistory();
    const blocks = getBlocks().map(({ id, markdown }) => ({ id, markdown }));
    runtime.mode = mode;
    syncModeButtons();
    renderBlocks(blocks, { publishValue: false });
    schedulePublish();
    updateCopyButtons();
  };

  const closeHelp = () => {
    help.hidden = true;
    helpToggle.setAttribute('aria-expanded', 'false');
  };

  const syncRibbonPanel = (panel) => {
    const editing = panel.classList.contains('md-edit-row');
    const collapsed = Boolean(runtime[editing ? 'editorRibbonCollapsed' : 'reviewRibbonCollapsed']);
    const groups = panel.querySelector('.md-ribbon-groups');
    const button = panel.querySelector('.md-ribbon-toggle');
    groups.id ||= `md-ribbon-groups-${crypto.randomUUID()}`;
    groups.hidden = collapsed;
    panel.dataset.collapsed = String(collapsed);
    const label = `${collapsed ? 'Mostrar' : 'Ocultar'} ${editing ? 'herramientas de edición' : 'controles de versión'}`;
    button.title = label;
    button.setAttribute('aria-label', label);
    button.setAttribute('aria-controls', groups.id);
    button.setAttribute('aria-expanded', String(!collapsed));
    button.querySelector('.md-icon').textContent = collapsed ? 'expand_more' : 'expand_less';
  };

  const toggleRibbonPanel = (button) => {
    const panel = button.closest('.md-ribbon-panel');
    const key = panel.classList.contains('md-edit-row') ? 'editorRibbonCollapsed' : 'reviewRibbonCollapsed';
    if (!runtime.onlyView) runtime.bookmark = captureBookmark() ?? runtime.bookmark;
    runtime[key] = !runtime[key];
    syncRibbonPanel(panel);
    button.focus();
    runtime.onResize?.();
  };

  const syncToolbarSections = () => {
    toolbar.querySelectorAll('[data-toolbar-section]').forEach((section) => {
      section.hidden = !runtime.options.toolbarSections.includes(section.dataset.toolbarSection)
        || (section.dataset.toolbarSection === 'changes' && saveButton.hidden && reviewButton.hidden);
    });
    const hasEditing = [...toolbar.querySelectorAll('.md-edit-row .md-toolbar-group')].some((group) => !group.hidden);
    const hasQuick = [...toolbar.querySelectorAll('.md-quickbar [data-toolbar-section]')].some((section) => !section.hidden);
    toolbar.querySelector('.md-quickbar-start').hidden =
      [...toolbar.querySelector('.md-quickbar-start').children].every((section) => section.hidden);
    toolbar.querySelector('.md-quickbar').hidden = !hasQuick;
    toolbar.querySelector('.md-edit-row').hidden = !hasEditing;
    toolbar.hidden = runtime.onlyView || (!hasEditing && !hasQuick);
    if (!runtime.options.toolbarSections.includes('view')) closeHelp();
    syncRibbonPanel(toolbar.querySelector('.md-ribbon-panel'));
  };

  const positionHelp = () => {
    const height = toolbar.querySelector('.md-quickbar').offsetHeight;
    help.style.top = `${height + 4}px`;
    help.style.maxHeight = `${Math.max(0, Math.min(360, root.clientHeight * 0.65,
      root.clientHeight - height - 8))}px`;
  };

  const updatePlaceholders = () => root.querySelectorAll('.md-block').forEach((article) => {
    const editable = article.querySelector('.md-editable');
    const untouched = editable.innerHTML === article.__visualInitial;
    article.querySelectorAll('.md-editable,.md-list-text,.md-quote-text').forEach((leaf) => {
      leaf.dataset.placeholder = runtime.options.placeholder;
    });
    if (untouched) article.__visualInitial = editable.innerHTML;
  });

  const updateCopyButtons = () => root.querySelectorAll('.md-copy-all').forEach((button) => {
    button.hidden = !runtime.options.showCopy || !runtime.options.toolbarSections.includes('view');
    const sources = runtime.onlyView ? reviewSources() : null;
    const before = sources && runtime.reviewMode === 'visual' && runtime.reviewLayout === 'before';
    const label = runtime.onlyView
      ? sources ? `Copiar la versión ${before ? 'Antes' : 'Después'} sin marcas, con formato` : 'Copiar documento con formato'
      : runtime.mode === 'visual' ? 'Copiar todo con formato' : 'Copiar todo como Markdown';
    button.title = label;
    button.setAttribute('aria-label', label);
  });

  const notifyCopy = (message, error = false) => {
    if (runtime.feedbackTimer) clearTimeout(runtime.feedbackTimer);
    feedback.hidden = false;
    feedback.dataset.error = String(error);
    feedback.textContent = message;
    if (!error) runtime.feedbackTimer = setTimeout(() => { feedback.hidden = true; }, 5000);
  };

  const diagramImage = async (svg) => {
    const box = svg.viewBox.baseVal;
    const width = box.width || 800;
    const height = box.height || 400;
    const scale = Math.min(1, 1200 / width, 2000 / height);
    const clone = svg.cloneNode(true);
    clone.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
    clone.setAttribute('width', String(width));
    clone.setAttribute('height', String(height));
    const image = new Image();
    image.src = `data:image/svg+xml;charset=utf-8,${encodeURIComponent(new XMLSerializer().serializeToString(clone))}`;
    await image.decode();
    const bitmap = document.createElement('canvas');
    bitmap.width = Math.ceil(width * scale);
    bitmap.height = Math.ceil(height * scale);
    const context = bitmap.getContext('2d');
    if (!context) throw new Error('No se puede convertir el diagrama a imagen.');
    context.drawImage(image, 0, 0, bitmap.width, bitmap.height);
    const result = document.createElement('img');
    result.src = bitmap.toDataURL('image/png');
    result.alt = 'Diagrama Mermaid';
    result.width = Math.min(bitmap.width, 600);
    return result;
  };

  const richCopyDocument = async (blocks) => {
    const sandbox = document.createElement('div');
    sandbox.style.cssText = 'position:fixed;left:-10000px;top:0;width:800px;pointer-events:none';
    sandbox.setAttribute('aria-hidden', 'true');
    sandbox.inert = true;
    root.append(sandbox);
    try {
      const articles = blocks.map((item) => makeBlock(item, { readOnly: true, mode: 'visual' }));
      sandbox.append(...articles);
      await Promise.all(articles.map((article) => article.__renderPromise));
      const failure = sandbox.querySelector('.md-render-error');
      if (failure) throw new Error(`No se puede copiar el renderizado: ${failure.textContent}`);
      const documentBody = document.createElement('div');
      documentBody.style.fontFamily = getComputedStyle(root).fontFamily;
      documentBody.style.fontSize = '14px';
      documentBody.style.color = '#222';
      sandbox.append(documentBody);
      for (const article of articles) {
        const type = article.dataset.type;
        const editable = article.querySelector('.md-editable');
        let content;
        if (type === 'mermaid') {
          content = await diagramImage(article.querySelector('svg'));
        } else if (type === 'math') {
          content = article.querySelector('.md-rendered-preview').cloneNode(true);
        } else if (type === 'code') {
          content = document.createElement('pre');
          const code = document.createElement('code');
          code.innerHTML = article.querySelector('.md-code-highlight').innerHTML;
          content.append(code);
        } else if (type === 'rule') content = document.createElement('hr');
        else if (/^h[1-6]$/.test(type)) {
          content = document.createElement(type);
          content.innerHTML = editable.innerHTML;
          content.style.fontSize = getComputedStyle(editable).fontSize;
        } else if (isListType(type) || ['quote', 'table'].includes(type)) {
          content = document.createElement('div');
          content.innerHTML = editable.innerHTML;
        } else {
          content = document.createElement('p');
          content.innerHTML = editable.innerHTML;
        }
        documentBody.append(content);
      }
      const walker = document.createTreeWalker(documentBody, NodeFilter.SHOW_TEXT);
      const lines = [];
      let text;
      while ((text = walker.nextNode())) {
        if (text.textContent.includes('\n') && !text.parentElement.closest('pre,math')) lines.push(text);
      }
      for (const node of lines) {
        const fragment = document.createDocumentFragment();
        node.textContent.split('\n').forEach((line, index) => {
          if (index) fragment.append(document.createElement('br'));
          fragment.append(document.createTextNode(line));
        });
        node.replaceWith(fragment);
      }
      for (const checkbox of documentBody.querySelectorAll('.md-task-checkbox')) {
        const marker = document.createElement('span');
        marker.textContent = checkbox.checked ? '\u2611 ' : '\u2610 ';
        checkbox.closest('li').querySelector(':scope > .md-list-text').prepend(marker);
        checkbox.remove();
      }
      for (const element of documentBody.querySelectorAll('*')) {
        if (element.matches('li.md-task-item')) element.style.listStyleType = 'none';
        if (element.matches('[data-md-filler]')) { element.remove(); continue; }
        if (element.matches('[class*="hljs-"]')) element.style.color = getComputedStyle(element).color;
        for (const attribute of [...element.attributes]) {
          if (/^(data-|aria-)/.test(attribute.name)
            || ['class', 'contenteditable', 'spellcheck', 'role', 'tabindex'].includes(attribute.name)) {
            element.removeAttribute(attribute.name);
          }
        }
        if (element.matches('table')) element.style.cssText += ';border-collapse:collapse;width:100%';
        if (element.matches('th,td')) element.style.cssText += ';border:1px solid #888;padding:6px';
        if (element.matches('th')) element.style.backgroundColor = '#f4f4f4';
        if (element.matches('blockquote')) element.style.cssText += ';border-left:3px solid #888;padding-left:14px;margin-left:0';
        if (element.matches('pre')) element.style.cssText += ';background:#f4f4f4;padding:12px;white-space:pre-wrap';
        if (element.matches('code,pre')) element.style.fontFamily = 'Consolas, "Courier New", monospace';
        if (element.localName === 'code' && element.parentElement.localName !== 'pre') element.style.backgroundColor = '#eee';
        if (element.matches('img')) {
          element.style.maxWidth = '100%';
          const source = [...canvas.querySelectorAll('img'), ...articles.flatMap((article) => [...article.querySelectorAll('img')])]
            .find((image) => image.src === element.src);
          if (!element.width) element.width = Math.min(source?.naturalWidth || element.naturalWidth || 600, 600);
        }
      }
      const plain = documentBody.cloneNode(true);
      plain.querySelectorAll('annotation,annotation-xml').forEach((element) => element.remove());
      plain.querySelectorAll('img').forEach((image) => image.replaceWith(document.createTextNode(image.alt)));
      sandbox.append(plain);
      return { html: documentBody.outerHTML, text: plain.innerText };
    } finally { sandbox.remove(); }
  };

  const copyDocument = async (button, block = null) => {
    if (!runtime.options.showCopy) return;
    const sources = runtime.onlyView ? reviewSources() : null;
    const before = sources && runtime.reviewMode === 'visual' && runtime.reviewLayout === 'before';
    const blocks = block ? [{ markdown: blockSource(block) }] : sources
      ? before ? sources.beforeBlocks : sources.afterBlocks
      : runtime.onlyView ? runtime.pendingBlocks ?? (canvas.childElementCount ? getBlocks() : runtime.inputBlocks) : getBlocks();
    const rich = runtime.onlyView || runtime.mode === 'visual';
    button.disabled = true;
    try {
      if (!navigator.clipboard) throw new Error('El portapapeles necesita HTTPS o localhost y permiso del navegador.');
      let plainFallback = false;
      if (!rich) await navigator.clipboard.writeText(blocks.map((item) => item.markdown).join('\n\n'));
      else {
        const content = richCopyDocument(blocks);
        if (navigator.clipboard.write && globalThis.ClipboardItem
          && (!ClipboardItem.supports || ClipboardItem.supports('text/html'))) {
          const html = content.then(({ html }) => new Blob([html], { type: 'text/html' }));
          const text = content.then(({ text }) => new Blob([text], { type: 'text/plain' }));
          const settled = Promise.allSettled([content, html, text]);
          try {
            await navigator.clipboard.write([new ClipboardItem({ 'text/html': html, 'text/plain': text })]);
          } finally { await settled; }
        } else {
          await navigator.clipboard.writeText((await content).text);
          plainFallback = true;
        }
      }
      notifyCopy(plainFallback ? 'Copiado como texto plano: este navegador no admite copiar formato enriquecido.'
        : rich ? 'Copiado con formato, sin marcas de cambios.' : 'Markdown copiado.');
    } catch (error) {
      console.error('Markdown editor: no se pudo copiar', error);
      notifyCopy(`No se pudo copiar: ${error.message}`, true);
    } finally { button.disabled = false; }
  };

  const formatTable = (rows, alignments = []) => {
    const width = Math.max(1, ...rows.map((row) => row.length));
    const normalized = rows.map((row) =>
      Array.from({ length: width }, (_, index) => String(row[index] ?? '').replace(/\|/g, '\\|')));
    const normalizedAlignments = Array.from({ length: width }, (_, index) => alignments[index] ?? '---');
    return [
      `| ${normalized[0].join(' | ')} |`,
      `| ${normalizedAlignments.join(' | ')} |`,
      ...normalized.slice(1).map((row) => `| ${row.join(' | ')} |`),
    ].join('\n');
  };

  const placeListCaret = (block, items, item, offset = 0) => {
    const entry = listPathEntries(items).find((entry) => entry.item === item);
    if (!entry) return;
    if (runtime.mode === 'visual') {
      restoreBookmark({ id: block.dataset.blockId, path: entry.path.join('.'), start: offset, end: offset });
    } else {
      const parsed = listLocation(parseList(blockSource(block)), entry.path)?.item;
      if (!parsed) return;
      const lines = blockSource(block).split('\n');
      const start = lines.slice(0, parsed.line).reduce((sum, line) => sum + line.length + 1, 0);
      setCaret(block.querySelector('.md-editable'), start + parsed.indent + listTextOffset(parsed) + offset);
    }
  };

  const listState = (block, pathOverride = null) => {
    const source = blockSource(block);
    const items = parseList(source);
    const leaf = selectedLeaf(block);
    let path;
    if (pathOverride) path = pathOverride;
    else if (runtime.mode === 'visual') path = (leaf?.dataset.path ?? '0').split('.').map(Number);
    else {
      const context = rawContext(block);
      const entry = listPathEntries(items).filter(({ item }) => item.line <= context.line)
        .sort((a, b) => b.item.line - a.item.line)[0];
      path = entry?.path ?? [0];
    }
    const location = listLocation(items, path);
    return { items, path, ...location };
  };

  const changeList = (block, action, split = null, pathOverride = null) => {
    const state = listState(block, pathOverride);
    const { items, path, item, siblings, index, parent } = state;
    if (!item) return;
    if (action === 'indent' && index === 0) {
      status.textContent = 'El primer ítem no puede indentarse sin un ítem anterior.';
      return;
    }
    if (action === 'outdent' && !parent) {
      status.textContent = 'El ítem ya está en el nivel raíz.';
      return;
    }
    let startNumber;
    if (action === 'start-number') {
      const answer = window.prompt('Número inicial de esta sublista:', String(parseInt(siblings.find(numbered)?.marker ?? '1', 10)));
      if (answer === null) return;
      if (!/^[1-9]\d*$/.test(answer) || !Number.isSafeInteger(Number(answer))) {
        status.textContent = 'El número inicial debe ser un entero positivo.';
        return;
      }
      startNumber = Number(answer);
    }
    flushHistory();
    let focusItem = item;
    if (action === 'indent') {
      siblings.splice(index, 1);
      siblings[index - 1].children.push(item);
    } else if (action === 'outdent') {
      const parentLocation = listLocation(items, path.slice(0, -1));
      item.children.push(...siblings.splice(index + 1));
      siblings.splice(index, 1);
      parentLocation.siblings.splice(parentLocation.index + 1, 0, item);
    } else if (action === 'item-delete') {
      siblings.splice(index, 1, ...item.children);
      focusItem = siblings[index] ?? siblings[index - 1] ?? parent;
    } else if (action === 'item-add') {
      if (split) item.text = split.before;
      focusItem = {
        marker: numbered(item) ? `${parseInt(item.marker, 10) + 1}${item.marker.at(-1)}` : item.marker,
        checked: item.checked == null ? null : false,
        text: split?.after ?? '', children: [],
      };
      siblings.splice(index + 1, 0, focusItem);
    } else if (action === 'item-check') {
      item.checked = !item.checked;
    } else if (action === 'toggle-list' || action === 'start-number' || action === 'task-list') {
      const originalKind = numbered(item);
      const originalTask = item.checked != null;
      let first = index;
      let last = index;
      while (first > 0 && numbered(siblings[first - 1]) === originalKind
        && (siblings[first - 1].checked != null) === originalTask) first--;
      while (last + 1 < siblings.length && numbered(siblings[last + 1]) === originalKind
        && (siblings[last + 1].checked != null) === originalTask) last++;
      const ordered = action === 'start-number' || (action === 'toggle-list' && !originalKind && !originalTask);
      siblings.slice(first, last + 1).forEach((entry, offset) => {
        entry.marker = ordered ? `${(startNumber ?? 1) + offset}.` : '-';
        entry.checked = action === 'task-list' ? entry.checked ?? false : null;
      });
    }
    let replacement;
    if (!items.length) {
      setBlockMarkdown(block, '');
    } else {
      replacement = setBlockMarkdown(block, listLines(items, 0, true).join('\n'));
      placeListCaret(replacement, items, focusItem);
    }
    flushHistory();
    schedulePublish();
    return replacement;
  };

  const handleListEnter = (block, shift) => {
    const { item, path, items, index } = listState(block);
    if (!item) return;
    const leaf = selectedLeaf(block);
    if (shift) {
      if (runtime.mode === 'visual') insertAtSelection(leaf, '\n');
      else insertAtSelection(block.querySelector('.md-editable'), '\n' + ' '.repeat(item.indent + listTextOffset(item)));
      return;
    }
    if (!item.text.trim()) {
      if (path.length > 1) changeList(block, 'outdent');
      else {
        flushHistory();
        const before = items.slice(0, index);
        const after = [...item.children, ...items.slice(index + 1)];
        const paragraph = makeBlock({
          id: before.length ? `block-${crypto.randomUUID()}` : block.dataset.blockId, markdown: '',
        });
        const replacements = [];
        if (before.length) replacements.push(makeBlock({
          id: block.dataset.blockId, markdown: listLines(before, 0, true).join('\n'),
        }));
        replacements.push(paragraph);
        if (after.length) replacements.push(makeBlock({ markdown: listLines(after, 0, true).join('\n') }));
        block.replaceWith(...replacements);
        floatingMenu.hidden = true;
        runtime.menuBlock = null;
        activate(paragraph);
        setCaret(paragraph.querySelector('.md-editable'), 0);
        flushHistory();
        schedulePublish();
      }
      return;
    }
    let split;
    if (runtime.mode === 'visual') split = splitLeaf(leaf);
    else {
      const context = rawContext(block);
      const lines = item.text.split('\n');
      const relativeLine = Math.max(0, context.line - item.line);
      const rawLine = blockSource(block).split('\n')[context.line] ?? '';
      const prefix = ' '.repeat(item.indent + listTextOffset(item));
      const fallback = ' '.repeat(item.indent + item.marker.length + 1);
      const contentStart = relativeLine === 0 || rawLine.startsWith(prefix) ? prefix.length
        : rawLine.startsWith(fallback) ? fallback.length : indentation(rawLine.match(/^[ \t]*/)?.[0] ?? '');
      const column = Math.max(0, context.column - contentStart);
      const offset = lines.slice(0, relativeLine).reduce((sum, line) => sum + line.length + 1, 0) + column;
      split = { before: item.text.slice(0, offset), after: item.text.slice(offset + context.end - context.start) };
    }
    changeList(block, 'item-add', split);
  };

  const quoteState = (block) => {
    const lines = quoteLines(blockSource(block));
    let line;
    if (runtime.mode === 'visual') {
      const leaf = selectedLeaf(block);
      const leaves = Array.from(block.querySelectorAll('.md-quote-text'));
      line = leaves.slice(0, Math.max(0, leaves.indexOf(leaf))).reduce((sum, text) =>
        sum + Array.from(text.childNodes).map(inlineMarkdown).join('').split('\n').length, 0);
      if (leaf) line += splitLeaf(leaf).before.split('\n').length - 1;
    } else line = rawContext(block).line;
    return { lines, line: Math.min(line, lines.length - 1) };
  };

  const changeQuote = (block, action) => {
    const { lines, line } = quoteState(block);
    const depth = lines[line].depth;
    if (action === 'outdent' && depth === 1) {
      status.textContent = 'Usa «A párrafo» para quitar el nivel raíz de la cita.';
      return;
    }
    flushHistory();
    for (let index = line; index < lines.length; index++) {
      if (index > line && lines[index].depth <= depth) break;
      lines[index].depth += action === 'indent' ? 1 : -1;
    }
    const source = formatQuote(lines);
    const replacement = setBlockMarkdown(block, source);
    if (runtime.mode === 'visual') restoreBookmark({ id: replacement.dataset.blockId, line: String(line), start: 0, end: 0 });
    else setCaret(replacement.querySelector('.md-editable'),
      source.split('\n').slice(0, line).reduce((sum, text) => sum + text.length + 1, 0) + lines[line].depth * 2);
    flushHistory();
    schedulePublish();
  };

  const tableContext = (block) => {
    if (runtime.mode === 'visual') {
      const cell = selectedLeaf(block);
      return { row: cell?.closest('tr')?.rowIndex ?? 0, column: cell?.cellIndex ?? 0 };
    }
    const context = rawContext(block);
    const lines = context.source.split('\n');
    const rawLine = lines[context.line] ?? '';
    const before = rawLine.slice(0, context.column);
    const pipes = before.match(/(?<!\\)\|/g)?.length ?? 0;
    const column = Math.max(0, pipes - (rawLine.trimStart().startsWith('|') ? 1 : 0));
    return { row: Math.max(0, context.line - (context.line > 0 ? 1 : 0)), column };
  };

  const placeTableCaret = (block, row, column) => {
    const rows = parseTable(blockSource(block));
    row = Math.max(0, Math.min(row, rows.length - 1));
    column = Math.max(0, Math.min(column, rows[0].length - 1));
    if (runtime.mode === 'visual') restoreBookmark({ id: block.dataset.blockId, row, column, start: 0, end: 0 });
    else {
      const lines = blockSource(block).split('\n');
      const lineIndex = row === 0 ? 0 : row + 1;
      const line = lines[lineIndex];
      const delimiters = Array.from(line.matchAll(/(?<!\\)\|/g));
      const offset = lines.slice(0, lineIndex).reduce((sum, text) => sum + text.length + 1, 0);
      setCaret(block.querySelector('.md-editable'), offset + (delimiters[column]?.index ?? 0) + 2);
    }
  };

  const changeTable = (block, action) => {
    flushHistory();
    const source = blockSource(block);
    const rows = parseTable(source);
    const width = rows[0].length;
    const alignments = tableAlignments(source, width);
    let { row, column } = tableContext(block);
    row = Math.min(row, rows.length - 1);
    column = Math.min(column, width - 1);
    if (action === 'row-add' || action === 'row-before') {
      row = Math.max(1, row + (action === 'row-add' ? 1 : 0));
      rows.splice(row, 0, Array(width).fill(''));
    }
    if (action === 'row-delete') {
      if (row === 0) {
        status.textContent = 'La cabecera es obligatoria en Markdown; no se puede eliminar.';
        return;
      }
      rows.splice(row, 1);
    }
    if (action === 'column-add' || action === 'column-before') {
      column += action === 'column-add' ? 1 : 0;
      rows.forEach((cells, index) => cells.splice(column, 0, index === 0 ? `Columna ${width + 1}` : ''));
      alignments.splice(column, 0, '---');
    }
    if (action === 'column-delete') {
      if (width === 1) {
        status.textContent = 'La tabla necesita al menos una columna.';
        return;
      }
      rows.forEach((cells) => cells.splice(column, 1));
      alignments.splice(column, 1);
    }
    const replacement = setBlockMarkdown(block, formatTable(rows, alignments));
    placeTableCaret(replacement, row, column);
    flushHistory();
    schedulePublish();
  };

  const deleteBlock = (block) => {
    flushHistory();
    const blocks = Array.from(canvas.querySelectorAll(':scope > .md-block'));
    const index = blocks.indexOf(block);
    if (blocks.length === 1) {
      setBlockMarkdown(block, '');
      flushHistory();
      schedulePublish();
      return;
    }
    const next = blocks[index + 1] ?? blocks[index - 1];
    block.remove();
    floatingMenu.hidden = true;
    runtime.menuBlock = null;
    runtime.activeBlock = next;
    (next.querySelector('[contenteditable="true"]') ?? next.querySelector('.md-editable')).focus();
    flushHistory();
    schedulePublish();
  };

  const changeCodeIndent = (block, outdent) => {
    const editable = block.querySelector('.md-editable');
    const context = rawContext(block);
    const text = editable.textContent;
    const lines = text.split('\n');
    let first = text.slice(0, context.start).split('\n').length - 1;
    let last = text.slice(0, Math.max(context.start, context.end - 1)).split('\n').length - 1;
    if (runtime.mode === 'raw_visual') {
      first = Math.max(1, first);
      last = Math.min(lines.length - (lines.at(-1).startsWith('```') ? 2 : 1), last);
    }
    if (last < first) return;
    flushHistory();
    const offset = lines.slice(0, first).reduce((sum, line) => sum + line.length + 1, 0);
    let removedFirst = 0;
    for (let index = first; index <= last; index++) {
      const removed = outdent ? (lines[index].match(/^( {1,4}|\t)/)?.[0].length ?? 0) : 0;
      if (index === first) removedFirst = removed;
      lines[index] = outdent ? lines[index].slice(removed) : '    ' + lines[index];
    }
    editable.textContent = lines.join('\n');
    if (runtime.mode === 'visual') refreshRender(block);
    setCaret(editable, Math.max(offset, context.start + (outdent ? -removedFirst : 4)));
    flushHistory();
    schedulePublish();
  };

  const positionMenu = () => {
    const block = runtime.menuBlock;
    if (!block?.isConnected || floatingMenu.hidden) return;
    const bounds = block.getBoundingClientRect();
    const base = root.getBoundingClientRect();
    const canvasBounds = canvas.getBoundingClientRect();
    if (bounds.bottom < canvasBounds.top || bounds.top > canvasBounds.bottom) {
      floatingMenu.hidden = true;
      return;
    }
    floatingMenu.style.left = `${Math.max(4, Math.min(bounds.right - base.left - floatingMenu.offsetWidth,
      base.width - floatingMenu.offsetWidth - 4))}px`;
    floatingMenu.style.top = `${Math.max(canvasBounds.top - base.top,
      Math.min(bounds.top - base.top - floatingMenu.offsetHeight - 2,
        base.height - floatingMenu.offsetHeight - 4))}px`;
  };

  const updateMenuArrows = () => {
    floatingMenu.querySelector('[data-scroll="-1"]').disabled = floatingActions.scrollLeft <= 1;
    floatingMenu.querySelector('[data-scroll="1"]').disabled =
      floatingActions.scrollLeft + floatingActions.clientWidth >= floatingActions.scrollWidth - 1;
  };

  const showMenu = (block) => {
    if (runtime.onlyView || runtime.draggedBlock) return;
    runtime.menuBlock = block;
    floatingMenu.hidden = false;
    const type = blockType(blockSource(block));
    runtime.menuType = type;
    const actions = [
      ['add-before', '+ Antes'], ['add-below', '+ Debajo'], ['delete', 'Eliminar bloque'],
    ];
    if (runtime.options.showCopy) actions.push(['copy', runtime.mode === 'visual' ? 'Copiar bloque con formato' : 'Copiar bloque como Markdown']);
    const commonCount = actions.length;
    if (isListType(type)) actions.push(
      ['item-add', '+ Ítem'], ['item-delete', 'Eliminar ítem'],
      ['toggle-list', 'Viñetas / números'], ['task-list', 'Convertir sublista a checkboxes'], ['start-number', 'Número inicial']);
    if (isListType(type) && listState(block).item?.checked != null) actions.push(['item-check', 'Marcar / desmarcar tarea']);
    if (type === 'quote') actions.push(
      ['quote-add', '+ Cita debajo'], ['paragraph', 'A párrafo']);
    if (/^h[1-6]$/.test(type)) {
      actions.push(...Array.from({ length: 6 }, (_, index) => [`h${index + 1}`, `H${index + 1}`]), ['paragraph', 'A párrafo']);
    }
    if (type === 'table') actions.push(
      ['row-before', 'Fila arriba'], ['row-add', 'Fila abajo'], ['row-delete', 'Eliminar fila'],
      ['column-before', 'Columna izquierda'], ['column-add', 'Columna derecha'], ['column-delete', 'Eliminar columna']);
    if (type === 'code' || type === 'mermaid') {
      if (type === 'code') actions.push(['language', 'Lenguaje']);
    }
    if (type === 'math' || type === 'mermaid') actions.push(['edit-source',
      block.querySelector('.md-editable').hidden
        ? type === 'math' ? 'Editar fórmula' : 'Editar diagrama'
        : type === 'math' ? 'Ver fórmula' : 'Ver diagrama']);
    if (type === 'link') actions.push(['edit-link', 'Editar enlace']);
    if (type === 'image') actions.push(['edit-image', 'Modificar imagen']);
    floatingActions.replaceChildren(...actions.flatMap(([action, label], index) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.dataset.action = action;
      button.title = label;
      button.setAttribute('aria-label', label);
      const icon = document.createElement('span');
      icon.className = 'md-icon';
      icon.setAttribute('aria-hidden', 'true');
      icon.textContent = ({
        'add-before': 'vertical_align_top', 'add-below': 'vertical_align_bottom', delete: 'delete',
        'item-add': 'add', 'item-delete': 'remove', 'toggle-list': 'format_list_bulleted',
        'task-list': 'checklist', 'item-check': 'check_box',
        'start-number': 'format_list_numbered', 'quote-add': 'format_quote', paragraph: 'notes',
        'row-before': 'vertical_align_top', 'row-add': 'vertical_align_bottom', 'row-delete': 'remove',
        'column-before': 'align_horizontal_left', 'column-add': 'align_horizontal_right', 'column-delete': 'remove',
        language: 'code', 'edit-link': 'link', 'edit-image': 'edit', 'edit-source': 'edit', copy: 'content_copy',
      })[action] ?? (/^h[1-6]$/.test(action) ? `format_${action}` : 'edit');
      button.append(icon);
      if (index !== commonCount) return [button];
      const divider = document.createElement('span');
      divider.className = 'md-divider';
      divider.setAttribute('role', 'separator');
      divider.setAttribute('aria-orientation', 'vertical');
      return [divider, button];
    }));
    positionMenu();
    updateMenuArrows();
  };

  const menuAction = (block, actionName) => {
    if (!block?.isConnected || runtime.onlyView) return;
    if (actionName === 'copy') {
      copyDocument(floatingActions.querySelector('[data-action="copy"]'), block);
      floatingMenu.hidden = true;
      return;
    }
    if (runtime.bookmark?.id === block.dataset.blockId) restoreBookmark(runtime.bookmark);
    else {
      activate(block);
      (block.querySelector('[contenteditable="true"]') ?? block.querySelector('.md-editable')).focus();
    }
    const type = blockType(blockSource(block));
    if (actionName === 'edit-source') {
      const editable = block.querySelector('.md-editable');
      editable.hidden = !editable.hidden;
      if (editable.hidden) block.focus();
      else setCaret(editable, 0);
    } else if (actionName === 'delete') deleteBlock(block);
    else if (actionName === 'add-below' || actionName === 'add-before') {
      addBlock('paragraph', block, actionName === 'add-before', '');
    } else if (actionName.startsWith('row-') || actionName.startsWith('column-')) {
      changeTable(block, actionName);
    } else if (isListType(type)) {
      changeList(block, actionName);
    } else if (actionName === 'indent' || actionName === 'outdent') {
      if (type === 'quote') changeQuote(block, actionName);
      else changeCodeIndent(block, actionName === 'outdent');
    } else if (actionName === 'quote-add') {
      const { lines, line } = quoteState(block);
      addBlock('quote', block, false, `${'> '.repeat(lines[line].depth)}`);
    } else if (actionName === 'language') {
      const parts = codeParts(blockSource(block));
      const language = window.prompt('Lenguaje del bloque de código:', parts.language);
      if (language === null) return;
      if (!/^[a-zA-Z0-9_+#.-]*$/.test(language)) {
        status.textContent = 'El lenguaje debe ser un identificador sin espacios ni saltos.';
        return;
      }
      flushHistory();
      setBlockMarkdown(block, `\`\`\`${language}\n${parts.body}\n\`\`\``);
      flushHistory();
      schedulePublish();
    } else if (actionName === 'paragraph' || /^h[1-6]$/.test(actionName)) {
      flushHistory();
      setBlockMarkdown(block, convertBlockMarkdown(actionName, blockSource(block)));
      flushHistory();
      schedulePublish();
    } else if (actionName === 'edit-link' || actionName === 'edit-image') {
      const markdown = blockSource(block);
      const match = markdown.match(/^!?\[([^\]]*)\]\(([^)]+)\)$/);
      const label = window.prompt(actionName === 'edit-link' ? 'Texto del enlace:' : 'Texto alternativo:', match?.[1] ?? '');
      if (label === null) return;
      const url = window.prompt('URL (http, https o mailto):', match?.[2] ?? '');
      if (url === null) return;
      const normalizedUrl = url.trim().replace(/[()\s]/g, (char) => encodeURIComponent(char));
      if (!(actionName === 'edit-link'
        ? /^(https?:\/\/|mailto:)/i.test(normalizedUrl) : /^https?:\/\//i.test(normalizedUrl))) {
        status.textContent = 'La URL debe usar http, https o mailto.';
        return;
      }
      flushHistory();
      const escapedLabel = label.replace(/([\\[\]])/g, '\\$1');
      setBlockMarkdown(block, `${actionName === 'edit-image' ? '!' : ''}[${escapedLabel}](${normalizedUrl})`);
      flushHistory();
      schedulePublish();
    }
    floatingMenu.hidden = true;
  };

  if (!root.dataset.initialized) {
    root.dataset.initialized = 'true';
    root.dataset.inputFingerprint = inputFingerprint;
    root.dataset.blocksFingerprint = blocksFingerprint;
    root.dataset.diffFingerprint = diffFingerprint;
    root.dataset.onlyView = String(Boolean(data?.only_view));
    root.dataset.mode = runtime.mode;
    root.dataset.saveMode = runtime.saveMode;
    root.dataset.revision = revision;
    syncModeButtons();
    saveButton.hidden = runtime.saveMode !== 'button';
    if (data?.only_view) {
      renderReadOnly();
    } else {
      replaceBlocks(data?.blocks ?? []);
    }

    toolbar.addEventListener('mousedown', (event) => {
      if (event.target.closest('button')) event.preventDefault();
    });
    toolbar.addEventListener('click', (event) => {
      const toggle = event.target.closest('.md-ribbon-toggle');
      if (toggle) { toggleRibbonPanel(toggle); return; }
      const copy = event.target.closest('.md-copy-all');
      if (copy) { copyDocument(copy); return; }
      if (event.target.closest('.md-help-toggle')) {
        help.hidden = !help.hidden;
        helpToggle.setAttribute('aria-expanded', String(!help.hidden));
        positionHelp();
        return;
      }
      const button = event.target.closest('button[data-format]');
      if (button) {
        restoreBookmark(runtime.bookmark);
        wrapSelection(button.dataset.format);
      }
      if (event.target.closest('[data-history="undo"]')) performUndo();
      if (event.target.closest('[data-history="redo"]')) performRedo();
      if (event.target.closest('.md-save')) {
        flushHistory();
        publish(true);
      }
      if (event.target.closest('.md-review-button')) openReview();
    });
    reviewToolbar.addEventListener('click', (event) => {
      const toggle = event.target.closest('.md-ribbon-toggle');
      if (toggle) { toggleRibbonPanel(toggle); return; }
      const copy = event.target.closest('.md-copy-all');
      if (copy) { copyDocument(copy); return; }
      const mode = event.target.closest('[data-review-mode]');
      const layout = event.target.closest('[data-review-layout]');
      if (event.target.closest('.md-back-editor')) {
        closeReview();
        return;
      }
      if (mode && runtime.options.reviewModes.includes(mode.dataset.reviewMode)) runtime.reviewMode = mode.dataset.reviewMode;
      if (layout && runtime.options.reviewLayouts.includes(layout.dataset.reviewLayout)) runtime.reviewLayout = layout.dataset.reviewLayout;
      if (mode || layout) renderReadOnly();
    });
    modeSelector.addEventListener('click', (event) => {
      const button = event.target.closest('[data-mode]');
      if (button) setMode(button.dataset.mode);
    });
    toolbar.querySelector('.md-add-block').addEventListener('click', () => {
      const type = toolbar.querySelector('.md-block-type').value;
      addBlock(type, runtime.activeBlock);
    });
    typeSelector.addEventListener('change', () => {
      const type = toolbar.querySelector('.md-block-type').value;
      if (runtime.bookmark?.id === runtime.activeBlock?.dataset.blockId) restoreBookmark(runtime.bookmark);
      if (!runtime.activeBlock) {
        addBlock(type, null);
        return;
      }
      const current = getBlocks().find((item) => item.id === runtime.activeBlock.dataset.blockId);
      const converted = convertBlockMarkdown(type, current?.markdown ?? '');
      flushHistory();
      setBlockMarkdown(runtime.activeBlock, converted);
      flushHistory();
      schedulePublish();
    });

    root.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && !help.hidden) {
        event.preventDefault();
        closeHelp();
        helpToggle.focus();
        return;
      }
      if (runtime.onlyView) return;
      if (event.key === 'Escape') {
        floatingMenu.hidden = true;
        const active = runtime.activeBlock;
        if (active && ['math', 'mermaid'].includes(active.dataset.type) && runtime.mode === 'visual') {
          active.querySelector('.md-editable').hidden = true;
          active.focus();
        } else restoreBookmark(runtime.bookmark);
        return;
      }
      if (!(event.ctrlKey || event.metaKey) || event.target.matches('input:not(.md-task-checkbox),textarea,select')) return;
      const key = event.key.toLowerCase();
      if (key === 'z' && !event.shiftKey) {
        event.preventDefault();
        performUndo();
      } else if (key === 'y' || (key === 'z' && event.shiftKey)) {
        event.preventDefault();
        performRedo();
      }
    }, true);

    canvas.addEventListener('focusin', (event) => {
      const block = event.target.closest('.md-block');
      if (!block || runtime.onlyView) return;
      if (event.target.matches('.md-task-checkbox')) {
        runtime.bookmark = { id: block.dataset.blockId, path: event.target.dataset.path, start: 0, end: 0 };
      }
      activate(block);
      showMenu(block);
    });
    runtime.onSelectionChange = () => {
      const bookmark = captureBookmark();
      if (bookmark) runtime.bookmark = bookmark;
    };
    document.addEventListener('selectionchange', runtime.onSelectionChange);
    canvas.addEventListener('beforeinput', () => {
      if (runtime.onlyView) return;
      runtime.historySelections?.set(snapshot(), captureBookmark() ?? runtime.bookmark);
    });
    canvas.addEventListener('pointerover', (event) => {
      const block = event.target.closest('.md-block');
      if (block && runtime.menuBlock !== block) showMenu(block);
    });
    root.addEventListener('pointerleave', () => {
      if (!floatingMenu.contains(document.activeElement)) floatingMenu.hidden = true;
      runtime.menuBlock = null;
    });
    canvas.addEventListener('scroll', positionMenu);
    runtime.onResize = () => { positionMenu(); positionHelp(); };
    window.addEventListener('resize', runtime.onResize);
    runtime.toolbarResize = new ResizeObserver(runtime.onResize);
    runtime.toolbarResize.observe(root);
    runtime.toolbarResize.observe(toolbar);
    runtime.toolbarResize.observe(reviewToolbar);
    root.querySelectorAll('.md-toolbar-group').forEach((group) => {
      const summary = group.querySelector('summary');
      const syncGroup = () => {
        summary.title = `${group.open ? 'Colapsar' : 'Expandir'} ${summary.textContent.trim()}`;
        runtime.onResize();
      };
      group.addEventListener('toggle', syncGroup);
      syncGroup();
    });
    runtime.onHelpDismiss = (event) => {
      if (!help.contains(event.target) && !helpToggle.contains(event.target)) closeHelp();
    };
    document.addEventListener('pointerdown', runtime.onHelpDismiss);
    help.id = `md-help-${crypto.randomUUID()}`;
    helpToggle.setAttribute('aria-controls', help.id);
    floatingActions.addEventListener('scroll', updateMenuArrows);
    floatingMenu.addEventListener('mousedown', (event) => {
      if (event.target.closest('button')) event.preventDefault();
    });
    floatingMenu.addEventListener('click', (event) => {
      const button = event.target.closest('button');
      if (!button) return;
      if (button.dataset.scroll) {
        floatingActions.scrollBy({ left: Number(button.dataset.scroll) * 180 });
        updateMenuArrows();
      } else menuAction(runtime.menuBlock, button.dataset.action);
    });
    canvas.addEventListener('input', (event) => {
      if (event.target.matches('.md-task-checkbox')) return;
      if (!runtime.onlyView && event.target.closest('.md-editable')) {
        const block = event.target.closest('.md-block');
        if (runtime.mode === 'visual') refreshRender(block, true);
        if (block === runtime.activeBlock) typeSelector.value = blockType(blockSource(block));
        if (runtime.menuBlock === block && runtime.menuType !== blockType(blockSource(block))) showMenu(block);
        scheduleHistory();
        schedulePublish();
      }
    });
    canvas.addEventListener('change', (event) => {
      const checkbox = event.target;
      if (!checkbox.matches('.md-task-checkbox') || runtime.onlyView) return;
      const path = checkbox.dataset.path;
      // Restore the pre-click value so history includes the checkbox change, even after text edits.
      checkbox.checked = !checkbox.checked;
      const replacement = changeList(checkbox.closest('.md-block'), 'item-check', null, path.split('.').map(Number));
      replacement?.querySelector(`.md-task-checkbox[data-path="${path}"]`)?.focus();
    });
    canvas.addEventListener('paste', (event) => {
      const editable = event.target.closest('.md-list-text,.md-quote-text,th,td,.md-editable');
      if (!editable || runtime.onlyView) return;
      event.preventDefault();
      const text = event.clipboardData.getData('text/plain');
      flushHistory();
      insertAtSelection(editable, text);
      flushHistory();
    });
    canvas.addEventListener('keydown', (event) => {
      if (event.target.matches('.md-task-checkbox') && !event.ctrlKey && !event.metaKey && event.key !== 'F10') return;
      const editable = event.target.closest('.md-editable');
      if (!editable || runtime.onlyView) return;
      const block = editable.closest('.md-block');
      const leaf = selectedLeaf(block) ?? editable;
      const blocks = Array.from(canvas.querySelectorAll(':scope > .md-block'));
      const index = blocks.indexOf(block);
      const text = editable.textContent;
      const { start, end } = selectionOffsets(leaf);
      const type = runtime.mode === 'visual' ? block.dataset.type : blockType(text);

      if (event.key === 'F10' && event.shiftKey) {
        event.preventDefault();
        runtime.bookmark = captureBookmark() ?? runtime.bookmark;
        showMenu(block);
        floatingActions.querySelector('button').focus();
        return;
      }
      if (event.key === 'Tab') {
        if (isListType(type) || ['quote', 'code', 'mermaid', 'table'].includes(type)) {
          if (type !== 'table') event.preventDefault();
          if (isListType(type)) changeList(block, event.shiftKey ? 'outdent' : 'indent');
          else if (type === 'quote') changeQuote(block, event.shiftKey ? 'outdent' : 'indent');
          else if (type === 'code' || type === 'mermaid') changeCodeIndent(block, event.shiftKey);
          else {
            const rows = parseTable(blockSource(block));
            const context = tableContext(block);
            const position = context.row * rows[0].length + context.column + (event.shiftKey ? -1 : 1);
            if (position < 0 || position >= rows.length * rows[0].length) {
              const adjacent = blocks[index + (event.shiftKey ? -1 : 1)];
              if (adjacent) {
                event.preventDefault();
                (adjacent.querySelector('[contenteditable="true"]') ?? adjacent.querySelector('.md-editable')).focus();
              }
              else {
                const preferred = event.shiftKey ? toolbar.querySelector('button')
                  : saveButton.hidden ? modeSelector.querySelector('[data-mode]:not([hidden])') : saveButton;
                const target = [preferred, ...toolbar.querySelectorAll('button,select,summary')]
                  .find((control) => control && !control.disabled && control.getClientRects().length);
                if (target) {
                  event.preventDefault();
                  target.focus();
                }
              }
            } else {
              event.preventDefault();
              placeTableCaret(block, Math.floor(position / rows[0].length), position % rows[0].length);
            }
          }
        }
        return;
      }
      if (event.key === 'Enter') {
        event.preventDefault();
        if (event.ctrlKey || event.metaKey) {
          addBlock('paragraph', block, false, '');
          return;
        }
        if (type === 'table') {
          changeTable(block, event.shiftKey ? 'column-add' : 'row-add');
          return;
        }
        if (isListType(type)) {
          handleListEnter(block, event.shiftKey);
          return;
        }
        if ((!event.shiftKey && /^h[1-6]$/.test(type)) || type === 'image' || type === 'rule') {
          if (!event.shiftKey) addBlock('paragraph', block, false, '');
          return;
        }
        if (type === 'quote' && runtime.mode === 'raw_visual') {
          const context = quoteState(block);
          insertAtSelection(editable, '\n' + '> '.repeat(context.lines[context.line].depth));
        } else if (type === 'code' || type === 'mermaid') {
          const currentLine = text.slice(0, start).split('\n').at(-1);
          insertAtSelection(editable, '\n' + (currentLine.match(/^[ \t]*/)?.[0] ?? ''));
        } else insertAtSelection(leaf, '\n');
        return;
      }

      if (event.key === 'Backspace' && isListType(type)) {
        const { item } = listState(block);
        if (item && !item.text.trim()) {
          event.preventDefault();
          changeList(block, 'item-delete');
          return;
        }
      }
      if (event.key === 'Backspace' && start === 0 && end === 0 && !text.trim() && blocks.length > 1) {
        event.preventDefault();
        flushHistory();
        const previous = blocks[index - 1] ?? blocks[index + 1];
        block.remove();
        runtime.activeBlock = previous;
        previous.querySelector('.md-editable').focus();
        flushHistory();
        schedulePublish();
      }
    });

    canvas.addEventListener('dragstart', (event) => {
      const handle = event.target.closest('.md-drag-handle');
      if (!handle) {
        event.preventDefault();
        return;
      }
      const block = handle.closest('.md-block');
      floatingMenu.hidden = true;
      flushHistory();
      runtime.draggedBlock = block;
      runtime.dragSnapshot = snapshot();
      block.classList.add('is-dragging');
      event.dataTransfer.effectAllowed = 'move';
      event.dataTransfer.setData('text/plain', block.dataset.blockId);
    });
    canvas.addEventListener('dragover', (event) => {
      const target = event.target.closest('.md-block');
      if (!runtime.draggedBlock || !target || target === runtime.draggedBlock) return;
      event.preventDefault();
      const bounds = target.getBoundingClientRect();
      if (event.clientY > bounds.top + bounds.height / 2) target.after(runtime.draggedBlock);
      else target.before(runtime.draggedBlock);
    });
    canvas.addEventListener('drop', (event) => {
      if (!runtime.draggedBlock) return;
      event.preventDefault();
      if (runtime.dragSnapshot !== snapshot()) {
        flushHistory();
        schedulePublish();
      }
    });
    canvas.addEventListener('dragend', () => {
      runtime.draggedBlock?.classList.remove('is-dragging');
      if (runtime.dragSnapshot && runtime.dragSnapshot !== snapshot()) {
        flushHistory();
        schedulePublish();
      }
      runtime.draggedBlock = null;
      runtime.dragSnapshot = '';
    });

    canvas.addEventListener('click', (event) => {
      const block = event.target.closest('.md-block');
      if (block && !runtime.onlyView) {
        activate(block);
        showMenu(block);
      }
      if (event.target.closest('.md-editable a')) {
        if (!runtime.onlyView) event.preventDefault();
      }
    });
  } else {
    runtime.setStateValue = setStateValue;
    if (root.dataset.inputFingerprint !== inputFingerprint || root.dataset.revision !== revision) {
      const blocksChanged = root.dataset.blocksFingerprint !== blocksFingerprint
        || root.dataset.revision !== revision;
      const diffChanged = root.dataset.diffFingerprint !== diffFingerprint
        || root.dataset.onlyView !== String(Boolean(data?.only_view));
      const modeChanged = root.dataset.mode !== (data?.mode ?? 'raw_visual');
      const saveModeChanged = root.dataset.saveMode !== (data?.save_mode ?? 'auto');
      root.dataset.inputFingerprint = inputFingerprint;
      root.dataset.blocksFingerprint = blocksFingerprint;
      root.dataset.diffFingerprint = diffFingerprint;
      root.dataset.onlyView = String(Boolean(data?.only_view));
      root.dataset.mode = data?.mode ?? 'raw_visual';
      root.dataset.saveMode = data?.save_mode ?? 'auto';
      root.dataset.revision = revision;
      runtime.saveMode = data?.save_mode ?? runtime.saveMode;
      saveButton.hidden = runtime.saveMode !== 'button';
      if (modeChanged && !runtime.onlyView) setMode(data?.mode ?? 'raw_visual');
      else if (modeChanged && runtime.reviewing) runtime.requestedMode = data?.mode ?? 'raw_visual';
      if (data?.only_view) {
        runtime.reviewing = false;
        runtime.onlyView = true;
        if (blocksChanged) runtime.pendingBlocks = data?.blocks ?? [];
        if (diffChanged || blocksChanged) renderReadOnly();
      }
      else {
        if (blocksChanged || runtime.pendingBlocks
          || (diffChanged && !runtime.reviewing && !canvas.childElementCount)) {
          runtime.reviewing = false;
          runtime.onlyView = false;
          replaceBlocks(blocksChanged ? data?.blocks ?? [] : runtime.pendingBlocks ?? data?.blocks ?? []);
          runtime.pendingBlocks = null;
        }
        if (runtime.reviewing) renderReadOnly();
        else {
          runtime.onlyView = false;
          showEditor();
          if (runtime.mode !== (data?.mode ?? 'raw_visual')) setMode(data?.mode ?? 'raw_visual');
          if (runtime.saveMode === 'auto' && saveModeChanged) schedulePublish();
        }
      }
    }
  }
  if (optionsChanged) {
    root.dataset.optionsFingerprint = optionsFingerprint;
    status.hidden = runtime.onlyView || !runtime.options.showStatus;
    updatePlaceholders();
    updateCopyButtons();
    syncModeButtons();
    syncToolbarSections();
    if (runtime.onlyView) renderReadOnly();
    else {
      if (!runtime.options.editorModes.includes(runtime.mode)) setMode(runtime.options.editorModes[0]);
      if (!floatingMenu.hidden && runtime.menuBlock) showMenu(runtime.menuBlock);
    }
  }
  return () => {
    document.removeEventListener('selectionchange', runtime.onSelectionChange);
    window.removeEventListener('resize', runtime.onResize);
    runtime.toolbarResize?.disconnect();
    document.removeEventListener('pointerdown', runtime.onHelpDismiss);
    if (runtime.timer) clearTimeout(runtime.timer);
    if (runtime.historyTimer) clearTimeout(runtime.historyTimer);
    if (runtime.feedbackTimer) clearTimeout(runtime.feedbackTimer);
  };
}
