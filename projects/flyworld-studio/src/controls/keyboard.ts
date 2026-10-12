import { useEffect } from 'react';
import { controlsActive, useStudio } from '../state/store';
import type { BehaviorCommand } from '../data/contracts';
import { isInputKey } from './input';

export { motionKeys } from './input';
const behaviorKeys: Record<string, BehaviorCommand> = { Space: 'TAKEOFF_LAND', KeyF: 'FEED', KeyG: 'GROOM', KeyE: 'ESCAPE', KeyC: 'COURTSHIP', KeyX: 'STOP' };
const editable = 'input,textarea,select,[contenteditable]:not([contenteditable="false"])';

/** Record element identity, never the contents of a form field. */
export function handleFocusTarget(target: EventTarget | null) {
  const element = target as HTMLElement | null;
  const viewport = !!element?.closest?.('[data-world-viewport]') && !element?.closest?.(`dialog,${editable},button,a`);
  const label = viewport ? '3D viewport' : element?.tagName
    ? `${element.tagName.toLowerCase()}${element.id ? `#${element.id}` : ''}${element.getAttribute('aria-label') ? `: ${element.getAttribute('aria-label')}` : ''}`.slice(0, 90)
    : 'No world focus';
  useStudio.getState().setControlsFocus(viewport, label);
}

export function activateViewport(element: HTMLElement) {
  element.focus({ preventScroll: true });
  handleFocusTarget(element);
}

export function handleKeyDown(event: KeyboardEvent) {
  const s = useStudio.getState();
  const target = event.target as HTMLElement | null;
  if (target?.closest?.(`dialog,${editable}`) || event.isComposing) return;
  if (event.ctrlKey || event.metaKey || event.altKey) return;
  if (event.code === 'Escape') { if (!event.repeat) s.backToWorld('KEYBOARD'); s.releaseMotion(); return; }
  if (!s.viewportFocused || !target?.closest?.('[data-world-viewport]') || target.closest('button,a')) return;
  if (isInputKey(event.code)) {
    if (!controlsActive(s)) return;
    // Prevent every repeated arrow event too; motion itself is driven by the clock.
    event.preventDefault();
    if (!event.repeat) s.setPressedKey(event.code, true);
    return;
  }
  if (event.code === 'Tab' && event.shiftKey) return;
  if (behaviorKeys[event.code] || event.code === 'Tab') event.preventDefault();
  // Cleared held keys must not restart after inspection, Stop, or a focus change.
  if (event.repeat) return;
  if (behaviorKeys[event.code]) { event.preventDefault(); s.command(behaviorKeys[event.code], 'KEYBOARD'); }
  else if (event.code === 'KeyB') s.toggleHead('KEYBOARD');
  else if (event.code === 'KeyP') s.toggleTimeline('KEYBOARD');
  else if (event.code === 'Tab') { event.preventDefault(); s.setCamera('BRAIN_INSPECTION', 'KEYBOARD'); }
}

export function handleKeyUp(event: KeyboardEvent) {
  // Releases are honored even when focus/modifiers have changed since the press.
  useStudio.getState().setPressedKey(event.code, false);
}

export function installKeyboardListeners(win: Window = window, doc: Document = document) {
  const release = () => { useStudio.getState().releaseMotion(); useStudio.getState().setControlsFocus(false, 'Window inactive'); };
  const visibility = () => { if (doc.hidden) release(); };
  const focusIn = (event: FocusEvent) => handleFocusTarget(event.target);
  const focusOut = (event: FocusEvent) => handleFocusTarget(event.relatedTarget);
  win.addEventListener('keydown', handleKeyDown);
  win.addEventListener('keyup', handleKeyUp);
  win.addEventListener('blur', release);
  doc.addEventListener('visibilitychange', visibility);
  doc.addEventListener('focusin', focusIn);
  doc.addEventListener('focusout', focusOut);
  handleFocusTarget(doc.activeElement);
  return () => {
    win.removeEventListener('keydown', handleKeyDown); win.removeEventListener('keyup', handleKeyUp);
    win.removeEventListener('blur', release); doc.removeEventListener('visibilitychange', visibility);
    doc.removeEventListener('focusin', focusIn); doc.removeEventListener('focusout', focusOut);
    release();
  };
}

export function useKeyboard() {
  useEffect(() => installKeyboardListeners(), []);
}
