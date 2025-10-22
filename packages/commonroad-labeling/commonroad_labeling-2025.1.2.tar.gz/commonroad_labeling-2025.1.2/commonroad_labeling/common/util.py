from pathlib import Path

from commonroad_labeling.common.tag import TagEnum


def print_tags_by_file(tags_by_file: dict[Path, set[TagEnum] | None]):
    for path in tags_by_file.keys():
        print_scenario_tags(path, tags_by_file[path])


def print_scenario_tags(path: Path, tags: set[TagEnum] | None):
    print(
        ("{0:-<50}".format(path.name + ":  ") + "------ "),
        list(map(lambda tag: TagEnum(tag).value, tags))
        if tags is not None
        else "Error occurred while parsing CommonRoad XML file",
    )


def print_parsing_error(path: Path, exception: Exception):
    print(
        ("{0:-<50}".format(path.name + ":  ") + "------ "),
        "Error occurred while parsing CommonRoad XML file:",
        exception,
    )
