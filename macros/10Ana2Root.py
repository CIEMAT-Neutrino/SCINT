import sys; sys.path.insert(0, '../'); from lib import *
default_dict = {"runs":["CALIB_RUNS","LIGHT_RUNS","ALPHA_RUNS","MUON_RUNS","NOISE_RUNS"],"channels":["CHAN_TOTAL"]}
user_input, info = initialize_macro("10Ana2Root",["input_file","variables","debug"],default_dict=default_dict, debug=True)
### 10Ana2Root
my_runs = load_npy(np.asarray(user_input["runs"]).astype(int), np.asarray(user_input["channels"]).astype(int), preset="EVA", info=info, compressed=True, debug=user_input["debug"])
delete_keys(my_runs, ["Label","NBinsWvf","TimeStamp","Sampling","PeakAmp","PedLim","ChargeRangeDict","AnaChargeRangeDict"])
root_df = npy2root(my_runs[user_input["runs"][0]][user_input["channels"][0]], debug=user_input["debug"])
root_df.Display().Print()

c1 = ROOT.TCanvas("c1","c1",800,600)
# cut_df = root_df.Filter("AnaChargeAveRange > 0")
histo = cut_df.Histo1D(user_input["variables"][0])
histo.Draw()

input("Press Enter to continue...")