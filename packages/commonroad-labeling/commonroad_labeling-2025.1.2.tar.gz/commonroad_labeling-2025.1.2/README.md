# CommonRoad Automatic Scenario Labeling

[![PyPI pyversions](https://img.shields.io/pypi/pyversions/commonroad-labeling.svg)](https://pypi.python.org/pypi/commonroad-labeling/)
[![PyPI version fury.io](https://badge.fury.io/py/commonroad-labeling.svg)](https://pypi.python.org/pypi/commonroad-labeling/)
[![PyPI download week](https://img.shields.io/pypi/dw/commonroad-labeling.svg?label=PyPI%20downloads)](https://pypi.python.org/pypi/commonroad-labeling/)
[![PyPI download month](https://img.shields.io/pypi/dm/commonroad-labeling.svg?label=PyPI%20downloads)](https://pypi.python.org/pypi/commonroad-labeling/)
[![PyPI license](https://img.shields.io/pypi/l/commonroad-labeling.svg)](https://pypi.python.org/pypi/commonroad-labeling/)

Automatically assign correct labels to CommonRoad scenarios and check whether existing tags are correct.

The full documentation of the API and introductory examples can be found at [cps.pages.gitlab.lrz.de/commonroad/automatic-scenario-labeling](https://cps.pages.gitlab.lrz.de/commonroad/automatic-scenario-labeling).

## Quick Start

### Installation

```sh
$ pip install commonroad-labeling
```

### Usage Example

```python
from pathlib import Path

from commonroad_labeling.common.general import get_detected_tags_by_file

# specify a directory and detect tags
tags_by_file = get_detected_tags_by_file(Path.cwd().joinpath("path", "to", "directory"))
```

## Sketched Functionality
1. Load scenario using commonroad-io.
2. Read all currently assigned scenario tags.
3. Determine which tags are correct.
   1. Using formalized rules.
   2. Using traffic rule monitor.
   3. Using criticality metrics.
4. Check whether the tags are consistent with the previously assigned tags. → Warning if necessary
5. Overwrite scenario with corrected tags.
