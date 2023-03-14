import os
import numpy             as np
import matplotlib.pyplot as plt
import pandas            as pd
import xlrd, csv

plt.rcParams.update({'font.size': 2})
plt.rc('font',   size=26)        # controls default text sizes
plt.rc('axes',   titlesize=28)   # fontsize of the axes title
plt.rc('axes',   labelsize=26)   # fontsize of the x and y labels
plt.rc('xtick',  labelsize=26)   # fontsize of the tick labels
plt.rc('ytick',  labelsize=26)   # fontsize of the tick labels
plt.rc('legend', fontsize=23)    # legend fontsize
plt.rc('figure', titlesize=20)   # fontsize of the figure title
plt.rc('axes.formatter', useoffset=False)

###################################################################
############################## DATA ###############################
###################################################################

def df_display(values,labels, name,index="",terminal_output=False,save=False):
    if index == "":  index=np.arange(len(values))
    df = pd.DataFrame(values, columns=labels, index=index)
    if save: print("\n Saving file ../fit_data/df_"+name+".txt"); df.to_csv('../fit_data/df_'+name+'.txt', sep=" ", quoting=csv.QUOTE_NONE, escapechar=" ")
    if terminal_output: print("\n--------- %s ---------"%name); display(df)
    return df 

def npy2df(values):
    mean = values.mean(axis=0)
    stds = values.std(axis=0)
    return mean, stds

def data2npy(folder, pcbs_labels, sipm_labels, pins_labels, sipm_number=6, pins_number=8, mode=1, debug=False):
    print("\nWARNING: the configuration for the xlsx is hard-coded, any change in the naming or how information is distributed in the cells WILL NEED to be CHANGED in the function")
    names           = os.listdir(folder)
    pcbs_values     = np.empty([len(names)*mode,              len(pcbs_labels)]) #solo anverso
    sipm_values     = np.empty([sipm_number*len(names)*mode,  len(sipm_labels)]) #solo anverso
    pins_values_anv = np.empty([pins_number*len(names) *mode, len(pins_labels)]) #solo anverso
    pins_values_rev = np.empty( pins_number*len(names) *mode)                    #solo reverso/solo altura pines
    
    names_sipms = []
    for i in range(sipm_number):
        names_sipms.append("SiPM #%i"%(i+1))
    if debug: print(names_sipms)

    names_pins = []
    for i in range(pins_number):
        names_pins.append("Pin #%i"%(i+1))
    if debug: print(names_pins)

    if mode == 1:
        print("\nYou have entered \"mode=1\", meaning that each bunch of 6xSiPMs is stored in ONE .xlsx")
    else:
        print("\nYou have entered \"mode=%i\", meaning that in each .xlsx you stored %i bunches of 6xSiPMs"%(mode,mode))

    for n in np.arange(len(names)): # Distintos archivos --> Placas PCBs
        ##PREVIOUS CONFIGURATION##
        # workbook_anv  = xlrd.open_workbook(folder + names[n] + '/' + names[n].replace("Nº","") + '_anverso_1.xlsx')
        # workbook_rev  = xlrd.open_workbook(folder + names[n] + '/' + names[n].replace("Nº","") + '_reverso_1.xlsx')
        workbooks_anv  = xlrd.open_workbook(folder + names[n] + '/' + names[n] + '_anverso.xlsx')
        workbooks_rev  = xlrd.open_workbook(folder + names[n] + '/' + names[n] + '_reverso.xlsx')
        worksheet_anv = workbooks_anv.sheet_by_index(0)
        worksheet_rev = workbooks_rev.sheet_by_index(0)

        # PCB #
        for l in np.arange(len(pcbs_labels)):    # Etiquetas x16
            for m in range(mode):                # Entries in each file
                pcbs_values[n*mode+m,l] = worksheet_anv.cell(3+l+m*197,11).value #cell allocation in xlsx file
               #pcbs_values[0-(names*mode*#LABELS),0-16] = cell(COLUMNA: 3+l(ETIQUETA(0-16))+m*197(SEPARACION ENTRE MEDIDAS), FILA: 11)
            
        # SiPMs #
        for l in np.arange(len(sipm_labels)):    # Etiquetas x6
            for m in range(mode):                # Entries in each file
                for j in np.arange(sipm_number): # SiPMs x6
                    sipm_values[j+m*sipm_number+n*(sipm_number*(mode-1)+sipm_number),l] = worksheet_anv.cell(3+l+j*8+m*197,14).value #cell allocation in xlsx file
                   #sipm_values[0-(names*mode*#SIPMS*#LABELS),0-6] = cell(COLUMNA: 3+l(ETIQUETA(0-6))+j*8(DISTANCIA ENTRE SIPMS)+m*197(SEPARACION ENTRE MEDIDAS), FILA: 14)

        # Pins anverso #
        for l in np.arange(len(pins_labels)):    # Etiquetas x3
            for m in range(mode):                # Entries in each file
                for j in np.arange(pins_number): # Pins x8
                    pins_values_anv[j+m*pins_number+n*(pins_number*(mode-1)+pins_number),l] = worksheet_anv.cell(3+l+j*5+m*197,17).value #cell allocation in xlsx file
                   #pins_values_anv[0-(names*mode**#PINS*#LABELS),0-8] = cell(COLUMNA: 3+l(ETIQUETA(0-3))+j*5(DISTANCIA ENTRE PINS)+m*197(SEPARACION ENTRE MEDIDAS), FILA: 17)

        # Pins reverso #
        for m in range(mode):                    # Entries in each file
            for j in np.arange(pins_number):     # Pins x8
                pins_values_rev[j+m*pins_number+n*(pins_number*(mode-1)+pins_number)] = worksheet_rev.cell(3+j+m*24,11).value # Etiqueta x1 (sin loop) REVERSO
               #pins_values_rev[0-(names*mode*#PINS)] = cell(COLUMNA: 3+l(ETIQUETA(0-6))+j(0-8 pins)+m*24(SEPARACION ENTRE MEDIDAS), FILA: 11)


    print("\nCHECK DIMENSIONS:")
    print("Files x Bunches:",len(pcbs_values))
    print("PCBs:",len(pcbs_values[0])*len(pcbs_values))
    print("SiPM:",len(sipm_values[0])*len(sipm_values))
    print("PIN_ANV:",len(pins_values_anv[0])*len(pins_values_anv))
    print("PIN_REV:",len(pins_values_rev))

    return pcbs_values, sipm_values, pins_values_rev, pins_values_anv

