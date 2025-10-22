from pathlib import Path

from commonroad_labeling.common.general import get_detected_tags_by_file

# specify a directory and detect tags
tags_by_file = get_detected_tags_by_file(Path.cwd().joinpath("..", "scenarios"))
