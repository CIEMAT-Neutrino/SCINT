import subprocess

bashCommand = "yum info texlive-latex-base"
process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
output, error = process.communicate()
if "Error" in str(output):
    print("You don't have latex installed. Changing default configuration to tex=False")
    tex_installed = False
else:
    print("You have latex installed!. Applying default configuration (tex=True)")
    tex_installed = True

from matplotlib import pyplot as plt
from matplotlib.ticker import MultipleLocator


def figure_features(tex=tex_installed, font="serif", dpi=300):
    """Customize figure settings.
    Args:
        tex (bool, optional): use LaTeX. Defaults to True.
        font (str, optional): font type. Defaults to "serif".
        dpi (int, optional): dots per inch. Defaults to 180.
    """
    plt.rcParams.update(
        {
            "font.size": 16,
            "font.family": font,
            "font.weight": "bold",
            "text.usetex": tex,
            "figure.subplot.top": 0.92,
            "figure.subplot.right": 0.95,
            "figure.subplot.left": 0.10,
            "figure.subplot.bottom": 0.12,
            "figure.subplot.hspace": 0.1,
            "savefig.dpi": dpi,
            "savefig.format": "png",
            "axes.titlesize": 16,
            "axes.labelsize": 16,
            "axes.axisbelow": True,
            "xtick.direction": "in",
            "ytick.direction": "in",
            "xtick.major.size": 5,
            "xtick.minor.size": 2.25,
            "xtick.major.pad": 7.5,
            "xtick.minor.pad": 7.5,
            "ytick.major.pad": 7.5,
            "ytick.minor.pad": 7.5,
            "ytick.major.size": 5,
            "ytick.minor.size": 2.25,
            "xtick.labelsize": 15,
            "ytick.labelsize": 15,
            "legend.fontsize": 12,
            "legend.framealpha": 1,
            "figure.titlesize": 18,
            "lines.linewidth": 2,
            "figure.constrained_layout.use": True
        }
    )


def add_grid(ax, lines=True, locations=None):
    """Add a grid to the current plot.
    Args:
        ax (Axis): axis object in which to draw the grid.
        lines (bool, optional): add lines to the grid. Defaults to True.
        locations (tuple, optional):
            (xminor, xmajor, yminor, ymajor). Defaults to None.
    """

    if lines:
        ax.grid(lines, alpha=0.5, which="minor", ls=":")
        ax.grid(lines, alpha=0.7, which="major")

    if locations is not None:

        assert (
            len(locations) == 4
        ), "Invalid entry for the locations of the markers"

        xmin, xmaj, ymin, ymaj = locations

        ax.xaxis.set_minor_locator(MultipleLocator(xmin))
        ax.xaxis.set_major_locator(MultipleLocator(xmaj))
        ax.yaxis.set_minor_locator(MultipleLocator(ymin))
        ax.yaxis.set_major_locator(MultipleLocator(ymaj))