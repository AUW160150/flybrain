# UX specification — Prompt 02

A local desktop-first workspace connects the procedural fly, layered brain, inspector, and reversible educational timeline. Narrow screens stack the inspector beneath the viewport. WebGL failure preserves the semantic UI and shows an explicit unavailable state; no 3D result is claimed in that state.

## Navigation and mode badges

The toolbar exposes **USER CONTROL**, **EDUCATIONAL RULE**, and **DATA REPLAY**, plus the persistent **SIMULATION UNAVAILABLE** badge. Selecting a mode clears held movement and stops the current live gesture. Only USER CONTROL accepts physical movement or behavior shortcuts. Camera controls and layer inspection remain available in every mode.

USER CONTROL captures explicit behavior/activity events. EDUCATIONAL RULE loops a fixed walk → left turn → right turn → feed → groom → escape → courtship tour. DATA REPLAY starts paused and offers the bundled synthetic timeline or the user's session recording. Rule/replay gestures animate in place; position and heading are held. Every event preserves its original educational activation label.

## Camera and selection

| Camera | Interaction | Physical locomotion |
| --- | --- | --- |
| WORLD_FOLLOW | Follow pose/heading; choose Orbit for manual rotation | User mode only |
| WORLD_ORBIT | Drag/zoom; preserve orbit offset as the fly moves | User mode only |
| FLY_INSPECTION | Closer avatar view, orbit/zoom | Paused |
| BRAIN_INSPECTION | Hide exterior, reveal all visible brain layers, orbit/zoom | Paused |

Click a visible brain region or demo neuron to enter inspection and populate the side panel. Region/node list buttons offer keyboard alternatives. Hover shows name, generic ID, and placeholder/evidence labels. Selection scrolls the inspector to its metadata. Focus selection moves toward that entity; Whole brain resets the target. Isolate system hides other regions and their nodes/relations. Reset brain view restores all five layers, default opacity, and the whole-brain camera. Each region has a show/hide checkbox and an 8–85% opacity slider; that range prevents an invisible but still interactive region.

Escape or Back returns to the previous world camera. Switching between inspection modes preserves that return target and the head-transparency preference. Camera focus changes have an explicit revision so focusing another entity works even within the same mode.

## Input and animations

Click the viewport to focus shortcuts. W/S or up/down arrows move, A/left-arrow and D/right-arrow turn left and right respectively, and held Shift boosts translation by 1.75×. Movement and turning combine into curved paths. Space toggles takeoff/land, F feeds, G grooms, E plays an escape gesture, C plays a courtship wing display, X stops, B toggles head transparency, P toggles timeline playback, and Tab enters brain inspection only when the viewport has focus. Shift+Tab remains native navigation. Inputs, buttons, links, native dialogs, and editable fields keep their own keyboard behavior.

Motion release, focus loss, mode changes, inspection entry, and Stop clear held movement. Key repeats do not restart a cleared key. The on-screen movement pad supports pointer capture, cancellation, blur, and keyboard holds. All major behavior actions have buttons.

CONTROLS ACTIVE means viewport keyboard focus in USER CONTROL with Follow/Orbit. Otherwise CONTROLS INACTIVE explains the focus/mode/inspection requirement. The movement pad is independently operable. Leaving the viewport, hiding the document or switching to MaleCNS data releases held input. Physical aliases retain separate ownership, so releasing W does not cancel a held ArrowUp. After Stop, behavior commands or mode changes, use a fresh press. Arrow repeats prevent scrolling only during active world controls.

World telemetry distinguishes forward/backward walking, turning, combined walking/turning, flight, collision blocking and inspection pause. Performance adds physical keys, pad inputs, XYZ, yaw, measured forward/turn speeds, gesture, camera, contact, focus and activation. Its motion values sample every 100 ms after collision; WebGL metrics remain actual one-second samples. A scrollable diagnostic panel accommodates constrained layouts. Browser layout and animation feel remain unverified; see Checkpoint 03A.

