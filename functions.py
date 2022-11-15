from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from scipy import integrate


def loadSER(debugging=False):
    new_SER=np.load("new_SER.npy")

    SER=[]
    SER.append(new_SER[0::10])
    if debugging: plt.plot(SER[0])

    for i in  range(1,10):
        SER.append(np.insert(new_SER[10-i::10],0,0))
        if debugging: 
            plt.plot(SER[i])
            plt.xlim(3,10)
            plt.ylim(3,10)
    if debugging: plt.legend(["SER {}".format(i) for i in range(10)]);

    for i in  range(1,10):
        SER[i]=SER[i][:-1]
        if debugging: print(len(SER[i]))
    return SER
def scint_prof(size,fast=6/12.5,slow=1300/12.5,ratio=0.3):
    bins=np.arange(size)
    prof=ratio*np.exp(-bins/fast)+(1-ratio)*np.exp(-bins/slow)
    return prof/np.sum(prof)

def rand_scint(N=1000,fast=6,slow=1300,ratio=0.3):
    aux=np.random.uniform(low=0,high=1,size=N);
    offset= np.random.random()#photon can arrive at any time
    return offset+(aux<(ratio))*np.random.exponential(scale=fast,size=N)+(aux>(ratio))*np.random.exponential(scale=slow,size=N)


def Add_GaussNoise(wvf,ADC=2.6):
    #  Adds gaussian random noise centered at 0 with STD=ADC(in adc counts) to the wvf in the time domain;
    return wvf+np.random.normal(scale=ADC,size=len(wvf));

def Add_signal(wvf,SER,time=1,npe=1):
    #time in bin units
    decimal=int((time*10)%10) #resto
    # print(len(npe*SER[decimal]))
    wvf[int(time):int(time)+len(SER[0])]=npe*SER[decimal]
    # wvf[int(time):int(time)+len(SER[decimal])]=npe*SER[decimal]
    return wvf

def Add_signal_OLD(wvf,SER,time=1,npe=1):
    #time in bin units
    wvf[int(time):int(time)+len(SER[0])]=npe*SER[0]
    return wvf


def Produce_WVFS(
                wvf_size,
                n_wvf   ,
                t_truth ,
                n_photo ,
                SER):
    """ Imputs number of bins(wvf size), #wvfs to simulate, time profile of the photons & #of total photons; \n Returns a vector of wvfs ready to proccess"""
    WVF     = []
    WVF_OLD = []
    for i in range(n_wvf):
        # Add_GaussNoise(  Add_signal(np.zeros(1000),SER,time=float(1+i/10),npe=10)
        wvf=np.zeros(wvf_size)
        times=t_truth[i]
        for t in times:
            # print(t)
            if t<500:
                wvf_aux=np.zeros(wvf_size)
                wvf+=Add_signal(wvf_aux,SER,time=t,npe=1)
        wvf=Add_GaussNoise(wvf)
        wvf=np.trunc(wvf)
        WVF.append(wvf)

        wvf=np.zeros(wvf_size)
        for t in times:
            # print(t)
            if t<500:
                wvf=Add_signal_OLD(wvf,SER,time=t,npe=1)
        wvf=Add_GaussNoise(wvf)
        wvf=np.trunc(wvf)
        WVF_OLD.append(wvf)

    return WVF,WVF_OLD;



def solve_lorenz(sigma=10.0, beta=8./3, rho=28.0):
    """Plot a solution to the Lorenz differential equations."""

    max_time = 4.0
    N = 30

    fig = plt.figure()
    ax = fig.add_axes([0, 0, 1, 1], projection='3d')
    ax.axis('off')

    # prepare the axes limits
    ax.set_xlim((-25, 25))
    ax.set_ylim((-35, 35))
    ax.set_zlim((5, 55))
    
    def lorenz_deriv(x_y_z, t0, sigma=sigma, beta=beta, rho=rho):
        """Compute the time-derivative of a Lorenz system."""
        x, y, z = x_y_z
        return [sigma * (y - x), x * (rho - z) - y, x * y - beta * z]

    # Choose random starting points, uniformly distributed from -15 to 15
    np.random.seed(1)
    x0 = -15 + 30 * np.random.random((N, 3))

    # Solve for the trajectories
    t = np.linspace(0, max_time, int(250*max_time))
    x_t = np.asarray([integrate.odeint(lorenz_deriv, x0i, t)
                      for x0i in x0])
    
    # choose a different color for each trajectory
    colors = plt.cm.viridis(np.linspace(0, 1, N))

    for i in range(N):
        x, y, z = x_t[i,:,:].T
        lines = ax.plot(x, y, z, '-', c=colors[i])
        plt.setp(lines, linewidth=2)
    angle = 104
    ax.view_init(30, angle)
    plt.show()

    return t, x_t