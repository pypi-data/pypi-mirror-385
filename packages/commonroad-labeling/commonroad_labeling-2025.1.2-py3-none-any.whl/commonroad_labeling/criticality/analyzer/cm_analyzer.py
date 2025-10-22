import copy

import numpy as np
import pandas as pd
from commonroad_crime.measure import DCE, ET, HW, PET, THW, TTC, TTCE, TTK, TTR, TTZ, WTTC, WTTR, ALongReq, TTCStar
from sklearn.feature_selection import VarianceThreshold
from sklearn.preprocessing import MinMaxScaler

from commonroad_labeling.criticality.input_output.crime_output import ScenarioCriticalityData

# TODO Could be automatically checked like this, but not all CriMe metrics have individual monotonicity specified
#  (for example TTK, TTZ, WTTR) so manual review is safer until it is double checked that all metrics in CriMe have
#  correct monotonicity assigned
# for name, obj in inspect.getmembers(commonroad_crime.measure):
#     if inspect.isclass(obj) and issubclass(obj, CriMeBase) and obj.monotone == TypeMonotone.NEG:
#         print(name)
NEGATIVE_MONOTONE_METRICS = [
    ALongReq,
    DCE,
    HW,
    ET,
    PET,
    THW,
    TTC,
    TTCStar,
    TTCE,
    TTK,
    TTR,
    TTZ,
    WTTC,
    WTTR,
]

METADATA_COLUMN_NAMES = ["scenario_id", "ego_id", "timestep"]


def correlation_chooser(df, correlation_threshold: float, verbose=True):
    """
    Finds CMs that are highly correlated and removes one of them from the DataFrame.
    :param df: Input DataFrame that contains the data on which correlation-based feature selection is to be performed.
    :param correlation_threshold: The threshold for correlation above which columns will be considered highly correlated
        and may be dropped.
    :param verbose: When set to True, prints detailed information about which columns are being dropped and why.
    :return: A tuple containing the DataFrame after dropping the highly correlated columns and a list of the columns
        that were dropped.
    """
    if df.empty:
        raise ValueError

    correlation_matrix = df.corr().abs()
    # Select upper triangle of correlation matrix
    upper = correlation_matrix.where(np.triu(np.ones(correlation_matrix.shape), k=1).astype(bool))

    # Find features with correlation greater than correlation_threshold
    to_drop = []
    for column in upper.columns:
        correlated = upper[column] > correlation_threshold
        if any(correlated):
            if verbose:
                correlated_columns = correlated.index[correlated].tolist()
                print(
                    f"Dropping column '{column}' due to high correlation greater than {correlation_threshold} with "
                    f"columns: {correlated_columns}"
                )
            to_drop.append(column)

    # Create a copy of the dataframe without the columns to be dropped
    df_selected = df.drop(columns=to_drop)

    return df_selected, to_drop


def robustness_chooser(df, threshold, verbose=True):
    """
    Removes CMs from the DataFrame which have a ratio of valid values that is below the specified threshold.
    The values 0 and +/- inf are considered not valid.
    :param df: The original DataFrame to be processed.
    :param threshold: The robustness threshold value below which columns will be dropped.
    :param verbose: A boolean flag to indicate whether to print details of the columns being dropped. Default is True.
    :return: A tuple containing the modified DataFrame with less robust columns removed and a list of the dropped
        columns.
    """
    df_copy = df.copy()
    dropped_cols = []
    if threshold < 0 or threshold > 1 or df_copy.empty:
        raise ValueError
    for col in df_copy.columns:
        valid_count = df_copy[col].replace([0, np.inf, -np.inf], np.nan).notna().sum()
        robustness = valid_count / len(df_copy)
        if robustness < threshold:
            df_copy.drop(col, axis=1, inplace=True)
            dropped_cols.append(col)
            if verbose:
                print(
                    f"Column '{col}' has been dropped since robustness of {robustness} is below threshold "
                    f"of {threshold}"
                )
    return df_copy, dropped_cols


