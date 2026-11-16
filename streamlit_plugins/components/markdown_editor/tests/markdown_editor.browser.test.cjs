const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { before, after, test } = require('node:test');
const { chromium } = require('playwright');

const assets = path.resolve(__dirname, '..', 'frontend', 'build');
const asset = (name) => fs.readFileSync(path.join(assets, name), 'utf8');
const html = asset('editor.html');
const css = asset('editor.css');
const js = asset('renderers.bundle.js') + '\n' + asset('editor.js');
let browser;
const errors = new WeakMap();

before(async () => {
  browser = await chromium.launch({
    headless: true,
    ...(process.env.EDITOR_BROWSER_CHANNEL ? { channel: process.env.EDITOR_BROWSER_CHANNEL } : {}),
  });
});
after(async () => browser?.close());

async function mount(mode, blocks, extra = {}) {
  const page = await browser.newPage({ viewport: { width: 950, height: 1000 } });
  errors.set(page, []);
  page.on('pageerror', (error) => errors.get(page).push(error.message));
  await page.route('http://localhost/editor', (route) => route.fulfill({
    contentType: 'text/html; charset=utf-8', body: html,
  }));
  await page.goto('http://localhost/editor');
  await page.addStyleTag({ content: css });
  await page.evaluate(async ({ js, blocks, mode, extra }) => {
    const module = await import(URL.createObjectURL(new Blob([js], { type: 'text/javascript' })));
    window.editor = module.default;
    window.editorData = { blocks, mode, save_mode: 'auto', autosave_delay: 500, height: 760, ...extra };
    window.published = [];
    window.rerender = (changes = {}) => {
      Object.assign(window.editorData, changes);
      window.cleanup = window.editor({
        parentElement: document.body, data: window.editorData,
        setStateValue: (_, value) => window.published.push(value),
      });
    };
    window.rerender();
  }, { js, blocks, mode, extra });
  return page;
}

async function settle(page) {
  await page.waitForTimeout(650);
  assert.deepEqual(errors.get(page), [], 'Browser JavaScript errors');
  return page.evaluate(() => window.published.at(-1));
}

test('status bar visibility can change without resetting the document', async () => {
  const page = await mount('visual', [{ id: 'body', markdown: 'Original' }]);
  try {
    assert.equal(await page.locator('.md-status').isVisible(), true);
    await page.evaluate(() => window.rerender({ show_status_bar: false }));
    assert.equal(await page.locator('.md-status').isVisible(), false);
    assert.equal(await page.locator('.md-editable').innerText(), 'Original');
    await page.evaluate(() => window.rerender({ show_status_bar: true }));
    assert.equal(await page.locator('.md-status').isVisible(), true);
    await page.evaluate(() => window.rerender({ only_view: true }));
    assert.equal(await page.locator('.md-status').isVisible(), false);
  } finally { await page.close(); }
});

test('raw Markdown input is split into blocks and edited without losing content', async () => {
  const markdown = "# Title\n\nText paragraph\n\n```python\nprint('ok')\n```";
  const page = await mount('visual', [], { initial_markdown: markdown });
  try {
    assert.equal(await page.locator('.md-block').count(), 3);
    await page.locator('.md-editable').nth(1).click();
    await page.keyboard.type(' edited');
    const state = await settle(page);
    assert.match(state.markdown, /Text paragraph edited/);
    assert.match(state.markdown, /print\('ok'\)/);
    await page.evaluate((markdown) => window.rerender({ initial_markdown: markdown, revision: 1 }), state.markdown);
    assert.equal(await page.locator('.md-block').count(), 3);
    assert.match(await page.locator('.md-editable').nth(1).innerText(), /Text paragraph edited/);
  } finally { await page.close(); }
});

async function caret(page, selector, offset) {
  await page.locator(selector).first().focus();
  await page.evaluate(({ selector, offset }) => {
    const element = document.querySelector(selector);
    const walker = document.createTreeWalker(element, NodeFilter.SHOW_TEXT);
    let node;
    let remaining = offset;
    while ((node = walker.nextNode())) {
      if (remaining <= node.textContent.length) break;
      remaining -= node.textContent.length;
    }
    const range = document.createRange();
    range.setStart(node ?? element, node ? remaining : element.childNodes.length);
    range.collapse(true);
    window.getSelection().removeAllRanges();
    window.getSelection().addRange(range);
    document.dispatchEvent(new Event('selectionchange'));
  }, { selector, offset });
}

async function action(page, name) {
  const button = page.locator(`.md-floating-menu [data-action="${name}"]`);
  await button.evaluate((element) => element.scrollIntoView({ block: 'nearest', inline: 'nearest' }));
  await button.click();
}

