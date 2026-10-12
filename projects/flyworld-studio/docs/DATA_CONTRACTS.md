# Data contracts

Canonical TypeScript interfaces are in `src/data/contracts.ts`. Biological/foundation schemas remain in `src/data/schema.ts`; the current educational package and timeline schemas are in `src/data/demoSchema.ts`. The active package is `public/data/demo/educational-circuits.json`. The original `foundation.json` is retained as a validation fixture.

## Records

| Record | Preserved fields |
| --- | --- |
| `BrainRegionRecord` | Display/source ID, name, optional role, evidence array, source refs, explicit geometry status |
| `NeuronRecord` | Decimal string body ID, optional type/side/role, aliases, region references, separate transmitter prediction and consensus, evidence and sources |
| `EdgeRecord` | Directed source/target body IDs, optional integer raw count, evidence and source refs |
| `CircuitPackage` | Schema version 1, package ID/name, dataset/version/optional UUID, scientific label, records, metadata |
| `ActivityFrame` | Nonnegative display timestamp, source mode, dimensionless target values, explanatory notes |
| `BehaviorEvent` | Event ID/name, start/end display timestamps, source mode, explicitly supplied circuit IDs |
| `ControlEvent` | ID, display time, `USER` control mode, user provenance, command, press/release phase, keyboard/pointer origin |

The `EvidenceStatus` union preserves the prompt's eight statuses. An evidence array permits multiple independent categories; it is not a ranking. `SourceMode` includes all six required provenance labels. `ActivityFrame` preserves the five specified activity-mode values in its type, while the current runtime schema accepts only the two implemented display modes. Reserved types are extension points, never authorization or evidence of an attached simulator.

## Runtime validation

`parseCircuitText` checks byte size before JSON parsing, then calls `parseCircuitPackage`. Records reject unknown fields. Required strings must be nonempty; optional biological fields remain absent when unknown. Body IDs are decimal strings to avoid precision loss. Counts must be finite safe nonnegative integers. Duplicate IDs, duplicate directed edges, missing endpoints, and unknown region references are rejected.

Verified geometry requires `ANATOMY_VERIFIED` plus references. Anatomy/literature evidence requires sources. Non-demo biological records require source references. These rules check provenance presence, not the authenticity or correctness of a reference. A dataset UUID is retained if supplied; the validator does not silently add the MaleCNS UUID or infer a version.

The foundation's `EDUCATIONAL_DEMO` packages contain display regions only, with zero neuron records and zero edges. This intentional narrow rule avoids creating fake body IDs for arbitrary shapes. Tests use explicitly synthetic parser-only ID fixtures that are never served to the browser.

The package dialog returns validation results only. It never changes the active demo or claims imported scientific data is verified. Real biological package rendering remains outside the current scope.

The retained `parseActivityFrame` validator rejects missing/unsupported source modes, negative/nonfinite times, and out-of-range/nonfinite intensities. Current live events enter through `acceptDisplayEvent`, which also rejects unknown display targets, duplicate IDs, future timestamps, and non-user provenance. User factories fix the source mode. Activity overlays cannot command motion.

## Source schema observations for a future adapter

The read-only source uses snake_case CSV fields. Its `nodes.csv` preserves `body_id`, `type`, `side`, `side_source`, `soma_side`, `root_side`, `predicted_neurotransmitter`, `consensus_nt`, provenance, evidence, and dataset identity. The edge table keeps `source`, `target`, raw `weight`, distinct `neuprint_weightHP` / `neuprint_weightHR`, side relationships, memberships, and query/flat-file provenance. The queried Neo4j edge schema has `columns: [source, target, edge]` and distinct weight properties.

A future adapter must preserve these distinctions and treat raw weights separately from effective-connectivity scores. Side labels cannot become morphological crossing coordinates. The source visualization selected-result contract also requires validation artifacts and exact dataset/version/algorithm references; this foundation schema does not replace that scientific gate. The source schemas and references are recorded in `docs/research-context-manifest.json`.

## Prompt 02 educational extensions (current)

The biological `CircuitPackage` remains unchanged. A separate `DemoCircuitPackage` uses `format: FLYWORLD_EDUCATIONAL_DEMO`, `schemaVersion: 1`, generic `demo-*` IDs, `DemoRegion`, `DemoNeuron`, and `ILLUSTRATIVE_RELATION` records. No body ID, transmitter, or synapse-count field exists in that schema; strict parsing rejects such additions. Every demo entity has `geometryStatus: PLACEHOLDER_GEOMETRY` and `evidence: [UNVERIFIED]`.

The active master package is `public/data/demo/educational-circuits.json`. Five independently valid category packages live in `public/data/demo/circuits/`. The Prompt 01 `foundation.json` remains a legacy validation fixture and is no longer the displayed brain. The package dialog detects the educational format and validates it with `src/data/demoSchema.ts`; it does not import biological data into the renderer.

`DisplayEvent` carries ID/name, start/end, normalized target values, original user/rule source, matching evidence, behavior command, origin, notes, and optional held key. A live held event can have `endMs: null`; serialized replay events must close it. Allowed origins are LIVE_USER, SCRIPTED_RULE, BUNDLED_DEMO, and SESSION_RECORDING. DATA_REPLAY is the transport mode; original event provenance is preserved. Simulator labels remain rejected.

`DemoTimeline` requires a synthetic label, finite bounded duration, source references, unique event IDs, known target IDs, and finite in-bounds replay ends. The bundled file is `public/data/demo/timeline.json`. Runtime budgets are at most 10 regions, 64 demo neurons, 128 illustrative relations, and 120 timeline events. The shipped scene uses only 5/13/8. These are engineering limits, not scientific selection thresholds.

The original `ActivityFrame` vocabulary and its strict two-mode MVP validator remain for future adapters. The active interactive renderer samples display events; it does not promote synthetic playback into recorded physiological data. `src/activity/timeline.ts` provides pure, deterministic envelope/behavior sampling for seek and reverse seek.

## Prompt 03 real-data packages (current)

The separate FLYWORLD_CIRCUIT_PACKAGE schema 3 now supports actual bounded imports through the MaleCNS workspace. It preserves all required source fields, nulls, warnings, exact dataset/run identity and hashes. The legacy package dialog still validates without replacing the demo; the new workspace is the guarded real-data loader.

Current limits are 500 bodies / 5,000 edges / 16 geometry objects / 4 MiB per real package, with additional path/asset limits. All geometry and raw/effective distinctions remain explicit. Full details: [CIRCUIT_PACKAGE_FORMAT](CIRCUIT_PACKAGE_FORMAT.md).
