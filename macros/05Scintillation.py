import sys; sys.path.insert(0, '../'); from lib import *

default_dict = {"runs":["ALPHA_RUNS"],"channels":["CHAN_TOTAL"],"variables":["TYPE"]}
user_input, info = initialize_macro("05Scintillation",["input_file","load_preset","key","filter","debug"],default_dict=default_dict, debug=True)
OPT = opt_selector(debug=user_input["debug"])
## 05Scintillation
my_runs = load_npy(np.asarray(user_input["runs"]).astype(int),np.asarray(user_input["channels"]).astype(int), info, preset=info["LOAD_PRESET"][4], compressed=True, debug=user_input["debug"])
popt_ch = []; pcov_ch = []; perr_ch = []; popt_nevt = []; pcov_nevt = []; perr_nevt = []
label, my_runs = cut_selector(my_runs, user_input)

for run, ch, key in product(np.asarray(user_input["runs"]).astype(int),np.asarray(user_input["channels"]).astype(int),np.asarray(user_input["key"])):
    data = np.asarray(my_runs[run][ch][key]) 
    R=[np.mean(data)-np.std(data)*3,np.mean(data)+np.std(data)*3]
    counts,bins= np.histogram(data,bins=OPT["ACCURACY"],range=R)
    xdata=bins[:-1]+(bins[1]-bins[0])/2
    ydata=counts
    fig, ax = plt.subplots(1,1, figsize = (8,6)); add_grid(ax)
    style_selector(OPT)
    plt.hist(data, bins=OPT["ACCURACY"], histtype="step", label="Data",range=R)
    # plt.scatter(xdata, ydata, label="Data", color="tab:blue", marker="o", s=10)
    m, y, yerr_prop = fit_selector(xdata=xdata,ydata=ydata,function=OPT["FIT"],debug=user_input["debug"])
    plt.plot(xdata, gaussian(xdata, *m.values), label="Fit")
    plt.legend()
    plt.legend(loc="upper right", frameon=False, 
               title=f"$\mu = {m.values[0]:.2f} \pm {m.errors[0]:.2f}$\n"
                f"$\sigma = {m.values[1]:.2f} \pm {m.errors[1]:.2f}$\n"
                f"$A = {m.values[2]:.2f} \pm {m.errors[2]:.2f}$\n"
                f'$\chi^2_n $ = {m.fval/m.ndof:.2f}',title_fontsize=8)
    plt.fill_between(xdata, y - yerr_prop*5, y + yerr_prop*5, alpha=0.2,color="tab:orange")
    plt.title("Run_{} Ch_{} - {} histogram".format(run,ch,key))
    # plt.xlabel(key+" ("+my_runs[run][ch]["UnitsDict"][key]+")"); plt.ylabel("Counts")
    plt.xlim([R[0]*0.97,R[1]*1.03])
    plt.show()


# popt, pcov, perr = charge_fit(my_runs, [user_input["key"][0].split("ADC")[0]+user_input["variables"][0]], OPT)
# popt_ch.append(popt); pcov_ch.append(pcov); perr_ch.append(perr)

# HAY QUE REVISAR ESTO
# counter = 0
# for run, ch in product(np.asarray(user_input["runs"]).astype(int),np.asarray(user_input["channels"]).astype(int)):
#     scintillation_txt(run, ch, popt[counter], pcov[counter], filename="pC", info=info) ## Charge parameters = mu,height,sigma,nevents ## 
#     counter += 1
    ###JSON --> mapa runes (posibilidad)