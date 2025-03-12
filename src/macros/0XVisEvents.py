import sys

sys.path.insert(0, "../../")
from lib import *

default_dict = {
    "input_file": ["TUTORIAL"],
}

user_input, info = initialize_macro(
    "0XVisEvents",
    ["input_file", "preset_load", "key", "runs", "channels", "filter", "save", "debug"],
    default_dict=default_dict,
    debug=True,
)
OPT = opt_selector(arguments=["COMPARE", "ALIGN", "SPACE_OUT", "NORM", "LIMITS", "XLIM", "YLIM", "ZLIM", "LOGZ"], debug=user_input["debug"])
### 0XVisEvent
my_runs = load_npy(
    np.asarray(user_input["runs"]).astype(str),
    np.asarray(user_input["channels"]).astype(str),
    preset=user_input["preset_load"][0],
    info=info,
    compressed=True,
    debug=user_input["debug"],
)
label, my_runs = cut_selector(my_runs, user_input, debug=user_input["debug"])
vis_npy(
    my_runs,
    info,
    user_input["key"],
    OPT=OPT,
    save=user_input["save"],
    debug=user_input["debug"],
)  # Remember to change key accordingly (ADC or RawADC)
