import sys

sys.path.insert(0, "../../")
from lib import *

default_dict = {
    "input_file": ["TUTORIAL"],
}

user_input, info = initialize_macro(
    "12GenerateSER",
    ["input_file", "runs", "channels", "save", "debug"],
    default_dict,
    debug=True,
)

### Configure SER
light_runs = ["00"]
calib_runs = ["00"]

OPT = opt_selector(arguments=["ALIGN", "SPACE_OUT", "NORM", "LIMITS", "XLIM", "YLIM", "ZLIM", "LOGZ"], debug=user_input["debug"])

### 12GenerateSER
for run in np.asarray(user_input["runs"]).astype(str):
    scint_runs = calib_runs + light_runs + [run]
    for ch in np.asarray(user_input["channels"]).astype(str):
        scint = load_npy(
            scint_runs,
            [ch],
            preset="WVF",
            info=info,
            compressed=True,
            debug=user_input["debug"],
        )  # Select runs to be deconvolved (tipichaly alpha)
        light = load_npy(
            light_runs,
            [ch],
            preset="WVF",
            info=info,
            compressed=True,
            debug=user_input["debug"],
        )  # Select runs to serve as dec template (tipichaly light)
        calib = load_npy(
            calib_runs,
            [ch],
            preset="WVF",
            info=info,
            compressed=True,
            debug=user_input["debug"],
        )  # Select runs to serve as dec template scaling (tipichaly SPE)
        generate_SER(scint, light, calib, debug=user_input["debug"])

        OPT["LOGY"] = True
        OPT["NORM"] = True
        keys_dict = {
            (run, ch): key
            for run, ch, key in zip(
                scint_runs, [ch] * 3, ["AnaAveWvfSPE", "AnaAveWvfSER", "AnaAveWvf"]
            )
        }
        vis_compare_wvf(
            scint,
            info,
            keys_dict,
            OPT=OPT,
            save=user_input["save"],
            debug=user_input["debug"],
        )

        ### Remove branches to exclude from saving
        save_proccesed_variables(
            scint,
            preset=None,
            branch_list=["AnaAveWvfSER"],
            info=info,
            force=True,
            debug=user_input["debug"],
        )
        del scint, light, calib
        gc.collect()
