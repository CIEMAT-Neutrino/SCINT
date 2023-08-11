import sys; sys.path.insert(0, '../'); from lib import *
user_input = initialize_macro("06Deconvolution",["input_file","debug"])
info = read_input_file(user_input["input_file"])

SiPM_OV  = 0 # Choose between OV value for SiPM in alpha run (0, 1 or 2)
raw_runs = np.asarray(info["ALPHA_RUNS"]).astype(int)
dec_runs = np.asarray(info["LIGHT_RUNS"]).astype(int)
ref_runs = np.asarray(info["CALIB_RUNS"]).astype(int)
noi_runs = np.asarray(info["NOISE_RUNS"]).astype(int)
ana_ch   = np.asarray(info["CHAN_TOTAL"]).astype(int)

for idx, run in enumerate(raw_runs):
    for jdx, ch in enumerate(ana_ch):
        my_runs = load_npy([run], [ch], preset=str(info["LOAD_PRESET"][6]), info=info, compressed=True, debug=user_input["debug"])  # Select runs to be deconvolved (tipichaly alpha)     
        
        if "SiPM" in str(my_runs[run][ch]["Label"]):
            light_runs =  load_npy([dec_runs[SiPM_OV]],[ch],preset="EVA",info=info,compressed=True) # Select runs to serve as dec template (tipichaly light)    
            single_runs = load_npy([ref_runs[SiPM_OV]],[ch],preset="EVA",info=info,compressed=True) # Select runs to serve as dec template scaling (tipichaly SPE)
            noise_runs = load_npy([noi_runs[SiPM_OV]],[ch],preset="ANA",info=info,compressed=True) # Select runs to serve as dec template scaling (tipichaly SPE)
        elif "SC" or "XA" in str(my_runs[run][ch]["Label"]):
            light_runs =  load_npy([dec_runs[idx]],[ch],preset="EVA",info=info,compressed=True) # Select runs to serve as dec template (tipichaly light)    
            single_runs = load_npy([ref_runs[idx]],[ch],preset="EVA",info=info,compressed=True) # Select runs to serve as dec template scaling (tipichaly SPE)
            noise_runs = load_npy([noi_runs[idx]],[ch],preset="ANA",info=info,compressed=True) # Select runs to serve as dec template scaling (tipichaly SPE)
        else:
            print("UNKNOWN DETECTOR LABEL!")
        
        keys = ["AveWvf","SER","AveWvf"] # keys contains the 3 labels required for deconvolution keys[0] = raw, keys[1] = det_response and keys[2] = deconvolution 
        # Entrada, deconvolucion, salida. That is: alpha wvf, SPE - Laser result (see in generate_SER to select type of wvf), name for dec wvf (Gauss + str) 
        generate_SER(my_runs, light_runs, single_runs, debug=user_input["debug"])
        # my_runs[run][ch]["GaussCutOff"] = 140 # El límite del limite de frecuencias
        OPT = {
            "NOISE_AMP": 1,
            "FIX_EXP":True,
            "FIXED_CUTOFF": False,
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
            "WIENER_BUFFER": 800,
            "THRLD": 1e-4
        }

        deconvolve(my_runs,keys=keys, noise_run=[], OPT=OPT, debug=user_input["debug"])

        OPT = {
            "SHOW": False,
            "FIXED_CUTOFF": True
        }

        keys[0] = "ADC"
        keys[2] = "ADC"
        deconvolve(my_runs,keys=keys,OPT=OPT, debug=user_input["debug"])

        save_proccesed_variables(my_runs,preset=str(info["SAVE_PRESET"][6]),info=info,force=True, debug=user_input["debug"])
        del my_runs,light_runs,single_runs

generate_input_file(user_input["input_file"],info,label="Gauss", debug=user_input["debug"])