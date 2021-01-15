import matplotlib.pyplot as plt, mpld3

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np


class MidpointNormalize(colors.Normalize):
    """
    Normalise the colorbar so that diverging bars work there way either side from a prescribed midpoint value)

    e.g. im=ax1.imshow(array, norm=MidpointNormalize(midpoint=0.,vmin=-100, vmax=100))
    """

    def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
        self.midpoint = midpoint
        colors.Normalize.__init__(self, vmin, vmax, clip)

    def __call__(self, value, clip=None):
        # I'm ignoring masked values and all kinds of edge cases to make a
        # simple example...
        x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.5, 1]
        return np.ma.masked_array(np.interp(value, x, y), np.isnan(value))


def graph_elex(cdf, state="Nationwide", year=2021, detained_num=0, save=False):

    df = cdf[cdf.has_election_2021]
    # if year == 2019:
    #     tups = to_tuples(get_2019_dict(cdf))
    # elif year == 2020:
    #     tups = to_tuples(get_2020_dict(cdf))

    # for i in tups:
    #     df = pd.concat([df, cdf[(cdf.State_init == i[0]) & (cdf.County == i[1])]])

    # df["total_detained"] = df.loc[:, "Detainers Total"]
    df = df[df["Detainers Total"] > detained_num]

    df = df.sort_values(by="per_dem")

    if state != "Nationwide":
        df = df[df.statecode == state]
    x = df["per_dem"]
    y = df["CAP Local/Detainers"]
    colors = df.per_dem
    cm = plt.cm.get_cmap("RdBu")
    # area = 4000
    area = (df.total_votes) / 100

    df["name_init"] = df["county_name"] + ", " + df["statecode"]
    text = df.name_init

    plt.rc("font", weight="bold", family="sans-serif", size=12)

    fig, ax = plt.subplots(figsize=(10, 10))
    sct = ax.scatter(
        x,
        y,
        linewidths=2,
        s=area,
        edgecolor="w",
        c=colors,
        cmap=cm,
        clim=(-1, 1),
    )
    ax.set_xlim([0, 1.05])
    ax.set_ylim([-0.02, 0.35])
    #     plugins.connect(fig, plugins.PointLabelTooltip(fig))
    sct.set_alpha(0.85)

    labels = ["{}".format(i) for i in text]
    label2 = ["{} detainees".format(i) for i in df["Detainers Total"]]

    #     tooltip = mpld3.plugins.PointLabelTooltip(sct, labels=zip(labels,label2))
    #     mpld3.plugins.connect(fig, tooltip)

    #     for labeli, xi, yi in zip(text, x, y):
    #         ax.annotate(labeli,xy=(xi, yi))

    for labeli, xi, yi in zip(text, x, y):
        if xi > 5000:
            ax.annotate(labeli, xy=(xi, yi))
        if yi > (0.01 * max(y)):
            ax.annotate(labeli, xy=(xi, yi))

    hfont = {"fontname": "DejaVu Sans"}

    # ax.set_xlabel("Total Detained", fontsize=16, **hfont)
    ax.set_xlabel("Percent Dem Presidential Vote 2020", fontsize=16, **hfont)
    ax.set_ylabel("Ratio of CAP Local to Detainers ", fontsize=16, **hfont)
    plt.title(f"Counties -- {state}", fontsize=22, **hfont)
    if state == "Nationwide":
        plt.text(
            0.5,
            0.99,
            f"Elections in {year} and {detained_num}+ detentions",
            horizontalalignment="center",
            verticalalignment="center",
            transform=ax.transAxes,
            fontsize=16,
        )
    else:
        plt.text(
            0.5,
            0.99,
            f"Elections in {year}",
            horizontalalignment="center",
            verticalalignment="center",
            transform=ax.transAxes,
            fontsize=16,
        )

    # sct_html = fig_to_html(fig)
    if save == True:
        mpld3.save_html(
            fig,
            f"../findings/2021_national_counties.html"
            # fig, f"../findings/elex_19_20/{year}/elections_{year}_counties_{state}.html"
        )
    return mpld3.display()


# graph_elex(cdf, detained_num=250, save=True)
