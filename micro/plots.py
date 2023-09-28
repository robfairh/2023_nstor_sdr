import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter


# my results
time = np.array([1e-05, 1.0, 1.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5])
time = np.cumsum(time)
keff = np.array([1.26797, 1.23563, 1.20865, 1.16463, 1.12299, 1.08451, 1.04860, 1.01426, 0.98096, 0.94877])

time_burn = np.interp([1.0], keff[::-1], time[::-1])[0]
print(f"Core life time: {time}")

plt.figure()
plt.plot(time, keff, marker='o', label='simplified')
micro = u"\u03bc"
# plt.legend()
plt.title(f'Exit time: {time_burn:.2f} years')
plt.ylabel('Keff [-]')
plt.xlabel('Time [years]')
plt.savefig('keff-irrad-time', dpi=300, bbox_inches="tight")
