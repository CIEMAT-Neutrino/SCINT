import sys; sys.path.insert(0, '../'); from lib import *

default_dict = {"runs":["ALPHA_RUNS"],"channels":["CHAN_TOTAL"]}
user_input, info = initialize_macro("05Scintillation",["input_file","preset_load","variables","filter","debug"],default_dict=default_dict, debug=True)
dat_config = read_yaml_file("DatConfig", path="./", debug=user_input["debug"])
OPT = opt_selector(debug=user_input["debug"])
## 05Scintillation
my_runs = load_npy(np.asarray(user_input["runs"]).astype(str),np.asarray(user_input["channels"]).astype(str), info, preset=info["LOAD_PRESET"][4], compressed=True, debug=user_input["debug"])
popt_ch = []; pcov_ch = []; perr_ch = []; popt_nevt = []; pcov_nevt = []; perr_nevt = []
label, my_runs = cut_selector(my_runs, user_input)

for run, ch, variable in product(np.asarray(user_input["runs"]).astype(str),np.asarray(user_input["channels"]).astype(str),np.asarray(user_input["variables"])):
    data = np.asarray(my_runs[run][ch][variable]) 
    # Percentile cut
    ypbot = np.percentile(data, dat_config["PERCENTILE"][0]); yptop = np.percentile(data, dat_config["PERCENTILE"][1])
    data = data[(data >= ypbot) & (data <= yptop)]
    
    # Data histogram and fit 
    ydata,bins = np.histogram(data,bins=OPT["ACCURACY"])
    xdata = bins[:-1]+(bins[1]-bins[0])/2
    m_fit = minuit_fit(xdata=data,function=OPT["FIT"],debug=user_input["debug"])

    # Plotting
    fig, ax = plt.subplots(1,1, figsize = (8,6)); add_grid(ax)
    plt.title("Run_{} Ch_{} - {} histogram".format(run,ch,variable))
    # plt.xlabel(variable+" ("+my_runs[run][ch]["UnitsDict"][variable]+")"); plt.ylabel("Counts")
    
    style_selector(OPT)
    # Plotting the fit curve using the parameters obtained from fit_selector
    y_fit, ycov = propagate(lambda p: fitting_functions(OPT["FIT"], debug=False)(xdata,  *p), m_fit.values, m_fit.covariance)
    yerr_prop = np.diag(ycov) ** 0.5

    plt.hist(xdata, xdata, weights=y_fit, label="Fit",color="tab:orange", histtype="step", align="left")
    ydata = np.max(y_fit) * ydata/np.max(ydata)
    plt.hist(xdata, xdata, weights=ydata, label="Data", color="tab:blue", histtype="step", align="left")
    plt.fill_between(xdata, (y_fit - yerr_prop), (y_fit + yerr_prop), alpha=0.2, color="tab:orange")

    legend = [ f"${m_fit.parameters[m]} = {value:.2f} \pm {m_fit.errors[m]:.2f}$\n" for m,value in enumerate(m_fit.values) ]
    legend.append(f'$\chi^2_n $ = {m_fit.fval/m_fit.ndof:.2f}')
    plt.legend()
    plt.legend(loc="upper right", frameon=False, title=' '.join(legend),title_fontsize=8)
    plt.show()