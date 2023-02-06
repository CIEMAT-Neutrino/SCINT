import numpy             as np
import matplotlib.pyplot as plt
import scipy
from scipy.signal   import find_peaks
from scipy.optimize import curve_fit
from itertools      import product

from .io_functions  import check_key,print_keys, write_output_file
from .vis_functions import vis_var_hist
from .fit_functions import gaussian,gaussian_train, loggaussian, loggaussian_train
from .ana_functions import generate_cut_array, get_units
from .fig_config    import *

def calibrate(my_runs, keys, OPT={}):
    """Computes calibration hist of a collection of runs and returns gain and SPE charge limits"""

    plt.ion()
    next_plot = False
    idx = 0
    for run, ch, key in product(my_runs["NRun"], my_runs["NChannel"], keys):        
        
        if check_key(my_runs[run][ch], "MyCuts") == False:
            generate_cut_array(my_runs)
        if check_key(my_runs[run][ch], "Units") == False:
            get_units(my_runs)
        
        try:
            idx = idx + 1

            # Threshold value (for height of peaks and valleys)
            thresh = int(len(my_runs[run][ch][key])/1000)
            wdth = 10
            prom = 0.5
            acc  = 1000

            counts, bins, bars = vis_var_hist(my_runs, run, ch, key, OPT=OPT)
            plt.close()

            # New Figure with the fit
            fig_cal, ax_cal = plt.subplots(1,1, figsize = (8,6))

            add_grid(ax_cal)
            counts = counts[0]; bins = bins[0]; bars = bars[0]
            ax_cal.hist(bins[:-1], bins, weights = counts)
            fig_cal.suptitle("Run_{} Ch_{} - {} histogram".format(run,ch,key)); fig_cal.supxlabel(key+" ("+my_runs[run][ch]["Units"][key]+")"); fig_cal.supylabel("Counts")

            # Create linear interpolation between bins to search peaks in these variables
            x = np.linspace(bins[1],bins[-2],acc)
            y_intrp = scipy.interpolate.interp1d(bins[:-1],counts)
            y = y_intrp(x)
            # plt.plot(x,y)

            # Find indices of peaks
            # peak_idx, _ = find_peaks(np.log10(y), height = np.log10(thresh), width = wdth, prominence = prom)
            peak_idx, _ = find_peaks(y, height = thresh, width = wdth, prominence = prom)

            # Find indices of valleys (from inverting the signal)
            # valley_idx, _ = find_peaks(-np.log10(y), height = [-np.max(np.log10(counts)), -np.log10(thresh)], width = wdth, prominence = prom)
            valley_idx, _ = find_peaks(-y, height = [-np.max(counts), -thresh], width = wdth)
            
            # Plot threshold, peaks (red) and valleys (blue)
            ax_cal.axhline(thresh, ls='--')
            ax_cal.plot(x[peak_idx], y[peak_idx], 'r.', lw=4)
            ax_cal.plot(x[valley_idx], y[valley_idx], 'b.', lw=6)

            initial = [] #Saving for input to the TRAIN FIT
            
            n_peaks = 6
            if len(peak_idx)-1 < n_peaks:
                n_peaks = len(peak_idx)-1 #Number of peaks found by find_peak
            
            for i in range(n_peaks):
                x_space = np.linspace(x[peak_idx[i]], x[peak_idx[i+1]], acc) #Array with values between the x_coord of 2 consecutives peaks
                step    = x_space[1]-x_space[0]
                x_gauss = x_space-int(acc/2)*step
                x_gauss = x_gauss[x_gauss >= bins[0]]
                y_gauss = y_intrp(x_gauss)
                # plt.plot(x_gauss,y_gauss,ls="--",alpha=0.9)

                try:
                    # popt, pcov = curve_fit(loggaussian,x_gauss,np.log10(y_gauss),p0=[np.log10(y[peak_idx[i]]),x[peak_idx[i]],abs(wdth*(bins[0]-bins[1]))])
                    popt, pcov = curve_fit(gaussian,x_gauss,y_gauss,p0=[y[peak_idx[i]],x[peak_idx[i]],abs(wdth*(bins[0]-bins[1]))])
                    perr = np.sqrt(np.diag(pcov))
                    # FITTED to gaussian(x, height, center, width)
                    initial.append(popt[1])         # HEIGHT
                    initial.append(popt[0])         # CENTER
                    initial.append(np.abs(popt[2])) # WIDTH
                    ax_cal.plot(x_gauss,gaussian(x_gauss, *popt), ls = "--", c = "black", alpha = 0.5)
                
                except:
                    initial.append(x[peak_idx[i]])
                    initial.append(y[peak_idx[i]])
                    initial.append(abs(wdth*(bins[0]-bins[1])))
                    print("Peak %i could not be fitted"%i)

            try:
                ## GAUSSIAN TRAIN FIT ## Taking as input parameters the individual gaussian fits with initial
                # popt, pcov = curve_fit(loggaussian_train,x[:peak_idx[-1]],np.log10(y[:peak_idx[-1]]),p0=initial)
                popt, pcov = curve_fit(gaussian_train,x[:peak_idx[-1]], y[:peak_idx[-1]], p0=initial) 
                perr = np.sqrt(np.diag(pcov))
            except:
                popt = initial
                print("Full fit could not be performed")
            ax_cal.plot(x[:peak_idx[-1]],gaussian_train(x[:peak_idx[-1]], *popt), label="")
            # plt.legend()

            if check_key(OPT,"LOGY") == True and OPT["LOGY"] == True:
                ax_cal.semilogy()
            
            # plt.ylim(thresh*0.9,np.max(counts)*1.1)
            # plt.xlim(x[peak_idx[0]]-abs(wdth*(bins[0]-bins[1])),x[peak_idx[-1]]*1.1)
            if check_key(OPT,"SHOW") == True and OPT["SHOW"] == True:
                while not plt.waitforbuttonpress(-1): pass

            plt.clf()
            if check_key(OPT,"PRINT_KEYS") == True and OPT["PRINT_KEYS"] == True:
                return print_keys(my_runs)

            my_runs[run][ch]["Gain"] = popt[3]-abs(popt[0])
            my_runs[run][ch]["MaxChargeSPE"] = popt[3] + abs(popt[5])
            print("SPE gauss parameters %.2E, %.2E, %.2E"%(popt[3],popt[4],popt[5]))
            # print("SPE max charge for run %i ch %i = %.2E"%(run,ch,popt[3] + abs(popt[5])))
            my_runs[run][ch]["MinChargeSPE"] = popt[3] - abs(popt[5])
            # print("SPE min charge for run %i ch %i = %.2E"%(run,ch,popt[3] - abs(popt[5])))

            
        except KeyError:
            print("Empty dictionary. No calibration to show.")
    
    # plt.ioff()
    plt.clf()
    plt.close()
    
    return popt, pcov, perr

