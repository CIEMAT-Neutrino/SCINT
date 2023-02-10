import numpy             as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.cm     import viridis
from itertools         import product
from scipy.optimize    import curve_fit
import scipy 

from .io_functions  import check_key, print_keys, write_output_file
from .vis_functions import vis_var_hist
from .fit_functions import gaussian, gaussian_train, loggaussian, loggaussian_train, gaussian_fit, gaussian_train_fit, pmt_spe_fit
from .ana_functions import generate_cut_array, get_units
from .cut_functions import cut_min_max
from .fig_config    import *

def vis_persistence(my_run, OPT = {}):
    """
    This function plot the PERSISTENCE histogram of the given runs&ch.
    It perfoms a cut in 20<"PeakTime"(bins)<50 so that all the events not satisfying the condition are removed. 
    Binning is fixed (x=5000, y=1000) [study upgrade].
    X_data (time) and Y_data (waveforms) are deleted after the plot to save space.
    WARNING! flattening long arrays leads to MEMORY problems :/
    """

    plt.ion()
    for run, ch in product(my_run["NRun"],my_run["NChannel"]):

        generate_cut_array(my_run)
        cut_min_max(my_run, ["PeakTime"], {"PeakTime":[my_run[run][ch]["PedLim"]-20,my_run[run][ch]["PedLim"]+50]})

        data_flatten = my_run[run][ch]["ADC"][np.where(my_run[run][ch]["MyCuts"] == True)].flatten() #####
        time = my_run[run][ch]["Sampling"]*np.arange(len(my_run[run][ch]["ADC"][0]))
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

def calibrate(my_runs, keys, OPT={}):
    """
    Computes calibration hist of a collection of runs. A fit is performed (train of gaussians) and we have as 
    a return the popt, pcov, perr for the best fitted parameters. Not only that but a plot is displayed.
    \n VARIABLES:
        - my_run: run(s) we want to check
        - keys: variables we want to plot as histograms. Type: List
        - OPT: several options that can be True or False. Type: List
            a) LOGY: True if we want logarithmic y-axis
            b) SHOW: if True, it will show the calibration plot
    """

    plt.ion()
    next_plot = False
    for run, ch, key in product(my_runs["NRun"], my_runs["NChannel"], keys):        
        if len(my_runs[run][ch].keys()) == 0:
            print("\n RUN DOES NOT EXIST. Looking for the next")
            popt = [-99, -99, -99]; pcov= [-99, -99, -99]; perr = [-99, -99, -99]
        
        else:
            label = my_runs[run][ch]["Label"]

            if check_key(my_runs[run][ch], "MyCuts") == False:
                generate_cut_array(my_runs)
            if check_key(my_runs[run][ch], "UnitsDict") == False:
                get_units(my_runs)

            try:
                counts, bins, bars = vis_var_hist(my_runs, run, ch, key, OPT=OPT)
                plt.close()

                ## New Figure with the fit ##
                fig_cal, ax_cal = plt.subplots(1,1, figsize = (8,6))

                add_grid(ax_cal)
                counts = counts[0]; bins = bins[0]; bars = bars[0]
                ax_cal.hist(bins[:-1], bins, weights = counts)
                fig_cal.suptitle("Run_{} Ch_{} - {} histogram".format(run,ch,key)); fig_cal.supxlabel(key+" ("+my_runs[run][ch]["UnitsDict"][key]+")"); fig_cal.supylabel("Counts")
            
                if label != "PMT": #Fit for SiPMs/SC
                    ### --- Nx GAUSSIAN FIT --- ### 
                    thresh = int(len(my_runs[run][ch][key])/1000)
                    x, y, peak_idx, valley_idx, popt, pcov, perr = gaussian_train_fit(counts, bins, bars, thresh,fit_function="gaussian")
                    ## Plot threshold, peaks (red) and valleys (blue) ##
                    ax_cal.axhline(thresh, ls='--')
                    ax_cal.plot(x[peak_idx], y[peak_idx], 'r.', lw=4)
                    ax_cal.plot(x[valley_idx], y[valley_idx], 'b.', lw=6)
                    ## Plot the fit ##
                    ax_cal.plot(x[:peak_idx[-1]],gaussian_train(x[:peak_idx[-1]], *popt), label="")

                    ## Repeat customized fit ## Ver si necesario -- añadir opcion customizar a gaussian_train_fit
                    # confirmation = input("Are you happy with the fit? (y/n) ")
                    # if "n" in confirmation:
                    #     print("\n--- Repeating the fit with input parameters (\u03BC \u00B1 \u03C3) \u03B5 [{:0.2f}, {:0.2f}] ---".format(x[0],x[-1]))
                    #     n_peaks = input("Introduce NPEAKS to fit: ")
                    #     mean  = input("Introduce MEAN value for the fit: ")
                    #     sigma = input("Introduce SIGMA value for the fit: ")

                    #     x, popt, pcov, perr = gaussian_train_fit(counts, bins, bars,thresh,custom_fit=[int(mean),int(sigma)])
                    #     ax_cal.plot(x, gaussian(x, *popt), label="")
                
                else: #Particular calibration fit for PMTs
                    print("Hello, we are working on a funtion to fit PMT spe :)")
                    thresh = int(len(my_runs[run][ch][key])/1e4)
                    x, y, peak_idx, valley_idx, popt, pcov, perr = pmt_spe_fit(counts, bins, bars, thresh)
                    ## Plot threshold, peaks (red) and valleys (blue) ##
                    ax_cal.axhline(thresh, ls='--')
                    ax_cal.plot(x[peak_idx], y[peak_idx], 'r.', lw=4)
                    ax_cal.plot(x[valley_idx], y[valley_idx], 'b.', lw=6)
                    ## Plot the fit ##
                    ax_cal.plot(x[:peak_idx[-1]],gaussian_train(x[:peak_idx[-1]], *popt), label="")

                if check_key(OPT,"LEGEND") == True and OPT["LEGEND"] == True:
                    ax_cal.legend()
                if check_key(OPT,"LOGY") == True and OPT["LOGY"] == True:
                    ax_cal.semilogy()
                if check_key(OPT,"SHOW") == True and OPT["SHOW"] == True:
                    while not plt.waitforbuttonpress(-1): pass
                plt.clf()

                my_runs[run][ch]["Gain"] = popt[3]-abs(popt[0])
                my_runs[run][ch]["MaxChargeSPE"] = popt[3] + abs(popt[5])
                my_runs[run][ch]["MinChargeSPE"] = popt[3] - abs(popt[5])
                # print("SPE min charge for run %i ch %i = %.2E"%(run,ch,popt[3] - abs(popt[5])))

            except KeyError:
                print("Empty dictionary. No calibration to show.")
        # plt.ioff()
        plt.clf()
        plt.close()
    
    return popt, pcov, perr

