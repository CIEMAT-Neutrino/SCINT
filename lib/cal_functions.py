#================================================================================================================================================#
# This library contains function to perform the calibration of our sensors. They are mostly used in the 04Calibration.py macro.                  #
#================================================================================================================================================#
from jacobi import propagate
import scipy, os, stat
import numpy             as np
import matplotlib.pyplot as plt
import pandas            as pd
from matplotlib.colors import LogNorm
from matplotlib.cm     import viridis
from itertools         import product
from rich              import print as print
from rich.table        import Table
from rich.console      import Console
from scipy.optimize    import curve_fit

# Import from other libraries
from .io_functions  import check_key, print_colored, write_output_file
from .ana_functions import generate_cut_array, get_units, get_wvf_label, compute_ana_wvfs
from .fig_config    import figure_features, add_grid
from .fit_functions import gaussian_train_fit, gaussian_train, pmt_spe_fit, gaussian_fit, gaussian, peak_valley_finder, PoissonPlusBinomial
from .vis_functions import vis_var_hist
from .sty_functions import style_selector, get_prism_colors


def vis_persistence(my_run, info, OPT, debug=False):
    '''
    \nThis function plot the PERSISTENCE histogram of the given runs&ch.
    \nIt perfoms a cut in 20<"PeakTime"(bins)<50 so that all the events not satisfying the condition are removed. 
    \nBinning is fixed (x=5000, y=1000) [study upgrade].
    \nX_data (time) and Y_data (waveforms) are deleted after the plot to save space.
    \n
    \nWARNING! flattening long arrays leads to MEMORY problems :/
    '''

    style_selector(OPT)
    plt.ion()
    true_key, true_label = get_wvf_label(my_run, "", "", debug=debug)
    if true_key == "RawADC":
        compute_ana_wvfs(my_run, info, debug=False)
        key = "AnaADC"
    else: key = true_key
    for run, ch in product(my_run["NRun"],my_run["NChannel"]):
        if check_key(my_run[run][ch], "MyCuts") == False: generate_cut_array(my_run, debug=debug)
        data_flatten = my_run[run][ch][true_key][np.where(my_run[run][ch]["MyCuts"] == True)].flatten() ##### Flatten the data array
        time = my_run[run][ch]["Sampling"]*np.arange(len(my_run[run][ch][true_key][0])) # Time array
        time_flatten = np.array([time] * int(len(data_flatten)/len(time))).flatten() 

        plt.hist2d(time_flatten,data_flatten,density=True,bins=[5000,1000], cmap = viridis, norm=LogNorm()) 

        plt.colorbar()
        plt.grid(True, alpha = 0.7) # , zorder = 0 for grid behind hist
        plt.title("Run_{} Ch_{} - Persistence".format(run,ch),size = 14)
        plt.xticks(size = 11); plt.yticks(size = 11)
        plt.xlabel("Time (s)", size = 11); plt.ylabel("Counts", size = 11)
        del data_flatten, time, time_flatten
        while not plt.waitforbuttonpress(-1): pass
        plt.clf()
    plt.ioff()
    plt.clf()

