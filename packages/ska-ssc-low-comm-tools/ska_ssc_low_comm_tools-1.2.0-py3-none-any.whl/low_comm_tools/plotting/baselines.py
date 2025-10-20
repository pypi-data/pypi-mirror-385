from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Literal

import astropy.units as u
import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
from casacore.tables import table, taql
from matplotlib.colors import Normalize
from matplotlib.figure import Figure
from tqdm.auto import tqdm

from low_comm_tools.ms_utils import (
    get_antenna_names_from_ms,
    get_antennas_from_ms,
    get_freq_from_ms,
    get_time_from_table,
)


def _plot_subtable(
    data_column: str,
    subtab: table,
    freq_chan: u.Quantity[u.Hz],
    ant_1: int,
    ant_2: int,
    station_names: list[str],
    fast_plot: bool = True,
    norm: Normalize | None = None,
    plot_type: Literal["spectrum", "delay", "delay-rate"] = "spectrum",
    data_type: Literal["amp", "phase"] = "amp",
) -> Figure | None:
    data = subtab.getcol(data_column)

    # Can happen due to weird antenna ordering...
    if data.shape == (0,):
        return None

    # Get and apply flags
    flags = subtab.getcol("FLAG")
    masked_data = np.ma.masked_array(data, mask=flags)  # type: ignore[no-untyped-call]

    time_centroid = get_time_from_table(subtab)
    time = time_centroid - time_centroid.min()

    if plot_type == "spectrum":
        return make_plot(
            x_array=freq_chan.to("MHz").value,
            y_array=time.to("s").value,
            z_array=masked_data,
            ant_1=ant_1,
            ant_2=ant_2,
            station_names=station_names,
            xlabel="Frequency / MHz",
            ylabel="Time / s",
            fast_plot=fast_plot,
            norm=norm,
            data_type=data_type,
        )

    delay_time_array = np.fft.fftshift(
        np.fft.fft(masked_data.filled(0 + 0j), axis=1), axes=1
    )

    delay_s = np.fft.fftshift(
        np.fft.fftfreq(
            n=len(freq_chan.to("Hz").value),
            d=np.diff(freq_chan.to("Hz").value).mean(),
        )
    )

    if plot_type == "delay":
        return make_plot(
            x_array=delay_s * 1e6,
            y_array=time.to("s").value,
            z_array=delay_time_array,
            ant_1=ant_1,
            ant_2=ant_2,
            station_names=station_names,
            xlabel="Delay / µs",
            ylabel="Time / s",
            fast_plot=fast_plot,
            norm=norm,
            data_type=data_type,
        )

    delay_rate_array = np.fft.fftshift(
        np.fft.fft2(masked_data.filled(0 + 0j), axes=(0, 1)),
        axes=(0, 1),
    )
    delay_rate = np.fft.fftshift(
        np.fft.fftfreq(
            n=len(time),
            d=np.diff(time).mean(),
        )
    )

    return make_plot(
        x_array=delay_s * 1e6,
        y_array=delay_rate,
        z_array=delay_rate_array,
        ant_1=ant_1,
        ant_2=ant_2,
        station_names=station_names,
        xlabel="Delay / µs",
        ylabel="Delay rate / Hz",
        fast_plot=fast_plot,
        norm=norm,
        data_type=data_type,
    )


def plot_baselines(
    ms_path: Path | str,
    fast_plot: bool = True,
    norm: Normalize | None = None,
    plot_type: Literal["spectrum", "delay", "delay-rate"] = "spectrum",
    data_column: str = "DATA",
    data_type: Literal["amp", "phase"] = "amp",
) -> dict[str, Figure]:
    """Plot delays for every baseline.
    Args:
        ms_path (Path): Path to visibilities.
        fast_plot (bool, optional): Use `pcolorfast` over `pcolormesh`. Defaults to True.
        norm (Normalize | None, optional): Colourscale normalisation. Defaults to plt.cm.colors.LogNorm().
        do_delay_rate (bool, optional): Compute and plot delay-rate over time axis. Defaults to False.
    """
    if isinstance(ms_path, str):
        ms_path = Path(ms_path)

    figures: dict[str, Figure] = {}
    ant_1s, ant_2s = get_antennas_from_ms(ms_path)
    station_names = get_antenna_names_from_ms(ms_path)
    freq_chan = get_freq_from_ms(ms_path)
    with (
        table(ms_path.as_posix()) as tab,
    ):
        _ = tab
        for ant_1 in tqdm(ant_1s, desc="antenna 1"):
            for ant_2 in tqdm(ant_2s, desc="antenna 2"):
                if ant_1 == ant_2:
                    continue
                with taql(
                    "select from $tab where ANTENNA1 == $ant_1 and ANTENNA2 == $ant_2",
                ) as subtab:
                    figure = _plot_subtable(
                        data_column=data_column,
                        subtab=subtab,
                        freq_chan=freq_chan,
                        ant_1=ant_1,
                        ant_2=ant_2,
                        station_names=station_names,
                        fast_plot=fast_plot,
                        norm=norm,
                        plot_type=plot_type,
                        data_type=data_type,
                    )
                    if figure is not None:
                        figures[f"{ant_1}-{ant_2}"] = figure

    return figures


