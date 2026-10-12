import { vi } from 'vitest';
import { handleFocusTarget, handleKeyDown, handleKeyUp } from '../../src/controls/keyboard';

type Target = 'viewport' | 'body' | 'dialog' | 'button' | 'input' | 'textarea' | 'select' | 'contenteditable';
/** Adapter fixture only; browser focus/hit testing is covered separately by Playwright. */
export function element(kind: Target = 'viewport') {
  return {
    tagName: kind === 'contenteditable' || kind === 'viewport' ? 'DIV' : kind.toUpperCase(),
    id: '', getAttribute: () => null, focus: vi.fn(),
    closest: (selector: string) => {
      if (selector.includes('[data-world-viewport]')) return kind === 'viewport' ? {} : null;
      if (kind === 'body' || kind === 'viewport') return null;
      return selector.includes(kind) ? {} : null;
    },
  } as unknown as HTMLElement;
}
export function focus(kind: Target = 'viewport') { handleFocusTarget(element(kind)); }
export function key(code: string, options: { target?: Target; repeat?: boolean; shiftKey?: boolean; ctrlKey?: boolean; metaKey?: boolean; altKey?: boolean; isComposing?: boolean; up?: boolean } = {}) {
  const preventDefault = vi.fn();
  const event = { code, repeat: false, shiftKey: false, ctrlKey: false, metaKey: false, altKey: false, isComposing: false,
    ...options, preventDefault, target: element(options.target),
  } as unknown as KeyboardEvent;
  if (options.up) handleKeyUp(event); else handleKeyDown(event);
  return preventDefault;
}
