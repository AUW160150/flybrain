"""Offline, receipt-checked native SWC conversion. No downloads or branch inference."""
from pathlib import Path
import hashlib
import json
import math
import re

OFFICIAL_BASE = "https://storage.googleapis.com/flyem-male-cns/v1.0/segmentation/skeletons-malecns/skeletons-swc/"


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_swc(text, max_points):
    rows, headers = [], []
    for line in text.splitlines():
        if not line.strip():
            continue
        if line.lstrip().startswith("#"):
            headers.append(line)
            continue
        parts = line.split()
        if len(parts) != 7:
            raise ValueError("SWC rows must have seven fields")
        row = [int(parts[0]), int(parts[1]), *map(float, parts[2:6]), int(parts[6])]
        if row[0] <= 0 or row[1] < 0 or not all(math.isfinite(v) for v in row) or row[5] < 0:
            raise ValueError("Invalid SWC coordinate, radius, or ID")
        rows.append(row)
        if len(rows) > max_points:
            raise ValueError("SWC exceeds geometry point limit; no branches were truncated")
    by_id = {row[0]: row for row in rows}
    if not rows or len(by_id) != len(rows):
        raise ValueError("Empty SWC or duplicate point IDs")
    for row in rows:
        if row[6] != -1 and row[6] not in by_id:
            raise ValueError("Missing SWC parent; no branch repair is permitted")
    # Detect parent cycles in linear time, independent of source ordering.
    complete = set()
    for point in by_id:
        visiting, cursor = set(), point
        while cursor != -1 and cursor not in complete:
            if cursor in visiting:
                raise ValueError("Cyclic SWC parent relation")
            visiting.add(cursor)
            cursor = by_id[cursor][6]
        complete.update(visiting)
    return rows, headers


def cached_geometry(directory, body_ids, limits):
    """Return exact native-coordinate payloads only for explicitly selected IDs."""
    result = {}
    if directory is None:
        return result
    directory = Path(directory)
    for body_id in sorted(body_ids, key=int):
        path = directory / (body_id + ".swc")
        receipt_path = path.with_suffix(".source.json")
        if not path.exists() or not receipt_path.exists():
            continue
        receipt = json.loads(receipt_path.read_text())
        digest = sha256(path)
        if receipt.get("source_url") != OFFICIAL_BASE + body_id + ".swc" or receipt.get("sha256") != digest:
            raise ValueError("Geometry receipt/release/hash mismatch for " + body_id)
        if path.stat().st_size > limits["maxGeometryBytes"]:
            raise ValueError("SWC exceeds geometry byte limit")
        rows, headers = parse_swc(path.read_text(), limits["maxGeometryPoints"])
        result[body_id] = {
            "format": "FLYWORLD_NATIVE_SWC", "schemaVersion": 1, "bodyId": body_id,
            "dataset": "male-cns:v1.0", "releaseEvidence": "OFFICIAL_RELEASE_URL_AND_SHA256_RECEIPT",
            "sourceUrl": receipt["source_url"], "sourceSha256": digest,
            "receiptSha256": sha256(receipt_path), "retrievedAt": receipt["retrieved_utc"],
            "coordinateSpace": "MaleCNS native EM", "units": "8 nm",
            "scaleToMicrometers": 0.008, "orientationStatus": "UNVERIFIED",
            "transformApplied": False, "sourceHeaders": headers, "points": rows,
        }
    return result


def encode(value):
    return (json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False) + "\n").encode()


def geometry_record(payload, limits):
    data = encode(payload)
    if len(data) > limits["maxGeometryBytes"]:
        raise ValueError("Converted geometry exceeds byte limit")
    digest = hashlib.sha256(data).hexdigest()
    return {
        "status": "SOURCE_BACKED_SWC", "asset": "/data/geometry/" + digest + ".json",
        "sha256": digest, "bytes": len(data), "pointCount": len(payload["points"]),
        "sourceSha256": payload["sourceSha256"], "sourceUrl": payload["sourceUrl"],
        "receiptSha256": payload["receiptSha256"], "units": "8 nm",
        "coordinateSpace": "MaleCNS native EM", "orientationStatus": "UNVERIFIED",
    }, data
