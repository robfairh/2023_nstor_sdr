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

cells += """c
9999 0                   9130:-9131:9132                 imp:n=0
"""

if 'mcnp' not in os.listdir('.'):
     os.mkdir('mcnp')

filename = "mcnp/micro.i"
with open(filename, 'w+') as f:
    f.write(indef.comments)
    f.write(cells)
    f.write(surfaces)
    f.write(materials)
    f.write(indef.source)