def variance_chooser(df, variance_threshold: float, verbose=True):
    """
    Removes CMs from the DataFrame which have a variance below or equal to the specified threshold.
    :param df: The input dataframe containing the features to be evaluated.
    :param variance_threshold: The variance threshold value below which features will be removed.
    :param verbose: A boolean flag to indicate whether to print the names of the removed features.
    :return: A tuple containing the dataframe with selected features and a list of removed feature names.
    """
    sel = VarianceThreshold(threshold=variance_threshold)
    sel.fit(df)
    selected_features_mask = sel.get_support()
    feature_names = df.columns

    # Get the names of the features that were removed
    removed_metrics = feature_names[~selected_features_mask]

    if verbose:
        print(
            f"The following metrics have been dropped since they did not meet the variance threshold"
            f" of {variance_threshold}: " + ", ".join(removed_metrics)
        )

    # Create a new dataframe with only the selected features
    df_selected = df.loc[:, selected_features_mask]

    return df_selected, list(removed_metrics)


def monotonicity_adjustment(df):
    """
    Adjusts CMs that have a negative monotonic relationship with criticality to have a positive relationship instead.
    :param df: DataFrame containing metrics where some columns may need monotonicity adjustment.
    :return: DataFrame where all CMs are now positively monotonic with criticality.
    """
    inverted_df = df.copy()
    contained_neg_scale_metric_names = [
        metric.measure_name for metric in NEGATIVE_MONOTONE_METRICS if metric.measure_name in inverted_df.columns
    ]
    inverted_df.loc[:, [metric for metric in contained_neg_scale_metric_names]] = (
        1 - inverted_df.loc[:, [metric for metric in contained_neg_scale_metric_names]]
    )
    return inverted_df


def choose_and_scale_metrics(
    df: pd.DataFrame,
    robustness_threshold: float,
    correlation_threshold: float,
    variance_threshold: float,
    verbose=True,
):
    """
    Applies feature selection (robustness, variance, correlation) and data preprocessing to the input DataFrame.
    :param df: DataFrame containing the dataset to be processed.
    :param robustness_threshold: Float value used as the threshold for dropping metrics based on robustness criteria.
    :param correlation_threshold: Float value used as the threshold for dropping metrics based on correlation criteria.
    :param variance_threshold: Float value used as the threshold for dropping metrics based on variance criteria.
    :param verbose: Boolean flag to indicate if detailed output should be printed during processing.
    :return: A tuple consisting of the processed DataFrame, a list of accepted metrics, and a list of dropped metrics.
    """
    df_no_metadata = df.drop(METADATA_COLUMN_NAMES, axis=1)

    df_dropped, rob_dropped_metrics = robustness_chooser(
        df_no_metadata, threshold=robustness_threshold, verbose=verbose
    )
    df_dropped = min_max_scale_df(df_dropped)
    df_dropped, var_dropped_metrics = variance_chooser(
        df_dropped, variance_threshold=variance_threshold, verbose=verbose
    )
    df_dropped, cor_dropped_metrics = correlation_chooser(df_dropped, correlation_threshold, verbose=verbose)

    df_metadata = df[METADATA_COLUMN_NAMES]

    dropped_metrics = rob_dropped_metrics + var_dropped_metrics + cor_dropped_metrics
    accepted_metrics = df_no_metadata.columns.difference(dropped_metrics)
    return (
        pd.concat([df_metadata, df_dropped], axis=1),
        accepted_metrics,
        dropped_metrics,
    )


def scale_metrics(df: pd.DataFrame):
    """
    Applies min-max scaling to the input DataFrame, ignoring metadata columns.
    :param df: Pandas DataFrame containing the data to be scaled. Expected to have specific columns defined in
        METADATA_COLUMN_NAMES.
    :return: A new DataFrame with metadata columns retained and the remaining columns scaled using Min-Max scaling.
    """
    df_no_metadata = df.drop(METADATA_COLUMN_NAMES, axis=1)
    df_scaled = min_max_scale_df(df_no_metadata)

    df_metadata = df[METADATA_COLUMN_NAMES]
    return pd.concat([df_metadata, df_scaled], axis=1)


