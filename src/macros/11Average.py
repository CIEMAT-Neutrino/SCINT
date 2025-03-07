import sys

sys.path.insert(0, "../../")
from lib import *

default_dict = {
    "input_file": ["TUTORIAL"],
    "channels": ["CHAN_TOTAL"]
}

user_input, info = initialize_macro(
    "11Average",
    ["input_file", "runs", "preset_load", "filter", "debug"],
    default_dict=default_dict,
    debug=True,
)
### 11Average
my_runs = load_npy(
    np.asarray(user_input["runs"]).astype(str),
    np.asarray(user_input["channels"]).astype(str),
    info,
    preset=user_input["preset_load"][0],
    compressed=True,
    debug=user_input["debug"],
)
### Process
if user_input["preset_load"][0] == "ANA":
    if (
        check_key(my_runs[my_runs["NRun"][0]][my_runs["NChannel"][0]], "AnaADC")
        == False
    ):
        if not compute_ana_wvfs(my_runs, info=info, debug=user_input["debug"]):
            pass
    delete_keys(
        my_runs,
        [
            "RawADC",
            "RawPeakAmp",
            "RawPeakTime",
            "RawPedSTD",
            "RawPedMean",
            "RawPedMax",
            "RawPedMin",
            "RawPedLim",
        ],
    )
### Check if the run is empty
key, label = get_wvf_label(my_runs, "", "", debug=user_input["debug"])
if key == "" and label == "":
    pass
### Compute
cut_label, my_runs = cut_selector(my_runs, user_input)
average_wvfs(
    my_runs,
    info,
    key=key,
    label=label,
    cut_label="SPE",
    centering="NONE",
    debug=user_input["debug"],
)
### Remove branches to exclude from saving
save_proccesed_variables(
    my_runs, preset="WVF", info=info, force=True, debug=user_input["debug"]
)
del my_runs
gc.collect()
