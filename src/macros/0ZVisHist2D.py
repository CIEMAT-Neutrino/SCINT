import sys

sys.path.insert(0, "../../")
from lib import *

default_dict = {
    "input_file": ["TUTORIAL"],
}

user_input, info = initialize_macro(
    "0ZVisHist2D",
    ["input_file", "runs", "channels", "variables", "filter", "group", "save", "debug"],
    default_dict=default_dict,
    debug=True,
)
OPT = opt_selector(arguments=["COMPARE", "NORM", "LIMITS", "XLIM", "YLIM", "ZLIM", "LOGZ"], debug=user_input["debug"])

### 0ZVisHist2D
my_runs = load_npy(
    np.asarray(user_input["runs"]).astype(str),
    np.asarray(user_input["channels"]).astype(str),
    preset="EVA",
    info=info,
    compressed=True,
    debug=user_input["debug"],
)
print(my_runs.keys())
if user_input["group"]:
    my_runs = group_selector(my_runs)
label, my_runs = cut_selector(my_runs, user_input, debug=user_input["debug"])

vis_two_var_hist(
    my_runs,
    info,
    user_input["variables"],
    percentile=OPT["PERCENTILE"],
    select_range=False,
    OPT=OPT,
    save=user_input["save"],
    debug=user_input["debug"],
)
