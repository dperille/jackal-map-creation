import matplotlib.pyplot as plt
import numpy as np

combined_results = np.load('./combined_results_stats/combined_penalty40.npy')
eband_results = np.load('./eband_results_stats/eband_only_penalty40.npy')
dwa_results = np.load('./dwa_results_stats/dwa_only_penalty40.npy')

class Env:
    # combined, eband, dwa are all len(2) lists -- first element is mean, second is std
    def __init__(self, combined, eband, dwa):
        self.combined = combined
        self.eband = eband
        self.dwa = dwa

    # for ordering by difficulty, worlds are sorted by combined mean
    def __eq__(self, other):
        return self.combined[0] == other.combined[0]

    def __ne__(self, other):
        return self.combined[0] != other.combined[0]

    def __lt__(self, other):
        return self.combined[0] < other.combined[0]

    def __le__(self, other):
        return self.combined[0] <= other.combined[0]

    def __gt__(self, other):
        return self.combined[0] > other.combined[0]

    def __ge__(self, other):
        return self.combined[0] >= other.combined[0]


# list of 300 Env objects
sorted_results = []
for num in range(len(combined_results)):
    sorted_results.append( Env(combined_results[num], eband_results[num], dwa_results[num]) )

# sort environments in order of ascending difficulty
sorted_results.sort()

combined_mean = np.zeros(300)
combined_std = np.zeros(300)

eband_mean = np.zeros(300)
eband_std = np.zeros(300)

dwa_mean = np.zeros(300)
dwa_std = np.zeros(300)

for num in range(len(sorted_results)):
    combined_mean[num] = sorted_results[num].combined[0]
    combined_std[num] = sorted_results[num].combined[1]

    eband_mean[num] = sorted_results[num].eband[0]
    eband_std[num] = sorted_results[num].eband[1]

    dwa_mean[num] = sorted_results[num].dwa[0]
    dwa_std[num] = sorted_results[num].dwa[1]

plt.plot(combined_mean)
plt.fill_between(np.arange(0, 300), combined_mean + combined_std, combined_mean - combined_std, alpha=0.45)
plt.show()

plt.plot(eband_mean)
plt.fill_between(np.arange(0, 300), eband_mean + eband_std, eband_mean - eband_std, alpha=0.45)
plt.show()

plt.plot(dwa_mean)
plt.fill_between(np.arange(0, 300), dwa_mean + dwa_std, dwa_mean - dwa_std, alpha=0.45)
plt.show()

plt.show()