def calibrate(my_runs, info, keys, OPT={}, save = False, debug=False):
    '''
    \nComputes calibration hist of a collection of runs. A fit is performed (train of gaussians) and we have as 
    \na return the popt, pcov, perr for the best fitted parameters. Not only that but a plot is displayed.
    \n**VARIABLES:**
    \n- my_run: run(s) we want to check
    \n- keys: variables we want to plot as histograms. Type: List
    \n- OPT: several options that can be True or False. Type: List
      (a) LOGY: True if we want logarithmic y-axis
      (b) SHOW: if True, it will show the calibration plot
    '''

    style_selector(OPT)
    for run in my_runs["NRun"]:
        for ch in my_runs["NChannel"]:
            for key in keys:
                if len(my_runs[run][ch].keys()) == 0: 
                    print_colored("\n RUN DOES NOT EXIST. Looking for the next", "WARNING")
                    popt = [-99, -99, -99]; pcov= [-99, -99, -99]; perr = [-99, -99, -99]
                
                else: 
                    det_label = my_runs[run][ch]["Label"]
                    if check_key(my_runs[run][ch], "MyCuts") == False:
                        print_colored("Cuts not generated. Generating them now...", "WARNING")
                        generate_cut_array(my_runs,debug=debug) # If cuts not generated, generate them
                    
                    if check_key(my_runs[run][ch], "UnitsDict") == False: get_units(my_runs)          # Get units
                    
                    OPT["SHOW"] == False
                    counts, bins, bars = vis_var_hist(my_runs, info=info, key=[key], OPT=OPT, percentile = [1, 99])
                    counts = counts[0]; bins = bins[0]; bars = bars[0]

                    ## New Figure with the fit ##
                    plt.ion() 
                    plt.rcParams.update({'font.size': 16})
                    fig_cal, ax_cal = plt.subplots(1,1, figsize = (8,6))
                    ax_cal.hist(bins[:-1], bins, weights = counts, histtype = "step",label="Data", align="left")
                    fig_cal.suptitle("Run_{} Ch_{} - {} histogram".format(run,ch,key))
                    fig_cal.supxlabel(key+" ("+my_runs[run][ch]["UnitsDict"][key]+")"); fig_cal.supylabel("Counts")
                    add_grid(ax_cal)
                    
                    fig_xt, ax_xt = plt.subplots(1,1, figsize = (8,6))
                    fig_xt.suptitle("Run_{} Ch_{} - {} Vinogradov X-Talk".format(run,ch,key))
                    fig_xt.supxlabel("PE"); fig_xt.supylabel("Counts (density)")
                    add_grid(ax_xt)

                    #This if could be simplified!!!
                    if det_label != "PMT": #Fit for SiPMs/SC
                        new_params = {}
                        params = {"THRESHOLD": 0.1, "WIDTH": 5, "PROMINENCE": 0.01, "PEAK_DISTANCE":20, "ACCURACY": 1000, "FIT": "gaussian"}
                        for i,param in enumerate(list(params.keys())):
                            if check_key(OPT,param) == True: new_params[param] = OPT[param]
                            else:                            new_params[param] = params[param]

                        ## Create linear interpolation between bins to search peaks in these variables ##
                        x = np.linspace(bins[1],bins[-2],params["ACCURACY"])
                        y_intrp = scipy.interpolate.interp1d(bins[:-1],counts)
                        y = y_intrp(x)

                        peak_idx, valley_idx = peak_valley_finder(x, y, new_params)
                        ax_cal.axhline(np.max(y)*new_params["THRESHOLD"], ls='--')
                        ax_cal.plot(x[peak_idx], y[peak_idx], 'r.', lw=4, label="Peaks")
                        ax_cal.plot(x[valley_idx], y[valley_idx], 'b.', lw=6, label="Valleys")

                        popt, pcov = gaussian_train_fit(ax_cal, x=x, y=y, y_intrp=y_intrp, peak_idx=peak_idx, valley_idx=valley_idx, params=new_params, debug=debug)
                        ax_cal.plot(x,gaussian_train(x, *popt), label="Final fit", color=get_prism_colors()[4])
                        
                        # Prob is proportional to A*sigma (sqrt(2pi))
                        PNs=popt[1::3]*np.abs(popt[2::3])/sum(popt[1::3]*np.abs(popt[2::3]))
                        PNs_err=(popt[1::3]*np.abs(popt[2::3]))**0.5/sum(popt[1::3]*np.abs(popt[2::3]))

                        l=-np.log(PNs[0])
                        p=1-PNs[1]/(l*PNs[0])
                        xdata = np.arange(len(PNs))
                        ax_xt.bar(np.array(xdata),PNs,label="Data",width=0.4)
                        xt_popt, xt_pcov = curve_fit(PoissonPlusBinomial, xdata, PNs, sigma=PNs_err, p0=[len(PNs),p,l], bounds=([len(PNs)-1e-12,0,0],[len(PNs)+1e-12,1,10]))
                        ax_xt.plot(xdata, PoissonPlusBinomial(xdata, *xt_popt), 'x',label="Fit: CT = " +str(int(xt_popt[1]*100)) +"% - "+r'$\lambda = {:.2f}$'.format(xt_popt[2]),color="red")
                    
                    else: #Particular calibration fit for PMTs
                        print("Hello, we are working on a funtion to fit PMT spe :)")
                        thresh = int(len(my_runs[run][ch][key])/1e4)
                        x, y, peak_idx, valley_idx, popt, pcov, perr = pmt_spe_fit(counts, bins, bars, thresh)
                        ## Plot threshold, peaks (red) and valleys (blue) ##
                        ax_cal.axhline(thresh, ls='--')
                        ax_cal.plot(x[peak_idx], y[peak_idx], 'r.', lw=4)
                        ax_cal.plot(x[valley_idx], y[valley_idx], 'b.', lw=6)
                        ## Plot the fit ##
                        ax_cal.plot(x,gaussian_train(x, *popt), label="")

                    if check_key(OPT,"LEGEND") == True and OPT["LEGEND"] == True:
                        ax_cal.legend()
                        ax_xt.legend()
                    if check_key(OPT,"LOGY")   == True and OPT["LOGY"]   == True: 
                        ax_cal.semilogy()
                        ax_cal.set_ylim(1)
                    if check_key(OPT,"SHOW")   == True and OPT["SHOW"]   == True:
                        # print("SHOW BUT NO TERMINAL FRIEND")

                        if check_key(OPT, "TERMINAL_MODE") == True and OPT["TERMINAL_MODE"] == True:
                            # print("TERMINAL FRIEND")
                            plt.ion()
                            plt.show()
                            while not plt.waitforbuttonpress(-1): pass
                            # plt.close()
                    if save: 
                        # Increase the fontsize of the figures
                        fig_cal.savefig('{}{}/images/run{}_ch{}_{}_Hist.png'.format(info["PATH"][0],info["MONTH"][0],run,ch,'_'.join([key])), dpi = 500)
                        fig_xt.savefig('{}{}/images/run{}_ch{}_{}_XTalk.png'.format(info["PATH"][0],info["MONTH"][0],run,ch,'_'.join([key])), dpi = 500)
                        # Check if the file exists or give it permissions
                        try:
                            os.chmod('{}{}/images/run{}_ch{}_{}_Hist.png'.format(info["PATH"][0],info["MONTH"][0],run,ch,'_'.join([key])), stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
                            os.chmod('{}{}/images/run{}_ch{}_{}_XTalk.png'.format(info["PATH"][0],info["MONTH"][0],run,ch,'_'.join([key])), stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
                        except:
                            print("File permissions could not be changed. Check if the file exists & if you have permissions change them manually.")
                        
                        # Print the path of the saved file
                        if debug:
                            print("Saved figure as: run{}_ch{}_{}_Hist.png".format(run,ch,'_'.join([key])))
                            print("Saved figure as: run{}_ch{}_{}_XTalk.png".format(run,ch,'_'.join([key])))
                    
                    plt.close()
                    plt.close()

                    try:
                        my_runs[run][ch]["Gain"]         = popt[3] - abs(popt[0])
                        my_runs[run][ch]["MaxChargeSPE"] = popt[3] + abs(popt[5])
                        my_runs[run][ch]["MinChargeSPE"] = popt[3] - abs(popt[5])
                    
                    except IndexError:
                        print_colored("Fit failed to find min of 3 calibration peaks!", "WARNING")
                        my_runs[run][ch]["Gain"]         = -99
                        my_runs[run][ch]["MaxChargeSPE"] = -99
                        my_runs[run][ch]["MinChargeSPE"] = -99
    
    # if check_key(OPT, "TERMINAL_MODE") == True and OPT["TERMINAL_MODE"] == False: return fig_cal,ax_cal,popt, pcov, perr
    # else: 
    return popt, pcov, xt_popt, xt_pcov

def calibration_txt(run, ch, popt, pcov, xt_popt, xt_pcov, info, debug = False):
    '''
    \nComputes calibration parameters for each peak.
    \nGiven popt and pcov which are the output for the best parameters when performing the Gaussian fit.
    \nIt returns an array of arrays: 
    \nsave_calibration = [ [[mu,dmu],[height,dheight],[height,dheight],[sigma,dsigma],
    \n[gain,dgain],[sn0,dsn0],[sn1,dsn1],[sn2,dsn2]], [PEAK 1], [PEAK 2],...]
    \nSave in a txt the calibration parameters to be exported directly.
    \nTakes as input an array of arrays with the computed parameters (see compute_cal_parameters())
    '''
    if all(x !=-99 for x in popt):
        cal_parameters = []
        xt_parameters = []
        perr = np.sqrt(np.diag(pcov))          #error for each variable
        xt_perr = np.sqrt(np.diag(xt_pcov))    #error for each variable
        fitted_peaks = int(len(popt)/3)  #three parameters fitted for each peak
        for i in np.arange(fitted_peaks): 
            mu     = [popt[(i+0)+2*i], perr[(i+0)+2*i]]  # mu +- dmu
            height = [popt[(i+1)+2*i], perr[(i+1)+2*i]]  # height +- dheight (not saving in txt by default)
            sigma  = [popt[(i+2)+2*i], perr[(i+2)+2*i]]  # sigma +- dsigma
            cal_parameters.append([mu,height,sigma])
            copy_cal = cal_parameters
        
        npeaks = [xt_popt[0], xt_perr[0]]
        xt = [xt_popt[1], xt_perr[1]]
        l  = [xt_popt[2], xt_perr[2]]
        xt_parameters.append([npeaks,xt,l])

        for i in np.arange(fitted_peaks): #distances between peaks
            if i == fitted_peaks-1: gain = -99; dgain = -99; sn0 = -99; dsn0 = -99; sn1 = -99; dsn1 = -99; sn2 = -99; dsn2 = -99
            else:
                gain  = (copy_cal[i+1][0][0]-copy_cal[i][0][0]);
                dgain = (np.sqrt(copy_cal[i+1][0][1]**2+copy_cal[i][0][1]**2)) #*1e-12/1.602e-19 #when everythong was pC
                
                sn0 = (copy_cal[i+1][0][0]-copy_cal[i][0][0])/copy_cal[i][2][0]
                dsn0 = sn0 * np.sqrt(((copy_cal[i+1][0][1]**2+copy_cal[i][0][1]**2)/((copy_cal[i+1][0][0]-copy_cal[i][0][0])))**2+(copy_cal[i][2][1]/copy_cal[i][2][0])**2)
                
                sn1 = (copy_cal[i+1][0][0]-copy_cal[i][0][0])/copy_cal[i+1][2][0]
                dsn1 = sn1 * np.sqrt(((copy_cal[i+1][0][1]**2+copy_cal[i][0][1]**2)/((copy_cal[i+1][0][0]-copy_cal[i][0][0]))**2)+(copy_cal[i+1][2][1]/copy_cal[i+1][2][0])**2)
                
                sn2 = (copy_cal[i+1][0][0]-copy_cal[i][0][0])/(np.sqrt(copy_cal[i][2][0]**2+copy_cal[i+1][2][0]**2))
                dsn2 = sn2 * np.sqrt((dgain/gain)**2+((copy_cal[i][2][0]*copy_cal[i][2][1])/((copy_cal[i][2][0])**2+(copy_cal[i+1][2][0])**2))**2+((copy_cal[i+1][2][0]*copy_cal[i+1][2][1])/((copy_cal[i][2][0])**2+(copy_cal[i+1][2][0])**2))**2)

            cal_parameters[i].append([gain, dgain]) 
            cal_parameters[i].append([sn0, dsn0])
            cal_parameters[i].append([sn1, dsn1])
            cal_parameters[i].append([sn2, dsn2])

        fitted_peaks = len(cal_parameters)
        for i in np.arange(fitted_peaks): #three parameters fitted for each peak
            console = Console()
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Parameter")
            table.add_column("Value")
            table.add_column("Error")

            parameters = ["MU", "HEIGHT", "SIGMA", "GAIN", "SN0", "SN1", "SN2"]
            for j, parameter in enumerate(parameters):
                value, error = '{:.2E}'.format(cal_parameters[i][j][0]), '{:.2E}'.format(cal_parameters[i][j][1])
                table.add_row(parameter, value, error)

            console.print("\nPeak:", i)
            console.print(table)
        
        console = Console()
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Parameter")
        table.add_column("Value")
        table.add_column("Error")
        parameters = ["NPEAK", "XT", "LAMBDA"]
        for j, parameter in enumerate(parameters):
            value, error = '{:.2f}'.format(xt_parameters[0][j][0]), '{:.2f}'.format(xt_parameters[0][j][1])
            table.add_row(parameter, value, error)
        console.print("\nX-Talk:")
        console.print(table)

        write_output_file(run, ch, cal_parameters, "Calibration", info, write_mode = 'w', header_list=["MU","DMU","SIG","DSIG","GAIN","DGAIN","SN0","DSN0","SN1","DSN1","SN2","DSN2"])
        write_output_file(run, ch, xt_parameters, "XTalk", info, write_mode = 'w', header_list=["NPEAK","XT","DXT","LAMBDA","DLAMBDA"], not_saved = [1])

def get_gains(run,channels,folder_path="TUTORIAL",debug=False):
    gains = dict.fromkeys(channels) ; Dgain = dict.fromkeys(channels)
    for c, ch in enumerate(channels):
        my_table = pd.read_csv(folder_path+"/fit_data/run%i_ch%i/gain_ch%i.txt"%(run,ch,ch), header=None,sep = "\t",usecols=np.arange(16),names=["RUN","OV","PEAK","MU","DMU","SIG","DSIG","\t","GAIN","DGAIN","SN0","DSN0","SN1","DSN1","SN2","DSN2"])
        my_table = my_table.iloc[1:]
        gains[ch] = list(np.array(my_table["GAIN" ]).astype(float)[my_table["RUN"]==str(run)])
        Dgain[ch] = list(np.array(my_table["DGAIN"]).astype(float)[my_table["RUN"]==str(run)])
        # if debug: print("\nGAIN TXT FOR CHANNEL %i"%ch ); display(my_table)
    
    return gains, Dgain

def scintillation_txt(run, ch, popt, pcov, filename, info):
    '''
    \nComputes charge parameters.
    \nGiven popt and pcov which are the output for the best parameters when performing the Gaussian fit.
    \nIt returns an array of arrays: 
    \nsave_scintillation = [ [[mu,dmu],[height,dheight],[sigma,dsigma],] ]
    \nSave in a txt the calibration parameters to be exported directly.
    \nTakes as input an array of arrays with the computed parameters (see compute_charge_parameters())
    '''

    charge_parameters = []
    perr0 = np.sqrt(np.diag(pcov))  #error for each variable
    # perr1 = np.sqrt(np.diag(pcov[1]))  #error for each variable

    mu       = [popt[1], perr0[1]]  # mu +- dmu
    height   = [popt[0], perr0[0]]  # height +- dheight (not saving in txt by default)
    sigma    = [abs(popt[2]), perr0[2]]  # sigma +- dsigma
    charge_parameters.append([mu,height,sigma])
    
    print(len(charge_parameters))
    print(charge_parameters)

    print("MU +- DMU:",               ['{:.2f}'.format(item) for item in charge_parameters[0][0]])
    print("HEIGHT +- DHEIGHT:",       ['{:.2f}'.format(item) for item in charge_parameters[0][1]])
    print("SIGMA +- DSIGMA:",         ['{:.2f}'.format(item) for item in charge_parameters[0][2]])
    
    write_output_file(run, ch, charge_parameters, filename, info, header_list=["RUN","OV","PEAK","MU","DMU","SIG","DSIG"])


def charge_fit(my_runs, keys, OPT={}):
    '''
    \nComputes charge hist of a collection of runs. A fit is performed (1 gaussian) and we have as 
    \na return the popt, pcov, perr for the best fitted parameters. Not only that but a plot is displayed.
    \n**VARIABLES:**
    \n- my_run: run(s) we want to check
    \n- keys: variables we want to plot as histograms. Type: List
    \n- OPT: several options that can be True or False. Type: List
      (a) LOGY: True if we want logarithmic y-axis
      (b) SHOW: if True, it will show the calibration plot
    '''

    next_plot = False
    counter = 0
    all_counts, all_bins, all_bars = vis_var_hist(my_runs, keys, OPT=OPT)
    all_popt=[]; all_pcov=[]; all_perr=[]
    for run, ch, key in product(my_runs["NRun"], my_runs["NChannel"], keys):        
        
        if check_key(my_runs[run][ch], "MyCuts") == False:    generate_cut_array(my_runs) #if no cuts, generate them
        if check_key(my_runs[run][ch], "UnitsDict") == False: get_units(my_runs)          #if no units, generate them
        # try:
        thresh = int(len(my_runs[run][ch][key])/1000)

        ## New Figure with the fit ##
        plt.ion()
        fig_ch, ax_ch = plt.subplots(1,1, figsize = (8,6))
        add_grid(ax_ch)
        counts = all_counts[counter]; bins = all_bins[counter]; bars = all_bars[counter]
        ax_ch.hist(bins[:-1], bins, weights = counts, histtype="step")
        fig_ch.suptitle("Run_{} Ch_{} - {} histogram".format(run,ch,key)); fig_ch.supxlabel(key+" ("+my_runs[run][ch]["UnitsDict"][key]+")"); fig_ch.supylabel("Counts")
        
        ### --- 1x GAUSSIAN FIT --- ###
        x, popt, pcov, perr = gaussian_fit(counts, bins, bars,thresh,fit_function="gaussian")
        print("Chi2/N?: ", (sum((my_runs[run][ch][key]-gaussian(my_runs[run][ch]["Sampling"]*np.arange(len(my_runs[run][ch][key])), *popt))**2))/len(my_runs[run][ch][key]))
        ax_ch.plot(x,gaussian(x, *popt), label="")

        if check_key(OPT,"LEGEND") == True and OPT["LEGEND"] == True:
            ax_ch.legend()
        if check_key(OPT,"LOGY") == True and OPT["LOGY"] == True:
            ax_ch.semilogy()
            plt.ylim(ymin=1, ymax=1.2*max(counts))

        ## Repeat customized fit ##
        confirmation = input("Are you happy with the fit? (y/n) ")
        if "n" in confirmation:
            print("\n--- Repeating the fit with input parameters (\u03BC \u00B1 \u03C3) \u03B5 [{:0.2f}, {:0.2f}] ---".format(x[0],x[-1]))
            mean  = input("Introduce MEAN value for the fit: " )
            sigma = input("Introduce SIGMA value for the fit: ")

            x, popt, pcov, perr = gaussian_fit(counts, bins, bars,thresh,custom_fit=[float(mean),float(sigma)])
            ax_ch.plot(x, gaussian(x, *popt), label="")
            all_popt.append(popt); all_pcov.append(pcov); all_perr.append(perr)
        else:
            all_popt.append(popt); all_pcov.append(pcov); all_perr.append(perr)
            plt.close()
            continue
        
        if check_key(OPT,"SHOW") == True and OPT["SHOW"] == True:
            while not plt.waitforbuttonpress(-1): pass
        counter += 1
        plt.close()
        # except KeyError:
        #     print("Empty dictionary. No computed charge.")
    
    return all_popt, all_pcov, all_perr