# Prompt 04A anatomy audit

Start with [Checkpoint 04A](../CHECKPOINT_04A_ANATOMY_AUDIT.md). This directory records that historical local evidence audit. Subsequent user-authorized recovery and runtime integration are documented separately in [Checkpoint 04B](../CHECKPOINT_04B_ASSET_RECOVERY.md) and [the circuit atlas](../CHECKPOINT_04C_CIRCUIT_ATLAS.md). Current requested-body coverage is 5/110; the preserved 04A ledgers record their original 0/110 result. See the new [coverage snapshot](../validation/circuit-atlas/body-coverage.csv) and [source receipts](../validation/circuit-atlas/asset-receipts.json).

- [Current application anatomy state](CURRENT_ANATOMY_STATE.csv)
- [Local asset inventory](LOCAL_ASSET_INVENTORY.csv)
- [Body-to-geometry coverage](BODY_GEOMETRY_COVERAGE.csv)
- [Coordinate-frame ledger](COORDINATE_FRAME_LEDGER.csv)
- [Source manifest and checksums](ANATOMY_SOURCE_MANIFEST.json)
- [Claims](ANATOMY_CLAIM_LEDGER.csv), [mismatches and corrections](ANATOMY_MISMATCH_LEDGER.csv), [decisions](ANATOMY_DECISION_LOG.md), [unresolved evidence](ANATOMY_UNRESOLVED.md)
- [Bounded retrieval attempt](ANATOMY_RETRIEVAL_LOG.jsonl)
- [Proposed next prompt](PROMPT_04B_AUTHORITATIVE_ASSET_RECOVERY.md)

The inventory's candidate identity fields are discovery hints, not verified mappings. YES for coordinates can mean graph-layout or matrix-bin coordinates; consult the notes and body-coverage ledger. UNKNOWN means unestablished, not absent. A CSV/Feather of body IDs/weights is not neuron geometry. Archive member paths use `container::member`; large uninspected members have no independent checksum and their container digest is retained.

The audit uses standard Python plus the existing workspace Python's PyArrow for authoritative annotation and columnar-schema inspection, and NumPy for NPY headers. It does not load the full graph into memory or the browser. With the current workspace environment:

```sh
cd /Users/Rodela1/Code/Flybrain/sandbox/flyworld
PYTHONDONTWRITEBYTECODE=1 ../../.venv/bin/python scripts/anatomy/discover.py
PYTHONDONTWRITEBYTECODE=1 ../../.venv/bin/python scripts/anatomy/audit.py
npm run test:anatomy
npm test
npm run build
```

Discovery refuses to replace the source baseline if its file set or checksums change. Review and record changes under a new audit before creating a new baseline. Audit generation never fetches from the network; the retrieval log records the actual separate curl attempt. Claims are append-only: a changed assertion needs a new ID and a superseding correction.

Original/cache references are under `data/anatomy/raw_refs`, numeric conversions under `data/anatomy/converted`, and machine-readable provenance under `data/anatomy/manifests`. These are audit assets, not public browser assets. The conversion manifests record both converter and SWC parser hashes, exact source/output digests, frame, scale, identity matrix and absence of simplification.
