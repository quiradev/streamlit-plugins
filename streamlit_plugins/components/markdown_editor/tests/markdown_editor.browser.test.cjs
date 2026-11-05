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
    contentType: 'text/html', body: html,
  }));
  await page.goto('http://localhost/editor');
  await page.addStyleTag({ content: css });
  await page.evaluate(async ({ js, blocks, mode, extra }) => {
    const module = await import(URL.createObjectURL(new Blob([js], { type: 'text/javascript' })));
    window.editor = module.default;
    window.editorData = { blocks, mode, save_mode: 'auto', height: 760, ...extra };
    window.published = [];
    window.rerender = (changes = {}) => {
      Object.assign(window.editorData, changes);
      window.editor({
        parentElement: document.body, data: window.editorData,
        setStateValue: (_, value) => window.published.push(value),
      });
    };
    window.rerender();
  }, { js, blocks, mode, extra });
  return page;
}

async function settle(page) {
  await page.waitForTimeout(450);
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
      assert.equal(await page.locator('.md-block-tools > *:not(.md-drag-handle)').count(), 0);
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
      page.once('dialog', (dialog) => dialog.accept('8'));
      await action(page, 'start-number');
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
      page.once('dialog', (dialog) => dialog.accept('javascript'));
      await action(page, 'language');
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
    assert.equal(await page.locator('.md-diff-before ul ul').count(), 1);
    assert.equal(await page.locator('.md-diff-after blockquote blockquote').count(), 1);
    assert.equal(await page.locator('.md-floating-menu').isVisible(), false);
    assert.equal(await page.evaluate(() => window.published.length), 0);
  } finally { await page.close(); }
});

test('toolbar formatting and drag-handle reordering share undo/redo history', async () => {
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

test('floating controls are bounded, horizontally scrollable and above the block', async () => {
    const page = await mount('visual', [{ id: 'list', markdown: '- Parent\n    - Child' }]);
    try {
      await caret(page, '[data-path="0"]', 0);
      const menu = await page.locator('.md-floating-menu').boundingBox();
      const block = await page.locator('.md-block').boundingBox();
      assert.ok(menu.width <= 420);
      assert.ok(menu.y + menu.height <= block.y + 2);
      const overflow = await page.locator('.md-floating-actions').evaluate(
        (element) => element.scrollWidth > element.clientWidth + 1);
      assert.equal(await page.locator('[data-scroll="1"]').isEnabled(), overflow);
      if (overflow) {
        await page.locator('[data-scroll="1"]').click();
        assert.ok(await page.locator('.md-floating-actions').evaluate((element) => element.scrollLeft > 0));
      }
      await page.setViewportSize({ width: 350, height: 1000 });
      const small = await page.locator('.md-floating-menu').boundingBox();
      assert.ok(small.width <= 350 * 0.9);
      assert.ok(small.x >= 0 && small.x + small.width <= 350);
    } finally { await page.close(); }
});
