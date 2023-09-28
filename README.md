# README

# verification

Files:
* plots.py: plots figures comparing reference and repeated structures cases

All the following cases contain:
* mcnp1: MCNP input file
* results_heat_cell991.csv: csv files with delayed heating "H_T" by decay time step

## reference

MOAA calculates the depletion of cells:

101,102,103,104,105,106,107,108,109,110,
111,112,113,114,115,116,117,118,119,120,
121,122,123,124,125,126,127,128,129,130,
131,132,133,134,135,136,137,138,139,140,
141,142,143,144,145,146,147,148,149,150,
151,152,153,154,155,156,157,158,159,160,
161,162,163,164,991,

## repeated_structures

MOAA calculates the depletion of cells:

100,991

## repeated_structures2

MOAA calculates the depletion of cells:

101,102,103,104,105,106,107,108,109,110,
111,112,113,114,115,116,991


# agr-1

Files:
* bench.template: contains ATR quarter model, with some fillable sections
* MOAA_burnup_FIMA.csv: MOAA burnup results
* \*.csv files: contain benchmark data for power, neck shim insertion condition, and control drum angle
* create_files.py: automates the creation of the input files based on the \*.csv files: 
  * bench_{cycle}: MCNP input files for each cycle
  * sdr-agr.i: MCNP input files for the shutdown-dose rate calculations
* plots.py: plots burnup vs axial location and calculates the contribution from each photon source


MOAA calculates the depletion of cells:

* Stainless steel sections:
99971,91000,92000,93000,94000,
95000,96000,91091,92091,93091,
94091,95091,96091,91098,92098,
93098,94098,95098,96098,99980,
99981,99982,99983,99984,99985,

* Graphite spacers:
91001,92001,93001,94001,95001,
96001,91081,92081,93081,94081,
95081,96081,

* Borated graphite holder:
91080,92080,93080,94080,95080,
96080,

* Hf shroud:
91092,92092,93092,94092,95092,
96092,

* Fuel cells:
91101,91121,91141,91161,91201,
91221,91241,91261,91301,91321,
91341,91361,92101,92121,92141,
92161,92201,92221,92241,92261,
92301,92321,92341,92361,93101,
93121,93141,93161,93201,93221,
93241,93261,93301,93321,93341,
93361,94101,94121,94141,94161,
94201,94221,94241,94261,94301,
94321,94341,94361,95101,95121,
95141,95161,95201,95221,95241,
95261,95301,95321,95341,95361,
96101,96121,96141,96161,96201,
96221,96241,96261,96301,96321,
96341,96361,


# micro

