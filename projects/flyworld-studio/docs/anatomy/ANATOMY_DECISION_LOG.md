# Anatomy audit decisions — 8 October 2026

Prompt 04A is the current user-authorized scope. It permits an independent local anatomy audit and a bounded official retrieval test; it does not authorize avatar registration, a new rendered anatomy integration, or simulation. The research repository remains read-only. Earlier checkpoint and research claims remain historical evidence.

| ID | Decision | Evidence and consequence |
| --- | --- | --- |
| AD001 | Search only six project/data roots recorded in discovery.json. | 703 candidate rows, including archive members, are inventoried. Dependency folders, Git internals, credential files and symlinks are excluded. No unrelated home directories are scanned. |
| AD002 | Join the exact 110 requested bodies to the structural inventory and official v1.0 annotation table. | The 67 bodies across all 17 minimum requested types are included. LB3a/LB3d account for the other 43. All 110 lack verified local geometry. |
| AD003 | Verify incidental cached bodies against the full official annotation table. | All eight canonical SWCs have matching official per-body release URLs and SHA256 receipts. Five absent from the focused structural export are still valid annotated bodies; they are not added to the requested circuit. |
| AD004 | Recover originals into an immutable audit cache and convert separately. | Original source bytes are opened read-only. Eight raw SWCs and receipts are copied by content hash; separate JSON retains all numeric SWC fields, headers and parent links, with identity transform and no simplification. No public asset is replaced. |
| AD005 | Keep units, coordinate frame, orientation and mutation history separate. | S-DOWNLOAD establishes native SWC 8-nm units, not anatomical axis signs. Multiple segmentation UUIDs/mutation IDs are preserved. The neuPrint UUID is a distinct field. |
| AD006 | Stop bounded retrieval after the first transport failure. | Public official LB3b request 71254 returned curl 6 / HTTP 000. The other four test bodies were not requested. No token was read, printed or copied; the neuPrint environment credential was absent. |
| AD007 | Preserve native coordinates; record display centering separately. | Existing single-body rendering is valid as labeled. Reusing independently centered buffers for a joint/registered scene would lose common-origin placement: SCIENTIFIC_PLAN_REVISION_REQUIRED for that future assumption. |
| AD008 | Correct provisional probe uncertainty using byte-level evidence. | AM004 remains as history; AM005 supersedes it. 10029.probe.swc is byte-identical to receipt-backed 10029.swc, so it is a duplicate, not a ninth body. |
| AD009 | Verify existing derivatives without promoting them to raw assets. | Eight sibling visualization JSONs preserve XYZ after one 0.008 scale and all cable pairs. They omit raw SWC radius/type columns. Three browser JSONs preserve all raw numeric fields and headers. |
| AD010 | Stop after the audit and prepare an exact next prompt. | Missing requested bodies, reference context and orientation evidence require authoritative recovery. Prompt 04B is prepared in this directory, not executed. |

Claim corrections append new IDs and reference the superseded item. The generator refuses to replace an existing claim under the same ID. Data tables are reproducible current views; originals, acquisition records and audit history are retained.
