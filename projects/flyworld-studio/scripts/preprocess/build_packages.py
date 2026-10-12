#!/usr/bin/env python3
"""Build bounded FlyWorld packages from pinned local research files, read-only."""
import argparse
import csv
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from anatomy import cached_geometry, encode, geometry_record, sha256

PROJECT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = PROJECT.parents[1] / "Sugar/malecns_sugar_circuit_v1"
DEFAULT_GEOMETRY = PROJECT.parents[1] / "visualization/cache/morphology"
EXPECTED = {"dataset": "male-cns:v1.0", "version": "v1.0", "uuid": "4b2087c0fbe046bfaf0d60bc970e3e5d"}
KINDS = ("focused", "paper", "candidates", "lb3b", "lb3c", "motors", "sugar-selected", "custom", "anatomy")
LABELS = {"paper": "PAPER_ASSOCIATED", "candidates": "CANDIDATE", "sugar-selected": "UNRESOLVED", "anatomy": "ANATOMY_ONLY"}
NAMES = {
    "focused": "Focused verified bodies", "paper": "Paper-associated structural motif",
    "candidates": "Independent candidate comparison", "lb3b": "LB3b population",
    "lb3c": "LB3c population", "motors": "Requested motor neurons",
    "sugar-selected": "Sugar-selected circuit — unavailable", "custom": "Custom structural subset",
    "anatomy": "Locally cached anatomy subset",
}
ID = re.compile(r"^[1-9][0-9]*$")
MAX_SAFE_INTEGER = 9007199254740991


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    return json.loads(Path(path).read_text())


def rows(path):
    with Path(path).open(newline="") as handle:
        yield from csv.DictReader(handle)


def guard_dataset(dataset, uuid, version="v1.0"):
    require((dataset, version, uuid) == (EXPECTED["dataset"], EXPECTED["version"], EXPECTED["uuid"]),
            "Dataset guard: expected male-cns:v1.0 and UUID " + EXPECTED["uuid"])


def guarded_path(root, relative):
    path = (root / relative).resolve()
    require(path.is_relative_to(root.resolve()), "Source path escapes source root")
    return path


def verify_lock(root, lock, source_run=None):
    guard_dataset(lock["dataset"], lock["uuid"], lock["version"])
    require(source_run in (None, lock["structuralRun"], Path(lock["structuralRun"]).name),
            "Source run is not pinned in config/malecns_source_lock.json; do not mix runs")
    for item in lock["files"]:
        path = guarded_path(root, item["path"])
        require(path.is_file() and path.stat().st_size == item["bytes"] and sha256(path) == item["sha256"],
                "Source hash/size mismatch: " + item["path"])
    sm = read_json(root / lock["structuralRun"] / "manifest.json")
    vm = read_json(root / lock["visualizationRun"] / "build_manifest.json")
    wm = read_json(root / lock["workflowRun"] / "manifest.json")
    source_manifest = read_json(root / "config/source_manifest.yaml")  # Saved file is JSON-compatible YAML.
    guard_dataset(source_manifest["target_dataset"], source_manifest["dataset_uuid"])
    guard_dataset(sm["dataset"], sm["dataset_uuid"], sm["dataset_version"])
    for manifest in [vm, wm]:
        guard_dataset(manifest["dataset"], manifest["dataset_uuid"])
    require(vm["source_run"] == lock["structuralRun"], "Visualization and structural runs are incompatible")
    expected_hashes = {f["path"]: f["sha256"] for f in sm["output_files"] + sm["input_files"]}
    expected_hashes.update(vm["input_sha256"])
    expected_hashes.update(vm["output_sha256"])
    for item in lock["files"]:
        if item["path"] in expected_hashes:
            require(item["sha256"] == expected_hashes[item["path"]], "Frozen manifest hash conflict: " + item["path"])
    for name in ["meta_start.json", "meta_end.json"]:
        meta = read_json(root / lock["structuralRun"] / "raw" / name)
        record = dict(zip(meta["columns"], meta["data"][0]))
        guard_dataset(record["dataset"] + ":" + record["tag"], record["uuid"], record["tag"])
    require(sm["validation"]["status"] == "PASS", "Structural validation has not passed")
    validation = read_json(root / lock["visualizationRun"] / "validation.json")
    require(validation["status"] == "PASS", "Focused visualization validation has not passed")
    require(vm["selected_results"] is None and not wm["biological_selection_run"],
            "Source selection status changed; implement and review a validated selected-result adapter first")
    return sm, vm, wm