def calculate_row_average(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates the average value of over all CMs at each timestep.
    :param df: A pandas DataFrame containing multiple rows of data, with at least a "timestep" column.
    :return: A DataFrame consisting of the original "timestep" column and an "average" column which
        contains the average value of each row of CM values, excluding the "timestep" column.
    """
    average = df.drop(columns=["timestep"]).mean(axis=1)
    result_df = pd.DataFrame({"timestep": df["timestep"], "average": average})
    return result_df


def find_max_average(df: pd.DataFrame) -> tuple:
    """
    Finds the maximum value of the "average" column.
    :param df: A pandas DataFrame containing at least two columns 'timestep' and 'average'.
    :return: A tuple containing the 'timestep' and the maximum 'average' value.
    """
    max_average_index = df["average"].idxmax()
    max_average_row = df.loc[max_average_index]
    max_average_pair = (max_average_row["timestep"], max_average_row["average"])
    return max_average_pair


def get_column_average(df: pd.DataFrame, column_name: str) -> float:
    """
    Gets the average value of the specified column.
    :param df: The DataFrame containing the data.
    :param column_name: The name of the column to calculate the average for.
    :return: The average value of the specified column.
    """
    return df[column_name].mean()


def add_percentile_column(df, column_name):
    """
    Adds a column with percentile values of the specified column to the input DataFrame.
    :param df: DataFrame to which the percentile column will be added.
    :param column_name: Name of the column in the DataFrame for which percentiles are to be calculated.
    :return: DataFrame with an additional column containing percentiles based on the specified column.
    """
    df[column_name + "_percentile"] = pd.qcut(df[column_name].rank(method="first"), q=100, labels=False) + 1
    return df


def filter_by_quantile(df, column_name, lower_quantile, upper_quantile):
    """
    Filters the input DataFrame to include only rows where the specified column's value is between the
        specified lower and upper quantiles.
    :param df: The DataFrame containing the data to be filtered.
    :param column_name: The name of the column on which to apply the quantile filter.
    :param lower_quantile: The lower quantile value used as the filter's lower bound
        (e.g., 0.25 for the 25th percentile).
    :param upper_quantile: The upper quantile value used as the filter's upper bound
        (e.g., 0.75 for the 75th percentile).
    :return: A DataFrame filtered to include only the rows where the specified column's value is between
        the specified lower and upper quantiles.
    """
    lower_bound = df[column_name].quantile(lower_quantile)
    upper_bound = df[column_name].quantile(upper_quantile)

    return df[(df[column_name] >= lower_bound) & (df[column_name] <= upper_bound)]


def analyze_criticality(
    crit_data_list: list[ScenarioCriticalityData],
    filter_metrics=True,
    robustness_threshold=0.1,
    correlation_threshold=0.8,
    variance_threshold=0.01,
    verbose=True,
):
    """
    Performs the full analysis of the input CriticalityData objects, including feature selection and data-preprocessing.
    :param crit_data_list: A list of ScenarioCriticalityData objects that contain the criticality data for different
        scenarios.
    :param filter_metrics: A boolean flag that indicates whether to filter metrics before proceeding with the analysis.
    :param robustness_threshold: The threshold value for filtering metrics based on robustness.
    :param correlation_threshold: The threshold value for filtering metrics based on correlation.
    :param variance_threshold: The threshold value for filtering metrics based on variance.
    :param verbose: A boolean flag to enable or disable verbose output during the analysis.
    :return: A tuple containing the following:
        - DataFrame with average criticality values for each scenario and ego pair, including percentiles.
        - DataFrame with the most dangerous timestep's average criticality for each scenario and ego pair,
            including percentiles.
        - List of accepted metrics after filtering, or None if metrics were not filtered.
    """

    df = crit_data_to_df(crit_data_list)

    if filter_metrics:
        scaled_df, accepted_metrics, dropped_metrics = choose_and_scale_metrics(
            df,
            robustness_threshold,
            correlation_threshold,
            variance_threshold,
            verbose=verbose,
        )
    else:
        scaled_df = scale_metrics(df)
        accepted_metrics = None

    scaled_and_inverted_df = monotonicity_adjustment(scaled_df)
    grouped_by_scenario = scaled_and_inverted_df.groupby(["scenario_id", "ego_id"])
    scenario_data_df = {
        group_name: group_df.drop(["scenario_id", "ego_id"], axis=1) for group_name, group_df in grouped_by_scenario
    }

    # Calculate average criticality value of each timestep
    scenario_timestep_averages = {keys: calculate_row_average(df) for keys, df in scenario_data_df.items()}

    # Find the timestep with the highest average criticality and safe its time and value
    most_dangerous_timesteps = {keys: find_max_average(df) for keys, df in scenario_timestep_averages.items()}
    # Calculate average crit over all timesteps of scenario and add column with percentiles
    scenario_averages = {keys: get_column_average(df, "average") for keys, df in scenario_timestep_averages.items()}
    scenario_average_list = [
        [scenario_id, ego_id, average_crit] for (scenario_id, ego_id), average_crit in scenario_averages.items()
    ]
    scenario_average_df = pd.DataFrame(scenario_average_list, columns=["scenario_id", "ego_id", "average_crit"])
    scenario_average_df["percentile"] = scenario_average_df["average_crit"].rank(pct=True)

    # Add column with percentiles for the data with each scenarios most dangerous timestep
    scenario_max_list = [
        [scenario_id, ego_id, timestep, average_crit]
        for (scenario_id, ego_id), (
            timestep,
            average_crit,
        ) in most_dangerous_timesteps.items()
    ]
    scenario_max_df = pd.DataFrame(scenario_max_list, columns=["scenario_id", "ego_id", "timestep", "average_crit"])
    scenario_max_df["percentile"] = scenario_max_df["average_crit"].rank(pct=True)

    return scenario_average_df, scenario_max_df, accepted_metrics


def crit_data_to_df(crit_data_list: list[ScenarioCriticalityData]) -> pd.DataFrame:
    """
    Converts ScenarioCriticalityData objects to a pandas DataFrame.
    :param crit_data_list: List of ScenarioCriticalityData objects containing criticality data.
    :return: A pandas DataFrame where each row represents criticality data for a specific
        scenario + ego vehicle combination and timestep.
    """
    criticality_dict_lists = []
    for scenario_data in crit_data_list:
        for timestep, crit_data in scenario_data.data.items():
            crit_data = copy.deepcopy(crit_data)

            crit_data["scenario_id"] = scenario_data.scenario_id
            crit_data["timestep"] = str(timestep)
            crit_data["ego_id"] = str(scenario_data.ego_id)
            criticality_dict_lists.append(crit_data)

    return pd.DataFrame(data=criticality_dict_lists)


def min_max_scale_df(df) -> pd.DataFrame:
    """
    Applies min-max scaling to the input DataFrame.
    :param df: The DataFrame to be min-max scaled. Can contain infinite values which will be replaced before scaling.
    :return: A new DataFrame with values scaled to the range [0, 1] using min-max scaling.
    """
    scaler = MinMaxScaler()
    normalized_df = df.copy()
    # Need to replace infinite values as they will become NaN after scaling otherwise
    for column in normalized_df.columns:
        # Check for positive infinity values and replace them with the non-infinite maximum of that column
        if (normalized_df[column] == np.inf).any():
            max_value = normalized_df[normalized_df[column] != np.inf][column].max()
            normalized_df[column] = normalized_df[column].replace(np.inf, max_value)

        # Check for negative infinity values and replace them with the non-infinite minimum of that colum
        if (normalized_df[column] == -np.inf).any():
            min_value = normalized_df[normalized_df[column] != -np.inf][column].min()
            normalized_df[column] = normalized_df[column].replace(-np.inf, min_value)
    normalized_df[normalized_df.columns] = scaler.fit_transform(normalized_df[normalized_df.columns])
    return normalized_df
