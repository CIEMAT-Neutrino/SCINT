import sys

sys.path.insert(0, "../../")
from lib import *

user_input, info = initialize_macro(
    "0ZVisHist2D",
    ["input_file", "variables", "runs", "channels", "filter", "group", "save", "debug"],
    default_dict={},
    debug=True,
)
OPT = opt_selector(debug=user_input["debug"])
### 0ZVisHist2D
my_runs = load_npy(
    np.asarray(user_input["runs"]).astype(str),
    np.asarray(user_input["channels"]).astype(str),
    preset="EVA",
    info=info,
    compressed=True,
    debug=user_input["debug"],
)
if user_input["group"]:
    my_runs = group_selector(my_runs)
label, my_runs = cut_selector(my_runs, user_input, debug=user_input["debug"])
vis_two_var_hist(
    my_runs,
    info,
    user_input["variables"],
    OPT=OPT,
    percentile=[1, 99],
    select_range=False,
    save=user_input["save"],
    debug=user_input["debug"],
)
