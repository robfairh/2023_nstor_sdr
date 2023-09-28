import os
import sys
import input_definition as indef


cells = """c
c Cells
c
"""
surfaces = """
c
c Surfaces
c
"""
materials = """
c
c Materials
c
c Helium
m1000
     2004.00c -1.00
"""
for l, asse_list in indef.assemblies.items():
     for asse in asse_list:
          sp = asse.split('_')
          if len(sp) == 2:
               cell, surface, material = indef.control(l, sp[0])
          else:
               cell, surface, material = indef.fuel(l, sp[0])
          cells += cell
          surfaces += surface
          materials += material

cell, surface, material = indef.reflector()
cells += cell
surfaces += surface
materials += material

surfaces += """c
8000 c/z  0 0   175
8001 c/z  0 0   325
8002 c/z  0 0   425
8003 c/z  0 186.6  11.535
c
8010 pz  834
8011 pz  904
8012 pz 1074
"""

cells += """c
c SDR
8000 9996  -1.164e-03    9130 -8001 9131 -9132       imp:n=1
8001 9996  -1.164e-03   -8001 9132 -8010             imp:n=1
8002 9997  -2.3          8001 -8002 9131 -8010       imp:n=1
c
8003 9996  -1.164e-03   -8000 8010 -8011             imp:n=1
8004 9997  -2.3          8000 -8002 8010 -8011       imp:n=1
c
8005 9996  -1.164e-03   -8003 8011 -8012             imp:n=1
8006 9996  -1.164e-03    8003 -8002 8011 -8012       imp:n=1
c
9999 0                   8002:-9131:8012             imp:n=0
"""

materials += """c
c SDR calculation
m9996  $ Air                  density = -1.164e-03
     7014.80c -0.76
     8016.80c -0.24
m9997  $ Portland concrete
     1001.00c  -0.01
     6012.00c  -0.0009
     6013.00c  -0.0001
     8016.00c  -0.52911
     11023.00c  -0.016
     12024.00c  -0.001559
     12025.00c  -0.000206
     12026.00c  -0.000235
     13027.00c  -0.033872
     14028.00c  -0.309886
     14029.00c  -0.016343
     14030.00c  -0.010791
     19039.00c  -0.012087
     19041.00c  -0.000913
     20040.00c  -0.042574
     20042.00c  -0.000461
     20044.00c  -0.000966
     26054.00c  -0.000811
     26056.00c  -0.012903
     26057.00c  -0.000286
mt9997 grph.25t
"""

if 'mcnp' not in os.listdir('.'):
     os.mkdir('mcnp')

filename = "mcnp/sdr-ex.i"
with open(filename, 'w+') as f:
    f.write(indef.comments)
    f.write(cells)
    f.write(surfaces)
    f.write(materials)