def calibration_txt(run, ch, popt, pcov, filename, info):
    """
    Computes calibration parameters for each peak.
       \n Given popt and pcov which are the output for the best parameters when performing the Gaussian fit.
       \n It returns an array of arrays: 
       save_calibration = [ [[mu,dmu],[height,dheight],[height,dheight],[sigma,dsigma],
                            [gain,dgain],[sn0,dsn0],[sn1,dsn1],[sn2,dsn2]], [PEAK 1], [PEAK 2],...]
       \nSave in a txt the calibration parameters to be exported directly.
       \nTakes as input an array of arrays with the computed parameters (see compute_cal_parameters())
    """
    if all(x !=-99 for x in popt):
        cal_parameters = []
        perr = np.sqrt(np.diag(pcov))    #error for each variable
        fitted_peaks = int(len(popt)/3)  #three parameters fitted for each peak
        for i in np.arange(fitted_peaks): 
            mu     = [popt[(i+0)+2*i], perr[(i+0)+2*i]]  # mu +- dmu
            height = [popt[(i+1)+2*i], perr[(i+1)+2*i]]  # height +- dheight (not saving in txt by default)
            sigma  = [popt[(i+2)+2*i], perr[(i+2)+2*i]]  # sigma +- dsigma
            cal_parameters.append([mu,height,sigma])
            copy_cal = cal_parameters

        for i in np.arange(fitted_peaks): #distances between peaks
            if i == fitted_peaks-1:
                gain = -99; dgain = -99; sn0 = -99; dsn0 = -99; sn1 = -99; dsn1 = -99; sn2 = -99; dsn2 = -99
            else:
                # GAIN = [mu(i+1) - mu(i)] * 1e-12 /1.602e-19 (pC)
                gain  = (copy_cal[i+1][0][0]-copy_cal[i][0][0])*1e-12/1.602e-19; dgain = (np.sqrt(copy_cal[i+1][0][1]**2+copy_cal[i][0][1]**2))*1e-12/1.602e-19
                
                # SN0 = [mu(i+1)-mu(i)]/sigma(i)
                sn0 = (copy_cal[i+1][0][0]-copy_cal[i][0][0])/copy_cal[i][2][0]
                dsn0 = sn0 * np.sqrt(((copy_cal[i+1][0][1]**2+copy_cal[i][0][1]**2)/((copy_cal[i+1][0][0]-copy_cal[i][0][0])))**2+(copy_cal[i][2][1]/copy_cal[i][2][0])**2)
                
                # SN1 = [mu(i+1)-mu(i)]/sigma(i+1)
                sn1 = (copy_cal[i+1][0][0]-copy_cal[i][0][0])/copy_cal[i+1][2][0]
                dsn1 = sn1 * np.sqrt(((copy_cal[i+1][0][1]**2+copy_cal[i][0][1]**2)/((copy_cal[i+1][0][0]-copy_cal[i][0][0]))**2)+(copy_cal[i+1][2][1]/copy_cal[i+1][2][0])**2)
                
                # SNC = [mu(i+1)-mu(i)]/sqrt(sigma(i)**2+sigma(i+1)**2)
                sn2 = (copy_cal[i+1][0][0]-copy_cal[i][0][0])/(np.sqrt(copy_cal[i][2][0]**2+copy_cal[i+1][2][0]**2))
                dsn2 = sn2 * np.sqrt((dgain/gain)**2+((copy_cal[i][2][0]*copy_cal[i][2][1])/((copy_cal[i][2][0])**2+(copy_cal[i+1][2][0])**2))**2+((copy_cal[i+1][2][0]*copy_cal[i+1][2][1])/((copy_cal[i][2][0])**2+(copy_cal[i+1][2][0])**2))**2)

            cal_parameters[i].append([gain, dgain]); 
            cal_parameters[i].append([sn0, dsn0]);cal_parameters[i].append([sn1, dsn1]);cal_parameters[i].append([sn2, dsn2])

        fitted_peaks = len(cal_parameters)
        for i in np.arange(fitted_peaks): #three parameters fitted for each peak
                    print("\nPeak:", i)
                    print("MU +- DMU:",         ['{:.2E}'.format(item) for item in cal_parameters[i][0]])
                    print("HEIGHT +- DHEIGHT:", ['{:.2E}'.format(item) for item in cal_parameters[i][1]])
                    print("SIGMA +- DSIGMA:",   ['{:.2E}'.format(item) for item in cal_parameters[i][2]])
                    print("GAIN +- DGAIN",      ['{:.2E}'.format(item) for item in cal_parameters[i][3]])
                    print("SN0 +- DSN0",        ['{:.2E}'.format(item) for item in cal_parameters[i][4]])
                    print("SN1 +- DSN1",        ['{:.2E}'.format(item) for item in cal_parameters[i][5]])
                    print("SN2 +- DSN2",        ['{:.2E}'.format(item) for item in cal_parameters[i][6]])
        
        write_output_file(run, ch, cal_parameters, filename, info, header_list=["RUN","OV","PEAK","MU","DMU","SIG","DSIG","\t","GAIN","DGAIN","SN0","DSN0","SN1","DSN1","SN2","DSN2"], extra_tab=[3])

