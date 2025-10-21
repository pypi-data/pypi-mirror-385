"""
Plot QC outcomes
================

Some plotting routines for QC outcomes
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D


def _get_colours_labels(qc_outcomes):
    colours = []
    colour_passed = "#55ff55"
    colour_failed = "#ff5555"
    colour_other = "#808080"
    passed = 0
    failed = 0
    other = 0
    for outcome in qc_outcomes:
        if outcome == 0:
            colours.append(colour_passed)
            passed += 1
        elif outcome == 1:
            colours.append(colour_failed)
            failed += 1
        else:
            colours.append(colour_other)
            other += 1

    legend_elements = [
        Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            label=f"0: {passed}",
            markerfacecolor=colour_passed,
        ),
        Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            label=f"1: {failed}",
            markerfacecolor=colour_failed,
        ),
        Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            label=f"other: {other}",
            markerfacecolor=colour_other,
        ),
    ]
    return colours, legend_elements


def _make_plot(xvalue, yvalue, flags, xlim, ylim, xlabel, ylabel, filename):
    colours, legend_elements = _get_colours_labels(flags)

    colours = np.array(colours)

    mask_passed = flags == 0
    mask_failed = flags == 1
    mask_other = (flags != 0) & (flags != 1)

    fig, axes = plt.subplots(2, 2, figsize=(16, 9), sharex=True, sharey=True)
    axes = axes.flatten()

    titles = ["QC == 0 (Passed)", "QC == 1 (Failed)", "QC == Other", "All Points"]

    masks = [mask_passed, mask_failed, mask_other, np.ones_like(flags, dtype=bool)]

    for i in range(4):
        ax = axes[i]
        ax.scatter(xvalue[masks[i]], yvalue[masks[i]], c=colours[masks[i]], s=1)
        ax.set_title(titles[i])
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        if xlim:
            ax.set_xlim(*xlim)
        if ylim:
            ax.set_ylim(*ylim)

    fig.legend(
        handles=legend_elements,
        loc="center",
        ncol=len(legend_elements),
        bbox_to_anchor=(0.5, 0.53),
    )

    plt.tight_layout(rect=[0, 0.05, 1, 1])

    if filename is None:
        plt.show()
    else:
        plt.savefig(filename)

    plt.close()


def latitude_variable_plot(lat: np.ndarray, value: np.ndarray, qc_outcomes: np.ndarray, filename: str | None = None):
    """
    Plot a graph of points showing the latitude and value of a set of observations coloured according to
    the QC oucomes.

    Parameters
    ----------
    lat: np.ndarray
        Array of latitude values in degrees
    value: np.ndarray
        Array of observed values for the variable
    qc_outcomes: np.ndarray
        Array containing the QC outcomes, with 0 meaning pass and non-zero entries indicating failure
    filename: str or None
        Filename to save the figure to. If None, the figure is saved with a standard name

    Returns
    -------
    None
    """
    _make_plot(
        xvalue=value,
        yvalue=lat,
        flags=qc_outcomes,
        xlim=None,
        ylim=[-90.0, 90.0],
        xlabel="Variable",
        ylabel="Latitude",
        filename=filename,
    )


def latitude_longitude_plot(lat: np.ndarray, lon: np.ndarray, qc_outcomes: np.ndarray, filename: str | None = None) -> None:
    """
    Plot a graph of points showing the latitude and longitude of a set of observations coloured according to
    the QC outcomes.

    Parameters
    ----------
    lat: np.ndarray
        array of latitude values in degrees
    lon: np.ndarray
        array of longitude values in degrees
    qc_outcomes: np.ndarray
        array containing the QC outcomes, with 0 meaning pass and non-zero entries indicating failure
    filename: str or None
        Filename to save the figure to. If None, the figure is saved with a standard name

    Returns
    -------
    None
    """
    _make_plot(
        xvalue=lon,
        yvalue=lat,
        flags=qc_outcomes,
        xlim=[-180.0, 180.0],
        ylim=[-90.0, 90.0],
        xlabel="Longitude",
        ylabel="Latitude",
        filename=filename,
    )
