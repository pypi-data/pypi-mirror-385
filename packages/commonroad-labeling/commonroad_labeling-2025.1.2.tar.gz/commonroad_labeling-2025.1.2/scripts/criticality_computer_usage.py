from pathlib import Path

from commonroad_crime.measure import (
    BTN,
    CI,
    CPI,
    DCE,
    DST,
    ET,
    HW,
    MSD,
    P_MC,
    PET,
    PF,
    PSD,
    SOI,
    STN,
    TET,
    THW,
    TIT,
    TTB,
    TTC,
    TTCE,
    TTK,
    TTR,
    TTS,
    TTZ,
    WTTC,
    WTTR,
    ALatReq,
    ALongReq,
    AReq,
    LatJ,
    LongJ,
    TTCStar,
)

from commonroad_labeling.criticality.computer.cm_computer import CMComputer

# Specify the metrics that should be computed
metrics = [
    ALatReq,
    ALongReq,
    AReq,
    DST,
    HW,
    TTCE,
    WTTR,
    MSD,
    PSD,
    BTN,
    CI,
    CPI,
    STN,
    LatJ,
    LongJ,
    PF,
    P_MC,
    ET,
    PET,
    TET,
    THW,
    TIT,
    TTB,
    TTC,
    TTCStar,
    TTK,
    TTR,
    TTS,
    TTZ,
    WTTC,
    SOI,
    DCE,
]

# Create CMComputer. If overwrite=False the CMs will not be computed for a scenario if a output file with the same
# name as the one that would be created already exists in the output location. This can be very useful when resuming
# a previously stopped computation, as computed data that was already saved will not be recomputed.
cm_computer = CMComputer(metrics, verbose=True, overwrite=False)
# Specifiy location of the CommonRoad scenario files
scenario_dir = Path.cwd().joinpath("..", "scenarios", "MONA", "MONA-West")

# Start the computation, it this case parallel computation is used.
# !!!WARNING!!!
# Be careful with increasing the process count. Depending on how man CMs are computed
# each process can use multiple GIGABYTES of RAM. Running out of RAM can cause your system to crash.
cm_computer.compute_parallel(
    str(scenario_dir.absolute()),
    process_count=3,
    output_dir=str(Path.cwd().joinpath("..", "output").absolute()),
)
