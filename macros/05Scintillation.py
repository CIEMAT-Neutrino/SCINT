import sys; sys.path.insert(0, '../'); from lib import *

default_dict = {"runs":["ALPHA_RUNS"],"channels":["CHAN_TOTAL"]}
user_input, info = initialize_macro("05Scintillation",["input_file","preset_load","variables","filter","group","save","debug"],default_dict=default_dict, debug=True)
OPT = opt_selector(debug=user_input["debug"])
## 05Scintillation
my_runs = load_npy(np.asarray(user_input["runs"]).astype(str),np.asarray(user_input["channels"]).astype(str), info, preset=info["LOAD_PRESET"][4], compressed=True, debug=user_input["debug"])
my_runs = calibrate_charges(my_runs, info, user_input, debug=user_input["debug"])
if user_input["group"]: my_runs = group_selector(my_runs, remove = True, operation = "add", debug = user_input["debug"])
get_units(my_runs, debug = user_input["debug"])
label, my_runs = cut_selector(my_runs, user_input)

for run, ch, variable in product(np.asarray(my_runs["NRun"]).astype(str),np.asarray(my_runs["NChannel"]).astype(str),np.asarray(user_input["variables"])):
    data = np.asarray(my_runs[run][ch][variable]) 
    # Percentile cut
    ypbot = np.percentile(data, OPT["PERCENTILE"][0])
    yptop = np.percentile(data, OPT["PERCENTILE"][1])
    data = data[(data >= ypbot) & (data <= yptop)]
    
    # Data histogram and fit 
    hist, bins = np.histogram(data,bins=OPT["ACCURACY"])
    xdata = bins[:-1]+(bins[1]-bins[0])/2

    # Return fit and ydata normalized according to fit    
    m_fit, ydata = minuit_fit(info, data=data, ydata=hist, xdata=xdata, function=OPT["FIT"], debug=user_input["debug"])
    
    # Plotting
    style_selector(OPT)
    fig, ax = plt.subplots(1,1, figsize = (8,6)); add_grid(ax)
    plt.title("{} Fit".format(variable))
    plt.xlabel(variable+" ("+my_runs[run][ch]["UnitsDict"][variable]+")")
    plt.ylabel("Norm Counts")

    # Plotting the fit curve using the parameters obtained from fit_selector
    y_fit, ycov = propagate(lambda p: fitting_function(OPT["FIT"], debug=False)(xdata,  *p), m_fit.values, m_fit.covariance)

    colors = get_prism_colors()
    plt.hist(xdata, xdata, weights=ydata, label="run {} ch {}".format(run,ch), histtype="step", align="left", color = colors[6])
    plt.hist(xdata, xdata, weights=y_fit, label="{} fit".format(OPT["FIT"]), histtype="step", align="left", color = "red")

    yerr = np.sqrt(np.diag(ycov))
    plt.fill_between(xdata, (y_fit - yerr), (y_fit + yerr), alpha=0.2, color=colors[7])

    legend = [ f"${m_fit.parameters[m]} = {value:.2f} \pm {m_fit.errors[m]:.2f}$\n" for m,value in enumerate(m_fit.values) ]
    legend.append(r'$\chi^2$ = %.2f'%(m_fit.fval))
    plt.legend(frameon=False, title=' '.join(legend))
    # Increase font size of legend
    plt.setp(ax.get_legend().get_texts(), fontsize='14')   
    plt.show()
    if user_input["save"]: 
        fig.savefig('{}{}/images/run{}_ch{}_{}_Fit.png'.format(info["PATH"][0],info["MONTH"][0],run,ch,'_'.join([variable])), dpi = 500)
        try:
            os.chmod('{}{}/images/run{}_ch{}_{}_Fit.png'.format(info["PATH"][0],info["MONTH"][0],run,ch,'_'.join([variable])), 0o777)
        except:
            pass

        if user_input["debug"]: print("Saving plot in {}{}/images/run{}_ch{}_{}_{}_Fit.png".format(info["PATH"][0],info["MONTH"][0],run,ch,'_'.join([variable]),OPT["FIT"]))

    # Save fit parameters
    parameters = [[[m_fit.values[idx], m_fit.errors[idx]] for idx in range(len(m_fit.values))]]
    header = [m_fit.parameters[int(idx/2)].upper() if idx%2==0 else "D"+m_fit.parameters[int(idx/2)].upper() for idx in range(len(m_fit.values)*2)]
    write_output_file(run, ch, output=parameters, filename=OPT["FIT"]+variable, header_list=header, info=info, not_saved = [], debug=user_input["debug"])
    plt.close()
    