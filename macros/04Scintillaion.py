# ---------------------------------------------------------------------------------------------------------------------- #
#  ======================================== RUN:$ python3 04Scintillation.py TEST ====================================== #
# This macro will   #
# Ideally we want to work in /pnfs/ciemat.es/data/neutrinos/FOLDER and so we mount the folder in our computer with:      #
# $ sshfs USER@pcaeXYZ.ciemat.es:/pnfs/ciemat.es/data/neutrinos/FOLDER ../data  --> making sure empty data folder exists #
# ---------------------------------------------------------------------------------------------------------------------- #

import sys; sys.path.insert(0, '../')
from lib import *
print_header()

try:
    input_file = sys.argv[1]
except IndexError:
    input_file = input("Please select input File: ")

info = read_input_file(input_file)
runs = []; channels = []
runs = np.append(runs,info["ALPHA_RUNS"])
# runs = np.append(runs,info["MUONS_RUNS"])

channels = np.append(channels,info["CHAN_STNRD"])

for run, ch in product(runs.astype(int),channels.astype(int)):
    my_runs = load_npy([run],[ch], branch_list=["ADC","ChargeAveRange"], info=info,compressed=True)#preset="ANA"
    print_keys(my_runs)

    int_key = ["ChargeAveRange"]
    OPT = {
        "LOGY": False,
        "PRINT_KEYS":False,
        "SHOW": True
        }

    ## Integrated charge (scintillation runs) ##
    print("Run ", run, "Channel ", ch)
    popt, pcov, perr = charge_fit(my_runs,int_key,OPT)
    ## Charge parameters = mu,height,sigma,nevents ##
    scintillation_txt(run, ch, popt, pcov, filename="pC", info=info) #JSON --> mapa runes (posibilidad)
