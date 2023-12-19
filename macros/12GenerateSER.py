import sys; sys.path.insert(0, '../'); from lib import *
user_input, info = initialize_macro("12GenerateSER",["input_file","debug"],default_dict={}, debug=True)
### Load runs
my_runs     = load_npy([76], [6,7], preset="WVF", info=info, compressed=True, debug=user_input["debug"])  # Select runs to be deconvolved (tipichaly alpha)     
light_runs  = load_npy([62], [6,7], preset="WVF", info=info, compressed=True, debug=user_input["debug"]) # Select runs to serve as dec template (tipichaly light)    
single_runs = load_npy([2],  [6,7], preset="WVF", info=info, compressed=True, debug=user_input["debug"]) # Select runs to serve as dec template scaling (tipichaly SPE)
generate_SER(my_runs, light_runs, single_runs, debug=user_input["debug"])
### Remove branches to exclude from saving
save_proccesed_variables(my_runs, preset="WVF", info=info, force=True, debug=user_input["debug"])
del my_runs
gc.collect()