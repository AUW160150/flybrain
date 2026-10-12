# Measured reference optics and MaleCNS registration

This milestone adds an interactive optical-input arena using published microCT eye directions. It makes the optical sampling concrete while auditing the evidence required to attach those samples to the local MaleCNS neurons. No neural dynamics or physiological validation is claimed.

## Imported geometry

The source is the author repository accompanying [Eye structure shapes neuron function in Drosophila motion vision](https://pmc.ncbi.nlm.nih.gov/articles/PMC12488493/), pinned to [commit 99d2a43123db636cedb55af9ff31a59657e7d17e](https://github.com/reiserlab/eyemap_T4/tree/99d2a43123db636cedb55af9ff31a59657e7d17e). The paper relates female microCT eye measurements to the FAFB reconstruction. It does not provide a MaleCNS body-ID crosswalk in the files inspected here.

The imported 20240701 specimen contains 857 left-eye and 852 right-eye directions. These are the published smoothed unit vectors `ucl_rot_sm`, indexed by cone. The published `i_match` permutation associates each cone with its lens. We retain these indices, define ray IDs in a separate reference namespace, and never reinterpret them as connectome body IDs.

The author code defines the head frame as forward +x, left +y, up +z. The prototype preserves that basis and uses azimuth atan2(left, forward) and elevation asin(up). It uses both measured eyes; it does not generate the left eye by mirroring the right eye. Original lens positions are retained in the reference files but the prototype uses a shared camera origin because physical origin registration to the authored world has not been established.

## Numerical and source checks

The importer checks every downloaded file against its pinned Git blob hash and size and records SHA256 receipts. It then checks the full cone/lens permutation, agreement of their eye assignments, unit-vector norms, the published head basis, and the correspondence between full-eye rays and the paper's separate 778-column FAFB eyemap.

The current run reproduces the published neighboring-ray angles to a maximum difference of 3.57e-15 radians. Unit-vector norm error is at most 2.23e-16; the selected 778 reference directions match exactly. Median neighbor spacing is approximately 4.71 degrees for the left eye and 4.78 degrees for the right eye. These numbers describe this reference specimen and the authors' smoothing, not MaleCNS physiology.

R data conversion reports unhandled class constructors for prcomp and solve_LSAP and returns their underlying values. These warnings are preserved in the manifest. Geometry import uses the explicitly checked numeric arrays and does not run the source R analysis.

## Registration outcome

The local MaleCNS atlas contains 4,107 photoreceptor-labelled Traced bodies and source-coordinate coverage over 879 left-side and 892 right-side column locations. Those counts and coordinate namespaces differ from the microCT/FAFB reference. Matching numeric IDs, row order, or hex-coordinate numbers cannot establish correspondence.

The new malecns_photoreceptor_bindings.parquet retains each real body ID and its existing structural candidate support, but every physical ray binding remains null and input_eligible remains false. The current registered neuron count is zero. This is an unresolved evidence link, not missing raw connectivity.

The next mapping step needs anatomical landmarks such as the equator and central meridian in MaleCNS, or another dataset-compatible eye-to-column map. A cross-specimen transform must disclose scaling and orientation assumptions, reject unregistered regions, preserve uncertainty, and be checked against independent observations. The earlier structural holdout score does not validate such a transform.

## Optical simulation scope

The current viewer ray-traces an authored RGB garden from one pose. The main view fills the window with a forward perspective of the combined measured eye samples. Each pixel displays the nearest measured directional sample from either eye; it is neither a generic pixelation effect nor a model of binocular fusion. The 110-degree horizontal field is a display choice, not the fly's complete field of vision. A conventional pinhole camera at the same pose is available via Tab or 1 / 2. The full eye panoramas and provenance are in the optional I / About panel.

WASD translates the observer, mouse or arrow keys change head orientation, and Space / Shift change altitude. This is manual observer flight in arbitrary scene units, with simple clearance around the two fruits but no body physics or neural motor model. Movement changes the scene samples; headless execution supplies a fixed movement trajectory for repeatable software checks. The authored objects, scale, RGB intensities, surface shading, haze and drift of a seed are not inferred from anatomy or calibrated physics.

Three fly-shaped actors now provide moving social exploration targets. Each has an authored trajectory, stylized wing animation and an algebraic proximity response to the observer, all deterministic from time and pose. These are scene animations, not circuit models or calibrated fly behavior. Both the reference camera and the measured rays observe identical actor geometry. Scene and actor version strings and the actor code hash are retained in every recording.

The optional exploration HUD guides a player toward another fly and three landmarks. Directions and discovery thresholds use world coordinates only as interface aids; this privileged information is absent from raw samples and never becomes neural input. Discovery events are saved separately in `exploration.json` with an explicit nonbiological scope. G hides the aid. R returns the observer to the start while retaining discoveries.

Both the main projection and the eye panoramas mask locations more than 6 degrees from a sampled direction. That display cutoff is not a physiological acceptance angle. The RGB channels are illustrative display intensities, not calibrated spectral radiance or fly receptor activations; RGB does not supply a UV channel. Optical blur, spectral sensitivities, phototransduction, retinal muscle movements, adaptation, neural propagation and calibrated biomechanics remain absent. Temporal change in the displayed scene is not a simulated T4/T5 response.

Every session records the geometry manifest hash, code hashes, scene assumptions, trajectory, raw frame-by-ray-by-RGB samples and first/last screenshots. Schema version 2 records little-endian float32 RGB samples in reference CSV row order. Trajectory coordinates retain round-trip float precision; switching displays does not change the underlying samples. Earlier grayscale runs remain immutable and use their original schema and code version.

The 90-frame social garden acceptance run uses SDL's offscreen driver and replays frames 0, 45 and 89 with zero sample error. The 24-test suite includes actor visibility in optical samples, actor response reproducibility, directional guidance, discovery progression, fruit clearance, and synthetic event-loop checks for mouse direction, held movement keys, altitude, pause, view switching, help, window resizing, reset and focus-loss release. This tests software handling, not actual macOS mouse capture or biological validity. The sandbox exposes no desktop display. Display initialization failure is recorded as FAILED with an actionable terminal message.

## Artifacts

- [Reference geometry validation](../runs/eye-reference/geometry_validation.json)
- [MaleCNS registration audit](../runs/eye-reference/registration_audit.json)
- [Recorded garden preview](../runs/social-garden-preview-v1/first_frame.png)
- [Reference camera comparison](../runs/social-garden-camera-v1/first_frame.png)
- [Optical recording manifest](../runs/social-garden-preview-v1/manifest.json)
- [Software and reference consistency acceptance](../reports/social_garden_acceptance_v1.json)
- Source files and original GPL-3.0 license: references/eyemap_T4; source lock: config/eye_reference.json.
