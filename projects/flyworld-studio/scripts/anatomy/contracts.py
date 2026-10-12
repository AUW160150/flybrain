"""Offline anatomy audit guards; no renderer, registration, or network access."""
import hashlib
import json
import math
import re
from pathlib import Path

DATASET = "male-cns:v1.0"
VERSION = "v1.0"
UUID = "4b2087c0fbe046bfaf0d60bc970e3e5d"
OFFICIAL_BASE = "https://storage.googleapis.com/flyem-male-cns/v1.0/segmentation/skeletons-malecns/skeletons-swc/"
IDENTITY = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for block in iter(lambda: source.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_snapshot(snapshot):
    changed = [str(path) for path, expected in snapshot.items()
               if not Path(path).is_file() or sha256(path) != expected]
    if changed:
        raise ValueError("Raw-source immutability violation: " + ", ".join(changed))


def coordinate_metadata(headers):
    """Parse source properties without interpreting downsampling as XYZ units."""
    records = []
    for header in headers:
        if header.startswith("#$"):
            records.append(json.loads(header[2:]))
    return {
        "native_properties": records,
        "segmentation_uuids": sorted({r["uuid"] for r in records if "uuid" in r}),
        "mutation_ids": [r["mutation id"] for r in records if "mutation id" in r],
        "axis_order": "X,Y,Z",
        "axis_directions": None,
        "handedness": None,
        "origin": None,
        "orientation_status": "ORIENTATION_UNVERIFIED",
    }


def transform_point(point, matrix):
    """Apply an explicit finite affine transform. This supplies no anatomical axes."""
    if len(matrix) != 4 or any(len(row) != 4 for row in matrix):
        raise ValueError("Expected a 4x4 affine matrix")
    if matrix[3] != [0, 0, 0, 1] or not all(math.isfinite(x) for row in matrix for x in row):
        raise ValueError("Expected a finite affine matrix")
    if len(point) != 3 or not all(math.isfinite(x) for x in point):
        raise ValueError("Expected a finite XYZ point")
    return [sum(matrix[i][j] * point[j] for j in range(3)) + matrix[i][3] for i in range(3)]


def validate_mappings(records, inventory):
    """Fail closed before a geometry mapping can be called verified.

    inventory is the authoritative annotation lookup keyed by decimal-string ID.
    A filename alone never establishes identity. All referenced bytes are checked.
    """
    seen = set()
    for record in records:
        body = record.get("body_id")
        if not isinstance(body, str) or not re.fullmatch(r"[1-9][0-9]*", body):
            raise ValueError("Body IDs must be positive decimal strings")
        if body in seen:
            raise ValueError("Duplicate body-to-geometry mapping: " + body)
        seen.add(body)
        if record.get("dataset") != DATASET:
            raise ValueError("WRONG_DATASET")
        if record.get("version") != VERSION:
            raise ValueError("WRONG_VERSION")
        if body not in inventory or inventory[body].get("bodyId") != body:
            raise ValueError("Geometry/body-ID referential integrity failure")
        if record.get("status") != "VERIFIED_BODY_GEOMETRY" or record.get("geometry_kind") != "NATIVE_SWC":
            raise ValueError("No placeholder geometry may be labeled verified")
        required = ["source_path", "source_sha256", "receipt_path", "receipt_sha256",
                    "annotation_path", "annotation_sha256", "mapping_evidence", "coordinate_evidence"]
        if any(not record.get(key) for key in required):
            raise ValueError("Missing provenance")
        for prefix in ["source", "receipt", "annotation"]:
            if sha256(record[prefix + "_path"]) != record[prefix + "_sha256"]:
                raise ValueError("Checksum mismatch: " + prefix)
        receipt = json.loads(Path(record["receipt_path"]).read_text())
        url = OFFICIAL_BASE + body + ".swc"
        if receipt.get("source_url") != url or record.get("source_url") != url:
            raise ValueError("Official source/body/release mismatch")
        if receipt.get("sha256") != record["source_sha256"] or not receipt.get("retrieved_utc"):
            raise ValueError("Receipt provenance/checksum mismatch")
        if record.get("units") != "8 nm" or record.get("scale_to_micrometers") != 0.008:
            raise ValueError("Native SWC units mismatch")
        # This audit has no authoritative anatomical orientation evidence.
        if record.get("orientation_status") != "ORIENTATION_UNVERIFIED" or record.get("orientation_labels"):
            raise ValueError("Unverified orientation cannot be labeled anatomical")
        if record.get("transform") != IDENTITY:
            raise ValueError("This audit permits only the native identity transform")
    return records


def write_immutable(path, data):
    """Content-addressed output can be reused byte-for-byte, never overwritten."""
    path = Path(path)
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError("Refusing to overwrite immutable artifact: " + str(path))
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as output:
        output.write(data)


def convert_swc(record, output_dir, parser):
    """Lossless numeric SWC-to-JSON cache, separate from public application assets."""
    source = Path(record["source_path"])
    before = sha256(source)
    if before != record["source_sha256"]:
        raise ValueError("Source checksum mismatch")
    points, headers = parser(source.read_text(), 1_000_000)
    payload = {"format": "FLYWORLD_AUDIT_NATIVE_SWC", "schema_version": 1,
               "body_id": record["body_id"], "dataset": DATASET, "version": VERSION,
               "source_sha256": before, "coordinate_frame": "MaleCNS native EM",
               "units": "8 nm", "orientation_status": "ORIENTATION_UNVERIFIED",
               "transform": IDENTITY, "scale": 1, "simplification": None,
               "source_headers": headers, "points": points}
    data = (json.dumps(payload, separators=(",", ":"), allow_nan=False) + "\n").encode()
    digest = hashlib.sha256(data).hexdigest()
    output = Path(output_dir) / (digest + ".json")
    write_immutable(output, data)
    if sha256(source) != before:
        raise ValueError("Raw-source immutability violation")
    return {"source_path": str(source), "source_sha256": before,
            "conversion_script": str(Path(__file__).resolve()), "conversion_script_sha256": sha256(__file__),
            "output_path": str(output.resolve()), "output_sha256": digest,
            "body_id": record["body_id"], "dataset": DATASET, "version": VERSION,
            "coordinate_frame": "MaleCNS native EM", "units": "8 nm", "scale": 1,
            "scale_to_micrometers": 0.008, "transform": IDENTITY, "simplification": None,
            "point_count": len(points), "roots": sum(p[6] == -1 for p in points),
            "bounds": [[min(p[i] for p in points), max(p[i] for p in points)] for i in [2, 3, 4]],
            "native_metadata": coordinate_metadata(headers)}
