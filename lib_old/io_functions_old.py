
#  load_npy(runs, channels, prefix = "", in_path = "../data/raw/", debug = False):
#     """
#     Structure: run_dict[runs][channels][BRANCH] 
#     \n Loads the selected channels and runs, for simplicity, all runs must have the same number of channels
#     """

#     my_runs = dict()
#     my_runs["NRun"]     = runs
#     my_runs["NChannel"] = channels
#     # try: (aqúi había un try pero que no me cuadra la indentación, pero hará falta para el excetp de despu
#     for run in runs:
#         aux = dict()
#         for ch in channels:
#             try:    
#                 try:
#                     aux[ch] = np.load(in_path+prefix+"run"+str(run).zfill(2)+"_ch"+str(ch)+".npz",allow_pickle=True)["arr_0"]           
#                 except:    
#                     try:
#                         aux[ch] = np.load("../data/ana/Analysis_run"+str(run).zfill(2)+"_ch"+str(ch)+".npz",allow_pickle=True)["arr_0"]
#                         if debug: print("Selected file does not exist, loading default analysis run")
#                     except:
#                         aux[ch] = np.load("../data/raw/run"+str(run).zfill(2)+"_ch"+str(ch)+".npz",allow_pickle=True)["arr_0"]
#                         if debug: print("Selected file does not exist, loading raw run")
#                 my_runs[run] = aux

#                 print("\nLoaded %srun with keys:"%prefix,my_runs.keys())
#                 print("-----------------------------------------------")
#                 # print_keys(runs)
#             except FileNotFoundError:
#                 print("\nRun", run, ", channels" ,ch," --> NOT LOADED (FileNotFound)")
#     return my_runs


# SAVE:

            # try:
            #     for key in aux[run][ch]["RawFileKeys"]:
            #         del aux[run][ch][key]
            # except:
            #     if debug: print("Original raw branches have already been deleted for run %i ch %i"%(run,ch))

            # aux_path=out_path+prefix+"run"+str(run).zfill(2)+"_ch"+str(ch)+".npz"
            # np.save(aux_path,aux[run][ch])
            # print("Saved data in:", aux_path)
    # except KeyError: 
    #     return print("Empty dictionary. Not saved.")