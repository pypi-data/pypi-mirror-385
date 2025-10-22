import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
from matplotlib.axes import Axes
from typing import Optional
import matplotlib.pyplot as plt
from matplotlib.colors import to_hex


def fmt(value, fmt):
    if fmt == "$":
        return f"${value:,.0f}"
    if fmt == "%":
        return f"{value:.0%}"
    elif fmt == "d":
        return mdates.DateFormatter("%Y-%m-%d")
    else:
        return f"{value:{fmt}}"


def get_campaign_colors(names: list[str]) -> dict[str, str]:
    """
    Assigns distinct matplotlib colors for any number of campaign names.
    Returns a dict {name: color_hex}.
    """
    n = len(names)
    if n == 0:
        return {}

    # choose suitable colormap
    # if n <= 10:
    #     cmap = plt.get_cmap("tab10")
    # elif n <= 20:
    #     cmap = plt.get_cmap("tab20")
    # else:
    cmap = plt.get_cmap("viridis")  # or "viridis", "plasma", etc.

    # sample evenly spaced colors from the cmap
    colors = [to_hex(cmap(i / max(1, n - 1))) for i in range(n)]

    return dict(zip(names, colors))


def style(
    ax: Axes,
    x_fmt: Optional[str] = None,
    y_fmt: Optional[str] = None,
    x_label: Optional[str] = None,
    y_label: Optional[str] = None,
    title: Optional[str] = None,
    font_size: int = 10,
    legend: bool = True,
    legend_loc: Optional[str] = None,
) -> Axes:
    # Handle Y-axis formatting
    if y_fmt is not None:
        if y_fmt in ["d"]:
            ax.yaxis.set_major_formatter(fmt(None, y_fmt))
        else:
            ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: fmt(x, y_fmt)))

    # Handle X-axis formatting (dates)
    if x_fmt is not None:
        if x_fmt in ["d"]:
            ax.xaxis.set_major_formatter(fmt(None, x_fmt))
        else:
            ax.xaxis.set_major_formatter(FuncFormatter(lambda x, p: fmt(x, x_fmt)))

    # rotate x-axis labels
    ax.tick_params(axis="x", labelrotation=90)
    # Set labels and title
    if x_label is not None:
        ax.set_xlabel(x_label, fontsize=font_size)
    if y_label is not None:
        ax.set_ylabel(y_label, fontsize=font_size)
    if title is not None:
        ax.set_title(title, fontsize=font_size * 1.5)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, ax.get_ylim()[1])
    # Handle legend
    if legend:
        if legend_loc == "r":
            ax.legend(
                fontsize=font_size,
                frameon=False,
                loc="center left",
                bbox_to_anchor=(1, 0.5),
            )
        else:
            ax.legend(fontsize=font_size, frameon=False)

    fig = ax.get_figure()
    fig.tight_layout()

    return ax
