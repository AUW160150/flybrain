import type { MotionKey } from '../data/contracts';
import { useStudio, isInspection } from '../state/store';

export function MovementPad() {
  const paused = useStudio(s => isInspection(s.cameraMode) || s.mode !== 'USER_CONTROL');
  const keys: { key: MotionKey; letter: string; name: string }[] = [
    { key: 'FORWARD', letter: 'W', name: 'Move forward' },
    { key: 'LEFT', letter: 'A', name: 'Turn left' },
    { key: 'BACKWARD', letter: 'S', name: 'Move backward' },
    { key: 'RIGHT', letter: 'D', name: 'Turn right' },
  ];
  return <div className="movement-pad" aria-label="Hold to move">{keys.map(({ key, letter, name }) => <button key={key} disabled={paused} aria-label={name}
    onPointerDown={e => { e.currentTarget.focus({ preventScroll: true }); e.currentTarget.setPointerCapture(e.pointerId); useStudio.getState().setMotion(key, true, 'POINTER'); }}
    onPointerUp={() => useStudio.getState().setMotion(key, false, 'POINTER')}
    onPointerCancel={() => useStudio.getState().setMotion(key, false, 'POINTER')}
    onLostPointerCapture={() => useStudio.getState().setMotion(key, false, 'POINTER')}
    onBlur={() => useStudio.getState().setMotion(key, false, 'POINTER')}
    onKeyDown={e => { if (!e.repeat && (e.code === 'Space' || e.code === 'Enter')) { e.preventDefault(); useStudio.getState().setMotion(key, true, 'KEYBOARD'); } }}
    onKeyUp={e => { if (e.code === 'Space' || e.code === 'Enter') { e.preventDefault(); useStudio.getState().setMotion(key, false, 'KEYBOARD'); } }}
  >{letter}</button>)}</div>;
}