def scintillation_txt(run, ch, popt, pcov, filename, info):
    """
    Computes charge parameters.
        \n Given popt and pcov which are the output for the best parameters when performing the Gaussian fit.
        \n It returns an array of arrays: 
            save_scintillation = [ [[mu,dmu],[height,dheight],[sigma,dsigma], [nevents,dnevents]] ]
        \nSave in a txt the calibration parameters to be exported directly.
        \nTakes as input an array of arrays with the computed parameters (see compute_charge_parameters())
    """

    charge_parameters = []
    perr0 = np.sqrt(np.diag(pcov[0]))  #error for each variable
    perr1 = np.sqrt(np.diag(pcov[1]))  #error for each variable

    mu       = [popt[0][1], perr0[1]]  # mu +- dmu
    height   = [popt[0][0], perr0[0]]  # height +- dheight (not saving in txt by default)
    sigma    = [popt[0][2], perr0[2]]  # sigma +- dsigma
    nevents  = [popt[1], perr1[0][0]]  # nevents/s +- dnevents/s #HACER BIEN#
    charge_parameters.append([mu,height,sigma,nevents])
    
    print(len(charge_parameters))
    print(charge_parameters[0])

    print("MU +- DMU:",               ['{:.2f}'.format(item) for item in charge_parameters[0][0]])
    print("HEIGHT +- DHEIGHT:",       ['{:.2f}'.format(item) for item in charge_parameters[0][1]])
    print("SIGMA +- DSIGMA:",         ['{:.2f}'.format(item) for item in charge_parameters[0][2]])
    print("NEVENTS/s +- DNEVENTS/s:(HAY QUE CALCULARLO BIEN)", ['{:.2f}'.format(item) for item in charge_parameters[0][3]])
    
    write_output_file(run, ch, charge_parameters, filename, info, header_list=["RUN","MU","DMU","SIG","DSIG","NEVENTS","DNEVENTS"])


