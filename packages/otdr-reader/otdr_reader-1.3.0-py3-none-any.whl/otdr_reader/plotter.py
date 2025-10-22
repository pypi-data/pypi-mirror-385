import base64
from os import path, stat
from typing import List

import plotly.graph_objects as go
import plotly.io as pio
from rich import print

from .classes import Otdr

pio.templates["testoNero"] = go.layout.Template(
    layout=dict(
        font=dict(
            color="#212121",
            family="Segoe UI",
        ),
    ),
)
pio.templates.default = "plotly_white+testoNero"  # +presentation


arancione = "#fe9501"
grigio = "#5e5e5e"
logo_path = path.join(path.dirname(__file__), "logo", "cohaerentia.png")

with open(logo_path, "rb") as image_file:
    encoded_logo = base64.b64encode(image_file.read()).decode("utf-8")


def plot_trace_with_events(
    trace: Otdr, smooth: int = 0, logo: bool = True
) -> go.Figure:
    # title_str = f"{trace.filename}, {trace.timestamp}"

    if not smooth == 0:
        trace.smooth(window=smooth)

    fig = go.Figure(
        layout=dict(
            title=f"{trace.filename}"
            + "<br>"
            + f'<span style="font-size: 12px;">Wavelength: {trace.wavelength} nm, Pulse width: {trace.pulse_width_ns} ns.</span>'
            + "<br>"
            + f'<span style="font-size: 12px;">{trace.timestamp}</span>',
            yaxis_title="Power (dB)",
            xaxis_title="Position (km)",
        )
    )
    fig.add_trace(
        go.Scatter(x=trace.positions, y=trace.attenuations, line=dict(color=arancione))
    )

    for event in trace.events:
        fig.add_annotation(x=event.x, y=event.y, text=event.type)

    if logo:
        fig.add_layout_image(
            dict(
                source=f"data:image/png;base64,{encoded_logo}",
                xref="paper",
                yref="paper",
                x=1,
                y=1,
                sizex=0.2,
                sizey=0.2,
                xanchor="right",
                yanchor="bottom",
            )
        )

    return fig


def plot_list(
    traces: List[Otdr], folder: str = None, smooth: int = 0, logo: bool = True
) -> go.Figure:
    fig = go.Figure(
        layout=dict(title=folder, xaxis_title="Position (km)", yaxis_title="Power (dB)")
    )
    for trace in traces:
        _, legend_name = path.split(trace.filename)

        if not smooth == 0:
            trace.smooth(window=smooth)

        fig.add_trace(
            go.Scatter(
                x=trace.positions,
                y=trace.attenuations,
                name=path.splitext(legend_name)[0],
            )
        )

    if logo:
        fig.add_layout_image(
            dict(
                source=f"data:image/png;base64,{encoded_logo}",
                xref="paper",
                yref="paper",
                x=1,
                y=1,
                sizex=0.2,
                sizey=0.2,
                xanchor="right",
                yanchor="bottom",
            )
        )

    return fig


def export_fig_to_html(figure: go.Figure, filename: str):
    figure.write_html(file=filename)
    print(f"✅ [green]Plot {filename} created.[/green]")