def nullable(value):
    return value if value != "" else None


def numeric(value):
    if value == "":
        return None
    result = float(value)
    require(0 <= result <= 1, "Invalid transmitter confidence")
    return result


def weight(value):
    require(re.fullmatch(r"[0-9]+", value or "") is not None, "Raw synapse count must be an integer")
    result = int(value)
    require(0 < result <= MAX_SAFE_INTEGER, "Raw synapse count must be a positive safe integer")
    return result


def node_record(row, display, source_run, visual_run, geometry):
    body_id = row["body_id"]
    require(ID.fullmatch(body_id), "Body IDs must be positive decimal strings")
    guard_dataset(row["dataset"], row["dataset_uuid"])
    aliases = [part.strip() for part in row["synonyms"].split(";") if part.strip()]
    require(not re.search(r"\bpuddle\b", " ".join([row["type"], *aliases]), re.I),
            "Puddle identity remains unresolved; no inferred mapping is allowed")
    evidence = ["RAW_STRUCTURAL"]
    if display and "P" in display["evidence"]:
        evidence.append("LITERATURE_ASSOCIATED")
    if geometry:
        evidence.append("SOURCE_BACKED_ANATOMY")
    unknown = [field for field in ["type", "side", "root_side", "soma_side", "cell_class", "superclass", "entry_nerve",
                                    "predicted_neurotransmitter", "predicted_nt_confidence", "consensus_nt"] if not row[field]]
    return {
        "bodyId": body_id, "type": nullable(row["type"]), "aliases": aliases,
        "displayAlias": nullable(display["display_alias"]) if display else None,
        "side": nullable(row["side"]), "sideSource": nullable(row["side_source"]),
        "rootSide": nullable(row["root_side"]), "somaSide": nullable(row["soma_side"]),
        "cellClass": nullable(row["cell_class"]), "superclass": nullable(row["superclass"]),
        "classification": nullable(row["classification"]), "entryNerve": nullable(row["entry_nerve"]),
        "exitNerve": nullable(row["exit_nerve"]), "annotationPresent": row["annotation_present"] == "True",
        "neurotransmitterPrediction": nullable(row["predicted_neurotransmitter"]),
        "predictionConfidence": numeric(row["predicted_nt_confidence"]),
        "transmitterConsensus": nullable(row["consensus_nt"]),
        "cellTypePrediction": nullable(row["celltype_predicted_nt"]),
        "cellTypePredictionConfidence": numeric(row["celltype_predicted_nt_confidence"]),
        "evidence": evidence, "sourceRefs": [source_run + "/nodes.csv"] + ([visual_run + "/model.json"] if display else []),
        "evidenceSources": display["evidence_sources"] if display else {"R": source_run + "/nodes.csv"},
        "paperStatus": display["paper_status"] if display else "NOT ASSESSED",
        "annotationProvenance": row["annotation_provenance"], "ntProvenance": row["nt_provenance"],
        "rawSourceMemberships": [x for x in row["circuit_membership"].split("|") if x],
        "packageMemberships": [], "warningIds": [], "unresolvedFields": unknown,
        "anatomy": geometry or {"status": "UNAVAILABLE"},
    }


def edge_record(row, source_run):
    guard_dataset(row["dataset"], row["dataset_uuid"])
    require(ID.fullmatch(row["source"]) and ID.fullmatch(row["target"]), "Invalid edge body ID")
    require(row["verification_status"] == "VERIFIED", "Unverified raw edge")
    return {
        "source": row["source"], "target": row["target"], "rawSynapseCount": weight(row["weight"]),
        "neuprintWeightHP": int(row["neuprint_weightHP"]) if row["neuprint_weightHP"] else None,
        "neuprintWeightHR": int(row["neuprint_weightHR"]) if row["neuprint_weightHR"] else None,
        "sideRelationship": row["side_relationship"], "evidence": ["RAW_STRUCTURAL"],
        "sourceRefs": [source_run + "/raw_edges.csv"], "queryProvenance": [
            source_run + "/" + p.strip() if p.strip().startswith("raw/") else p.strip()
            for p in row["query_provenance"].split(";") if p.strip()],
        "flatProvenance": row["flat_provenance"], "verificationStatus": "VERIFIED",
    }