def charge_fit(my_runs, keys, OPT={}):
    """
    Computes charge hist of a collection of runs. A fit is performed (1 gaussian) and we have as 
    a return the popt, pcov, perr for the best fitted parameters. Not only that but a plot is displayed.
    \n VARIABLES:
        - my_run: run(s) we want to check
        - keys: variables we want to plot as histograms. Type: List
        - OPT: several options that can be True or False. Type: List
            a) LOGY: True if we want logarithmic y-axis
            b) SHOW: if True, it will show the calibration plot
    """

    plt.ion()
    next_plot = False
    for run, ch, key in product(my_runs["NRun"], my_runs["NChannel"], keys):        
        
        if check_key(my_runs[run][ch], "MyCuts") == False:
            generate_cut_array(my_runs)
        if check_key(my_runs[run][ch], "UnitsDict") == False:
            get_units(my_runs)
        
        try:
            thresh = int(len(my_runs[run][ch][key])/1000)
            counts, bins, bars = vis_var_hist(my_runs, run, ch, key, OPT=OPT)
            plt.close()

            ## New Figure with the fit ##
            fig_ch, ax_ch = plt.subplots(1,1, figsize = (8,6))
            add_grid(ax_ch)
            counts = counts[0]; bins = bins[0]; bars = bars[0]
            ax_ch.hist(bins[:-1], bins, weights = counts)
            fig_ch.suptitle("Run_{} Ch_{} - {} histogram".format(run,ch,key)); fig_ch.supxlabel(key+" ("+my_runs[run][ch]["UnitsDict"][key]+")"); fig_ch.supylabel("Counts")
            
            ### --- 1x GAUSSIAN FIT --- ###
            x, popt, pcov, perr = gaussian_fit(counts, bins, bars,thresh,fit_function="gaussian")
            print("Chi2/N?: ", (sum((my_runs[run][ch][key]-gaussian(my_runs[run][ch]["Sampling"]*np.arange(len(my_runs[run][ch][key])), *popt))**2))/len(my_runs[run][ch][key]))
            ax_ch.plot(x,gaussian(x, *popt), label="")
            
            ## Repeat customized fit ##
            confirmation = input("Are you happy with the fit? (y/n) ")
            if "n" in confirmation:
                print("\n--- Repeating the fit with input parameters (\u03BC \u00B1 \u03C3) \u03B5 [{:0.2f}, {:0.2f}] ---".format(x[0],x[-1]))
                mean  = input("Introduce MEAN value for the fit: ")
                sigma = input("Introduce SIGMA value for the fit: ")

                x, popt, pcov, perr = gaussian_fit(counts, bins, bars,thresh,custom_fit=[int(mean),int(sigma)])
                ax_ch.plot(x, gaussian(x, *popt), label="")
            
            if check_key(OPT,"LEGEND") == True and OPT["LEGEND"] == True:
                ax_ch.legend()
            if check_key(OPT,"LOGY") == True and OPT["LOGY"] == True:
                ax_ch.semilogy()
            if check_key(OPT,"SHOW") == True and OPT["SHOW"] == True:
                while not plt.waitforbuttonpress(-1): pass
            plt.clf()

        except KeyError:
            print("Empty dictionary. No computed charge.")
    
    # plt.ioff()
    plt.clf()
    plt.close()
    
    return popt, pcov, perr