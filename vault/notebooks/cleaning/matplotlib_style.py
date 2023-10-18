import matplotlib.pyplot as plt

# Matplotlib settings
plt.style.use('classic')
plt.rcParams['axes.facecolor'] = 'white'
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
          '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=colors)
plt.rcParams['xtick.major.width'] = 1.2
plt.rcParams['ytick.major.width'] = 1.2
# plt.rcParams["axes.labelweight"] = "bold"
