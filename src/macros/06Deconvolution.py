import sys

sys.path.insert(0, "../../")
from lib import *

default_dict = {
    "input_file": ["TUTORIAL"],
    "preset_load": {"LOAD_PRESET": 6},
    "preset_save": {"SAVE_PRESET": 6}
    }

user_input, info = initialize_macro(
    "06Deconvolution",
    ["input_file", "runs", "channels", "debug"],
    default_dict=default_dict,
    debug=True,
)
# info = read_input_file(user_input["input_file"][0])
for run, ch in product(
    np.asarray(user_input["runs"]).astype(str),
    np.asarray(user_input["channels"]).astype(str),
):
    # 06Deconvolution
    my_runs = load_npy(
        [run],
        [ch],
        preset=user_input["preset_load"][0],
        info=info,
        compressed=True,
        debug=user_input["debug"],
    )  # Select runs to be deconvolved (tipichaly alpha)
    keys = [
        "AnaAveWvf",
        "AnaAveWvfSER",
        "AveWvf",
    ]  # keys contains the 3 labels required for deconvolution keys[0] = raw, keys[1] = det_response and keys[2] = deconvolution

    OPT = {
        "NOISE_AMP": 1,
        "FIX_EXP": True,
        "FIXED_CUTOFF": False,
        "LOGY": True,
        "NORM": False,
        "FOCUS": False,
        "SHOW": False,
        "SHOW_F_SIGNAL": True,
        "SHOW_F_GSIGNAL": True,
        "SHOW_F_DET_RESPONSE": True,
        "SHOW_F_GAUSS": True,
        "SHOW_F_WIENER": True,
        "SHOW_F_DEC": True,
        "WIENER_BUFFER": 800,
        "THRLD": 1e-4,
    }

    deconvolve(my_runs, info, keys=keys, noise_run=[], OPT=OPT, debug=user_input["debug"])

    OPT = {"SHOW": False, "FIXED_CUTOFF": True}

    keys[0] = "RawADC"
    keys[2] = "ADC"
    deconvolve(my_runs, keys=keys, OPT=OPT, debug=user_input["debug"])

    save_proccesed_variables(
        my_runs,
        preset=user_input["preset_save"][0],
        info=info,
        force=True,
        debug=user_input["debug"],
    )
    del my_runs
    gc.collect()

generate_input_file(
    user_input["input_file"], info, label="Gauss", debug=user_input["debug"]
)