for (const mode of ['raw_visual', 'visual']) {
  test(`${mode}: nested mixed lists roundtrip without losing syntax`, async () => {
    const markdown = '5. **Parent**\n    - Child\n\n        3. Grandchild\n6. Next\n   continuation';
    const page = await mount(mode, [{ id: 'list', markdown }]);
    try {
      const other = mode === 'visual' ? 'raw_visual' : 'visual';
      await page.locator(`.md-editor-mode [data-mode="${other}"]`).click();
      assert.equal((await settle(page)).markdown, markdown);
      assert.equal(await page.locator('ol ul ol').count(), other === 'visual' ? 1 : 0);
      await page.locator(`.md-editor-mode [data-mode="${mode}"]`).click();
      assert.equal((await settle(page)).markdown, markdown);
    } finally { await page.close(); }
  });

  test(`${mode}: ordered Enter and continuation Shift+Enter`, async () => {
    const page = await mount(mode, [{ id: 'list', markdown: '5. First\n6. Second' }]);
    try {
      await caret(page, mode === 'visual' ? '[data-path="1"]' : '.md-editable', mode === 'visual' ? 6 : 18);
      await page.keyboard.press('Enter');
      assert.equal((await settle(page)).markdown, '5. First\n6. Second\n7. ');
      await page.keyboard.type('Third');
      await page.keyboard.press('Shift+Enter');
      await page.keyboard.type('continued');
      assert.equal((await settle(page)).markdown, '5. First\n6. Second\n7. Third\n   continued');
      await page.keyboard.press('Control+z');
      assert.equal((await settle(page)).markdown, '5. First\n6. Second\n7. ');
      await page.keyboard.press('Control+Shift+z');
      assert.equal((await settle(page)).markdown, '5. First\n6. Second\n7. Third\n   continued');
    } finally { await page.close(); }
  });

  test(`${mode}: indent/outdent moves descendants and is undoable`, async () => {
    const markdown = '- First\n- Parent\n\n    5. Child\n        - Grandchild\n- Last';
    const page = await mount(mode, [{ id: 'list', markdown }]);
    try {
      await caret(page, mode === 'visual' ? '[data-path="1"]' : '.md-editable', mode === 'visual' ? 0 : 10);
      await page.keyboard.press('Tab');
      assert.equal((await settle(page)).markdown,
        '- First\n    - Parent\n\n        5. Child\n            - Grandchild\n- Last');
      await page.keyboard.press('Shift+Tab');
      assert.equal((await settle(page)).markdown, markdown);
      await page.keyboard.press('Control+z');
      assert.match((await settle(page)).markdown, /        5\. Child/);
      await page.keyboard.press('Control+y');
      assert.equal((await settle(page)).markdown, markdown);
    } finally { await page.close(); }
  });

  test(`${mode}: table inserts adjacent rows/columns and navigates`, async () => {
    const markdown = '| A | B |\n| :--- | ---: |\n| one | two |\n| three | four |';
    const page = await mount(mode, [{ id: 'table', markdown }]);
    try {
      const position = markdown.indexOf('two');
      await caret(page, mode === 'visual' ? 'tr:nth-child(2) td:nth-child(2)' : '.md-editable',
        mode === 'visual' ? 0 : position);
      await page.keyboard.press('Enter');
      assert.equal((await settle(page)).markdown,
        '| A | B |\n| :--- | ---: |\n| one | two |\n|  |  |\n| three | four |');
      await page.keyboard.press('Shift+Enter');
      assert.equal((await settle(page)).markdown,
        '| A | B | Columna 3 |\n| :--- | ---: | --- |\n| one | two |  |\n|  |  |  |\n| three | four |  |');
      await page.keyboard.press('Shift+Tab');
      await page.keyboard.type('active');
      assert.match((await settle(page)).markdown, /\|  \| active \|  \|/);
      await page.keyboard.press('Control+z');
      await page.keyboard.press('Control+z');
      assert.equal((await settle(page)).markdown,
        '| A | B |\n| :--- | ---: |\n| one | two |\n|  |  |\n| three | four |');
    } finally { await page.close(); }
  });

  test(`${mode}: quotes preserve nested depth on Enter and Tab`, async () => {
    const markdown = '> Root\n> > Nested\n>\n> Tail';
    const page = await mount(mode, [{ id: 'quote', markdown }]);
    try {
      await caret(page, mode === 'visual' ? '[data-line="1"]' : '.md-editable', mode === 'visual' ? 6 : 17);
      await page.keyboard.press('Enter');
      await page.keyboard.type('More');
      assert.equal((await settle(page)).markdown, '> Root\n> > Nested\n> > More\n>\n> Tail');
      await page.keyboard.press('Tab');
      assert.equal((await settle(page)).markdown, '> Root\n> > Nested\n> > > More\n>\n> Tail');
      await page.keyboard.press('Shift+Tab');
      assert.equal((await settle(page)).markdown, '> Root\n> > Nested\n> > More\n>\n> Tail');
    } finally { await page.close(); }
  });

  test(`${mode}: headings, paragraph breaks and block controls`, async () => {
    const page = await mount(mode, [{ id: 'heading', markdown: '# Heading' }]);
    try {
      await caret(page, '.md-editable', mode === 'visual' ? 7 : 9);
      await page.keyboard.press('Enter');
      await page.keyboard.type('Line');
      await page.keyboard.press('Enter');
      await page.keyboard.type('two');
      assert.equal((await settle(page)).markdown, '# Heading\n\nLine\ntwo');
      assert.equal(await page.locator('.md-block-tools .md-move-block').count(), 4);
      await action(page, 'add-before');
      assert.equal(await page.locator('.md-canvas > .md-block').count(), 3);
      await page.keyboard.press('Control+z');
      assert.equal(await page.locator('.md-canvas > .md-block').count(), 2);
    } finally { await page.close(); }
  });

  test(`${mode}: empty list items exit in place and Backspace preserves children`, async () => {
    const markdown = '- Before\n- \n- After\n    - Child';
    const page = await mount(mode, [{ id: 'list', markdown }]);
    try {
      await caret(page, mode === 'visual' ? '[data-path="1"]' : '.md-editable', mode === 'visual' ? 0 : 11);
      await page.keyboard.press('Enter');
      await page.keyboard.type('Between');
      assert.equal((await settle(page)).markdown, '- Before\n\nBetween\n\n- After\n    - Child');
      await page.keyboard.press('Control+z');
      await page.keyboard.press('Control+z');
      assert.equal((await settle(page)).markdown, markdown);
      await caret(page, mode === 'visual' ? '[data-path="1"]' : '.md-editable', mode === 'visual' ? 0 : 11);
      await page.keyboard.press('Backspace');
      assert.equal((await settle(page)).markdown, '- Before\n- After\n    - Child');
    } finally { await page.close(); }
  });

  test(`${mode}: list submenu targets the active sublist`, async () => {
    const markdown = '5. Parent\n    - Child\n    - Other\n6. Tail';
    const page = await mount(mode, [{ id: 'list', markdown }]);
    try {
      await caret(page, mode === 'visual' ? '[data-path="0.0"]' : '.md-editable', mode === 'visual' ? 0 : markdown.indexOf('Child'));
      await action(page, 'toggle-list');
      assert.equal((await settle(page)).markdown, '5. Parent\n    1. Child\n    2. Other\n6. Tail');
      await page.locator('[data-history="undo"]').click();
      assert.equal((await settle(page)).markdown, markdown);
      await caret(page, mode === 'visual' ? '[data-path="0.0"]' : '.md-editable', mode === 'visual' ? 0 : markdown.indexOf('Child'));
      await action(page, 'start-number');
      await page.getByRole('spinbutton', { name: 'Número inicial', exact: true }).fill('8');
      await page.getByRole('button', { name: 'Aplicar', exact: true }).click();
      assert.equal((await settle(page)).markdown, '5. Parent\n\n    8. Child\n    9. Other\n6. Tail');
    } finally { await page.close(); }
  });

  test(`${mode}: code indentation, language change and history`, async () => {
    const markdown = '```python\n    value = 1\n```';
    const page = await mount(mode, [{ id: 'code', markdown }]);
    try {
      await caret(page, '.md-editable', mode === 'visual' ? 13 : markdown.indexOf('\n```'));
      await page.keyboard.press('Enter');
      await page.keyboard.type('next = 2');
      assert.equal((await settle(page)).markdown, '```python\n    value = 1\n    next = 2\n```');
      await page.keyboard.press('Shift+Tab');
      assert.equal((await settle(page)).markdown, '```python\n    value = 1\nnext = 2\n```');
      await action(page, 'language');
      await page.locator('.md-properties-dialog').getByLabel('Lenguaje', { exact: true }).fill('javascript');
      await page.getByRole('button', { name: 'Aplicar', exact: true }).click();
      assert.match((await settle(page)).markdown, /^```javascript/);
      await page.keyboard.press('Control+z');
      assert.match((await settle(page)).markdown, /^```python/);
    } finally { await page.close(); }
  });
}

