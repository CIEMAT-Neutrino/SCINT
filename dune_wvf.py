import numpy as np
import matplotlib.pyplot as plt

from lib.wvf_functions import find_baseline_cuts
from lib.fit_functions import sc_fit
from lib.dec_functions import deconvolve

RUN = np.loadtxt("data/raw/SPE_maritza.txt")
RUN = RUN[:-3]

RUN_X = 16e-9*np.arange(len(RUN))
TIMEBIN = RUN_X[1]-RUN_X[0]

RANGES = [0,0]
OPT = {
    # "SHOW": True
    }

fit = sc_fit(RUN,RUN_X,RANGES,OPT)

my_run = dict()
my_run["N_runs"] = [0]
my_run["N_channels"] = [0]
my_run[0] = dict()
my_run[0][0] = dict()
my_run[0][0]["ADC"] = [RUN]
my_run[0][0]["Sampling"] = TIMEBIN

OPT = {
    "KEY": "ADC",
    "NOISE_AMP": 0.1,
    "SHOW": True,
    "SHOW_F_SIGNAL":True,
    "SHOW_F_DET_RESPONSE":True,
    "SHOW_F_GAUSS":True,
    "SHOW_F_WIENER":True,
    "SHOW_F_DEC":True,
    # "TRIMM": 0,
    # "AUTO_TRIMM": False,
    "WIENER_BUFFER": 100,

    # "SINGLE": True,
    "TIMEBIN": TIMEBIN,
    # "REVERSE": False        
}

deconvolve(my_run,my_run,fit,OPT)
dec,dec_x = deconvolve(my_run,my_run,fit,OPT)

i_raw,f_raw = find_baseline_cuts(RUN)
plt.plot(RUN_X,RUN,label="RAW")
i_fit,f_fit = find_baseline_cuts(fit)
plt.plot(RUN_X,fit,label="FIT")
i_dec,f_dec = find_baseline_cuts(dec[0])
plt.plot(dec_x,dec[0],label="DEC int = %.2f PE"%(np.sum(dec[0][i_dec:f_dec])))
plt.xlabel("Time in [s]"); plt.ylabel("Amp in ADC")
plt.legend()
plt.show()