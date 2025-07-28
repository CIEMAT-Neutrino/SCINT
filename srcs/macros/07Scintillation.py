import sys

sys.path.insert(0, "../../")
from lib import *

default_dict = {
    "input_file": ["TUTORIAL"],
    "runs": ["ALPHA_RUNS"],
    "channels": ["CHAN_TOTAL"],
    "preset_load": {"LOAD_PRESET": 7},
}
user_input, info = initialize_macro(
    "07Scintillation",
    ["input_file", "variables", "save", "debug"],
    default_dict=default_dict,
    debug=True,
)

OPT = opt_selector(arguments=["SCINT_FIT", "CUT_THRESHOLD", "FILTER", "FILTER_SIGMA", "LOGX", "LOGY", "SHOW"], debug=user_input["debug"])
## 07Scintillation
my_runs = load_npy(
    np.asarray(user_input["runs"]).astype(str),
    np.asarray(user_input["channels"]).astype(str),
    info,
    preset=user_input["preset_load"][0],
    compressed=True,
    debug=user_input["debug"],
)

wvf_process = {
    "threshold":5e-6,
    "i_range":  2e-6,
    "f_range":  8e-6,
}

if OPT["SCINT_FIT"] == "SiPM":
    parameters = {
        "sigma":    1e-8,
        "a_fast":   1e-8,
        "a_slow":   1e-7,
        "tau_slow": 1e-6,
    }

elif OPT["SCINT_FIT"] == "TauFast":
    parameters = {
        "a_slow":   1e-7,
        "tau_slow": 1e-6,
    }

elif OPT["SCINT_FIT"] == "Scint":
    parameters = {
        "sigma":    1e-8,
        "a_fast":   1e-8,
        "tau_fast": 1e-9,
        "a_slow":   1e-7,
        "tau_slow": 1e-6,
    }

elif OPT["SCINT_FIT"] == "Quenching":
    parameters = {
        "PED":    1e-4,
        "A0":     1e-9,
        "A1":     1e-0,
        "SIGMA":  1e-8,
        "QUENCH": 1e6,
    }

ranges = (np.asarray([wvf_process["i_range"], wvf_process["f_range"]])/info["SAMPLING"][0]).astype(int)
variable = user_input["variables"][0]

fit, ref, popt, perr, labels = fit_wvfs(my_runs,info,OPT["SCINT_FIT"],thld=wvf_process['threshold'],fit_range=ranges,i_param=parameters,in_key=[variable], OPT=OPT, save=user_input['save'], debug=user_input["debug"])