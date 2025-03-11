from src.utils import get_project_root

import glob
import inquirer
import numpy as np

from itertools import product
from rich import print as print

from lib.io_functions import read_yaml_file

root = get_project_root()


def calibrate_charges(my_runs, info, user_input, debug=False):
    # Check if the calibration file exists
    if glob.glob(f'{root}/{info["OUT_PATH"][0]}/analysis/calibration.yml') != []:
        calibration_info = read_yaml_file(
        "calibration",
        path=f'{root}/{info["OUT_PATH"][0]}/analysis/',
        debug=user_input["debug"],
        )

        print("Calibration info: ", calibration_info)
        for run, ch in product(
            np.asarray(user_input["runs"]).astype(str),
            np.asarray(user_input["channels"]).astype(str),
        ):
            q = [
                inquirer.List(
                    "OV",
                    message=f"select gain value according to run {run} - ch {ch}",
                    choices=calibration_info[my_runs[run][ch]["Label"]].keys(),
                    default="MidOV",
                )
            ]
            ov_gain = inquirer.prompt(q)["OV"]
            variables = list(my_runs[run][ch].keys())
            for var in variables:
                if "Charge" in var and "Dict" not in var:
                    my_runs[run][ch][var + "PE"] = (
                        my_runs[run][ch][var]
                        / calibration_info[my_runs[run][ch]["Label"]][ov_gain]
                    )
    else:
        print("\n[red][ERROR] Calibration file not found, change VisConfig.yml PE settings to [/red]False!\n")

    return my_runs