Avatar states are idle, walk, left/right turn, feed, groom, takeoff, flight idle, land, escape, courtship, and stop. Animation emphasizes state correctness over biological realism. Takeoff/landing heights use game-world interpolation; the brain does not generate them.

## Timeline

Play/pause, scrubbing, 0.25×/0.5×/1×/1.5×/2× speed, Clear, and Reset are available. Scrubbing pauses playback. Scrubbing live user events switches into the session's DATA REPLAY view so historical events are not overwritten by a new recording branch. Returning to USER CONTROL resumes its saved live clock.

Pausing a live user timeline freezes the display clock and suppresses new overlays, while physical commands remain usable. Inspection pauses locomotion without automatically pausing display time. Held motion highlights have an open end until key release; release adds a short fade. Session replay closes any open spans. The inspector reports value, source, cause, event ID, start/end, evidence, behavior, placeholder status, sources, and demo relations. System relations list only connections across that system's demo boundary.

The bundled replay stops at its end; the rule tour loops its fixed event list. Clear removes the active display timeline, and clears recording data only in USER CONTROL. Reset restores the chosen scripted source at time zero (paused) or starts a fresh live user recording. History caps are visible. Timeline spans encode authored event intervals, not physiological signals.

## Accessibility and clarity

The five system colors use a subset of the Okabe–Ito palette, with persistent textual names and V/T/M/C/I symbols. Symbols use light text and a colored underline to retain contrast on the dark background. Palette/ redundant-encoding reference: [Masataka Okabe and Kei Ito, Color Universal Design](https://jfly.uni-koeln.de/color/index.html). Color is never the sole evidence or selection cue.

The reduced-motion option initializes from the system preference and can be overridden visibly. It removes periodic activity pulsing, node-size pulsing, idle bobbing, escape hops, gait/wing oscillation, and eased camera transitions. Direct movement, static gesture poses, and gentle intensity fades remain readable. Keyboard labels, native dialogs, visible focus rings, standard range/select controls, and disabled simulator actions support non-pointer access.

The performance overlay samples actual WebGL FPS, visible mesh objects, draw calls, active visible highlights, camera mode, and control mode once per second. FPS remains unavailable until rendering occurs; no target-device FPS is fabricated. Instanced neurons count as one mesh object. Manual browser, visual, and assistive-technology checks remain blocked in this sandbox; see the current checkpoint.

## Prompt 03: MaleCNS data workspace

The main navigation adds MaleCNS data; Explore restores the world and generic brain. The data workspace is independent of biological simulation. Package selection shows scientific label, exact dataset identity, counts, bytes and source assurance.

Body diagrams use selectable/focusable SVG nodes and directional raw edges. Population cards preserve individual IDs. Region context shows only the five educational placeholders and states that imported bodies have no verified assignment to them. Raw edges are paginated; morphology is enabled only for packages with local source-backed assets.

Side, type and evidence filters compose with incoming/outgoing/one-hop/full-membership isolation. A numbered selector addresses all 3,564 saved paper paths without constructing new pathways. The body dropdown and keyboard-accessible buttons provide alternatives to SVG picking. The graph's 300-arrow cap is labeled and does not remove table records.

The real inspector retains metadata, original source/evidence, missing fields, relevant mismatch warnings and IN-PACKAGE ONLY partners. A dataset panel exposes source hashes, run identity, budgets and absent effective-selection/simulation status. Custom imports show useful rejection messages without replacing the current valid package.

The FEED illustration button uses an explicitly educational, unreviewed mapping of source-labelled motors; original raw data remains unchanged. No imported data is presented as synthetic replay physiology. Native morphology remains in source space with unverified orientation and no anatomical camera labels.

These interactions compile and have unit/adapter/SSR coverage. Desktop/mobile browser, assistive technology and WebGL acceptance remain pending.