def selected_nodes(kind, model, all_rows, body_ids, types, cached_ids):
    if kind == "focused":
        return {n["body_id"] for n in model["nodes"]}
    if kind == "paper":
        return {n["body_id"] for n in model["nodes"] if n["paper_counterpart"]}
    if kind == "candidates":
        return {n["body_id"] for n in model["nodes"] if n["candidate"]}
    if kind in ("lb3b", "lb3c", "motors"):
        wanted = {"lb3b": {"LB3b"}, "lb3c": {"LB3c"}, "motors": {"MN4a", "MN6", "MN8", "MN9"}}[kind]
        return {n["body_id"] for n in all_rows.values() if n["type"] in wanted}
    if kind == "sugar-selected":
        return set()
    if kind == "anatomy":
        for body_id in body_ids:
            require(body_id in all_rows, "Unknown anatomy body ID in frozen source: " + body_id)
        return set(body_ids or cached_ids) & set(all_rows)
    require(bool(body_ids or types), "Custom subsets require --selected-body-ids or --selected-types")
    for body_id in body_ids:
        require(body_id in all_rows, "Unknown body ID in frozen source: " + body_id)
    for name in types:
        require(any(row["type"] == name for row in all_rows.values()), "Unknown type in frozen source: " + name)
    return set(body_ids) | {body for body, row in all_rows.items() if row["type"] in types}


def warnings_for(root, selected):
    warnings = []
    global_ids = {"M298", "M1288", "M1289"} | {"M" + str(i) for i in range(290, 298)} | {"M" + str(i) for i in range(1275, 1283)}
    for row in rows(root / "logs/mismatch_ledger.csv"):
        bodies = re.findall(r"\bbody\s+(\d+)\b", row["item"], flags=re.I)
        if not (set(bodies) & selected or row["mismatch_id"] in global_ids):
            continue
        warnings.append({
            "id": row["mismatch_id"], "status": "RESOLVED" if row["resolved"] == "yes" else "UNRESOLVED",
            "message": row["item"], "bodyIds": [body for body in bodies if body in selected],
            "sourceA": row["source_A"], "valueA": row["value_A"], "sourceB": row["source_B"], "valueB": row["value_B"],
            "resolution": row["resolution"], "sourceRef": "logs/mismatch_ledger.csv",
        })
    return warnings


def validate_package(package, limits):
    guard_dataset(package["dataset"]["name"], package["dataset"]["uuid"], package["dataset"]["version"])
    require(package["scientificLabel"] != "SELECTED_EFFECTIVE_CONNECTIVITY", "No validated selected-result adapter is available")
    nodes, edges = package["neurons"], package["edges"]
    require(len(nodes) <= limits["maxNodes"], "Body count exceeds browser limit; narrow the subset")
    require(len(edges) <= limits["maxEdges"], "Edge count exceeds browser limit; narrow the subset")
    ids = {n["bodyId"] for n in nodes}
    require(len(ids) == len(nodes), "Duplicate body ID")
    pairs = set()
    for edge in edges:
        pair = edge["source"], edge["target"]
        require(pair[0] in ids and pair[1] in ids, "Edge references missing body")
        require(pair not in pairs, "Duplicate directed edge")
        pairs.add(pair)
        require(type(edge["rawSynapseCount"]) is int and 0 < edge["rawSynapseCount"] <= MAX_SAFE_INTEGER, "Invalid raw edge count")
    require(len(package["paths"]) <= limits["maxPaths"], "Path count exceeds limit")
    require(sum(n["anatomy"]["status"] == "SOURCE_BACKED_SWC" for n in nodes) <= limits["maxGeometryObjects"], "Geometry object count exceeds limit")
    if package["packageType"] == "sugar-selected":
        require(not nodes and not edges and not package["paths"] and package["scientificLabel"] == "UNRESOLVED", "Sugar-selected placeholder must remain empty")
    data = encode(package)
    require(len(data) <= limits["maxPackageBytes"], "Package exceeds configured byte limit; no silent truncation")
    return data


