import matplotlib.pyplot as plt, mpld3

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.ticker as mtick
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


def graph_immigration_elections(cdf, state="Nationwide", save=False, **kwargs):

    if "year" in kwargs:
        year = kwargs["year"]
        df = cdf[cdf[f"has_election_{kwargs['year']}"]]
        kwargs.pop("year")
    else:
        df = cdf.copy()

    for kw in kwargs:
        if len(kwargs[kw]) > 1:
            sign, val = kwargs[kw]
            if sign == ">=":
                df = df[np.greater_equal(df[kw], val)]
            elif sign == "<=":
                df = df[np.less_equal(df[kw], val)]
            elif sign == "<":
                df = df[np.less(df[kw], val)]
            elif sign == ">":
                df = df[np.greater(df[kw], val)]
            elif sign == "==":
                df = df[np.equal(df[kw], val)]
        else:
            df = df[np.equal(df[kw], kwargs[kw])]

    # for i in tups:
    #     df = pd.concat([df, cdf[(cdf.State_init == i[0]) & (cdf.County == i[1])]])

    # df["total_detained"] = df.loc[:, "Detainers Total"]
    # df = df[df["Detainers Total"] > detained_num]

    df = df.sort_values(by="per_dem")

    if state != "Nationwide":
        df = df[df.statecode == state]
    x = df["per_dem"]
    y = df["CAP Local/All"]
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
        norm=MidpointNormalize(vmin=0, midpoint=0.5),
        clim=(-1, 1),
    )
    ax.set_xlim([0, 1.05])
    ax.set_ylim([-0.02, 1.02])
    ax.xaxis.set_major_formatter(mtick.PercentFormatter(1.0))
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
    ax.set_ylabel("Ratio of CAP Local to All Arrests ", fontsize=16, **hfont)
    plt.title(f"Counties -- {state}", fontsize=22, **hfont)
    if state == "Nationwide":
        plt.text(
            0.5,
            0.99,
            f"{year}",  # f"Elections in {year} and {detained_num}+ detentions",
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
            f"../findings/2021/{state}--CAP Local per immigration arrest.html"
            # fig, f"../findings/elex_19_20/{year}/elections_{year}_counties_{state}.html"
        )
    return mpld3.display()


# graph_elex(cdf, detained_num=250, save=True)


def graph_elex_deaths_per_pop(
    cdf, state="Nationwide", year=2021, detained_num=0, save=False
):
    df = cdf[cdf.has_election_2021]
    df = df[df["Detainers Total"] > detained_num]

    df = df.sort_values(by="per_dem")

    if state != "Nationwide":
        df = df[df.statecode == state]
    x = df["per_dem"]
    y = df["Deaths_per_thousand_pop"]
    colors = df.per_dem
    cm = plt.cm.get_cmap("RdBu")
    # area = 400
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
        norm=MidpointNormalize(vmin=0, midpoint=0.5),
        cmap=cm,
        clim=(-1, 1),
    )
    ax.xaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    # ax.set_xlim([0, 1.05])
    # ax.set_ylim([-0.02, 1.02])
    #     plugins.connect(fig, plugins.PointLabelTooltip(fig))
    sct.set_alpha(0.85)

    labels = ["{}".format(i) for i in text]
    label2 = ["{} detainees".format(i) for i in df["Detainers Total"]]

    #     tooltip = mpld3.plugins.PointLabelTooltip(sct, labels=zip(labels,label2))
    #     mpld3.plugins.connect(fig, tooltip)

    #     for labeli, xi, yi in zip(text, x, y):
    #         ax.annotate(labeli,xy=(xi, yi))

    for labeli, xi, yi in zip(text, x, y):
        # if yi > (0.001 * max(y)):
        ax.annotate(labeli, xy=(xi, yi))

    hfont = {"fontname": "DejaVu Sans"}

    # ax.set_xlabel("Total Detained", fontsize=16, **hfont)
    ax.set_xlabel("Percent Dem Presidential Vote 2020", fontsize=16, **hfont)
    ax.set_ylabel("Deaths per thousand jailed population", fontsize=16, **hfont)

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
            # fig, f"../findings/2021_national_counties.html"
            # fig, f"../findings/elex_19_20/{year}/elections_{year}_counties_{state}.html"
            fig,
            f"../findings/2021/{state}--deaths_per_thousand_pop.html",
        )
    return mpld3.display()