def make_plot(
    x_array: npt.NDArray[np.floating[Any]],
    y_array: npt.NDArray[np.floating[Any]],
    z_array: npt.NDArray[np.complexfloating[Any, Any]],
    ant_1: int,
    ant_2: int,
    station_names: list[str],
    data_type: str,
    xlabel: str | None = None,
    ylabel: str | None = None,
    fast_plot: bool = True,
    norm: Normalize | None = None,
) -> Figure:
    fig, axs = plt.subplots(2, 2, sharex=True, sharey=True, figsize=(12, 10))
    match data_type:
        case "amp":
            z_array = np.abs(z_array)
            z_label = "Amplitude / Jy"
            cmap = "viridis"
        case "phase":
            z_array = np.rad2deg(np.angle(z_array))
            z_label = "Phase / deg"
            cmap = "twilight"
        case _:
            msg = f"Unknown `dataype` '{data_type}'"
            raise ValueError(msg)

    # Using 'H' and 'V' to denote lack of common rotation
    for i, pol in enumerate(["HH", "HV", "VH", "VV"]):
        ax = axs.flatten()[i]
        if fast_plot:
            im = ax.pcolorfast(
                x_array,
                y_array,
                # :-1 is to make pcolorfast happy
                z_array[:-1, :-1, i],
                norm=norm,
                cmap=cmap,
            )
        else:
            im = ax.pcolormesh(
                x_array,
                y_array,
                z_array[..., i],
                norm=norm,
                cmap=cmap,
            )
        ax.set(
            aspect="auto",
            title=pol,
            xlabel=xlabel,
            ylabel=ylabel,
        )
        cbar = fig.colorbar(im, ax=ax)
        cbar.set_label(z_label)
    fig.suptitle(
        f"Baseline {ant_1}::{ant_2} ({station_names[ant_1]}::{station_names[ant_2]})"
    )
    fig.tight_layout()

    return fig


def save_figures(
    figures: dict[str, Figure],
    out_dir: Path | str,
    plot_type: Literal["spectrum", "delay", "delay-rate"],
    data_column: str,
    data_type: Literal["amp", "phase"],
    prefix: str | None = None,
) -> list[Path]:
    if isinstance(out_dir, str):
        out_dir = Path(out_dir)

    out_paths: list[Path] = []

    for baseline, fig in figures.items():
        out_name = f"baseline_{baseline}_{data_column}_{plot_type}_{data_type}.png"
        if prefix is not None:
            out_name = f"{prefix}_{out_name}"
        out_path = out_dir / out_name

        fig.savefig(
            out_path,
            dpi=300,
            bbox_inches="tight",
        )
        out_paths.append(out_path)

    return out_paths


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Plot visibilities per baseline.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "ms_path",
        type=Path,
        help="Path to visibilities.",
    )

    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Optional output directory for plots. Will default to same direactory as MS.",
    )

    parser.add_argument(
        "--no-fast-plot",
        action="store_true",
        help="Don't use `pcolorfast` (falls back to pcolormesh).",
    )

    parser.add_argument(
        "--norm",
        type=str,
        default=None,
        choices=["log", "sqrt"],
        help="Plot normalisation.",
    )

    parser.add_argument(
        "--plot-type",
        type=str,
        choices=["spectrum", "delay", "delay-rate"],
        default="spectrum",
        help="Type of plot. Dynamic 'spectrum', 'delay' vs time, or delay vs 'delay-rate'.",
    )

    parser.add_argument(
        "--data-column", type=str, default="DATA", help="Data column to plot."
    )

    parser.add_argument(
        "--data-type",
        type=str,
        choices=["amp", "phase"],
        default="amp",
        help="Type of data to plot.",
    )

    return parser


norms = {"log": plt.cm.colors.LogNorm(), "sqrt": plt.cm.colors.PowerNorm(0.5)}  # type: ignore[attr-defined]


def main() -> None:
    parser = get_parser()

    args = parser.parse_args()

    norm = norms.get(args.norm)

    figures = plot_baselines(
        ms_path=args.ms_path,
        fast_plot=not args.no_fast_plot,
        norm=norm,
        plot_type=args.plot_type,
        data_column=args.data_column,
        data_type=args.data_type,
    )

    out_dir = args.out_dir
    if out_dir is None:
        out_dir = args.ms_path.parent

    _ = save_figures(
        figures=figures,
        out_dir=out_dir,
        plot_type=args.plot_type,
        data_column=args.data_column,
        data_type=args.data_type,
        prefix=args.ms_path.stem,
    )


if __name__ == "__main__":
    main()
