from glob import glob
from os import makedirs, path
from typing import List

import jsonpickle
from rich.progress import track

from .classes import Otdr


def load_folder(folder: str) -> List[Otdr]:
    filelist = glob(path.join(folder, "*.sor"))

    traces = list()

    for file in track(filelist, description="Loading files..."):
        traces.append(Otdr(filename=file))

    return traces


def trace_to_json(trace: Otdr, filename: str):
    with open(filename, "w") as f:
        f.write(jsonpickle.encode(trace))


def traces_to_json(traces: List[Otdr], target_folder: str | None = None):
    for trace in track(traces, description="Exporting to json..."):
        output_filename = path.splitext(trace.filename)[0] + ".json"
        if target_folder:
            head, tail = path.split(output_filename)
            output_folder = path.join(head, target_folder)
            if not path.exists(output_folder):
                makedirs(output_folder)
            output_filename = path.join(output_folder, tail)
        trace_to_json(trace=trace, filename=output_filename)
    print(
        f"✅ [green]{len(traces)} files converted and stored in folder {output_folder}.[/green]"
    )
