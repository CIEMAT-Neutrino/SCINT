import sys

sys.path.insert(0, "../../")
from lib import *

default_dict = {
    "input_file": ["TUTORIAL"],
    "runs": ["CALIB_RUNS"],
    "channels": ["CHAN_TOTAL"],
    "variables": ["TYPE"],
    "preset_load": {"LOAD_PRESET": 4},
    "preset_save": {"SAVE_PRESET": 4},
}
user_input, info = initialize_macro(
    "04Calibration",
    ["input_file", "variables", "filter", "save", "debug"],
    default_dict=default_dict,
    debug=True,
)
OPT = opt_selector(debug=user_input["debug"])
### 04Calibration
for run, ch in product(
    np.asarray(user_input["runs"]).astype(str),
    np.asarray(user_input["channels"]).astype(str),
):
    my_runs = load_npy(
        [run],
        [ch],
        info,
        preset=user_input["preset_load"][0],
        compressed=True,
        debug=user_input["debug"],
    )
    label, my_runs = cut_selector(my_runs, user_input)
    data = calibrate(
        my_runs,
        info,
        user_input["variables"],
        OPT,
        save=user_input["save"],
        debug=user_input["debug"],
    )
    save_proccesed_variables(
        my_runs,
        preset=user_input["preset_save"][0],
        info=info,
        force=True,
        debug=user_input["debug"],
    )
