"""Stream raw unsigned synapse counts; retain all traced-to-traced rows."""
from __future__ import annotations

import numpy as np
import pyarrow as pa
import pyarrow.ipc as ipc
import pyarrow.parquet as pq


def locate_ids(sorted_ids, queried):
    if len(sorted_ids) == 0:
        raise ValueError("Cannot index an empty atlas")
    idx = np.searchsorted(sorted_ids, queried)
    valid = (idx < len(sorted_ids)) & (sorted_ids[np.minimum(idx, len(sorted_ids) - 1)] == queried)
    return idx, valid


def export_graph(source, output, atlas, consumers=(), progress=print):
    ids = atlas.bodyId.to_numpy(dtype=np.int64)
    n = len(ids)
    incoming, outgoing, omitted_in, omitted_out = [np.zeros(n, dtype=np.int64) for _ in range(4)]
    classes = sorted(atlas.superclass.fillna("MISSING").unique())
    group = atlas.superclass.fillna("MISSING").map({k: i for i, k in enumerate(classes)}).to_numpy(dtype=int)
    matrix = np.zeros((len(classes), len(classes)), dtype=np.int64)
    schema = pa.schema([
        ("pre_index", pa.int32()), ("post_index", pa.int32()),
        ("synapse_count", pa.int64()), ("source_row", pa.int64()),
    ], metadata={b"evidence": b"RAW_STRUCTURAL", b"dataset": b"male-cns:v1.0", b"index_table": b"atlas.parquet", b"weight_meaning": b"raw unsigned synapse count; no physiological sign or gain"})
    raw_rows = kept_rows = raw_mass = kept_mass = autapse_rows = 0
    with pa.memory_map(str(source), "r") as stream, pq.ParquetWriter(output, schema, compression="zstd") as writer:
        reader = ipc.open_file(stream)
        if reader.schema.names != ["body_pre", "body_post", "weight"]:
            raise ValueError("Unexpected raw connection schema")
        for b in range(reader.num_record_batches):
            batch = reader.get_batch(b)
            if any(batch.column(c).null_count for c in range(3)):
                raise ValueError("Missing raw edge endpoint/count")
            pre_id, post_id, weights = [batch.column(c).to_numpy(zero_copy_only=False) for c in range(3)]
            if (weights <= 0).any() or weights.dtype.kind not in "iu":
                raise ValueError("Raw synapse counts must be positive integers")
            pre, has_pre = locate_ids(ids, pre_id)
            post, has_post = locate_ids(ids, post_id)
            keep = has_pre & has_post
            rows = np.flatnonzero(keep)
            p, q, w = pre[keep].astype(np.int32), post[keep].astype(np.int32), weights[keep].astype(np.int64)
            writer.write_table(pa.Table.from_arrays([p, q, w, rows + raw_rows], schema=schema))
            # Integer accumulation avoids converting raw counts into modeled weights.
            np.add.at(incoming, q, w); np.add.at(outgoing, p, w)
            np.add.at(omitted_in, post[has_post & ~has_pre], weights[has_post & ~has_pre])
            np.add.at(omitted_out, pre[has_pre & ~has_post], weights[has_pre & ~has_post])
            np.add.at(matrix, (group[p], group[q]), w)
            for consume in consumers:
                consume(p, q, w)
            raw_rows += len(batch)
            kept_rows += len(w)
            raw_mass += int(weights.sum())
            kept_mass += int(w.sum())
            autapse_rows += int(np.count_nonzero(p == q))
            if b % 300 == 0:
                progress(f"Raw edge batches {b + 1}/{reader.num_record_batches}; retained {kept_rows:,} rows", flush=True)
    totals = dict(incoming_synapses=incoming, outgoing_synapses=outgoing,
                  incoming_from_excluded_synapses=omitted_in, outgoing_to_excluded_synapses=omitted_out)
    summary = dict(raw_edge_rows=raw_rows, traced_edge_rows=kept_rows, raw_synapse_count=raw_mass,
                   traced_synapse_count=kept_mass, autapse_rows=autapse_rows, minimum_synapse_count=1,
                   edge_rows_note="Rows retained as supplied; no deduplication or effective-connectivity selection",
                   superclass_order=classes, superclass_synapse_matrix=matrix.tolist())
    return totals, summary
