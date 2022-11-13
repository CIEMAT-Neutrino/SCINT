import numpy as np
import matplotlib.pyplot as plt
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
my_run[0][0]["ADC"] = RUN

OPT = {
    "TRIMM": 0,
    "AUTO_TRIMM": False,
    "WIENER_BUFFER": 100,
    "SHOW": False,
    "SINGLE": True,
    "TIMEBIN": TIMEBIN,
    "REVERSE": False        
}

dec,dec_x = deconvolve(my_run,fit,OPT,PATH="data/dec")

i_raw,f_raw = find_baseline_cuts(RUN)
plt.plot(RUN_X,RUN,label="RAW")
i_fit,f_fit = find_baseline_cuts(fit)
plt.plot(RUN_X,fit,label="FIT")
i_dec,f_dec = find_baseline_cuts(dec)
plt.plot(dec_x,dec,label="DEC")
plt.xlabel("Time in [s]"); plt.ylabel("Amp in ADC")
plt.legend()
plt.show()