import matplotlib.pylab as plt
import numpy as np

from autov.autov import lambda2freq

plt.style.use('seaborn-paper')

hf_data = np.genfromtxt("/home/koopman/lab/optics/mul/hf/hf_152_183_296_refl_data.txt", delimiter=',')
mf_data = np.genfromtxt("/home/koopman/lab/optics/mul/mf/mf_257_310_500_refl_data.txt", delimiter=',')

plt.plot(lambda2freq(hf_data[:, 0]), hf_data[:, 1])
# band numbers from Jan 5th, 2018 telecon here:
#https://phy-wiki.princeton.edu/advactwiki/pmwiki.php?n=Telecons.OpticsAndHWPlates?action=download&upname=FTS_2017_Janupdate.pdf
plt.axvspan((145-36/2.), (145+36/2.), alpha=0.2, color='black', label='_nolegend_')
plt.axvspan((222.0-73/2.), (222.0+73/2.), alpha=0.2, color='black', label='_nolegend_')
plt.ylim([0, 0.08])
plt.axhline(0.01, color='black', linestyle='--')
plt.xlabel("Frequency [GHz]")
plt.ylabel("Reflectance [%]")
plt.title("HF AR Coating Reflectance")
plt.savefig("./hf_arc_refl.png", format='png')

plt.clf()
plt.plot(lambda2freq(mf_data[:, 0]), mf_data[:, 1])
plt.axvspan((96-22/2.), (96+22/2.), alpha=0.2, color='black', label='_nolegend_')
plt.axvspan((148.0-35/2.), (148.0+35/2.), alpha=0.2, color='black', label='_nolegend_')
plt.ylim([0, 0.18])
plt.axhline(0.01, color='black', linestyle='--')
plt.xlabel("Frequency [GHz]")
plt.ylabel("Reflectance [%]")
plt.title("MF1 AR Coating Reflectance")
plt.savefig("./mf1_arc_refl.png", format='png')
