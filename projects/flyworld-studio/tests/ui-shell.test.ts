import { describe, expect, it } from 'vitest';
import { createElement } from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { App } from '../src/app/App';
import { ExperimentPanel } from '../src/experiments/ExperimentPanel';
import { DebugOverlay } from '../src/ui/DebugOverlay';

describe('UI shell without a browser or WebGL', () => {
  it('renders metadata, controls, and scientific labels through the unavailable-renderer path', () => {
    const html = renderToStaticMarkup(createElement(App));
    for (const label of ['3D rendering unavailable', 'PLACEHOLDER_GEOMETRY — NOT ANATOMICAL DATA', 'COLLISION HANDLING: GAME PHYSICS', 'SIMULATION UNAVAILABLE', 'USER CONTROL', 'EDUCATIONAL RULE', 'DATA REPLAY', 'Reduced motion', 'Activity timeline position', 'CONTROLS INACTIVE', 'USER_DRIVEN_ILLUSTRATION']) expect(html).toContain(label);
    expect(html).not.toContain('FULL_CONNECTOME_SIMULATION');
    expect(html).not.toContain('REDUCED_CIRCUIT_SIMULATION');
  });
  it('keeps all six experiment controls disabled and names the missing simulator', () => {
    const html = renderToStaticMarkup(createElement(ExperimentPanel));
    expect(html.match(/disabled=""/g)).toHaveLength(6);
    expect(html).toContain('NOT CONNECTED TO A VALIDATED SIMULATOR');
  });
  it('renders all diagnostic fields without inventing renderer measurements', () => {
    const html = renderToStaticMarkup(createElement(DebugOverlay));
    for (const field of ['Pressed keys', 'Position X / Y / Z', 'Heading / yaw', 'Forward speed', 'Turn speed', 'Movement state', 'Avatar gesture', 'Collision', 'Controls', 'Focus target', 'Camera', 'Awaiting WebGL']) expect(html).toContain(field);
  });
});
