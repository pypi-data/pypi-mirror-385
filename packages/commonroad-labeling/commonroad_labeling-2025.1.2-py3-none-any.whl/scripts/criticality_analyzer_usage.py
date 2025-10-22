from pathlib import Path

from commonroad_labeling.criticality.analyzer.cm_analyzer import (
    analyze_criticality,
    choose_and_scale_metrics,
    crit_data_to_df,
    filter_by_quantile,
)
from commonroad_labeling.criticality.input_output.crime_output import (
    parse_crime_output_dir_to_object,
    parse_crime_output_dirs_to_object,
)

# -----------------------------------------------------------------------------------------------------------
# Usage 1: You have a set of CriMe output files. Now you want to analyze the criticality of the scenarios and
# potentially find scenarios that have the desired criticality.
# -----------------------------------------------------------------------------------------------------------

# Specify the locations of the crime output files
path = str(Path.cwd().joinpath("output", "use_this", "urban").absolute())
path1 = str(Path.cwd().joinpath("output", "use_this", "east").absolute())
path2 = str(Path.cwd().joinpath("output", "use_this", "west").absolute())
path3 = str(Path.cwd().joinpath("output", "use_this", "merge").absolute())

# Parse the .xml files. There are methods to do this for multiple and single directories,
# as well as single files.
crit_data_list = parse_crime_output_dirs_to_object([path, path1, path2, path3])

# Analyze the parsed data. By default, different feature selection algorithms will be applied to eliminate features
# which contain little information. The thresholds for the filtering can be adjusted through the parameters.
# If all metrics in the CriMe output files are considered useful, the filtering can be disabled by the respective
# parameter.
scenario_average_df, scenario_max_df, used_metrics = analyze_criticality(crit_data_list, correlation_threshold=0.6)

# Now the data can be filtered to get a DataFrame of scenarios with the desired criticality.
# In this case the most critical 20% of scenarios are returned.
average_crit_quantile_result = filter_by_quantile(scenario_average_df, "average_crit", 0.8, 1)
max_crit_quantile_result = filter_by_quantile(scenario_max_df, "average_crit", 0.8, 1)

# -----------------------------------------------------------------------------------------------------------
# Usage 2: You have computed several Criticality Metrics for many scenarios using CriMe and want to find a
# smaller subset of metrics, eliminating metrics that contribute no to little information for the given
# scenarios.
# -----------------------------------------------------------------------------------------------------------

# Specify the locations of the crime output files
some_path = str(Path.cwd().joinpath("output", "use_this", "urban").absolute())

# Parse the .xml files.
crit_data_list2 = parse_crime_output_dir_to_object(some_path)
# Convert list to dataframe
crit_dataframe = crit_data_to_df(crit_data_list2)

# Get the list of accepted metrics by running this function while specifying the desired thresholds for the different
# feature selection steps
_, accepted_metrics, dropped_metrics = choose_and_scale_metrics(
    crit_dataframe,
    robustness_threshold=0.1,
    correlation_threshold=0.8,
    variance_threshold=0.01,
    verbose=True,
)
