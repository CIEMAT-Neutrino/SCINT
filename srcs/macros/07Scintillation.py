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

OPT = opt_selector(arguments=["NORM", "COMPARE", "XLIM", "YLIM", "LOGX", "LOGY", "SHOW"], debug=user_input["debug"])
## 07Scintillation
my_runs = load_npy(
    np.asarray(user_input["runs"]).astype(str),
    np.asarray(user_input["channels"]).astype(str),
    info,
    preset=user_input["preset_load"][0],
    compressed=True,
    debug=user_input["debug"],
)

# parameters = {
# "type": "SiPM",
# "sigma":    1e-8,
# "a_fast":   1e-8,
# "a_slow":   1e-7,
# "tau_slow": 1e-6,
# "threshold":1e-6,
# "i_range":  2.5e-6,
# "f_range":  5.5e-6,
# }


# parameters = {
# "type": "TauSlow",
# "threshold":1e-6,
# "a_slow":   1e-7,
# "tau_slow": 1e-6,
# "i_range":  5.0e-6,
# "f_range":  7.0e-6,
# }

parameters = {
    "type": "Scint",
    "threshold":1e-6,
    "sigma":    1e-8,
    "a_fast":   1e-8,
    "tau_fast": 1e-9,
    "a_slow":   1e-7,
    "tau_slow": 1e-6,
    "i_range":  1e-7,
    "f_range":  2.0e-6,
}

ranges = (np.asarray([parameters["i_range"], parameters["f_range"]])/info["SAMPLING"][0]).astype(int)
variable = user_input["variables"][0]

fit, ref, popt, perr, labels = fit_wvfs(my_runs,info,parameters['type'],thrld=parameters['threshold'],fit_range=ranges,i_param=parameters,in_key=[variable], OPT=OPT, save=user_input['save'], debug=user_input["debug"])