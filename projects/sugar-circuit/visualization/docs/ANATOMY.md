# Actual anatomy: source, blocker and reuse

**BLOCKED in the current build.** The filesystem execution environment cannot resolve/reach `storage.googleapis.com`; the official download returned curl transport code 6. The elevated download was rejected by automatic approval review because sandbox escalation is disabled. The web retrieval interface also could not read the SWC URL. No requested authentic SWCs were available in the project cache. The batch stopped after the first transport failure instead of making repeated requests for all bodies.

The [official MaleCNS download documentation](https://male-cns.janelia.org/download/) identifies a native, non-mirrored per-body SWC directory. Native SWC coordinates use **8-nm units**. The retrieval code pins this exact v1.0 path:

```text
https://storage.googleapis.com/flyem-male-cns/v1.0/segmentation/skeletons-malecns/skeletons-swc/{body_id}.swc
```

The optional secondary route is the [official neuPrint skeleton API](https://connectome-neuprint.github.io/neuprint-python/docs/client.html#neuprint.client.Client.fetch_skeleton), pinned to `male-cns:v1.0`:

```text
https://neuprint.janelia.org/api/skeletons/skeleton/male-cns:v1.0/{body_id}?format=swc
```

Set `NEUPRINT_APPLICATION_CREDENTIALS` in the environment only if the neuPrint fallback requires authentication. Credentials are passed through a temporary mode-0600 curl configuration and removed; they are never printed or written into scientific provenance. Public GCS retrieval does not require a token. The present blocker is transport access, not a claimed nonexistent neuron or an invalid token.

The explicit allowlist contains 110 bodies: 77 verified LB3 inputs, 15 mapped named counterparts, 10 target motors, and 8 additional requested candidate bodies. It is saved alongside the retrieval manifest. The program cannot enumerate or retrieve the tens of thousands of bodies in the structural path union. A hard 500-body safety limit requires larger future selections to be explicitly split into reviewable sets.

Every successful response is preserved byte-for-byte and SHA256-hashed. The parser checks finite coordinates, unique SWC indices, valid parents and absence of parent cycles. Disconnected roots remain disconnected. No neurite is healed, mirrored, synthesized, or substituted with soma points. Neurite parent links are geometric cable relationships, **not directed synaptic edges**, so anatomical cable segments are not given physiological arrowheads.

## Retry in a network-enabled session

From the project root, with dependencies installed:

```sh
MPLCONFIGDIR=/tmp/sugar-matplotlib python visualization/scripts/build.py --fetch-skeletons
```

This creates a new build. Alternatively retrieve against an existing model into a fresh directory:

```sh
python visualization/scripts/fetch_skeletons.py --model visualization/data/RUN_ID/model.json --output visualization/anatomy/RETRIEVAL_ID
MPLCONFIGDIR=/tmp/sugar-matplotlib python visualization/scripts/build.py --retrieval-manifest visualization/anatomy/RETRIEVAL_ID/retrieval_manifest.json
```

Replace the uppercase path placeholders with actual identifiers. Existing directories are never overwritten. Body URLs, timestamps, HTTP/transport outcomes and hashes are retained in the run query log and appended to the repository query log. An incomplete group is withheld in the viewer; the missing IDs are listed in `anatomy.json`.

## Coordinate orientation

The unit scale is documented, but this session did not establish an authoritative anterior/posterior/dorsal/ventral axis-sign mapping for the native EM space. `anatomy/orientation.json` therefore has `status: UNVERIFIED`, a null matrix, and a null orientation source. No anatomical handedness was guessed from body side or appearance.

Actual SWCs can still be rendered in explicitly labeled **native X/Y/Z** coordinates, scaled by 0.008 to micrometers. The local canvas viewer supports rotation, zoom, group/body/side controls and cable hover with body ID/type/source. It retains all segments. Native static XY/XZ/YZ projections can be generated without assigning anatomical view names.

To enable anterior, posterior, dorsal and lateral presets, supply a verified `raw_to_right_dorsal_anterior` orthonormal 3×3 matrix and a specific authoritative `orientation_source`, set `status` to `VERIFIED`, then build with `--orientation PATH`. The matrix maps native coordinates to anatomical right/dorsal/anterior coordinates. Validation rejects missing source, nonfinite/nonorthonormal matrices, wrong coordinate space or wrong unit scale. Translation for framing and camera rotation do not change the body identity or mirror individual cells. Static output includes labeled orientation axes. The renderer does not infer crossing synapses from overlap or opposite body sides.

## Groups and evidence

| Group | Label | Inclusion |
|---|---|---|
| LB3b / LB3c | RAW STRUCTURAL | Verified current body inventory |
| Paper downstream | PAPER-ASSOCIATED | Only the 15 verified named counterpart bodies |
| Selected downstream | SUGAR-RESTRICTED EFFECTIVE-CONNECTIVITY | Empty until independently validated selection exists |
| Motors | RAW STRUCTURAL | All 10 verified target motor bodies |
| Combined paper circuit | PAPER-ASSOCIATED | Verified LB3 inputs + mapped named counterparts + motors |
| Comparison candidates | CANDIDATE | Exactly the 12 bodies of the six requested comparison types |

The current status sheet and HTML explicitly report **BLOCKED**, with no actual anatomy drawn. They are not successful anatomical render outputs. The required access is a network-enabled authoritative SWC download; verified orientation evidence is additionally required for anatomically named cameras. Puddle cannot be retrieved until its body mapping is independently verified.

Dataset attribution: MaleCNS, FlyEM/HHMI Janelia, University of Cambridge, MRC Laboratory of Molecular Biology, Google Research; [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), as stated by the official download page.