test('visual: splitting inline formatting preserves both halves', async () => {
  const page = await mount('visual', [{ id: 'list', markdown: '- **HelloWorld**\n- Last' }]);
  try {
    await caret(page, '[data-path="0"]', 5);
    await page.keyboard.press('Enter');
    assert.equal((await settle(page)).markdown, '- **Hello**\n- **World**\n- Last');
  } finally { await page.close(); }
});

test('debug rerender does not publish, reset unsaved changes or reset history', async () => {
  const page = await mount('visual', [{ id: 'body', markdown: 'Original' }], { save_mode: 'button' });
  try {
    await caret(page, '.md-editable', 8);
    await page.keyboard.type(' edited');
    await settle(page);
    const before = await page.evaluate(() => ({
      publications: window.published.length,
      history: document.querySelector('.md-editor').__markdownEditorRuntime.history.length,
    }));
    await page.evaluate(() => window.rerender({ debug_blocks: true }));
    assert.equal(await page.locator('.md-editable').innerText(), 'Original edited');
    assert.equal(await page.locator('.md-block-head').isVisible(), true);
    assert.deepEqual(await page.evaluate(() => ({
      publications: window.published.length,
      history: document.querySelector('.md-editor').__markdownEditorRuntime.history.length,
    })), before);
    await page.locator('.md-save').click();
    assert.equal((await settle(page)).markdown, 'Original edited');
    await page.locator('[data-history="undo"]').click();
    assert.equal(await page.locator('.md-editable').innerText(), 'Original');
  } finally { await page.close(); }
});