def build(root, lock, kinds, body_ids, types, one_hop, limits, geometry_dir, generated_at):
    sm, vm, wm = verify_lock(root, lock)
    source_run, visual_run = lock["structuralRun"], lock["visualizationRun"]
    model = read_json(root / visual_run / "model.json")
    guard_dataset(model["dataset"], model["dataset_uuid"])
    selected_status = model["selected_results"]
    require(model["source_run"] == source_run and selected_status["status"] == "BLOCKED — VALIDATED RESULTS REQUIRED"
            and not selected_status["conditions"] and not selected_status["selected_intermediates"]
            and not selected_status["effective_edges"] and selected_status["algorithm"] is None, "Incompatible focused model")
    display = {n["body_id"]: n for n in model["nodes"]}
    require(len(display) == len(model["nodes"]), "Duplicate focused body ID")
    all_rows = {}
    for row in rows(root / source_run / "nodes.csv"):
        body_id = row["body_id"]
        require(ID.fullmatch(body_id) and body_id not in all_rows, "Invalid or duplicate source body ID")
        guard_dataset(row["dataset"], row["dataset_uuid"])
        # Only retain fields used by the adapter, not the large raw annotation JSON.
        all_rows[body_id] = {k: v for k, v in row.items() if k != "annotation"}
    for body, node in display.items():
        require(body in all_rows, "Focused body missing from the structural source")
        for model_field, raw_field in [("type", "type"), ("side", "side"), ("root_side", "root_side"),
                                       ("soma_side", "soma_side"), ("predicted_neurotransmitter", "predicted_neurotransmitter"),
                                       ("consensus_neurotransmitter", "consensus_nt")]:
            require(node[model_field] == all_rows[body][raw_field], "Focused-model/source metadata mismatch: " + body + " / " + model_field)
    cached_ids = {p.stem for p in Path(geometry_dir).glob("*.swc")} if geometry_dir else set()
    selections = {kind: selected_nodes(kind, model, all_rows, body_ids, types, cached_ids) for kind in kinds}
    for kind, selection in selections.items():
        require(selection <= set(all_rows), "Focused body missing from source run")
        require(len(selection) <= limits["maxNodes"], kind + ": body count exceeds limit")
    if one_hop:
        require(kinds == ["custom"], "--one-hop-neighborhood is available for one custom subset only")
        seeds = set(selections["custom"])
        for row in rows(root / source_run / "raw_edges.csv"):
            if row["source"] in seeds or row["target"] in seeds:
                selections["custom"].update([row["source"], row["target"]])
                require(len(selections["custom"]) <= limits["maxNodes"], "One-hop neighborhood exceeds body limit; narrow the seeds")
    wanted = set().union(*selections.values())
    require(wanted <= set(all_rows), "One-hop edge endpoint missing from frozen nodes")
    payloads = cached_geometry(geometry_dir, wanted, limits)
    geometry, assets = {}, {}
    for body_id, payload in payloads.items():
        record, data = geometry_record(payload, limits)
        geometry[body_id] = record
        assets[record["sha256"] + ".json"] = data
    raw_edges = {}
    for row in rows(root / source_run / "raw_edges.csv"):
        if row["source"] in wanted and row["target"] in wanted:
            edge = edge_record(row, source_run)
            pair = (edge["source"], edge["target"])
            require(pair not in raw_edges, "Duplicate source edge")
            raw_edges[pair] = edge
    focused_pairs = {(e["source"], e["target"]): e["raw_synapse_count"] for e in model["edges"]}
    for pair, count in focused_pairs.items():
        if pair[0] in wanted and pair[1] in wanted:
            require(pair in raw_edges and raw_edges[pair]["rawSynapseCount"] == count, "Focused-model/raw-edge mismatch")
    if "focused" in selections:
        expected = {pair for pair in raw_edges if set(pair) <= selections["focused"]}
        require(expected == set(focused_pairs), "Focused induced edge set differs from validated model")
    paper_paths, paper_pairs = [], set()
    if any(kind in kinds for kind in ["focused", "paper"]):
        for index, row in enumerate(rows(root / source_run / "paper_associated_paths.csv")):
            ids = [str(v) for v in json.loads(row["body_ids"])]
            weights = json.loads(row["edge_synapse_counts"])
            require(len(ids) == len(weights) + 1, "Malformed saved path")
            pairs = list(zip(ids, ids[1:]))
            for pair, count in zip(pairs, weights):
                require(pair in raw_edges and raw_edges[pair]["rawSynapseCount"] == count, "Saved path/raw-edge mismatch")
                paper_pairs.add(pair)
            paper_paths.append({"id": "paper-path-" + str(index + 1), "bodyIds": ids, "sourceRef": source_run + "/paper_associated_paths.csv",
                                "label": "PAPER_ASSOCIATED"})
    all_warnings = warnings_for(root, wanted)
    source_files = [{**f, "verification": "SHA256_MATCH"} for f in lock["files"]]
    # Keep hashes for the upstream bulk products without re-reading or copying the full graph.
    for item in sm["input_files"]:
        if item["path"].startswith("data/raw/"):
            source_files.append({**item, "verification": "RECORDED_IN_FROZEN_MANIFEST"})
    scripts = [{"path": "scripts/preprocess/" + name, "sha256": sha256(Path(__file__).parent / name)}
               for name in ["build_packages.py", "anatomy.py"]]
    packages = []
    for kind, selected in selections.items():
        if kind == "anatomy":
            require(selected and selected <= set(geometry), "Anatomy subset requires receipt-verified geometry for every body")
        nodes = [node_record(all_rows[body], display.get(body), source_run, visual_run, geometry.get(body))
                 for body in sorted(selected, key=int)]
        edges = [] if kind in ("candidates", "sugar-selected", "anatomy") else [
            {**edge, "evidence": ["RAW_STRUCTURAL"] + (["LITERATURE_ASSOCIATED"] if pair in paper_pairs else [])}
            for pair, edge in sorted(raw_edges.items(), key=lambda item: tuple(map(int, item[0])))
            if set(pair) <= selected and (kind != "paper" or pair in paper_pairs)]
        paths = [p for p in paper_paths if set(p["bodyIds"]) <= selected] if kind in ("paper", "focused") else []
        warnings = [w for w in all_warnings if not w["bodyIds"] or set(w["bodyIds"]) & selected]
        for node in nodes:
            node["warningIds"] = [w["id"] for w in warnings if node["bodyId"] in w["bodyIds"]]
            node["packageMemberships"] = ["malecns-" + other for other, members in selections.items() if node["bodyId"] in members]
        packages.append({
            "format": "FLYWORLD_CIRCUIT_PACKAGE", "schemaVersion": 3, "id": "malecns-" + kind, "name": NAMES[kind],
            "packageType": kind, "scientificLabel": LABELS.get(kind, "RAW_STRUCTURAL"),
            "dataset": {"name": EXPECTED["dataset"], "version": EXPECTED["version"], "uuid": EXPECTED["uuid"]},
            "generatedAt": generated_at, "sourceRun": source_run, "visualizationRun": visual_run,
            "workflowRun": lock["workflowRun"], "preprocessor": scripts,
            "sourceFiles": source_files, "neurons": nodes, "edges": edges, "paths": paths, "warnings": warnings,
            "unresolved": [{"name": "Puddle", "bodyId": None, "status": "UNRESOLVED", "reason": "Authoritative body/type mapping absent; Q-013 / M298"},
                           {"name": "effective selection", "bodyId": None, "status": "UNRESOLVED", "reason": "No validated selected result; workflow B01–B04 remain unresolved"}],
            "selection": {"status": "UNAVAILABLE", "validated": False}, "simulation": {"status": "UNAVAILABLE"},
            "anatomyStatus": "PARTIAL" if geometry.keys() & selected else "UNAVAILABLE",
            "limits": limits, "scope": "IN-PACKAGE ONLY",
            "inclusionRule": (
                "Independent source-tracked candidate bodies; no shared pathway asserted and no comparison edges."
                if kind == "candidates" else "Empty status only; never substitute raw paths for effective selection."
                if kind == "sugar-selected" else "Union of saved paper-associated path edges and all source-defined paper counterparts; not strict replication."
                if kind == "paper" else "Receipt-verified local native morphology; no connectivity graph claimed."
                if kind == "anatomy" else "Induced raw structural edges among the explicitly included bodies; no weight threshold."),
            "neighborhoodScope": "Frozen extracted raw_edges.csv, not the complete connectome" if one_hop else None,
            "limitations": ["Raw synapse counts are structural metrics, not activation strengths.",
                            "Body-side fields do not locate anatomical midline crossings.",
                            "Transmitter prediction and consensus are separate; no physiological sign assigned.",
                            "Paper-associated support is not strict replication or effective-connectivity selection.",
                            "Abstract layout positions are not anatomical coordinates. Source-backed SWCs retain native coordinates and uncertain orientation."],
        })
    for package in packages:
        validate_package(package, limits)
    return packages, assets


