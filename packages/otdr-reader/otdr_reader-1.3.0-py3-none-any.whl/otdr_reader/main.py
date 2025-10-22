from enum import Enum
from os import getcwd, path
from typing import Optional

import typer
from rich import print

from .classes import Otdr
from .helpers import load_folder, trace_to_json, traces_to_json
from .plotter import export_fig_to_html, plot_list, plot_trace_with_events


class Output(str, Enum):
    json = "json"
    plot = "html"


app = typer.Typer(name="OTDR .sor exporter")


@app.command("file")
# @app.callback(invoke_without_command=True)
def convert_file(
    file: str,
    output: Optional[Output] = Output.plot,
    smooth: Optional[int] = 0,
    logo: Optional[bool] = True,
):
    """Convert otdr .sor file. Default command."""
    if not path.isfile(file):
        print(f":warning: [red]File {file} not found.[/red]")
        return

    trace = Otdr(filename=file)

    output_filename = path.splitext(file)[0] + "." + output.value
    if output == output.plot:
        export_fig_to_html(
            plot_trace_with_events(trace, smooth=smooth, logo=logo),
            filename=output_filename,
        )
    else:
        trace_to_json(trace, output_filename)


@app.command("folder")
def convert_folder(
    folder: Optional[str] = getcwd(),
    output: Optional[Output] = Output.plot,
    target_folder: Optional[str] = "converted",
    target_filename: Optional[str] = "plot",
    smooth: Optional[int] = 0,
    logo: Optional[bool] = True,
):
    """Convert all otdr .sor files in a folder."""

    if not path.isdir(folder):
        print(f":warning: [red]Folder {folder} not found.[/red]")
        return
    traces = load_folder(folder=folder)

    if output == output.plot:
        export_fig_to_html(
            plot_list(traces=traces, folder=folder, smooth=smooth, logo=logo),
            filename=path.join(folder, target_filename + ".html"),
        )
    else:
        traces_to_json(traces, target_folder)