test('only_view is immutable, including keyboard and contextual controls', async () => {
  const page = await mount('visual', [], {
    only_view: true, debug_blocks: true,
    diff: { before: '# Before\n\n- First\n    - Child', after: '# After\n\n> > Nested' },
  });
  try {
    assert.equal(await page.locator('[contenteditable="true"]').count(), 0);
    assert.equal(await page.locator('.md-drag-handle').count(), 0);
    assert.equal(await page.locator('.md-block-head').first().isVisible(), true);
    assert.equal(await page.locator('.md-review-split > section:first-child ul ul').count(), 1);
    assert.equal(await page.locator('.md-review-split > section:last-child blockquote blockquote').count(), 1);
    assert.equal(await page.locator('.md-floating-menu').isVisible(), false);
    assert.equal(await page.evaluate(() => window.published.length), 0);
  } finally { await page.close(); }
});

test('toolbar formatting and block reordering share undo/redo history', async () => {
    const page = await mount('visual', [
      { id: 'one', markdown: 'First' }, { id: 'two', markdown: 'Second' }, { id: 'three', markdown: 'Third' },
    ]);
    try {
      await caret(page, '[data-block-id="one"] .md-editable', 0);
      await page.keyboard.press('Control+Shift+ArrowRight');
      await page.locator('[data-format="**"]').click();
      assert.equal((await settle(page)).blocks[0].markdown, '**First**');
      await page.locator('[data-history="undo"]').click();
      assert.equal((await settle(page)).blocks[0].markdown, 'First');
      await page.locator('[data-history="redo"]').click();
      assert.equal((await settle(page)).blocks[0].markdown, '**First**');
      assert.equal(await page.locator('[data-block-id="one"] .md-move-block[data-direction="up"]').isDisabled(), true);
      assert.equal(await page.locator('[data-block-id="three"] .md-move-block[data-direction="down"]').isDisabled(), true);
      const moveControls = page.locator('[data-block-id="two"] .md-block-move-controls');
      const dragHandle = page.locator('[data-block-id="two"] .md-drag-handle');
      assert.equal(await moveControls.isVisible(), false);
      await dragHandle.hover();
      assert.equal(await moveControls.isVisible(), true);
      const arrows = await moveControls.boundingBox();
      const handle = await dragHandle.boundingBox();
      assert.ok(arrows.x < handle.x);
      await page.locator('[data-block-id="two"] .md-move-block[data-direction="up"]').click();
      assert.deepEqual((await settle(page)).blocks.map((block) => block.id), ['two', 'one', 'three']);
      await page.locator('[data-history="undo"]').click();
      assert.deepEqual((await settle(page)).blocks.map((block) => block.id), ['one', 'two', 'three']);
      await page.locator('[data-history="redo"]').click();
      assert.deepEqual((await settle(page)).blocks.map((block) => block.id), ['two', 'one', 'three']);
      await page.locator('[data-history="undo"]').click();
      assert.deepEqual((await settle(page)).blocks.map((block) => block.id), ['one', 'two', 'three']);
      await page.locator('[data-block-id="one"] .md-drag-handle').dragTo(
        page.locator('[data-block-id="three"] .md-editable'));
      const reordered = (await settle(page)).blocks.map((block) => block.id);
      assert.notDeepEqual(reordered, ['one', 'two', 'three']);
      await page.locator('[data-history="undo"]').click();
      assert.deepEqual((await settle(page)).blocks.map((block) => block.id), ['one', 'two', 'three']);
      await page.locator('[data-history="redo"]').click();
      assert.deepEqual((await settle(page)).blocks.map((block) => block.id), reordered);
    } finally { await page.close(); }
});

