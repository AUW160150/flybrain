"""Optional offline scientific preview; requires matplotlib, not used by the app."""
from pathlib import Path
import json
import hashlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D

root = Path(__file__).resolve().parents[1]
package_path = root / "public/data/malecns/malecns-anatomy.json"
package = json.loads(package_path.read_text())
fig, ax = plt.subplots(figsize=(11, 8), facecolor="#122019")
ax.set_facecolor("#122019")
legend, inputs = [], {}
for node, color in zip(package["neurons"], ["#56B4E9", "#E69F00", "#CC79A7"]):
    asset = root / ("public" + node["anatomy"]["asset"])
    raw = asset.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == node["anatomy"]["sha256"]
    inputs[node["bodyId"]] = node["anatomy"]["sha256"]
    data = json.loads(raw)
    positions = {point[0]: (point[2], point[4]) for point in data["points"]}
    segments = [(positions[point[6]], positions[point[0]]) for point in data["points"] if point[6] != -1]
    ax.add_collection(LineCollection(segments, colors=color, linewidths=.45, alpha=.85))
    legend.append(Line2D([0], [0], color=color, label=node["bodyId"] + " · " + str(node["type"]) + " · " + str(len(segments)) + " cables"))
ax.autoscale()
ax.set_aspect("equal")
ax.set_xlabel("Native X (8 nm units)", color="#dfebdd")
ax.set_ylabel("Native Z (8 nm units)", color="#dfebdd")
ax.tick_params(colors="#cedecf")
for spine in ax.spines.values():
    spine.set_color("#627965")
ax.legend(handles=legend, loc="upper left", bbox_to_anchor=(1.06, .98), facecolor="#21352a", edgecolor="#627965", labelcolor="#eff3e9", fontsize=8)
fig.suptitle("Three source-backed local skeletons · native X/Z projection", color="#f1f3e4", fontsize=15, y=.96)
fig.text(.5, .035, "Offline data preview — not a browser screenshot. Orientation unverified; no branch inference.\nThese bodies are separate from the 110-body requested circuit package.", ha="center", color="#dce6cf", fontsize=10)
fig.subplots_adjust(left=.15, right=.65, top=.88, bottom=.16)
output = root / "docs/previews"
output.mkdir(exist_ok=True)
for suffix in ["png", "svg"]:
    fig.savefig(output / ("native-anatomy." + suffix), dpi=160, facecolor=fig.get_facecolor())
manifest = {"kind": "OFFLINE_NATIVE_XZ_PROJECTION_NOT_BROWSER_SCREENSHOT", "dataset": package["dataset"],
            "geometryInputs": inputs, "packageSha256": hashlib.sha256(package_path.read_bytes()).hexdigest(),
            "scriptSha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "units": "8 nm", "orientation": "UNVERIFIED", "branchesInferred": False,
            "outputs": {suffix: hashlib.sha256((output / ("native-anatomy." + suffix)).read_bytes()).hexdigest() for suffix in ["png", "svg"]}}
(output / "native-anatomy.manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
print("Wrote hash-linked native-anatomy.png/.svg and provenance manifest.")
