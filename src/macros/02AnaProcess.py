import sys

sys.path.insert(0, "../../")
from lib import *

default_dict = {
    "input_file": ["TUTORIAL"],
    "runs": ["CALIB_RUNS", "LIGHT_RUNS", "ALPHA_RUNS", "MUONS_RUNS", "NOISE_RUNS"],
    "channels": ["CHAN_TOTAL"],
    "preset_load": {"LOAD_PRESET": 2},
    "preset_save": {"SAVE_PRESET": 2},
}
user_input, info = initialize_macro(
    "02AnaProcess", ["input_file", "debug"], default_dict=default_dict, debug=True
)
### 02AnaProcess
for run, ch in product(
    np.asarray(user_input["runs"]).astype(str),
    np.asarray(user_input["channels"]).astype(str),
):
    ### Load
    my_runs = load_npy(
        [run],
        [ch],
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
                continue
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
        continue
    ### Compute
    compute_peak_variables(
        my_runs, info=info, key=key, label=label, debug=user_input["debug"]
    )
    compute_pedestal_variables(
        my_runs, info=info, key=key, label=label, debug=user_input["debug"]
    )
    average_wvfs(
        my_runs,
        info=info,
        key=key,
        label=label,
        centering="NONE",
        debug=user_input["debug"],
    )
    average_wvfs(
        my_runs,
        info=info,
        key=key,
        label=label,
        centering="PEAK",
        debug=user_input["debug"],
    )
    compute_peak_RMS(
        my_runs, info=info, key=key, label=label, debug=user_input["debug"]
    )
    ### Remove branches to exclude from saving
    save_proccesed_variables(
        my_runs, preset=user_input["preset_save"][0], info=info, force=True
    )
    ### Free memory
    del my_runs
    gc.collect()