def publish(packages, assets, output, geometry_output, limits):
    # Complete all validation before any publication; atomic replacement per artifact.
    encoded = [(package, validate_package(package, limits)) for package in packages]
    output.mkdir(parents=True, exist_ok=True)
    geometry_output.mkdir(parents=True, exist_ok=True)
    manifest = {"format": "FLYWORLD_PACKAGE_CATALOG", "schemaVersion": 1,
                "dataset": packages[0]["dataset"], "generatedAt": packages[0]["generatedAt"], "packages": []}
    checksums = []
    for package, data in encoded:
        name = package["id"] + ".json"
        digest = hashlib.sha256(data).hexdigest()
        temp = output / (name + ".tmp"); temp.write_bytes(data); temp.replace(output / name)
        manifest["packages"].append({"id": package["id"], "name": package["name"], "file": name,
                                     "scientificLabel": package["scientificLabel"], "nodes": len(package["neurons"]),
                                     "edges": len(package["edges"]), "bytes": len(data), "sha256": digest})
        checksums.append(digest + "  " + name)
    for name, data in assets.items():
        temp = geometry_output / (name + ".tmp"); temp.write_bytes(data); temp.replace(geometry_output / name)
    data = encode(manifest)
    temp = output / "manifest.json.tmp"; temp.write_bytes(data); temp.replace(output / "manifest.json")
    checksums.append(hashlib.sha256(data).hexdigest() + "  manifest.json")
    (output / "SHA256SUMS").write_text("\n".join(checksums) + "\n")
    if assets:
        cached = sorted(p for p in geometry_output.glob("*.json") if re.fullmatch(r"[a-f0-9]{64}\.json", p.name))
        geometry_sums = []
        for path in cached:
            digest = sha256(path)
            require(digest == path.stem, "Existing content-addressed geometry cache is corrupt: " + path.name)
            geometry_sums.append(digest + "  " + path.name)
        (geometry_output / "SHA256SUMS").write_text("\n".join(geometry_sums) + "\n")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--source-run", default=None, help="Pinned structural run ID or relative path")
    parser.add_argument("--package-type", choices=["all", *KINDS], default="all")
    parser.add_argument("--selected-body-ids", default="", help="Comma-separated decimal IDs")
    parser.add_argument("--selected-types", default="", help="Comma-separated exact source type names")
    parser.add_argument("--one-hop-neighborhood", action="store_true")
    parser.add_argument("--max-body-count", type=int)
    parser.add_argument("--max-edge-count", type=int)
    parser.add_argument("--max-geometry-objects", type=int)
    parser.add_argument("--max-package-bytes", type=int)
    parser.add_argument("--output-directory", type=Path, default=PROJECT / "public/data/malecns")
    parser.add_argument("--geometry-directory", type=Path, default=DEFAULT_GEOMETRY)
    parser.add_argument("--geometry-output-directory", type=Path, default=PROJECT / "public/data/geometry")
    args = parser.parse_args()
    require(not args.selected_types or args.package_type == "custom", "--selected-types requires --package-type custom")
    require(not args.selected_body_ids or args.package_type in ("custom", "anatomy"), "--selected-body-ids requires a custom or anatomy package")
    lock = read_json(PROJECT / "config/malecns_source_lock.json")
    require(args.source_run in (None, lock["structuralRun"], Path(lock["structuralRun"]).name), "Unpinned source run")
    for destination in [args.output_directory, args.geometry_output_directory]:
        require(not destination.resolve().is_relative_to(args.source_root.resolve()), "Output may not modify the research repository")
        require(not args.source_root.resolve().is_relative_to(destination.resolve()), "Output may not contain the research repository")
    limits = read_json(PROJECT / "config/browser_limits.json")
    for option, key in [("max_body_count", "maxNodes"), ("max_edge_count", "maxEdges"), ("max_geometry_objects", "maxGeometryObjects"), ("max_package_bytes", "maxPackageBytes")]:
        value = getattr(args, option)
        if value is not None:
            require(0 < value <= limits[key], "CLI safety limits may only narrow the configured browser budget")
            limits[key] = value
    kinds = [kind for kind in KINDS if kind != "custom"] if args.package_type == "all" else [args.package_type]
    split = lambda value: [part.strip() for part in value.split(",") if part.strip()]
    packages, assets = build(args.source_root.resolve(), lock, kinds, split(args.selected_body_ids), split(args.selected_types),
                             args.one_hop_neighborhood, limits, args.geometry_directory, datetime.now(timezone.utc).isoformat())
    manifest = publish(packages, assets, args.output_directory, args.geometry_output_directory, limits)
    for item in manifest["packages"]:
        print(f"{item['id']}: {item['nodes']} bodies, {item['edges']} edges, {item['bytes']} bytes")
    print(f"Geometry assets: {len(assets)}. Read-only source. No network queries. No neural dynamics.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as error:
        print("Rejected:", error, file=sys.stderr)
        sys.exit(1)