test('reorder mode selects drag, buttons, or both and reveals buttons in context', async () => {
  for (const [mode, controlDisplay, dragDisplay] of [
    ['drag', 'none', 'grid'],
    ['drag_buttons', 'flex', 'grid'],
    ['buttons', 'flex', 'none'],
  ]) {
    const page = await mount('visual', [{ id: 'one', markdown: 'First' }], { reorder_mode: mode });
    try {
      const moveControls = page.locator('.md-block-move-controls');
      const dragHandle = page.locator('.md-drag-handle');
      assert.equal(await moveControls.evaluate((element) => getComputedStyle(element).display), controlDisplay);
      assert.equal(await dragHandle.evaluate((element) => getComputedStyle(element).display), dragDisplay);
      assert.equal(await moveControls.isVisible(), false);
      if (mode === 'buttons') {
        await page.locator('.md-block').hover();
      } else {
        await dragHandle.hover();
        if (mode === 'drag') continue;
        const arrows = await moveControls.boundingBox();
        const handle = await dragHandle.boundingBox();
        assert.ok(arrows.x < handle.x);
      }
      if (mode !== 'drag') assert.equal(await moveControls.isVisible(), true);
    } finally { await page.close(); }
  }
  const page = await mount('visual', [{ id: 'one', markdown: 'First' }], { reorder_mode: 'drag' });
  try {
    await page.evaluate(() => window.rerender({ reorder_mode: 'buttons' }));
    await page.waitForFunction(() => document.querySelector('.md-block').dataset.reorderMode === 'buttons');
    assert.equal(await page.locator('.md-drag-handle').evaluate((element) =>
    getComputedStyle(element).display), 'none');
    await page.locator('.md-block').hover();
    assert.equal(await page.locator('.md-block-move-controls').isVisible(), true);
  } finally { await page.close(); }
});

test('editor ribbon scrolls horizontally and keeps non-selectable group labels collapsed', async () => {
  const page = await mount('visual', [{ id: 'body', markdown: 'Text' }]);
  try {
    await page.setViewportSize({ width: 430, height: 900 });
    const groups = page.locator('.md-edit-row .md-ribbon-groups');
    const layout = await groups.evaluate((element) => ({
      flexWrap: getComputedStyle(element).flexWrap,
      overflowX: getComputedStyle(element).overflowX,
      scrollWidth: element.scrollWidth,
      clientWidth: element.clientWidth,
    }));
    assert.equal(layout.flexWrap, 'nowrap');
    assert.equal(layout.overflowX, 'auto');
    assert.ok(layout.scrollWidth > layout.clientWidth);
    const controlHeights = await page.locator(
      '.md-edit-row .md-toolbar-group-body > button, .md-edit-row .md-block-type',
    ).evaluateAll((elements) => elements.map((element) => element.getBoundingClientRect().height));
    assert.ok(Math.max(...controlHeights) - Math.min(...controlHeights) < 1);

    await page.locator('.md-edit-row .md-ribbon-toggle').click();
    assert.equal(await groups.isVisible(), true);
    assert.equal(await groups.locator('.md-toolbar-group-body').first().isVisible(), false);
    assert.equal(await groups.locator('.md-toolbar-group summary').first().isVisible(), true);
    const summary = groups.locator('.md-toolbar-group summary').first();
    const formatGroup = groups.locator('.md-toolbar-group[data-toolbar-section="format"]');
    assert.equal(await formatGroup.evaluate((element) =>
      getComputedStyle(element).borderRightWidth), '1px');
    assert.equal(await summary.locator(':scope > span').evaluate((element) =>
      getComputedStyle(element).writingMode), 'horizontal-tb');
    assert.equal(await summary.evaluate((element) => element.tabIndex), -1);
    assert.equal(await summary.getAttribute('aria-disabled'), 'true');
    assert.equal(await summary.evaluate((element) => getComputedStyle(element).pointerEvents), 'none');
    const panel = page.locator('.md-edit-row');
    const labels = await groups.boundingBox();
    const collapseButton = await page.locator('.md-edit-row .md-ribbon-toggle').boundingBox();
    assert.ok(Math.abs(labels.y + labels.height / 2 - collapseButton.y - collapseButton.height / 2) < 1);
    assert.ok(Math.abs(labels.x + labels.width - collapseButton.x) < 1);
    assert.equal(await panel.evaluate((element) => getComputedStyle(element).flexDirection), 'row');
    assert.equal(await panel.evaluate((element) => element.style.width), '');
    const group = summary.locator('xpath=..');
    const wasOpen = await group.evaluate((element) => element.open);
    await summary.evaluate((element) => element.dispatchEvent(
      new MouseEvent('click', { bubbles: true, cancelable: true }),
    ));
    assert.equal(await group.evaluate((element) => element.open), wasOpen);
    await page.locator('.md-edit-row .md-ribbon-toggle').click();
    assert.equal(await formatGroup.evaluate((element) =>
      getComputedStyle(element).borderRightWidth), '1px');
    assert.equal(await panel.evaluate((element) => getComputedStyle(element).flexDirection), 'column');
    assert.equal(await groups.evaluate((element) => element.style.flex), '');
  } finally { await page.close(); }
});

