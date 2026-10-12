import { useEffect } from 'react';
import { useStudio } from '../state/store';

/** One display clock even when WebGL is unavailable. No neural-model integration. */
export function useStudioClock() {
  useEffect(() => {
    let previous = performance.now();
    let request = 0;
    const step = (now: number) => {
      if (!document.hidden) useStudio.getState().tick((now - previous) / 1000);
      previous = now;
      request = requestAnimationFrame(step);
    };
    request = requestAnimationFrame(step);
    const media = matchMedia('(prefers-reduced-motion: reduce)');
    const sync = () => useStudio.getState().setReducedMotion(media.matches);
    sync(); media.addEventListener('change', sync);
    return () => { cancelAnimationFrame(request); media.removeEventListener('change', sync); };
  }, []);
}
