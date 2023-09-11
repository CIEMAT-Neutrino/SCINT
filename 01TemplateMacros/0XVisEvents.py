import sys; sys.path.insert(0, '../'); from lib import *
user_input = initialize_macro("0XVisEvents",["input_file","load_preset","key","runs","channels","cuts","debug"],default_dict={}, debug=True)
info = read_input_file(user_input["input_file"], debug=user_input["debug"])

OPT = opt_selector(debug=True)

### 0XVisEvent
my_runs = load_npy(np.asarray(user_input["runs"]).astype(int),np.asarray(user_input["channels"]).astype(int),preset=user_input["load_preset"][0],info=info,compressed=True) # preset could be RAW or ANA
label, my_runs = cut_selector(my_runs, user_input)
vis_npy(my_runs, user_input["key"],OPT=OPT) # Remember to change key accordingly (ADC or RawADC)