def graph_per_k_arrests(cdf, state="Nationwide", save=False, **kwargs):

    if "year" in kwargs:
        year = kwargs["year"]
        df = cdf[cdf[f"has_election_{kwargs['year']}"]]
        kwargs.pop("year")
    else:
        df = cdf.copy()

    for kw in kwargs:
        if len(kwargs[kw]) > 1:
            sign, val = kwargs[kw]
            if sign == ">=":
                df = df[np.greater_equal(df[kw], val)]
            elif sign == "<=":
                df = df[np.less_equal(df[kw], val)]
            elif sign == "<":
                df = df[np.less(df[kw], val)]
            elif sign == ">":
                df = df[np.greater(df[kw], val)]
            elif sign == "==":
                df = df[np.equal(df[kw], val)]
        else:
            df = df[np.equal(df[kw], kwargs[kw])]

    # for i in tups:
    #     df = pd.concat([df, cdf[(cdf.State_init == i[0]) & (cdf.County == i[1])]])

    # df["total_detained"] = df.loc[:, "Detainers Total"]
    # df = df[df["Detainers Total"] > detained_num]

    df = df.sort_values(by="per_dem")

    if state != "Nationwide":
        df = df[df.statecode == state]
    x = df["per_dem"]
    y = df["killings_per_k_arrests"]
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
        norm=MidpointNormalize(vmin=0, midpoint=0.5),
        clim=(-1, 1),
    )
    ax.set_xlim([0, 1.05])
    ax.set_ylim([0, max(y) + max(y) * 0.2])
    # ax.set_ylim([-0.02, 1.02])
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
        if yi >= 0:
            ax.annotate(labeli, xy=(xi, yi))

    hfont = {"fontname": "DejaVu Sans"}

    # ax.set_xlabel("Total Detained", fontsize=16, **hfont)
    ax.set_xlabel("Percent Dem Presidential Vote 2020", fontsize=16, **hfont)
    ax.set_ylabel("Deaths per 1000 Arrested", fontsize=16, **hfont)
    ax.xaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    plt.title(f"Counties -- {state}", fontsize=22, **hfont)
    if state == "Nationwide":
        plt.text(
            0.5,
            0.99,
            f"{year}",  # f"Elections in {year} and {detained_num}+ detentions",
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
            f"../findings/2021/{state}--deaths_per_thousand_arrests.html"
            # fig, f"../findings/elex_19_20/{year}/elections_{year}_counties_{state}.html"
        )
    return mpld3.display()


def graph_low_level_per_arrest(cdf, state="Nationwide", save=False, **kwargs):

    if "year" in kwargs:
        year = kwargs["year"]
        df = cdf[cdf[f"has_election_{kwargs['year']}"]]
        kwargs.pop("year")
    else:
        df = cdf.copy()

    for kw in kwargs:
        if len(kwargs[kw]) > 1:
            sign, val = kwargs[kw]
            if sign == ">=":
                df = df[np.greater_equal(df[kw], val)]
            elif sign == "<=":
                df = df[np.less_equal(df[kw], val)]
            elif sign == "<":
                df = df[np.less(df[kw], val)]
            elif sign == ">":
                df = df[np.greater(df[kw], val)]
            elif sign == "==":
                df = df[np.equal(df[kw], val)]
        else:
            df = df[np.equal(df[kw], kwargs[kw])]

    df = df.sort_values(by="per_dem")

    if state != "Nationwide":
        df = df[df.statecode == state]
    y_var = "low_level_per_arrest"
    df = df.loc[df[y_var].dropna().index]
    x = df["per_dem"]
    y = df[y_var]
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
        norm=MidpointNormalize(vmin=0, midpoint=0.5),
        clim=(-1, 1),
    )
    ax.set_xlim([0, 1.05])
    try:
        ax.set_ylim([0, max(y) + max(y) * 0.2])
    except ValueError:
        ax.set_ylim([0, 1])
    ax.xaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    # ax.set_ylim([-0.02, 1.02])
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
        if yi >= 0:
            ax.annotate(labeli, xy=(xi, yi))

    hfont = {"fontname": "DejaVu Sans"}

    # ax.set_xlabel("Total Detained", fontsize=16, **hfont)
    ax.set_xlabel("Percent Dem Presidential Vote 2020", fontsize=16, **hfont)
    ax.set_ylabel(
        "Proportion of Arrests Categorized as Low-Level", fontsize=16, **hfont
    )
    plt.title(f"Counties -- {state}", fontsize=22, **hfont)
    if state == "Nationwide":
        plt.text(
            0.5,
            0.99,
            f"{year}",  # f"Elections in {year} and {detained_num}+ detentions",
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
            f"../findings/2021/{state}--low_level_arrests.html"
            # fig, f"../findings/elex_19_20/{year}/elections_{year}_counties_{state}.html"
        )
    return mpld3.display()