test('floating controls are bounded, horizontally scrollable and beside the block', async () => {
    const page = await mount('visual', [{ id: 'list', markdown: '- Parent\n    - Child' }]);
    try {
      await caret(page, '[data-path="0"]', 0);
      const menu = await page.locator('.md-floating-menu').boundingBox();
      const block = await page.locator('.md-block').boundingBox();
      const canvas = await page.locator('.md-canvas').boundingBox();
      assert.ok(menu.width <= 420);
      assert.ok(menu.y >= canvas.y - 1);
      assert.ok(menu.y + menu.height <= canvas.y + canvas.height + 1);
      assert.ok(menu.y + menu.height <= block.y + 2 || menu.y >= block.y + block.height - 2);
      const overflow = await page.locator('.md-floating-actions').evaluate(
        (element) => element.scrollWidth > element.clientWidth + 1);
      assert.equal(await page.locator('[data-scroll="1"]').isEnabled(), overflow);
      if (overflow) {
        await page.locator('[data-scroll="1"]').click();
        assert.ok(await page.locator('.md-floating-actions').evaluate((element) => element.scrollLeft > 0));
      }
      await page.setViewportSize({ width: 350, height: 1000 });
      await caret(page, '[data-path="0"]', 0);
      await page.keyboard.press('Shift+F10');
      const small = await page.locator('.md-floating-menu').boundingBox();
      assert.ok(small.width <= 350 * 0.9);
      assert.ok(small.x >= 0 && small.x + small.width <= 350);
    } finally { await page.close(); }
});

test('type controls limit headings without changing existing Markdown', async () => {
  const page = await mount('visual', [{ id: 'title', markdown: '# Existing' }], {
    allowed_block_types: ['paragraph', 'h2', 'h4'],
  });
  try {
    assert.deepEqual(await page.locator('.md-block-type option').evaluateAll((options) =>
      options.map((option) => option.value)), ['paragraph', 'h2', 'h4']);
    assert.equal(await page.locator('.md-add-block').isEnabled(), true);
    await caret(page, '.md-editable', 2);
    assert.equal(await page.locator('.md-block-type').inputValue(), '');
    assert.equal(await page.locator('.md-add-block').isDisabled(), true);
    assert.deepEqual(await page.locator('.md-floating-actions [data-action^="h"]').evaluateAll((buttons) =>
      buttons.map((button) => button.dataset.action)), ['h2', 'h4']);
    await page.locator('.md-block-type').selectOption('h2');
    assert.equal((await settle(page)).markdown, '## Existing');
    await page.locator('[data-history="undo"]').click();
    assert.equal((await settle(page)).markdown, '# Existing');
  } finally { await page.close(); }
});

for (const mode of ['visual', 'raw_visual']) {
  for (const [markdown, selector, offset] of [
    ['Before [one](https://one.test) and [two](https://two.test) after', '.md-editable', 18],
    ['[one](https://one.test) after', '.md-editable', 1],
    ['## Before [one](https://one.test) after', '.md-editable', 9],
    ['- Before [one](https://one.test) after\n- Keep', '.md-list-text', 9],
    ['> Before [one](https://one.test) after', '.md-quote-text', 9],
    ['| Link | Keep |\n| --- | --- |\n| [one](https://one.test) | unchanged |', 'td', 1],
  ]) {
    test(`${mode}: inline link editing preserves its ${markdown.slice(0, 10)} block`, async () => {
      const page = await mount(mode, [{ id: 'body', markdown }]);
      try {
        await caret(page, mode === 'visual' ? selector : '.md-editable',
          mode === 'visual' ? (selector === '.md-editable' && markdown.startsWith('Before') ? 8 : offset)
            : markdown.indexOf('[one]') + 2);
        assert.equal(await page.locator('.md-edit-link').isVisible(), true);
        await page.locator('.md-edit-link').click();
        await page.getByLabel('Texto del enlace', { exact: true }).fill('changed');
        await page.getByLabel('URL (http, https o mailto)', { exact: true }).fill('mailto:hello@example.com');
        await page.getByRole('button', { name: 'Aplicar', exact: true }).click();
        assert.equal((await settle(page)).markdown, markdown.replace('[one](https://one.test)', '[changed](mailto:hello@example.com)'));
        await page.locator('[data-history="undo"]').click();
        assert.equal((await settle(page)).markdown, markdown);
      } finally { await page.close(); }
    });
  }
}

for (const mode of ['visual', 'raw_visual']) {
  test(`${mode}: adds an inline link from Format`, async () => {
    const page = await mount(mode, [{ id: 'body', markdown: 'Click here.' }]);
    try {
      await page.locator('.md-editable').focus();
      await page.evaluate(() => {
        const text = document.querySelector('.md-editable').firstChild;
        const range = document.createRange();
        range.setStart(text, 6);
        range.setEnd(text, 10);
        window.getSelection().removeAllRanges();
        window.getSelection().addRange(range);
        document.dispatchEvent(new Event('selectionchange'));
      });
      assert.equal(await page.locator('[data-toolbar-section="format"] .md-edit-link').isVisible(), true);
      assert.equal(await page.locator('.md-floating-menu [data-action="add-link"], .md-floating-menu [data-action="edit-link"]').count(), 0);
      await page.locator('.md-edit-link').click();
      await page.getByLabel('Texto del enlace', { exact: true }).fill('destination');
      await page.getByLabel('URL (http, https o mailto)', { exact: true }).fill('https://example.com/help');
      await page.getByRole('button', { name: 'Aplicar', exact: true }).click();
      assert.equal(
        (await settle(page)).markdown,
        'Click [destination](https://example.com/help).',
      );
    } finally { await page.close(); }
  });
}

