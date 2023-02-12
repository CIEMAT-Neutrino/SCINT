# ---------------------------------------------------------------------------------------------------------------------- #
#  ======================================== RUN:$ python3 06Deconvolution.py TEST ====================================== #
# This macro will    #
# Ideally we want to work in /pnfs/ciemat.es/data/neutrinos/FOLDER and so we mount the folder in our computer with:      #
# $ sshfs USER@pcaeXYZ.ciemat.es:/pnfs/ciemat.es/data/neutrinos/FOLDER ../data  --> making sure empty data folder exists #
# ---------------------------------------------------------------------------------------------------------------------- #

import sys; sys.path.insert(0, '../'); from lib import *; print_header()

try:
    input_file = sys.argv[1]
except IndexError:
    input_file = input("Please select input File: ")

info = read_input_file(input_file)
channels = []
raw_runs = np.asarray(info["ALPHA_RUNS"]).astype(int)
dec_runs = np.asarray(info["LIGHT_RUNS"]).astype(int)
ref_runs = np.asarray(info["CALIB_RUNS"]).astype(int)

ana_ch = np.asarray(info["CHAN_TOTAL"]).astype(int)

my_runs =     load_npy(raw_runs,ana_ch,preset="CUTS",info=info,compressed=True) # Select runs to be deconvolved (tipichaly alpha)   
# my_runs =     load_npy(raw_runs,ana_ch,preset="ANA",info=info,compressed=True) # Activate in case deconvolution of ADC wvfs   
light_runs =  load_npy(dec_runs,ana_ch,preset="CUTS",info=info,compressed=True) # Select runs to serve as dec template (tipichaly light)    
single_runs = load_npy(ref_runs,ana_ch,preset="CUTS",info=info,compressed=True) # Select runs to serve as dec template scaling (tipichaly SPE)   

keys = ["AveWvf","SER","AveWvf"] # keys contains the 3 labels required for deconvolution keys[0] = raw, keys[1] = det_response and keys[2] = deconvolution 

for ii in range(len(my_runs["NRun"])):
    for jj in range(len(my_runs["NChannel"])):
        det_response =    light_runs[light_runs["NRun"][ii]][ana_ch[jj]]["AveWvf"][0]
        single_response = single_runs[single_runs["NRun"][ii]][ana_ch[jj]]["AveWvfSPE"][0]
        SER = np.max(single_response)*det_response/np.max(det_response)
        i_idx,f_idx = find_amp_decrease(SER, 1e-4)
        SER = np.roll(SER,-i_idx)
        my_runs[my_runs["NRun"][ii]][my_runs["NChannel"][jj]]["SER"] = [SER]

# plt.plot(np.arange(0,len(my_runs[25][0]["SER"][0]),1),my_runs[25][0]["SER"][0])
# plt.show()

OPT = {
    "NOISE_AMP": 1,
    "FIX_EXP":True,
    "LOGY":True,
    "NORM":False,
    "FOCUS":False,
    "SHOW": True,
    "SHOW_F_SIGNAL":True,
    "SHOW_F_GSIGNAL":True,
    "SHOW_F_DET_RESPONSE":True,
    "SHOW_F_GAUSS":True,
    "SHOW_F_WIENER":True,
    "SHOW_F_DEC":True,
    "AUTO_TRIMM":False,
    "WIENER_BUFFER": 800,
    "THRLD": 1e-4,
    "CONVERT_ADC": False
    }

deconvolve(my_runs,keys=keys,OPT=OPT)
save_proccesed_variables(my_runs,branch_list=["SER",keys[2]],info=info,force=True)