def calibration_txt(run, ch, popt, pcov, filename, info):
    """Computes calibration parameters for each peak.
       \n Given popt and pcov which are the output for the best parameters when performing the Gaussian fit.
       \n It returns an array of arrays: 
       save_calibration = [ [[mu,dmu],[height,dheight],[height,dheight],[sigma,dsigma],
                            [gain,dgain],[sn0,dsn0],[sn1,dsn1],[sn2,dsn2]], [PEAK 1], [PEAK 2],...]
       \nSave in a txt the calibration parameters to be exported directly.
       \nTakes as input an array of arrays with the computed parameters (see compute_cal_parameters())
    """

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
    
    write_output_file(run, ch, cal_parameters, filename, info, header_list=["RUN","MU","DMU","SIG","DSIG","NEVENTS","DNEVENTS"], extra_tab=[3])

def scintillation_txt(run, ch, popt, pcov, filename, info):
    """Computes charge parameters.
        \n Given popt and pcov which are the output for the best parameters when performing the Gaussian fit.
        \n It returns an array of arrays: 
            save_scintillation = [ [[mu,dmu],[height,dheight],[sigma,dsigma], [nevents,dnevents]] ]
        \nSave in a txt the calibration parameters to be exported directly.
        \nTakes as input an array of arrays with the computed parameters (see compute_charge_parameters())
    """
    charge_parameters = []
    perr = np.sqrt(np.diag(pcov))  #error for each variable

    mu       = [popt[0], perr[0]]  # mu +- dmu
    height   = [popt[1], perr[1]]  # height +- dheight (not saving in txt by default)
    sigma    = [popt[2], perr[2]]  # sigma +- dsigma
    nevents  = [popt[2], perr[2]]  # nevents/s +- dnevents/s
    charge_parameters.append([mu,height,sigma,nevents])

    print("MU +- DMU:",               ['{:.2f}'.format(item) for item in charge_parameters[0][0]])
    print("HEIGHT +- DHEIGHT:",       ['{:.2f}'.format(item) for item in charge_parameters[0][1]])
    print("SIGMA +- DSIGMA:",         ['{:.2f}'.format(item) for item in charge_parameters[0][2]])
    print("NEVENTS/s +- DNEVENTS/s:(HAY QUE CALCULARLO BIEN)", ['{:.2f}'.format(item) for item in charge_parameters[0][3]])
    
    write_output_file(run, ch, charge_parameters, filename, info, header_list=["RUN","MU","DMU","SIG","DSIG","NEVENTS","DNEVENTS"])