def create_combined_metrics(
    odf,
    *args,
    year=2021,
):
    df = odf[odf[f"has_election_{year}"]]
    for col in args:
        df["z_" + col] = (df[col] - df[col].mean()) / df[col].std()
    df["combined_score"] = (
        df[[i for i in df.columns if "z_" in i]].fillna(0).sum(axis=1)
    )
    df["zero_adj_comb_score"] = df["combined_score"] + abs(min(df["combined_score"]))
    return df


def graph_combined_metrics(cdf, year=2021, state="Nationwide", save=False, **kwargs):

    df = create_combined_metrics(
        cdf[cdf[f"has_election_{year}"]],
        "CAP Local/All",
        "Deaths_per_thousand_pop",
        "killings_per_k_arrests",
        "low_level_per_arrest",
        year=year,
    )
    for kw in kwargs:
        if len(kwargs[kw]) > 1:
            sign, val = kwargs[kw]
            if sign == ">=":
                df = df[np.greater_equal(df[kw], val)]
            elif sign == "<=":
                df = df[np.less_equal(df[kw], val)]
            elif sign == "<":
                df = df[np.less(df[kw], val)]
            elif sign == ">":
                df = df[np.greater(df[kw], val)]
            elif sign == "==":
                df = df[np.equal(df[kw], val)]
        else:
            df = df[np.equal(df[kw], kwargs[kw])]

    df = df.sort_values(by="per_dem")

    if state != "Nationwide":
        df = df[df.statecode == state]
    y_var = "zero_adj_comb_score"
    df = df.loc[df[y_var].dropna().index]
    x = df["per_dem"]
    y = df[y_var]
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
        norm=MidpointNormalize(vmin=0, midpoint=0.5),
        clim=(-1, 1),
    )
    ax.set_xlim([0, 1.05])
    ax.set_ylim([0, max(y) + max(y) * 0.2])
    ax.xaxis.set_major_formatter(mtick.PercentFormatter(1.0))

    # ax.set_ylim([-0.02, 1.02])
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
        if yi >= 0:
            ax.annotate(labeli, xy=(xi, yi))

    hfont = {"fontname": "DejaVu Sans"}

    # ax.set_xlabel("Total Detained", fontsize=16, **hfont)
    ax.set_xlabel("Percent Dem Presidential Vote 2020", fontsize=16, **hfont)
    ax.set_ylabel(
        "Combined Score -- Immigration, Deaths, Low-Level Arrests", fontsize=16, **hfont
    )
    plt.title(f"Counties -- {state}", fontsize=22, **hfont)
    if state == "Nationwide":
        plt.text(
            0.5,
            0.99,
            f"{year}",  # f"Elections in {year} and {detained_num}+ detentions",
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
            f"../findings/2021/{state}--combined_metrics.html"
            # fig, f"../findings/elex_19_20/{year}/elections_{year}_counties_{state}.html"
        )
    return mpld3.display()