def sanity_check(df_values,values):
    if df_values.duplicated().any(): 
        print("You have repeated rows")
        aux = []
        for i, element in enumerate(np.where(df_values.duplicated())[0]):
                for j,y in enumerate(values):
                        where_array = np.where(values[element] == y)[0]
                        try: 
                                if len(where_array) == len(values[element]): 
                                        if j != element: aux.append((element,j)) 
                        except TypeError: 
                               if j != element: aux.append((element,j))
        resta = []
        for a in aux:
                resta.append(abs(a[0]-a[1]))
        resta.sort()
        # print(resta)
        plt.scatter(np.arange(len(resta)),resta)
        plt.show()

    else: print("Great! All your entries are unique :)")



###################################################################
########################### VISUALIZATION #########################
###################################################################

def plotitos(title, xlabel, ylabel, df, df_mean, columns, colors, bars =[], decimales=2):
    '''
    Histogram given two df one with the values to plot an the other with the Mean and STD to be shown with vertical lines.
    You can give as input variables the title, x/ylabels, the color and the decimals to round the mean/std.
    '''
    left, width = .25, .23
    bottom, height = .25, .6
    right = left + width
    top = bottom + height
    decimales = decimales
    # if bars == []:
    
    if bars == []: 
        fig, ax = plt.subplots(1,1, figsize = (12,10), sharey=True)
        fig.tight_layout()
        
        ax.hist(df[columns], color = colors[0]) #, density=True
        media_std_1 = str(np.round(df_mean[columns]['Mean'],decimales))+ r"$\pm$" +str(np.round(df_mean[columns]['STD'],decimales))
        ax.axvline(np.round(df_mean[columns]['Mean'],decimales), color=colors[1])
        ax.axvline(np.round(df_mean[columns]['Mean'],decimales)-np.round(df_mean[columns]['STD'],decimales), color=colors[2], linestyle='dashed')
        ax.axvline(np.round(df_mean[columns]['Mean'],decimales)+np.round(df_mean[columns]['STD'],decimales), color=colors[2], linestyle='dashed')
        ax.text(right, top, 'Mean = ' + media_std_1, horizontalalignment='right', verticalalignment='bottom', transform=ax.transAxes)

    else: 
        fig, ax = plt.subplots(2,int(len(bars)/2), figsize = (40,15), sharey=True)
        fig.tight_layout(pad=2.5)

        x = [0] * int(len(bars)/2) + [1] * int(len(bars)/2)
        y = list(np.arange(int(len(bars)/2))) * 2
        for i, b in enumerate(bars):
            mean, std = npy2df(df.loc[b])
            df_mean = df_display(np.array((mean,std)),labels = list(df.columns),index=["Mean","STD"],name="")
            media_std_1 = str(np.round(df_mean[columns]['Mean'],decimales))+ r"$\pm$" +str(np.round(df_mean[columns]['STD'],decimales))
            ax[x[i],y[i]].set_title(b)
            ax[x[i],y[i]].hist(df.loc[b][columns])
            ax[x[i],y[i]].axvline(np.round(df_mean[columns]['Mean'],decimales), color=colors[1])
            ax[x[i],y[i]].axvline(np.round(df_mean[columns]['Mean'],decimales)-np.round(df_mean[columns]['STD'],decimales), color=colors[2], linestyle='dashed')
            ax[x[i],y[i]].axvline(np.round(df_mean[columns]['Mean'],decimales)+np.round(df_mean[columns]['STD'],decimales), color=colors[2], linestyle='dashed')
            ax[x[i],y[i]].text(right, top, 'Mean = ' + media_std_1, horizontalalignment='right', verticalalignment='bottom', transform=ax[x[i],y[i]].transAxes)
    
    fig.suptitle(title)
    fig.supxlabel(xlabel)
    fig.supylabel(ylabel)

    plt.show()