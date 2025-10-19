import { describe, it, expect, beforeEach } from 'vitest';
import { JSDOM } from 'jsdom';
import { buildTreeView } from './TreeView';
import type { WidgetData, WidgetMetadata, ChunkSize } from '../types';
import { FoldingController } from '../folding/controller';
import type { FoldingClient, FoldingEvent, FoldingState } from '../folding/types';

const dom = new JSDOM('<!DOCTYPE html><html><body></body></html>');
global.document = dom.window.document;
global.window = dom.window as unknown as Window & typeof globalThis;

describe('TreeView', () => {
  let data: WidgetData;
  let metadata: WidgetMetadata;
  let foldingController: FoldingController;
  let controllerHarness: TestFoldingController;

  beforeEach(() => {
    data = {
      ir: {
        chunks: [
          { id: 'chunk-a', element_id: 'elem-static', type: 'TextChunk', text: 'Hello world', metadata: {} },
          { id: 'chunk-b', element_id: 'elem-interp', type: 'TextChunk', text: 'Dynamic', metadata: {} },
        ],
        source_prompt_id: 'root',
        id: 'ir',
        metadata: {},
      },
      source_prompt: {
        prompt_id: 'root',
        children: [
          {
            id: 'elem-static',
            type: 'static',
            key: 'Analyze this prompt',
            children: [
              { id: 'elem-interp', type: 'interpolation', key: 'query', children: [] },
            ],
          },
        ],
      },
      compiled_ir: { ir_id: 'root', subtree_map: {}, num_elements: 1 },
      config: { wrapping: true, sourcePrefix: '' },
    };

    metadata = {
      elementTypeMap: {},
      elementLocationMap: {},
      chunkSizeMap: {
        'chunk-a': { character: 11, pixel: 0 } satisfies ChunkSize,
        'chunk-b': { character: 7, pixel: 0 } satisfies ChunkSize,
      },
    };

    controllerHarness = new TestFoldingController(['chunk-a', 'chunk-b']);
    foldingController = controllerHarness as unknown as FoldingController;
  });

  it('renders tree hierarchy with correct structure', () => {
    const tree = buildTreeView({ data, metadata, foldingController });
    const root = tree.element;

    expect(root.classList.contains('tp-tree-view')).toBe(true);

    const header = root.querySelector('.tp-tree-header');
    const title = header?.querySelector('.tp-tree-title');
    expect(title?.textContent).toBe('Structure');

    const itemsContainer = root.querySelector('.tp-tree-items');
    expect(itemsContainer).toBeTruthy();

    const items = itemsContainer?.querySelectorAll('.tp-tree-item');
    expect(items?.length).toBe(2); // parent + child

    const firstRow = items?.[0].querySelector('.tp-tree-row');
    const firstKey = firstRow?.querySelector('.tp-tree-key');
    // Static elements now show their text content instead of key
    expect(firstKey?.textContent).toBe('Hello world');
    expect(firstRow?.querySelector('.tp-tree-icon')?.textContent).toBe('▪');

    const childRow = items?.[1].querySelector('.tp-tree-row');
    const childKey = childRow?.querySelector('.tp-tree-key');
    expect(childKey?.textContent).toBe('query');
    expect(childRow?.querySelector('.tp-tree-icon')?.textContent).toBe('◆');

    const meterText = firstRow?.querySelector('.tp-meter-text--characters')?.textContent;
    expect(meterText).toBe('18/18ch');
  });

  it('toggles expansion when row clicked', async () => {
    const tree = buildTreeView({ data, metadata, foldingController });
    const itemsContainer = tree.element.querySelector('.tp-tree-items');
    const firstItem = itemsContainer?.querySelector('.tp-tree-item');
    expect(firstItem).toBeTruthy();

    const row = firstItem?.querySelector('.tp-tree-row') as HTMLElement;
    const toggleButton = firstItem?.querySelector('.tp-tree-toggle') as HTMLButtonElement;
    expect(row).toBeTruthy();
    expect(toggleButton.textContent).toBe('▸'); // Starts collapsed

    row.click();
    // Wait for debounce delay (250ms) plus buffer
    await new Promise(resolve => setTimeout(resolve, 300));
    expect(firstItem?.classList.contains('tp-tree-item--expanded')).toBe(true);
    expect(toggleButton.textContent).toBe('▾');

    row.click();
    // Wait for debounce delay again
    await new Promise(resolve => setTimeout(resolve, 300));
    expect(firstItem?.classList.contains('tp-tree-item--collapsed')).toBe(true);
    expect(toggleButton.textContent).toBe('▸');
  });

  it('handles leaf nodes without toggles', () => {
    const tree = buildTreeView({ data, metadata, foldingController });
    const leafItem = tree.element.querySelectorAll('.tp-tree-item')[1];

    const toggleButton = leafItem.querySelector('.tp-tree-toggle') as HTMLButtonElement;
    expect(toggleButton.textContent).toBe('');
    expect(toggleButton.disabled).toBe(true);
  });

  it('updates visibility meter when folding state changes', () => {
    const tree = buildTreeView({ data, metadata, foldingController });
    const firstRow = tree.element.querySelector('.tp-tree-row');
    const meter = firstRow?.querySelector('.tp-meter-text--characters');
    expect(meter?.textContent).toBe('18/18ch');

    controllerHarness.collapse(['chunk-a']);
    expect(meter?.textContent).toBe('7/18ch');

    controllerHarness.expand(['chunk-a']);
    expect(meter?.textContent).toBe('18/18ch');
  });

  it('collapses and expands chunks on double click', () => {
    const realController = new FoldingController(['chunk-a', 'chunk-b']);
    const tree = buildTreeView({ data, metadata, foldingController: realController });

    const firstRow = tree.element.querySelector('.tp-tree-row') as HTMLElement;
    const meter = firstRow.querySelector('.tp-meter-text--characters');
    expect(meter?.textContent).toBe('18/18ch');

    firstRow.dispatchEvent(new dom.window.MouseEvent('dblclick', { bubbles: true }));
    expect(realController.isCollapsed('chunk-a')).toBe(true);
    expect(meter?.textContent).toBe('0/18ch');

    firstRow.dispatchEvent(new dom.window.MouseEvent('dblclick', { bubbles: true }));
    expect(realController.isCollapsed('chunk-a')).toBe(false);
    expect(meter?.textContent).toBe('18/18ch');
  });
});

class TestFoldingController {
  private collapsed = new Set<string>();
  private clients = new Set<FoldingClient>();

  constructor(private readonly chunkIds: string[]) {}

  isCollapsed = (chunkId: string): boolean => this.collapsed.has(chunkId);

  addClient = (client: FoldingClient): void => {
    this.clients.add(client);
  };

  removeClient = (client: FoldingClient): void => {
    this.clients.delete(client);
  };

  collapse(ids: string[]): void {
    ids.forEach((id) => this.collapsed.add(id));
    this.notifyClients({ type: 'chunks-collapsed' } as FoldingEvent);
  }

  expand(ids: string[]): void {
    ids.forEach((id) => this.collapsed.delete(id));
    this.notifyClients({ type: 'chunk-expanded' } as FoldingEvent);
  }

  private notifyClients(event: FoldingEvent): void {
    const state: FoldingState = {
      visibleSequence: this.chunkIds.filter((id) => !this.collapsed.has(id)),
      collapsedChunks: new Map(),
      selections: [],
    };

    for (const client of this.clients) {
      client.onStateChanged(event, state);
    }
  }
}
