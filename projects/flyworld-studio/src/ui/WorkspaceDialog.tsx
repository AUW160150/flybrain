import { PackageValidator } from '../data/PackageValidator';
import { ExperimentPanel } from '../experiments/ExperimentPanel';
import { PLACEHOLDER_LABEL } from '../circuits/demo';

export type DialogName = 'science' | 'data' | 'experiments' | 'help';
export default function WorkspaceDialog({ name }: { name: DialogName }) {
  if (name === 'data') return <PackageValidator />;
  if (name === 'experiments') return <ExperimentPanel />;
  if (name === 'science') return <><div className="source-label">{PLACEHOLDER_LABEL}</div>
    <p>The world avatar, brain systems, and generic demo neurons are procedural illustrations. The separate MaleCNS data workspace contains bounded packages of source-backed body records and raw structural edges. Its abstract node positions are not anatomical coordinates.</p>
    <p><strong>USER_DRIVEN_ILLUSTRATION</strong> identifies direct user mappings. <strong>RULE_DRIVEN_EDUCATIONAL</strong> identifies authored display sequences. Neither is emerging MaleCNS activity.</p>
    <p><strong>DATA REPLAY</strong> describes timeline playback. This bundled replay is synthetic; every event keeps its original educational activation label. Session playback retains user provenance. Activity values are normalized display intensities, not firing rates.</p>
    <p>Collision handling is game physics. No neural dynamics are implemented. Real-record source hashes, run IDs, missing fields, and mismatch warnings remain inspectable. Paper-associated views are not strict replication; the sugar-selected package stays empty.</p>
    <p>Requested circuit bodies have no verified local morphology. Three separate source-matched bodies have cached native SWCs; their orientation remains unverified. No neurites are fabricated. Real-body behavior highlights retain USER_DRIVEN_ILLUSTRATION and an unreviewed educational mapping disclaimer.</p></>;
  return <><p>Click the 3D viewport to focus it. Drag and zoom in Orbit or inspection modes. All major commands have visible controls.</p>
    <dl className="help-grid"><dt>W / S or ↑ / ↓</dt><dd>Hold forward / backward</dd><dt>A / ←</dt><dd>Hold left turn; combine with forward or backward</dd><dt>D / →</dt><dd>Hold right turn; combine with forward or backward</dd><dt>Shift</dt><dd>Hold for 1.75× movement speed</dd><dt>Space</dt><dd>Take off / land</dd><dt>F / G / E / C</dt><dd>Feed / groom / escape / courtship</dd><dt>X</dt><dd>Stop movement</dd><dt>B</dt><dd>Transparent head</dd><dt>Tab (viewport)</dt><dd>Inspect brain</dd><dt>Escape</dt><dd>Return to world</dd><dt>P</dt><dd>Pause / play display timeline</dd></dl>
    <p>CONTROLS ACTIVE means the viewport has keyboard focus in USER CONTROL and a world camera. Clicking another control or typing releases held movement. Click the viewport again to resume. After Stop, a behavior command, inspection, or a focus change, release and press movement keys again. The movement pad also accepts held mouse/touch or focused Space/Enter.</p>
    <p>Inspection pauses physical motion. Rule mode and replay show gestures in place. Scrubbing a user session switches to its recording; return to USER CONTROL to resume physical input. Reduced motion suppresses pulsing, bobbing, wing oscillation, gait animation, and camera easing.</p></>;
}
