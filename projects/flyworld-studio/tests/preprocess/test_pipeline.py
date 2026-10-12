import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

PROJECT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT / "scripts/preprocess"))
from build_packages import guard_dataset, verify_lock, validate_package, selected_nodes, weight, EXPECTED
from anatomy import parse_swc, cached_geometry, geometry_record, OFFICIAL_BASE

LIMITS = json.loads((PROJECT / "config/browser_limits.json").read_text())
LOCK = json.loads((PROJECT / "config/malecns_source_lock.json").read_text())


def package(kind="focused"):
    return json.loads((PROJECT / ("public/data/malecns/malecns-" + kind + ".json")).read_text())


class PipelineTests(unittest.TestCase):
    def test_exact_target(self):
        guard_dataset(EXPECTED["dataset"], EXPECTED["uuid"], EXPECTED["version"])

    def test_wrong_release_uuid_version_rejected(self):
        for dataset, uuid, version in [
            ("male-cns:v0.9", EXPECTED["uuid"], "v0.9"),
            ("FlyWire", EXPECTED["uuid"], "v1.0"),
            (EXPECTED["dataset"], "0" * 32, "v1.0"),
            (EXPECTED["dataset"], EXPECTED["uuid"], "v0.9"),
        ]:
            with self.subTest(dataset=dataset, uuid=uuid, version=version), self.assertRaisesRegex(ValueError, "Dataset guard"):
                guard_dataset(dataset, uuid, version)

    def test_tampered_source_hash_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); path = root / "input.csv"; path.write_text("body_id\n123\n")
            lock = {**LOCK, "files": [{"path": "input.csv", "bytes": path.stat().st_size, "sha256": "0" * 64}]}
            with self.assertRaisesRegex(ValueError, "hash/size"):
                verify_lock(root, lock)

    def test_unpinned_source_run_rejected(self):
        with self.assertRaisesRegex(ValueError, "not pinned"):
            verify_lock(Path("."), LOCK, "another-run")

    def test_source_path_escape_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            lock = {**LOCK, "files": [{"path": "../outside.csv", "bytes": 1, "sha256": "0" * 64}]}
            with self.assertRaisesRegex(ValueError, "escapes"):
                verify_lock(Path(folder), lock)

    def test_generated_catalog_counts_sizes_checksums(self):
        manifest = json.loads((PROJECT / "public/data/malecns/manifest.json").read_text())
        expected = {"focused": (110, 1923), "paper": (102, 274), "candidates": (12, 0), "lb3b": (11, 43),
                    "lb3c": (23, 221), "motors": (10, 29), "sugar-selected": (0, 0), "anatomy": (3, 0)}
        for entry in manifest["packages"]:
            with self.subTest(package=entry["id"]):
                path = PROJECT / "public/data/malecns" / entry["file"]; data = path.read_bytes()
                parsed = json.loads(data)
                self.assertEqual(hashlib.sha256(data).hexdigest(), entry["sha256"])
                self.assertEqual(len(data), entry["bytes"])
                self.assertEqual((len(parsed["neurons"]), len(parsed["edges"])), expected[parsed["packageType"]])
                validate_package(parsed, LIMITS)

    def test_hash_provenance_preserved(self):
        pkg = package()
        actual = {item["path"]: item["sha256"] for item in pkg["sourceFiles"]}
        for record in LOCK["files"]:
            self.assertEqual(actual[record["path"]], record["sha256"])
        for script in pkg["preprocessor"]:
            self.assertEqual(hashlib.sha256((PROJECT / script["path"]).read_bytes()).hexdigest(), script["sha256"])

    def test_side_class_and_unresolved_fields_not_backfilled(self):
        node = next(n for n in package()["neurons"] if n["bodyId"] == "957530")
        self.assertIsNone(node["entryNerve"])
        self.assertIn("entry_nerve", node["unresolvedFields"])
        self.assertIn("M003", node["warningIds"])
        self.assertEqual(node["sideSource"], "rootSide")

    def test_no_guessed_puddle_or_selected_result(self):
        pkg = package()
        self.assertFalse(any("puddle" in str(n).lower() for n in pkg["neurons"]))
        unresolved = next(u for u in pkg["unresolved"] if u["name"] == "Puddle")
        self.assertIsNone(unresolved["bodyId"])
        sugar = package("sugar-selected")
        self.assertEqual((sugar["neurons"], sugar["edges"], sugar["paths"]), ([], [], []))
        sugar["neurons"] = [pkg["neurons"][0]]
        with self.assertRaisesRegex(ValueError, "remain empty"):
            validate_package(sugar, LIMITS)

    def test_selected_label_rejected(self):
        pkg = package(); pkg["scientificLabel"] = "SELECTED_EFFECTIVE_CONNECTIVITY"
        with self.assertRaisesRegex(ValueError, "selected-result"):
            validate_package(pkg, LIMITS)

    def test_edge_missing_body_duplicate_invalid_weight_rejected(self):
        for field in ["missing", "duplicate", "weight"]:
            pkg = package()
            if field == "missing": pkg["edges"][0]["target"] = "999999999"
            if field == "duplicate": pkg["edges"].append(pkg["edges"][0])
            if field == "weight": pkg["edges"][0]["rawSynapseCount"] = 0.5
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate_package(pkg, LIMITS)

    def test_resource_limits_reject_without_truncation(self):
        pkg = package()
        for key in ["maxNodes", "maxEdges", "maxPackageBytes", "maxPaths"]:
            low = {**LIMITS, key: 1}
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate_package(pkg, low)
        self.assertEqual((len(pkg["neurons"]), len(pkg["edges"])), (110, 1923))
        with self.assertRaisesRegex(ValueError, "Geometry object"):
            validate_package(package("anatomy"), {**LIMITS, "maxGeometryObjects": 1})

    def test_raw_weight_precision_and_missing_values(self):
        for invalid in ["1.5", "-1", "nan", "", "0", str(2**53)]:
            with self.subTest(value=invalid), self.assertRaises(ValueError):
                weight(invalid)
        self.assertEqual(weight("2591"), 2591)

    def test_custom_selector_rejects_unknown_body_and_type(self):
        nodes = {"15321": {"type": "GNG042"}}
        for ids, types in [(["999"], []), ([], ["Puddle"]), ([], [])]:
            with self.subTest(ids=ids, types=types), self.assertRaises(ValueError):
                selected_nodes("custom", {}, nodes, ids, types, set())

    def test_custom_generation_uses_real_frozen_source_without_source_mutation(self):
        source = PROJECT.parents[1] / "Sugar/malecns_sugar_circuit_v1"
        source_manifest = source / LOCK["structuralRun"] / "manifest.json"
        before = source_manifest.read_bytes()
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "packages"
            command = [sys.executable, str(PROJECT / "scripts/preprocess/build_packages.py"), "--package-type", "custom",
                       "--selected-body-ids", "15321,15734", "--source-run", "20261006T180116Z",
                       "--output-directory", str(output), "--geometry-output-directory", str(Path(folder) / "geometry")]
            result = subprocess.run(command, cwd=PROJECT, capture_output=True, text=True, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
            self.assertEqual(result.returncode, 0, result.stderr)
            custom = json.loads((output / "malecns-custom.json").read_text())
            self.assertEqual({n["bodyId"] for n in custom["neurons"]}, {"15321", "15734"})
            baseline = [e for e in package()["edges"] if e["source"] in {"15321", "15734"} and e["target"] in {"15321", "15734"}]
            self.assertEqual([(e["source"], e["target"], e["rawSynapseCount"]) for e in custom["edges"]],
                             [(e["source"], e["target"], e["rawSynapseCount"]) for e in baseline])
            self.assertEqual(custom["scientificLabel"], "RAW_STRUCTURAL")
        self.assertEqual(before, source_manifest.read_bytes())

    def test_oversized_one_hop_rejects_before_publication(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "packages"
            command = [sys.executable, str(PROJECT / "scripts/preprocess/build_packages.py"), "--package-type", "custom",
                       "--selected-body-ids", "15321", "--one-hop-neighborhood", "--max-body-count", "2",
                       "--output-directory", str(output), "--geometry-output-directory", str(Path(folder) / "geometry")]
            result = subprocess.run(command, cwd=PROJECT, capture_output=True, text=True, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("One-hop neighborhood exceeds body limit", result.stderr)
            self.assertFalse(output.exists())


class AnatomyTests(unittest.TestCase):
    SWC = "# Native example; test fixture only\n1 0 100 200 300 2 -1\n2 0 101 202 303 1 1\n"

    def test_exact_native_coordinates_and_parent_links(self):
        points, headers = parse_swc(self.SWC, 100)
        self.assertEqual(points[1], [2, 0, 101.0, 202.0, 303.0, 1.0, 1])
        self.assertEqual(len(headers), 1)

    def test_no_branch_repair_or_cycles_or_duplicates(self):
        for text in [self.SWC.replace("1 1\n", "1 999\n"), self.SWC.replace("2 0", "1 0"),
                     self.SWC.replace("2 -1", "2 2"), self.SWC.replace("101", "nan")]:
            with self.subTest(text=text), self.assertRaises(ValueError):
                parse_swc(text, 100)

    def test_geometry_caps(self):
        with self.assertRaisesRegex(ValueError, "point limit"):
            parse_swc(self.SWC, 1)

    def test_receipt_hash_release_and_body_guard(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); path = root / "123.swc"; path.write_text(self.SWC)
            receipt = {"source_url": OFFICIAL_BASE + "123.swc", "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "retrieved_utc": "2026-10-07T00:00:00Z"}
            (root / "123.source.json").write_text(json.dumps(receipt))
            payload = cached_geometry(root, {"123"}, LIMITS)["123"]
            record, data = geometry_record(payload, LIMITS)
            self.assertEqual(record["sha256"], hashlib.sha256(data).hexdigest())
            self.assertFalse(payload["transformApplied"])
            for key, value in [("source_url", OFFICIAL_BASE.replace("v1.0", "v0.9") + "123.swc"), ("source_url", OFFICIAL_BASE + "999.swc"), ("sha256", "0" * 64)]:
                changed = {**receipt, key: value}; (root / "123.source.json").write_text(json.dumps(changed))
                with self.subTest(key=key, value=value), self.assertRaisesRegex(ValueError, "mismatch"):
                    cached_geometry(root, {"123"}, LIMITS)


if __name__ == "__main__":
    unittest.main()
