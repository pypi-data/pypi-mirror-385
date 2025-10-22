import pandas as pd

def reduce_to_tracks(df, custom_agg=None):
    """

    Parameters
    ----------
    df pandas dataframe
    custom_agg: dict column : aggregation function or list of aggregation function

    Returns
    -------
    dataframe in which each row is a track, that correspond to rows of df aggregated by TrackHeadIndices for each Position, DatasetName
    """
    if 'TrackHeadIndices' not in df.columns:
        raise ValueError("TrackHeadIndices not in columns")
    # Default aggregation functions for tracking measurements
    agg_functions = {
        'Frame': ['min', 'max'],
        'TrackLength': 'first',
        'TrackObjectCount': 'first',
        'ParentTrackHeadIndices': 'first',
        'PositionIdx': 'first',
        'Time': 'first',
        'TrackErrorNext': 'max',  # True if any is True, False if all are False
        'TrackErrorPrev': 'max',  # True if any is True, False if all are False
        'NextDivisionFrame': 'first',
        'PreviousDivisionFrame' : 'first',
        'BacteriaLineage': 'first',
    }

    # Remove default aggregation columns that are not in the dataframe
    del_agg_cols = [agg_col for agg_col in agg_functions.keys() if agg_col not in df.columns]
    for del_agg_col in del_agg_cols:
        del agg_functions[del_agg_col]

    # Add custom aggregations if specified
    if custom_agg:
        agg_functions.update(custom_agg)
    else:
        custom_agg = {}

    # Add aggregation for other columns based on their data type, excluding custom_agg columns
    for col in df.columns:
        if col not in ['DatasetName', 'Position', 'Indices', 'TrackHeadIndices', 'Next', 'Prev', 'Idx'] and col not in agg_functions:
            if df[col].dtype == 'object':  # Assuming strings are of type 'object'
                agg_functions[col] = ['first', 'last']
            elif df[col].dtype == 'bool':
                agg_functions[col] = ['max', 'min']
            elif pd.api.types.is_numeric_dtype(df[col]):
                agg_functions[col] = ['mean', 'std']

    # Group by both TrackHeadIndices and Position, then aggregate
    group_cols = [col for col in ['DatasetName', 'Position', 'TrackHeadIndices'] if col in df.columns]
    track_df = df.groupby(group_cols).agg(agg_functions).reset_index()

    # Flatten the MultiIndex columns created by the aggregation
    track_df.columns = ['_'.join(col) if isinstance(col, tuple) else col for col in track_df.columns]

    # Rename columns to remove suffixes
    rename_cols =  { f"{c}_":c for c in group_cols }
    if 'Frame' in agg_functions:
        rename_cols['Frame_min'] = 'Frame'
        rename_cols['Frame_max'] = 'FrameLast'

    for c, agg in agg_functions.items():
        if isinstance(agg, str):
            rename_cols[f"{c}_{agg}"] = c
    track_df.rename(columns=rename_cols, inplace=True)

    return track_df
