from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.axes import Axes
from matplotlib.container import BarContainer
from pydantic import validate_call

from sereto.risk import Risks


def _label_plot(ax: Axes, rect: BarContainer) -> None:
    """Add labels to the bars in the bar plot.

    Args:
        ax: Object containing the bar plot.
        rect: Object containing the bars in the bar plot.
    """
    for r in rect:
        height = r.get_height()
        if height > 0:
            ax.annotate(
                str(height),
                xy=(r.get_x() + r.get_width() / 2, height),
                xytext=(0, 3),  # 3 points vertical offset
                textcoords="offset points",
                ha="center",
                va="bottom",
            )


@validate_call
def risks_plot(risks: Risks, path: Path) -> None:
    """Generate a bar plot with the number of vulnerabilities per risk rating.

    Args:
        risks: Object containing the counts of vulnerabilities for each risk rating.
        path: Desired destination for the generated PNG file.
    """
    NAMES = ["Critical", "High", "Medium", "Low", "Info"]
    COUNTS = [risks.critical, risks.high, risks.medium, risks.low, risks.info]
    COLORS = ["red", "orange", "#f0f000", "#33cc33", "#3366ff"]

    # Set global font size
    rcParams["font.size"] = 14

    fig, ax = plt.subplots()
    fig.set_size_inches(10, 5)
    ax.set_title("Number of Vulnerabilities by Risk Rating")

    rect = ax.bar(range(len(NAMES)), COUNTS, align="center", color=COLORS)
    ax.set_xticks(range(len(NAMES)))
    ax.set_xticklabels(NAMES)
    ax.set_yticks(range(max(risks.critical, risks.high, risks.medium, risks.low, risks.info) + 1))
    _label_plot(ax, rect)

    fig.tight_layout()
    plt.margins(0.15)
    plt.savefig(path, dpi=100)
    plt.close("all")
