import pandas as pd
from pandas import merge
from .indices_utils import get_next, get_previous
import math

def subset_by_dataframe(df, df_subset, on, sub_on=None, keep_cols=[], remove:bool=False):
    """Return rows of dataframe df that are present in dfSubset

    Parameters
    ----------
    df : DataFrame
        DataFrame to subset
    df_subset : DataFrame
        DataFrame used to define the subset
    on : list of Strings
        Column names to join on. These must be found in both DataFrames if sub_on is None.
    sub_on : list of Strings
        Column names to join on in the dfSubset DataFrame.
    keep_cols : list of Strings
        columns of dfSubset that should be kept in resulting DataFrame
    remove : boolean
        if true, rows of df matching with dfSubset will be removed.
        if false, only rows of df matching with a row of dfSubset will be kept
    Returns
    -------
    DataFrame
        subset of df

    """
    if sub_on is None:
        sub_on=on
        rem_cols=[]
    else:
        assert len(sub_on)==len(on), "sub_on should have same length as on"
        rem_cols = [c+'_y' for c in sub_on if not c in on]
    if len(keep_cols)==0:
        subcols = sub_on
    else:
        subcols = sub_on + keep_cols
    df_subset = df_subset[subcols].drop_duplicates()
    if not remove:
        res = merge(df, df_subset, how='inner', left_on=on, right_on=sub_on, suffixes=('', '_y'))
    else:
        res = merge(df, df_subset, how='left', left_on=on, right_on=sub_on, suffixes=('', '_y'), indicator=True)
        res = res.query('_merge != "both"')
        rem_cols.append("_merge")
    if len(rem_cols)>0:
        res.drop(columns=rem_cols, inplace=True)
    return res

def map_columns(df, df2, columns, on, on2=None):
    """Return mapped columns from df2 with the index of df using on (resp. on2) columns to match rows

    Parameters
    ----------
    df : DataFrame
        DataFrame to subset
    df2 : DataFrame
        DataFrame used to define the subset
    columns : String or list of Strings
        column(s) of df2 to be returned
    on : list of Strings
        Column names to map df and df2. These must be found in both DataFrames if on2 is None.
    on2 : list of Strings
        Column names in the df2 DataFrame to be mapped to on columns in df.


    Returns
    -------
    DataFrame
        list of columns with rows

    """
    if on2 is None:
        on2=on
    if not isinstance(on2, list):
        on2 = [on2]
    if not isinstance(on, list):
        on = [on]
    assert len(on2)==len(on), "on2 should have same length as on"
    if not isinstance(columns, list):
        columns = [columns]
    subcols = on2 + columns
    df2 = df2[subcols].drop_duplicates()
    res = pd.merge(df[on], df2, how='left', left_on=on, right_on=on2)
    res.index = df.index
    if len(columns)==1:
        return res.loc[:,columns[0]]
    else:
        return [res.loc[:,c] for c in columns]

def merge_dataframes(df, df2, on, on2=None, columns_from_df2=None):
    """
    Merge two DataFrames based on specified columns and retain the index of the first DataFrame.

    Parameters:
    df (pd.DataFrame): The first DataFrame.
    df2 (pd.DataFrame): The second DataFrame.
    on (str or list): The column(s) in df to merge on.
    on2 (str or list, optional): The column(s) in df2 to merge on. Defaults to on if not provided.
    columns_from_df2 (list, optional): List of columns from df2 to include in the merged DataFrame.
                                       If None, all columns from df2 will be included.

    Returns:
    pd.DataFrame: The merged DataFrame with the index of df.
    """
    if on2 is None:
        on2 = on
    if not isinstance(on2, list):
        on2 = [on2]
    if not isinstance(on, list):
        on = [on]
    assert len(on2) == len(on), "on2 should have the same length as on"
    if columns_from_df2 is None:
        columns_from_df2 = df2.columns.tolist()
    for on2_el in on2:
        if on2_el not in columns_from_df2:
            columns_from_df2.append(on2_el)
    df2 = df2[columns_from_df2]
    df2 = df2.drop_duplicates(subset=on2) # otherwise len(merged_df.index) != len(df.index)
    merged_df = pd.merge(df, df2, left_on=on, right_on=on2, how='left', suffixes=(None, '_df2'))
    cols_to_drop = [f"{col}_df2" for col in on2 if col not in on]
    cols_to_drop = [col for col in cols_to_drop if col in merged_df.columns.tolist()]
    if len(cols_to_drop)>0:
        merged_df.drop(columns=cols_to_drop, inplace=True)
    merged_df.index = df.index

    return merged_df

def set_selection_edges(dfSelection, left=True):
    """Create a boolean column that defines the edge of the selection (in terms of Frames). If left=True: value is True when there is no previous object. If left = false, value is True when there is no next object

    Parameters
    ----------
    dfSelection : DataFrame
        dataframe with a column SelectionName, Position & Indices
    left : boolean
        see summary

    Returns
    -------
    void
        inplace modification of dfSelection

    """
    colName = "LeftEdge" if left else "RightEdge"
    fun = get_next if left else get_previous
    dfNeigh = pd.DataFrame({"SelectionName":dfSelection.SelectionName, "Position":dfSelection.Position, "Indices":dfSelection.Indices.apply(fun)})
    leftEdges = pd.concat([dfSelection[["SelectionName", "Position", "Indices"]], dfNeigh, dfNeigh]).drop_duplicates(keep=False)
    dfSelection[colName] = False
    dfSelection.loc[leftEdges.index, colName] = True

def group_plot(groupedData, plotFun, xlabel=None, ylabel=None, ncols=4, figsize=(12, 4)):
    import matplotlib.pyplot as plt
    """Short summary.

    Parameters
    ----------
    groupedData : grouped dataframe
        Description of parameter `groupedData`.
    plotFun : function
        inputs : group and pyplot axe and plot graph on the axe
    xlabel : type
        Description of parameter `xlabel`.
    ylabel : type
        Description of parameter `ylabel`.
    ncols : type
        Description of parameter `ncols`.
    figsize : type
        Description of parameter `figsize`.

    Returns
    -------
    groupPlot(groupedData, plotFun, xlabel=None, ylabel=None, ncols=4,
        Description of returned object.

    """
    ncols=min(ncols, groupedData.ngroups)
    nrows = int(math.ceil(groupedData.ngroups/ncols))
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=figsize, sharex=True, sharey=True)
    if ncols>1 or nrows>1:
        axflat =  axes.flatten()
    else:
        axflat = [axes]
    for (key, ax) in zip(groupedData.groups.keys(),axflat):
        data = groupedData.get_group(key)
        plotFun(data, ax)
        ax.set_title(key)
    ax.legend()
    if xlabel:
        fig.text(0.5, 0.02, xlabel, ha='center')
    if ylabel:
        fig.text(0.08, 0.5, ylabel, va='center', rotation='vertical')
    return fig, axes