test('hovered links can be edited without moving the caret', async () => {
  const page = await mount('visual', [{ id: 'body', markdown: 'Before [link](https://one.test) after' }]);
  try {
    await caret(page, '.md-editable', 0);
    await page.locator('.md-editable a').hover();
    await page.locator('.md-edit-link').click();
    assert.equal(await page.getByLabel('URL (http, https o mailto)', { exact: true }).inputValue(), 'https://one.test');
    await page.getByRole('button', { name: 'Cancelar', exact: true }).click();
    assert.equal(await page.locator('.md-properties-dialog').isVisible(), false);
    assert.equal((await settle(page)).markdown, 'Before [link](https://one.test) after');
  } finally { await page.close(); }
});

test('image properties use a cancellable dialog with URL validation and history', async () => {
  const markdown = '![Before](https://example.com/image.png)';
  const page = await mount('visual', [{ id: 'image', markdown }]);
  page.on('dialog', () => assert.fail('Unexpected native browser dialog'));
  try {
    await page.locator('.md-editable').click();
    await action(page, 'edit-image');
    await page.getByLabel('Texto alternativo', { exact: true }).fill('After');
    await page.getByLabel('URL (http o https)', { exact: true }).fill('javascript:alert(1)');
    await page.getByRole('button', { name: 'Aplicar', exact: true }).click();
    assert.equal(await page.locator('.md-properties-error').isVisible(), true);
    await page.keyboard.press('Escape');
    assert.equal((await settle(page)).markdown, markdown);
    await action(page, 'edit-image');
    await page.getByLabel('Texto alternativo', { exact: true }).fill('After');
    await page.getByLabel('URL (http o https)', { exact: true }).fill('https://example.com/new image.png');
    await page.getByRole('button', { name: 'Aplicar', exact: true }).click();
    assert.equal((await settle(page)).markdown, '![After](https://example.com/new%20image.png)');
    await page.locator('[data-history="undo"]').click();
    assert.equal((await settle(page)).markdown, markdown);
  } finally { await page.close(); }
});

test('single editor and review choices hide their selectors', async () => {
  const page = await mount('visual', [{ id: 'body', markdown: 'Original' }], {
    editor_modes: ['visual'], save_mode: 'button', review_modes: ['visual'], review_layouts: ['after'],
  });
  try {
    assert.equal(await page.locator('.md-editor-mode').isVisible(), false);
    await page.evaluate(() => window.rerender({ editor_modes: ['raw_visual', 'visual'] }));
    assert.equal(await page.locator('.md-editor-mode').isVisible(), true);
    await caret(page, '.md-canvas .md-editable', 8);
    await page.keyboard.type(' draft');
    await page.locator('.md-review-button').click();
    assert.equal(await page.locator('.md-back-editor').evaluate((button) => document.activeElement === button), true);
    await page.locator('.md-back-editor').click();
    assert.equal(await page.locator('.md-canvas .md-editable').innerText(), 'Original draft');
    await page.evaluate(() => window.rerender({
      only_view: true, diff: { before: 'Old', after: 'New' },
      review_modes: ['visual'], review_layouts: ['after'],
    }));
    assert.equal(await page.locator('[aria-label="Formato de comparación"]').isVisible(), false);
    assert.equal(await page.locator('.md-review-versions').isVisible(), false);
    assert.equal(await page.locator('.md-review-content h4').textContent(), 'Después');
    assert.equal(await page.locator('.md-review-content .md-editable').innerText(), 'New');
  } finally { await page.close(); }
});

test('autosave debounces edits, ignores server echoes and flushes before viewing', async () => {
  const page = await mount('visual', [{ id: 'body', markdown: 'Original' }], { autosave_delay: 1000 });
  try {
    await caret(page, '.md-editable', 8);
    const initial = await page.evaluate(() => window.published.length);
    await page.keyboard.type(' first');
    await page.waitForTimeout(550);
    assert.equal(await page.evaluate(() => window.published.length), initial);
    await page.keyboard.type(' second');
    await page.waitForTimeout(550);
    assert.equal(await page.evaluate(() => window.published.length), initial);
    await page.waitForFunction((initial) => window.published.length === initial + 1, initial);
    const published = await page.evaluate(() => window.published.at(-1));
    assert.equal(published.markdown, 'Original first second');
    await page.keyboard.type(' draft');
    await page.evaluate((blocks) => window.rerender({ blocks }), published.blocks);
    assert.equal(await page.locator('.md-canvas .md-editable').innerText(), 'Original first second draft');
    await page.evaluate(() => window.rerender({ only_view: true }));
    assert.equal(await page.evaluate(() => window.published.at(-1).markdown), 'Original first second draft');
    await page.evaluate(() => window.rerender({ only_view: false }));
    assert.equal(await page.locator('.md-canvas .md-editable').innerText(), 'Original first second draft');
    await page.locator('[data-history="undo"]').click();
    assert.notEqual(await page.locator('.md-canvas .md-editable').innerText(), 'Original first second draft');
  } finally { await page.close(); }
});

