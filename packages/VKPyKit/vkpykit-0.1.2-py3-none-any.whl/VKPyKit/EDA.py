
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# class EDA:

# def __init__(self):
#     pass

"""
To plot simple EDA visualizations
"""
# function to plot stacked bar chart
def barplot_stacked(self, 
                    data : pd.DataFrame, 
                    predictor: str , 
                    target: str) -> None:
    """
    Print the category counts and plot a stacked bar chart
    data: dataframe \n
    predictor: independent variable \n
    target: target variable \n
    return: None
    """
    count = data[predictor].nunique()
    sorter = data[target].value_counts().index[-1]
    crosstab = pd.crosstab(data[predictor], data[target], margins=True).sort_values(
        by=sorter, ascending=False
    )
    print(crosstab)
    print("-" * 120)
    tab = pd.crosstab(data[predictor], data[target], normalize="index").sort_values(
        by=sorter, ascending=False
    )
    tab.plot(kind="bar", stacked=True, figsize=(count + 5, 6))
    plt.legend(
        loc="lower left", frameon=False,
    )
    plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
    plt.show()

# function to create labeled barplot
def barplot_labeled(
        self,
        data: pd.DataFrame, 
        feature: str, 
        percentages: bool =False, 
        category_levels : int =None):
    """
    Barplot with percentage at the top

    data: dataframe \n  
    feature: dataframe column \n
    perc: whether to display percentages instead of count (default is False) \n
    category_levels: displays the top n category levels (default is None, i.e., display all levels) \n
    return: None
    """

    total = len(data[feature])  # length of the column
    count = data[feature].nunique()
    if category_levels is None:
        plt.figure(figsize=(count + 2, 6))
    else:
        plt.figure(figsize=(category_levels + 2, 6))

    plt.xticks(rotation=90, fontsize=15)
    ax = sns.countplot(
        data=data,
        x=feature,
        palette="Paired",
        order=data[feature].value_counts().index[:category_levels] if category_levels else None,
    )

    for p in ax.patches:
        if percentages == True:
            label = "{:.1f}%".format(
                100 * p.get_height() / total
            )  # percentage of each class of the category
        else:
            label = p.get_height()  # count of each level of the category

        x = p.get_x() + p.get_width() / 2  # width of the plot
        y = p.get_height()  # height of the plot

        ax.annotate(
            label,
            (x, y),
            ha="center",
            va="center",
            size=12,
            xytext=(0, 5),
            textcoords="offset points",
        )  # annotate the percentage

    plt.show()  # show the plot

# function to plot a boxplot and a histogram along the same scale.
def histogram_boxplot(
        self,
        data : pd.DataFrame, 
        feature: str, 
        figsize : tuple[float, float] =(12, 7), 
        kde : bool = False, 
        bins : int = None) -> None:
    """
    Boxplot and histogram combined
    data: dataframe \n
    feature: dataframe column \n
    figsize: size of figure (default (12,7)) \n
    kde: whether to the show density curve (default False) \n
    bins: number of bins for histogram (default None) \n
    return: None
    """
    f2, (ax_box2, ax_hist2) = plt.subplots(
        nrows=2,  # Number of rows of the subplot grid= 2
        sharex=True,  # x-axis will be shared among all subplots
        gridspec_kw={"height_ratios": (0.25, 0.75)},
        figsize=figsize,
    )  # creating the 2 subplots
    sns.boxplot(
        data=data, x=feature, ax=ax_box2, showmeans=True, color="violet"
    )  # boxplot will be created and a star will indicate the mean value of the column
    sns.histplot(
        data=data, x=feature, kde=kde, ax=ax_hist2, bins=bins, palette="winter"
    ) if bins else sns.histplot(
        data=data, x=feature, kde=kde, ax=ax_hist2
    )  # For histogram
    ax_hist2.axvline(
        data[feature].mean(), color="green", linestyle="--"
    )  # Add mean to the histogram
    ax_hist2.axvline(
        data[feature].median(), color="black", linestyle="-"
    )  # Add median to the histogram`

    plt.show()