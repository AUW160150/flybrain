import { beforeEach, expect, it, vi } from 'vitest';
import { activateViewport, installKeyboardListeners } from '../src/controls/keyboard';
import { controlsActive, useStudio } from '../src/state/store';
import { element, focus, key } from './support/keyboard';

const state = () => useStudio.getState();
beforeEach(() => { useStudio.setState(useStudio.getInitialState(), true); focus(); });

it('does not restart cleared movement on browser key repeat', () => {
  key('KeyW'); state().setCamera('BRAIN_INSPECTION'); key('Escape');
  key('KeyW', { repeat: true }); expect(state().motion.FORWARD).toBe(false);
  key('KeyW', { up: true }); key('KeyW'); expect(state().motion.FORWARD).toBe(true);
});
it('keeps Tab and Shift+Tab navigation outside the scoped shortcut', () => {
  expect(key('Tab', { target: 'body' })).not.toHaveBeenCalled();
  expect(state().cameraMode).toBe('WORLD_FOLLOW');
  expect(key('Tab', { shiftKey: true })).not.toHaveBeenCalled();
  expect(key('Tab')).toHaveBeenCalled(); expect(state().cameraMode).toBe('BRAIN_INSPECTION');
});
it('leaves native dialog Escape and form shortcuts alone', () => {
  state().setCamera('BRAIN_INSPECTION');
  key('Escape', { target: 'dialog' }); expect(state().cameraMode).toBe('BRAIN_INSPECTION');
  key('Escape', { target: 'input' }); expect(state().cameraMode).toBe('BRAIN_INSPECTION');
  key('KeyB', { target: 'button' }); expect(state().transparentHead).toBe(false);
});
it('logs Escape as keyboard input and restores the preceding orbit camera', () => {
  state().setCamera('WORLD_ORBIT'); state().setCamera('BRAIN_INSPECTION'); key('Escape');
  expect(state().cameraMode).toBe('WORLD_ORBIT'); expect(state().controls.at(-1)?.input).toBe('KEYBOARD');
});
it('does not retrigger held behavior commands or duplicate held motion events', () => {
  key('KeyF'); key('KeyF', { repeat: true }); expect(state().controls).toHaveLength(1);
  expect(state().behavior?.sourceMode).toBe('USER_DRIVEN_ILLUSTRATION');
  key('KeyW'); key('KeyW'); key('KeyW', { repeat: true }); expect(state().controls).toHaveLength(2);
});
it('viewport activation calls focus and enables world controls', () => {
  focus('body'); expect(controlsActive(state())).toBe(false);
  const viewport = element(); activateViewport(viewport);
  expect(viewport.focus).toHaveBeenCalledWith({ preventScroll: true });
  expect(controlsActive(state())).toBe(true); expect(state().focusTarget).toBe('3D viewport');
});
it.each(['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'])('prevents scrolling for every active %s event, including repeats', code => {
  expect(key(code)).toHaveBeenCalled(); expect(key(code, { repeat: true })).toHaveBeenCalled();
  focus('body'); expect(key(code, { target: 'body' })).not.toHaveBeenCalled();
  expect(Object.values(state().motion).some(Boolean)).toBe(false);
});
it.each(['input', 'textarea', 'select', 'contenteditable'] as const)('releases held input before typing in %s and leaves keys native', target => {
  key('KeyW'); state().tick(0.05); focus(target); const pose = state().pose;
  for (const code of ['KeyW', 'ArrowUp', 'KeyS', 'KeyA', 'KeyF', 'Space', 'Tab']) expect(key(code, { target })).not.toHaveBeenCalled();
  state().tick(0.05); expect(state().pose).toEqual(pose); expect(state().pressedKeys.size).toBe(0);
  expect(controlsActive(state())).toBe(false);
});
it('independently releases key aliases and movement pad inputs', () => {
  key('KeyW'); key('ArrowUp'); key('KeyW', { up: true }); expect(state().motion.FORWARD).toBe(true);
  expect([...state().pressedKeys]).toEqual(['ArrowUp']);
  state().setMotion('FORWARD', true, 'POINTER'); key('ArrowUp', { up: true }); expect(state().motion.FORWARD).toBe(true);
  state().setMotion('FORWARD', false, 'POINTER'); expect(state().motion.FORWARD).toBe(false);
  expect(state().events.filter(e => e.heldKey === 'FORWARD')).toHaveLength(1);
  expect(state().events[0].endMs).not.toBeNull();
});
it('honors key releases after modifiers or focus change', () => {
  key('KeyW'); key('KeyW', { up: true, target: 'input', metaKey: true }); expect(state().motion.FORWARD).toBe(false);
  key('ArrowUp', { ctrlKey: true }); key('KeyA', { metaKey: true }); key('KeyD', { altKey: true });
  key('KeyS', { isComposing: true }); expect(state().pressedKeys.size).toBe(0);
});
it('X clears held input without browser-repeat restart', () => {
  key('KeyW'); key('KeyA'); key('ShiftLeft'); key('KeyX');
  expect(state().pressedKeys.size).toBe(0); expect(Object.values(state().motion).some(Boolean)).toBe(false);
  const pose = state().pose; key('KeyW', { repeat: true }); state().tick(0.05); expect(state().pose).toEqual(pose);
});
it('registers one listener set, cleans up, and handles blur/hidden without stuck input', () => {
  const win = new EventTarget() as unknown as Window;
  const doc = Object.assign(new EventTarget(), { hidden: false, activeElement: element() }) as unknown as Document;
  const add = vi.spyOn(win, 'addEventListener'), remove = vi.spyOn(win, 'removeEventListener');
  const addDoc = vi.spyOn(doc, 'addEventListener'), removeDoc = vi.spyOn(doc, 'removeEventListener');
  const cleanup = installKeyboardListeners(win, doc);
  key('KeyW'); win.dispatchEvent(new Event('blur')); expect(state().pressedKeys.size).toBe(0); expect(controlsActive(state())).toBe(false);
  focus(); key('KeyW'); Object.defineProperty(doc, 'hidden', { value: true });
  doc.dispatchEvent(new Event('visibilitychange')); expect(state().motion.FORWARD).toBe(false);
  cleanup(); expect(add.mock.calls).toEqual(remove.mock.calls); expect(addDoc.mock.calls).toEqual(removeDoc.mock.calls);
  const cleanupAgain = installKeyboardListeners(win, doc); key('KeyW'); cleanupAgain();
  expect(state().pressedKeys.size).toBe(0); expect(add).toHaveBeenCalledTimes(6); expect(remove).toHaveBeenCalledTimes(6);
});