test('cleanup flushes autosave and rerender restores selection listeners', async () => {
  const page = await mount('visual', [{ id: 'body', markdown: 'Original' }], { autosave_delay: 1000 });
  try {
    await caret(page, '.md-editable', 8);
    await page.keyboard.type(' pending');
    await page.evaluate(() => { window.cleanup(); window.rerender(); });
    assert.equal(await page.evaluate(() => window.published.at(-1).markdown), 'Original pending');
    await caret(page, '.md-editable', 0);
    assert.equal(await page.evaluate(() => document.querySelector('.md-editor').__markdownEditorRuntime.bookmark.start), 0);
    await page.locator('[data-history="undo"]').click();
    assert.equal(await page.locator('.md-editable').innerText(), 'Original');
    await page.waitForTimeout(1100);
    assert.equal(await page.evaluate(() => window.published.at(-1).markdown), 'Original');
  } finally { await page.close(); }
});

test('styles apply to diagrams and tables in editing and readonly views', async () => {
  const page = await mount('visual', [
    { id: 'diagram', markdown: '```mermaid\nflowchart LR\n A[Start] --> B[End]\n```' },
    { id: 'table', markdown: '| Head |\n| --- |\n| Body |' },
  ], {
    mermaid_config: { theme: 'base', themeVariables: { primaryColor: '#ff0000' } },
    table_styles: { table: { width: '75%' }, th: { color: 'rgb(255, 0, 0)' }, td: { padding: '20px' } },
  });

  try {
    await page.waitForSelector('.md-rendered-preview svg .node rect');
    assert.equal(await page.locator('.node rect').first().evaluate((element) =>
      getComputedStyle(element).fill), 'rgb(255, 0, 0)');
    assert.equal(await page.locator('.md-editable th').evaluate((element) => getComputedStyle(element).color), 'rgb(255, 0, 0)');
    assert.equal(await page.locator('.md-editable td').evaluate((element) => getComputedStyle(element).padding), '20px');
    await page.evaluate(() => window.rerender({
      mermaid_config: { theme: 'base', themeVariables: { primaryColor: '#00ff00' } },
      table_styles: { td: { padding: '12px' } },
    }));
    await page.waitForFunction(() => {
      const rect = document.querySelector('.node rect');
      return rect && getComputedStyle(rect).fill === 'rgb(0, 255, 0)';
    });
    assert.equal(await page.locator('.md-editable td').evaluate((element) => getComputedStyle(element).padding), '12px');
    assert.equal(await page.locator('.md-editable th').evaluate((element) => element.style.color), '');
    await page.evaluate(() => window.rerender({ only_view: true }));
    await page.waitForSelector('.md-review-content .node rect');
    assert.equal(await page.locator('.md-review-content .node rect').first().evaluate((element) =>
      getComputedStyle(element).fill), 'rgb(0, 255, 0)');
    assert.equal(await page.locator('.md-review-content td').evaluate((element) => getComputedStyle(element).padding), '12px');
    assert.deepEqual(errors.get(page), []);
  } finally { await page.close(); }
});

test('Mermaid styles remain isolated between editors rendering concurrently', async () => {
  const page = await mount('visual', [{ id: 'body', markdown: '' }]);
  try {
    await page.evaluate(async (html) => {
      const editors = ['#ff0000', '#00ff00'].map((color) => {
        const container = document.createElement('div');
        container.innerHTML = html;
        document.body.append(container);
        window.editor({
          parentElement: container,
          data: {
            mode: 'visual', save_mode: 'auto', autosave_delay: 500,
            blocks: [{ id: color, markdown: '```mermaid\nflowchart LR\n A[Start] --> B[End]\n```' }],
            mermaid_config: { theme: 'base', themeVariables: { primaryColor: color } },
          },
          setStateValue: () => {},
        });
        return container;
      });
      await Promise.all(editors.map((container) => container.querySelector('.md-block').__renderPromise));
      window.diagramColors = editors.map((container) =>
        getComputedStyle(container.querySelector('.node rect')).fill);
    }, html);
    assert.deepEqual(await page.evaluate(() => window.diagramColors), ['rgb(255, 0, 0)', 'rgb(0, 255, 0)']);
    assert.deepEqual(errors.get(page), []);
  } finally { await page.close(); }
});
