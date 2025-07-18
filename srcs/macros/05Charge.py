import sys

sys.path.insert(0, "../../")
from lib import *

default_dict = {
    "input_file": ["TUTORIAL"],
    "runs": ["ALPHA_RUNS"],
    "channels": ["CHAN_TOTAL"],
    "preset_load": {"LOAD_PRESET": 4},
}
user_input, info = initialize_macro(
    "05Charge",
    ["input_file", "variables", "filter", "group", "export", "save", "debug"],
    default_dict=default_dict,
    debug=True,
)

OPT = opt_selector(arguments=["PE", "PERCENTILE", "FIT", "NORM", "LIMITS", "XLIM", "YLIM", "SHOW_LEGEND", "SHOW_FIT_PARAMETERS"], debug=user_input["debug"])
## 05Charge
my_runs = load_npy(
    np.asarray(user_input["runs"]).astype(str),
    np.asarray(user_input["channels"]).astype(str),
    info,
    preset=user_input["preset_load"][0],
    compressed=True,
    debug=user_input["debug"],
)
if check_key(OPT, "PE") and OPT["PE"]:
    my_runs = calibrate_charges(my_runs, info, user_input, debug=user_input["debug"])
    for var_idx, var in enumerate(user_input["variables"]):
        user_input["variables"][var_idx] = var + "PE"

if user_input["group"]:
    my_runs = group_selector(
        my_runs, remove=True, operation="add", debug=user_input["debug"]
    )
get_run_units(my_runs, debug=user_input["debug"])
label, my_runs = cut_selector(my_runs, user_input)

for run, ch, variable in product(
    np.asarray(my_runs["NRun"]).astype(str),
    np.asarray(my_runs["NChannel"]).astype(str),
    np.asarray(user_input["variables"]),
):
    data = np.asarray(my_runs[run][ch][variable])
    m_fit, xdata, ydata = minuit_fit(data, OPT, user_input["export"], user_input["debug"])
    plot_minuit_fit(m_fit, xdata, ydata, (run, ch, variable), user_input, info, OPT)
    if user_input["export"]:
        save_fit_parameters(run, ch, m_fit, OPT["FIT"], variable, info, user_input)
        export_minuit_fit(
            m_fit,
            xdata,
            ydata,
            (run, ch, variable),
            info,
            OPT,
            user_input["debug"],
        )

