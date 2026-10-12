# Circuit package format — schema 3

Format: **FLYWORLD_CIRCUIT_PACKAGE**, schemaVersion 3. It is separate from the legacy biological scaffold and generic demo schema. [Runtime validator](../src/realdata/schema.ts), [offline generator](../scripts/preprocess/build_packages.py).

## Records

| Fields | Meaning |
| --- | --- |
| id, name, packageType, scientificLabel | Derivative identity, inclusion category, explicit scientific scope |
| dataset | Exact name/version/UUID tuple |
| generatedAt | UTC generation time |
| sourceRun, visualizationRun, workflowRun | Frozen record, evidence and status runs |
| preprocessor | Both adapter script paths and SHA256 |
| sourceFiles | Paths, bytes, SHA256 and verification scope |
| neurons, edges, paths | Bounded bodies, raw directed edges and already-saved paper paths |
| warnings, unresolved | Source disagreements and missing identities/results |
| selection, simulation | UNAVAILABLE; selection.validated is false |
| anatomyStatus, limits, scope | Geometry coverage, safety limits and IN-PACKAGE ONLY |
| inclusionRule, neighborhoodScope, limitations | Inclusion and interpretation boundaries |

Allowed label vocabulary: RAW_STRUCTURAL, PAPER_ASSOCIATED, CANDIDATE, SELECTED_EFFECTIVE_CONNECTIVITY, ANATOMY_ONLY, UNRESOLVED. **SELECTED_EFFECTIVE_CONNECTIVITY is reserved but rejected by this adapter** because no validated selected result exists. Sugar-selected remains empty and UNRESOLVED. Independent candidate packages have no comparison edges. Anatomy-only packages cannot claim connectivity edges.

Unknown fields are rejected; simulated firing, activation strength or effective scores cannot silently enter raw records.

## Bodies

bodyId is a positive decimal **string**. Nullable fields retain type, displayAlias, side, sideSource, rootSide, somaSide, cellClass, superclass, classification, entryNerve and exitNerve. Raw aliases and annotationPresent remain explicit.

neurotransmitterPrediction, predictionConfidence, transmitterConsensus, cellTypePrediction and cellTypePredictionConfidence are separate. Confidence is the supplied value in [0,1], not confidence in the entire package. No NT field is used to infer edge sign.

sourceRefs resolve to hashed sourceFiles. evidenceSources, paperStatus, annotationProvenance and ntProvenance retain scope. rawSourceMemberships name earlier bounded structural searches; packageMemberships name these display packages. Neither is effective selection.

warningIds resolve to package warnings. unresolvedFields retain absent source columns as null rather than guessed values. LB3c 957530 keeps its missing entry nerve and M003 warning. Puddle remains unresolved with null bodyId; a guessed Puddle body alias/type is rejected.

## Edges and paths

Edges preserve string source/target, positive safe-integer rawSynapseCount, separate nullable neuprintWeightHP/neuprintWeightHR, sideRelationship, evidence, sourceRefs, queryProvenance, flatProvenance and the saved verificationStatus.

Endpoints must exist; duplicate directed pairs and invalid counts are rejected. Missing edges are not inserted as weight-zero records. Paths have IDs, ordered bodyIds, a hashed sourceRef and PAPER_ASSOCIATED label. Every consecutive body pair must have an edge. Generation also checks every saved path weight against its raw record.

## Geometry

Anatomy is either UNAVAILABLE or SOURCE_BACKED_SWC. Source-backed records contain a local content-addressed asset path, cache bytes/hash, point count, original SWC hash, official release URL, receipt hash, native coordinate space, 8 nm units and UNVERIFIED orientation.

The asset format is FLYWORLD_NATIVE_SWC, version 1. It retains headers and all seven SWC columns: point ID, type, X/Y/Z, radius and parent ID. Coordinates remain native; scaleToMicrometers 0.008 is metadata. Display centering changes only the render buffer.

Missing parents, cycles, duplicate IDs, nonfinite coordinates, negative radii, mismatched body/receipt/hash or excessive size are rejected. No repair, mirroring or inferred branches. A selected body's asset is checked for bytes, SHA256, ID, point count and provenance before rendering. Native SWC header UUID and neuPrint dataset UUID stay separate.

## Limits and transport

[Shared configuration](../config/browser_limits.json):

| Limit | Default |
| --- | ---: |
| Bodies | 500 |
| Raw edges | 5,000 |
| Geometry objects referenced per package | 16 |
| Package bytes | 4,194,304 (4 MiB) |
| Saved paths | 5,000 |
| Points per geometry asset | 100,000 |
| Geometry asset bytes | 8,388,608 (8 MiB) |
| Graph arrows displayed | 300 |

CLI limits may narrow these ceilings. Raising them requires reviewing config, validation and renderer together. Scientific records are never silently truncated; the separate arrow-display cap is disclosed.

manifest.json lists package identities, labels, counts, bytes and SHA256. SHA256SUMS covers the packages and catalog; geometry caches have their own checksums. Bundled loads verify catalog hashes and stream with a byte cap. Custom imports verify size/schema/dataset with a visible supplied-provenance caveat. Schema validity does not authenticate a scientific claim. Cross-dataset comparison mode is unavailable.
