"""Ingest the rsoxs simulation data into Event Model."""

import event_model
from pathlib import Path
import h5py
import pandas as pd
import time


def build_pandas_index(nxs_path):
    nxs_path = Path(nxs_path)
    nxs_files = list(nxs_path.glob("*nxs"))

    # progress = ipywidgets.IntProgress(0,0,len(nxs_files))
    # display(progress)

    index_table = []
    for i, nxs_file in enumerate(nxs_files):
        # progress.value = i
        with h5py.File(nxs_file, "r") as nxs:
            notes = nxs["entry/instrument/simulation_engine/notes"]
            config = {k: v[()] for k, v in notes.items()}
            config["nxs"] = nxs_file
            index_table.append(config)
    return pd.DataFrame(index_table)


def ingest_simulations(path):
    path = Path(path)

    for f in path.glob("*nxs"):
        with h5py.File(f, "r") as nxs:
            notes = nxs["entry/instrument/simulation_engine/notes"]
            config = {k: v[()] for k, v in notes.items()}
            run_bundle = event_model.compose_run(
                metadata={"source": "rsoxs_simulation", "input_file": f.name, **config}
            )
            yield "start", run_bundle.start_doc
            group_name = "/entry/sasdata_singleimg"
            group = nxs[group_name]
            dset_name = group.attrs["signal"]
            ylabel, xlabel = group.attrs["I_axes"].split(",")
            ds = group[dset_name]
            xlabel_ds = group[xlabel]
            ylabel_ds = group[ylabel]
            desc_bundle = run_bundle.compose_descriptor(
                data_keys={
                    "image": {
                        "dtype": "array",
                        "shape": list(ds.shape),
                        "source": f"simulation:{f.name}{group_name}/{dset_name}",
                        "dims": (ylabel, xlabel),
                        "external": "FILESTORE:",
                    },
                    xlabel: {
                        "dtype": "array",
                        "shape": list(xlabel_ds.shape),
                        "source": f"simulation:{f.name}{group_name}/{xlabel}",
                        "external": "FILESTORE:",
                    },
                    ylabel: {
                        "dtype": "array",
                        "shape": list(ylabel_ds.shape),
                        "source": f"simulation:{f.name}{group_name}/{ylabel}",
                        "external": "FILESTORE:",
                    },
                },
                name="primary",
            )

            yield "descriptor", desc_bundle.descriptor_doc

            resource_bundle = run_bundle.compose_resource(
                spec="nist_rsoxs_simulation_v1",
                root=str(path),
                resource_path=str(f.name),
                resource_kwargs={"group": group_name},
            )
            yield "resource", resource_bundle.resource_doc
            xdatum = resource_bundle.compose_datum(
                datum_kwargs={"dset": xlabel, "dims": None}
            )
            yield "datum", xdatum
            ydatum = resource_bundle.compose_datum(
                datum_kwargs={"dset": ylabel, "dims": None}
            )
            yield "datum", ydatum
            Idatum = resource_bundle.compose_datum(
                datum_kwargs={"dset": dset_name, "dims": (ylabel, xlabel)}
            )
            yield "datum", Idatum
            ts = time.time()
            data = {
                "image": Idatum["datum_id"],
                xlabel: xdatum["datum_id"],
                ylabel: ydatum["datum_id"],
            }
            yield "event", desc_bundle.compose_event(
                data=data,
                timestamps={k: ts for k in data},
                filled={k: False for k in data},
            )
            yield "stop", run_bundle.compose_stop()
