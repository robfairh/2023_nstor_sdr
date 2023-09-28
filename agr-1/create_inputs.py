import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from jinja2 import Environment, FileSystemLoader


def define_irrad_case(filename, time, power):
    irradiation_case = f"""
    mcnp_input_file: {filename}
    time: {time:.2f} days
    power: {power:.2f} MW"""
    return irradiation_case


def find_closest_value(angles, ave_angle):
    n_angles = np.array(angles) - ave_angle
    idx = np.absolute(n_angles).argmin()
    return angles[idx]


def calculate_radii(thick):
    radii = [sum(thick[:i+1])/1e4 for i in range(len(thick))]
    return radii


def compact_surfaces(s, thick, n_particles):
    radii = calculate_radii(thick)

    vol_compact = np.pi * 0.63500 ** 2 * (10.16/4 - 0.16 - 0.2)
    vol_triso = 4./3 * np.pi * radii[-1]**3
    vol_triso_tot = vol_triso * n_particles
    pf = vol_triso_tot / vol_compact
    vol_cube = vol_triso/pf
    side = vol_cube**(1./3) / 2

    surfaces=f"""\nc
{s}1 so   {radii[0]:.6f}  $ Kernel
{s}2 so   {radii[1]:.6f}  $ Buffer
{s}3 so   {radii[2]:.6f}  $ InnerPyC
{s}4 so   {radii[3]:.6f}  $ SiC
{s}5 so   {radii[4]:.6f}  $ OuterPyC
{s}6 so   1.000000  $ Matrix
{s}7 rpp -{side:.6f} {side:.6f} -{side:.6f} {side:.6f} -0.050000 0.050000
{s}8 rpp -0.650000 0.650000 -0.650000 0.650000 -{side:.6f} {side:.6f}
{s}9 c/z  0.0 0.0   0.6500"""

    return surfaces


def compact_cells(cap, stack, comp, particle):
    c = int(90000 + cap*1000 + stack*100 + 2*(comp-1)*10)
    s = int(9000 + cap*100 + stack*10 + comp)
    m1 = int(9000 + cap*100 + stack*10 + comp)
    u = int(cap*100 + stack*10 + comp)

    if particle == 'baseline':
        dens = [10.924, 1.100, 1.904, 3.208, 1.907, 1.297]
        vol = 0.093015
    elif particle == 'variant1':
        dens = [10.924, 1.100, 1.853, 3.206, 1.898, 1.219]
        vol = 0.092813
    elif particle == 'variant2':
        dens = [10.924, 1.100, 1.912, 3.207, 1.901, 1.256]
        vol = 0.091694
    elif particle == 'variant3':
        dens = [10.924, 1.100, 1.904, 3.205, 1.911, 1.344]
        vol = 0.092522

    cells = f"""c Capsule {cap}, stack {stack}, compact #{comp}
{c+1} {m1} -{dens[0]:.3f} -{s}1         u={u}4 vol={vol:.6f}    $ Kernel
{c+2} 9090 -{dens[1]:.3f}  {s}1 -{s}2  u={u}4                 $ Buffer
{c+3} 9091 -{dens[2]:.3f}  {s}2 -{s}3  u={u}4                 $ IPyC
{c+4} 9092 -{dens[3]:.3f}  {s}3 -{s}4  u={u}4                 $ SiC
{c+5} 9093 -{dens[4]:.3f}  {s}4 -{s}5  u={u}4                 $ OPyC
{c+6} 9094 -{dens[5]:.3f}  {s}5         u={u}4                 $ SiC Matrix
{c+7} 9094 -{dens[5]:.3f} -{s}6         u={u}5                 $ SiC Matrix
"""

    if particle == 'baseline':
        cells += f"""c
{c+8} 0   -{s}7  u={u}6 lat=1  fill=-7:7 -7:7 0:0  $ Lattice of Particles
     {u}5 {u}5 {u}5 {u}5 {u}5 {u}5 {u}4 {u}4 {u}4 {u}5 {u}5 {u}5 {u}5 {u}5 {u}5 $ Layer
     {u}5 {u}5 {u}5 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}5 {u}5 {u}5
     {u}5 {u}5 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}5 {u}5
     {u}5 {u}5 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}5 {u}5
     {u}5 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}5
     {u}5 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}5
     {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4
     {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4
     {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4
     {u}5 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}5
     {u}5 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}5
     {u}5 {u}5 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}5 {u}5
     {u}5 {u}5 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}5 {u}5
     {u}5 {u}5 {u}5 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}5 {u}5 {u}5
     {u}5 {u}5 {u}5 {u}5 {u}5 {u}5 {u}4 {u}4 {u}4 {u}5 {u}5 {u}5 {u}5 {u}5 {u}5
"""

    elif particle == 'variant1':
        cells += f"""c
{c+8} 0   -{s}7  u={u}6 lat=1  fill=-7:7 -7:7 0:0  $ Lattice of Particles
     {u}5 {u}5 {u}5 {u}5 {u}5 {u}5 {u}4 {u}4 {u}4 {u}5 {u}5 {u}5 {u}5 {u}5 {u}5 $ Layer
     {u}5 {u}5 {u}5 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}5 {u}5 {u}5
     {u}5 {u}5 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}5 {u}5
     {u}5 {u}5 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}5
     {u}5 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}5
     {u}5 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}5
     {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4
     {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4
     {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4
     {u}5 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}5
     {u}5 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}5
     {u}5 {u}5 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}5 {u}5
     {u}5 {u}5 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}5 {u}5
     {u}5 {u}5 {u}5 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}5 {u}5 {u}5
     {u}5 {u}5 {u}5 {u}5 {u}5 {u}5 {u}4 {u}4 {u}4 {u}5 {u}5 {u}5 {u}5 {u}5 {u}5
"""

    elif particle == 'variant2':
        cells += f"""c
{c+8} 0   -{s}7  u={u}6 lat=1  fill=-7:7 -7:7 0:0  $ Lattice of Particles
     {u}5 {u}5 {u}5 {u}5 {u}5 {u}5 {u}4 {u}4 {u}4 {u}5 {u}5 {u}5 {u}5 {u}5 {u}5 $ Layer
     {u}5 {u}5 {u}5 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}5 {u}5 {u}5 {u}5
     {u}5 {u}5 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}5 {u}5
     {u}5 {u}5 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}5 {u}5
     {u}5 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}5
     {u}5 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}5
     {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4
     {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4
     {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4
     {u}5 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}5
     {u}5 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}5
     {u}5 {u}5 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}5 {u}5
     {u}5 {u}5 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}5 {u}5
     {u}5 {u}5 {u}5 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}5 {u}5 {u}5
     {u}5 {u}5 {u}5 {u}5 {u}5 {u}5 {u}4 {u}4 {u}4 {u}5 {u}5 {u}5 {u}5 {u}5 {u}5
"""

    elif particle == 'variant3':
        cells += f"""c
{c+8} 0   -{s}7  u={u}6 lat=1  fill=-7:7 -7:7 0:0  $ Lattice of Particles
     {u}5 {u}5 {u}5 {u}5 {u}5 {u}5 {u}4 {u}4 {u}4 {u}5 {u}5 {u}5 {u}5 {u}5 {u}5 $ Layer
     {u}5 {u}5 {u}5 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}5 {u}5 {u}5
     {u}5 {u}5 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}5 {u}5
     {u}5 {u}5 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}5 {u}5
     {u}5 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}5
     {u}5 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}5
     {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4
     {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4
     {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4
     {u}5 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}5
     {u}5 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}5
     {u}5 {u}5 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}5 {u}5
     {u}5 {u}5 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}5 {u}5
     {u}5 {u}5 {u}5 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}4 {u}5 {u}5 {u}5
     {u}5 {u}5 {u}5 {u}5 {u}5 {u}5 {u}4 {u}4 {u}4 {u}5 {u}5 {u}5 {u}5 {u}5 {u}5
"""

    cells += f"""c
{c+9} 9094 -{dens[5]} -{s}9    u={u}7                 $ Matrix
{c+10} 0  -{s}8 u={u}0 lat=1  fill=0:0 0:0 -15:15 {u}7 2R {u}6 24R {u}7 2R
"""
    return cells


def compact_center(cap, stack, comp):
     
    if stack == 1:
        cx, cy = 25.547039, -24.553123
    elif stack == 2:
        cx, cy = 24.553123, -25.547039
    elif stack == 3:
        cx, cy = 25.910838, -25.910838

    if cap == 1:
        cz = 17.81810
    elif cap == 2:
        cz = 33.04540
    elif cap == 3:
        cz = 48.27270
    elif cap == 4:
        cz = 63.50000
    elif cap == 5:
        cz = 78.72730
    elif cap == 6:
        cz = 93.95460

    cz += (comp-1)*2.54 + 0.2 + (2.54-0.16-0.2)/2
    # print(f'cz: {cz:.6f}')
    return cx, cy, cz

# --------------------
#
# --- MCNP INPUT FILES
#
# --------------------
thick = {}
thick['baseline'] = [349.7/2,  103.5, 39.4, 35.3, 41.0]
thick['variant1'] = [349.7/2,  102.5, 40.5, 35.7, 41.1]
thick['variant2'] = [349.7/2,  102.9, 40.1, 35.0, 39.8]
thick['variant3'] = [349.7/2,  104.2, 38.8, 35.9, 39.3]

n_particles = {}
n_particles['baseline'] = 4154
n_particles['variant1'] = 4145
n_particles['variant2'] = 4095
n_particles['variant3'] = 4132

cells = """c
99970 8900 -1.164e-03 -97064     98000 -98001  $ bottom air filler
99971 9000 -8.03      -97064     98001 -98002  vol=8.6736  $ capsule support
99972 9040 -1.015     -97064     98002 -98003  $ graphite spacer
"""

capsule_particle = {
    1: 'variant3',
    2: 'variant2',
    3: 'baseline',
    4: 'variant3',
    5: 'variant1',
    6: 'baseline',
}

stack_cylinders = {
    1: (97011, 97012),
    2: (97021, 97022),
    3: (97031, 97032),
}

for cap, particle in capsule_particle.items():

    limit = 98004 + (cap-1)*7
    cells += f"""c Capsule {cap}
9{cap}000 900{cap} -8.03      -97064         {limit-1} -{limit}  vol=6.179954  $ bottom support: ss316L
9{cap}001 904{cap} -1.015     -97060         {limit} -{limit+1}  vol=5.027315  $ lower graphite spacer: graphite
"""

    for stack in range(1, 4):
        c = int(cap*1000 + stack*100)
        s1, s2 = stack_cylinders[stack]
        cells += f"""c
9{c} 8902  1.2493e-4  {s1} -{s2}  {limit+1} -{limit+3}  $ stack {stack} gas gap 
"""
        for comp in range(1, 5):
            c = int(90000 + cap*1000 + stack*100 + 2*(comp-1)*10)
            u = int(cap*100 + stack*10 + comp)
            cells += compact_cells(cap, stack, comp, particle)
            cx, cy, cz = compact_center(cap, stack, comp)

            if comp == 1:
                cells += f"""c
{c+11} 0               -{s1}         {limit+1} -{limit+47} fill={u}0  ({cx:.6f} {cy:.6f} {cz:.6f})
"""
            elif comp == 2:
                cells += f"""c
{c+11} 0               -{s1}         {limit+47} -{limit+2} fill={u}0  ({cx:.6f} {cy:.6f} {cz:.6f})
"""
            elif comp == 3:
                cells += f"""c
{c+11} 0               -{s1}         {limit+2} -{limit+48} fill={u}0  ({cx:.6f} {cy:.6f} {cz:.6f})
"""
            elif comp == 4:
                cells += f"""c
{c+11} 0               -{s1}         {limit+48} -{limit+3} fill={u}0  ({cx:.6f} {cy:.6f} {cz:.6f})
"""

    if cap == 1:
        cells += f"""c
9{cap}080 9070 -1.7695     97012 97022 97032 -97060   {limit+1} -{limit+3}  vol=34.27310  $ compact holder: borated graphite
"""
    elif cap == 2:
        cells += f"""c
9{cap}080 9072 -1.7788     97012 97022 97032 -97060   {limit+1} -{limit+3}  vol=34.27310  $ compact holder: borated graphite
"""
    elif cap == 3:
        cells += f"""c
9{cap}080 9073 -1.7788     97012 97022 97032 -97060   {limit+1} -{limit+3}  vol=34.27310  $ compact holder: borated graphite
"""
    elif cap == 4:
        cells += f"""c
9{cap}080 9074 -1.7788     97012 97022 97032 -97060   {limit+1} -{limit+3}  vol=34.27310  $ compact holder: borated graphite
"""
    elif cap == 5:
        cells += f"""c
9{cap}080 9075 -1.7788     97012 97022 97032 -97060   {limit+1} -{limit+3}  vol=34.27310  $ compact holder: borated graphite
"""
    elif cap == 6:
        cells += f"""c
9{cap}080 9071 -1.7695     97012 97022 97032 -97060   {limit+1} -{limit+3}  vol=34.27310  $ compact holder: borated graphite
"""

    cells += f"""c
9{cap}081 905{cap} -0.95      -97060         {limit+3} -{limit+4}  vol=6.297955  $ upper graphite spacer: graphite
9{cap}090 8902  1.2493e-4  97060 -97061  {limit} -{limit+4}  $ holder gas gap: he
9{cap}091 901{cap} -8.03       97061 -97062  {limit} -{limit+4}  vol=4.052581  $ inner wall: ss316L
9{cap}092 908{cap}  4.4348e-2  97062 -97063  {limit} -{limit+4}  vol=3.057745  $ middle wall: hf
9{cap}094 8902  1.2493e-4  97063 -97064  {limit} -{limit+4}  $ gas gap: he
9{cap}098 902{cap} -8.03      -97064         {limit+4} -{limit+5}  vol=8.239939  $ top support: ss316L
"""

    if cap < 6:
        cells += f"""c
9{cap}099 8902  1.2493e-4  -97064         {limit+5} -{limit+6}  $ capsule {cap}-{cap+1}: gas plenum: he
"""

cells += f"""c
99973 8900 -1.164e-03 -97064     98044 -98045 $ top air filler
99980 9031 -8.03       97064 -97065  98000 -98090 vol=49.216462  $ capsule wall: ss316L
99981 9032 -8.03       97064 -97065  98090 -98091 vol=22.532566  $ capsule wall: ss316L
99982 9033 -8.03       97064 -97065  98091 -98092 vol=22.532566  $ capsule wall: ss316L
99983 9034 -8.03       97064 -97065  98092 -98093 vol=22.532566  $ capsule wall: ss316L
99984 9035 -8.03       97064 -97065  98093 -98094 vol=22.532566  $ capsule wall: ss316L
99985 9036 -8.03       97064 -97065  98094 -98045 vol=52.339826  $ capsule wall: ss316L
99990 8901 -0.9853     97065 -97066  98000 -98045 $ ATR channel: h2o"""

surfaces = """c
97011 c/z   25.547039 -24.553123   0.63500  $ Stack 1 Compact outer R
97012 c/z   25.547039 -24.553123   0.64135  $ Stack 1 Gas gap outer R
97021 c/z   24.553123 -25.547039   0.63500  $ Stack 2 Compact outer R
97022 c/z   24.553123 -25.547039   0.64135  $ Stack 2 Gas gap outer R
97031 c/z   25.910838 -25.910838   0.63500  $ Stack 3 Compact outer R
97032 c/z   25.910838 -25.910838   0.64135  $ Stack 3 Gas gap outer R
c
97060 c/z   25.337    -25.337      1.51913  $ Compact holder outer R
97061 c/z   25.337    -25.337      1.58750  $ Gas gap outer R
97062 c/z   25.337    -25.337      1.62179  $ Inner Capsule wall outer R
97063 c/z   25.337    -25.337      1.64719  $ Middle Capsule wall (Hf or SS) outer R
97064 c/z   25.337    -25.337      1.64846  $ Gas gap outer R
97065 c/z   25.337    -25.337      1.78562  $ Capsule wall outer R
97066 c/z   25.337    -25.337      1.90500  $ B10 channel outer R
c
98000 pz   -2.54000
98001 pz   13.65758
98002 pz   14.67358
98003 pz   16.40078
98004 pz   17.12468
98005 pz   17.81810
98051 pz   20.35810  $ calculated
98006 pz   22.89810
98052 pz   25.43810  $ calculated
98007 pz   27.97810
98008 pz   28.84678
98009 pz   29.81198
98090 pz   30.72003  $ calculated 
98010 pz   31.62808
98011 pz   32.35198
98012 pz   33.04540
98058 pz   35.58540  $ calculated
98013 pz   38.12540
98059 pz   40.66540  $ calculated
98014 pz   43.20540
98015 pz   44.07408
98016 pz   45.03928
98091 pz   45.94733  $ calculated
98017 pz   46.85538
98018 pz   47.57928
98019 pz   48.27270
98065 pz   50.81270  $ calculated
98020 pz   53.35270
98066 pz   55.89270  $ calculated
98021 pz   58.43270
98022 pz   59.30138
98023 pz   60.26658
98092 pz   61.17463  $ calculated
98024 pz   62.08268
98025 pz   62.80658
98026 pz   63.50000
98072 pz   66.04000  $ calculated
98027 pz   68.58000
98073 pz   71.12000  $ calculated
98028 pz   73.66000
98029 pz   74.52868
98030 pz   75.49388
98093 pz   76.40193  $ calculated
98031 pz   77.30998
98032 pz   78.03388
98033 pz   78.72730
98079 pz   81.26730  $ calculated
98034 pz   83.80730
98080 pz   86.34730  $ calculated
98035 pz   88.88730
98036 pz   89.75598
98037 pz   90.72118
98094 pz   91.62923  $ calculated
98038 pz   92.53728
98039 pz   93.26118
98040 pz   93.95460
98086 pz   96.49460  $ calculated
98041 pz   99.03460
98087 pz  101.57460  $ calculated
98042 pz  104.11460
98043 pz  104.98328
98044 pz  105.94848
98045 pz  127.00000"""
for cap, particle in capsule_particle.items():
    for stack in range(1, 4):
        for comp in range(1, 5):
            s = int(9000 + cap*100 + stack*10 + comp)
            surfaces += compact_surfaces(s, thick[particle], n_particles[particle])

materials = """c 
c air, density = -1.164e-03
m8900
      7014.80c -0.76
      8016.80c -0.24
c
c light water, 62 C, 2.5 MPa, density ~= 0.9853 g/mc3
m8901
      1001.00c  2
      8016.00c  1
c
c helium, NT = 1.24931E-04 a/b/cm
m8902
      2004.00c  1
c"""

materials_ss = """
     24050.00c -0.00653131
     24052.00c -0.14263466
     24053.00c -0.01730730
     24054.00c -0.00352673
     25055.00c -0.02000000
     26054.00c -0.03799186
     26056.00c -0.60409084
     26057.00c -0.01336731
     28058.00c -0.08053185
     28060.00c -0.03185216
     28061.00c -0.00124553
     28062.00c -0.00506366
     28064.00c -0.00130679
     42092.00c -0.00354458
     42094.00c -0.00220235
     42095.00c -0.00395701
     42096.00c -0.00424858
     42097.00c -0.00239899
     42098.00c -0.00612312
     42100.00c -0.00252537
c"""

materials += f"""\nc ss316l, density = 8.03 g/cm3
m9000"""
materials += materials_ss

for idx in range(0, 4):
    for cap, particle in capsule_particle.items():
        materials += f"""\nc ss316l, density = 8.03 g/cm3
m90{idx}{cap}"""
        materials += materials_ss

materials_graph = """
      6012.00c  0.9890
      6013.00c  0.0110
c"""

materials += f"""\nc pure graphite (lower spacer) density = 1.015 g/cm3
m9040"""
materials += materials_graph

for cap, particle in capsule_particle.items():
    materials += f"""\nc pure graphite (lower spacer) density = 1.015 g/cm3
m904{cap}"""
    materials += materials_graph

    materials += f"""\nc pure graphite (upper spacer) density = 0.95 g/cm3
m905{cap}"""
    materials += materials_graph

materials += """\nc borated graphite holder, 4.76 atom percent boron, 1.7695 g/cm3, capsule 1,6
m9070    
      6012.00c  8.4900E-2
      5010.20c  8.4496E-4
      5011.00c  3.4003E-3
m9071    
      6012.00c  8.4900E-2
      5010.20c  8.4496E-4
      5011.00c  3.4003E-3
c
c borated graphite holder, 6.05 atom percent boron, 1.7788 g/cm3, capsule 2-5
m9072    
      6012.00c  8.4300E-2
      5010.20c  1.0804E-3
      5011.00c  4.3476E-3
m9073    
      6012.00c  8.4300E-2
      5010.20c  1.0804E-3
      5011.00c  4.3476E-3
m9074    
      6012.00c  8.4300E-2
      5010.20c  1.0804E-3
      5011.00c  4.3476E-3
m9075    
      6012.00c  8.4300E-2
      5010.20c  1.0804E-3
      5011.00c  4.3476E-3
c"""

materials_hf = """
      8016.00c  1.3500E-4
      6012.00c  4.4300E-5
     14028.00c  6.3341E-6
     14029.00c  3.2289E-7
     14030.00c  2.1297E-7
     40090.00c  1.0169E-3
     40091.00c  2.2288E-4
     40092.00c  3.4029E-4
     40094.00c  3.4626E-4
     40096.00c  5.5719E-5
     72174.00c  6.7512E-5
     72176.00c  2.1934E-3
     72177.00c  7.8473E-3
     72178.00c  1.1431E-2
     72179.00c  5.7955E-3
     72180.00c  1.4845E-2
c"""

for cap, particle in capsule_particle.items():
    materials += f"""\nc hafnium shroud
m908{cap}"""
    materials += materials_hf


materials +="""\nc
c TRISO
c
c buffer, density: 1.10 g/cm3
m9090
      6012.00c  0.9890  
      6013.00c  0.0110
c
c IPyc, density= baseline: 1.904, variant1: 1.853, variant2: 1.912, variant3: 1.904 g/cm3
m9091
      6012.00c  0.9890  
      6013.00c  0.0110
c
c SiC, density= baseline: 3.208, variant1: 3.206, variant2: 3.207, variant3: 3.205 g/cm3
m9092
     14028.00c  0.9220
     14029.00c  0.0470
     14030.00c  0.0310
      6012.00c  0.9890  
      6013.00c  0.0110
c
c OPyc, density= baseline: 1.907, variant1: 1.898, variant2: 1.901, variant3: 1.911 g/cm3
m9093
      6012.00c  0.9890  
      6013.00c  0.0110
c
c matrix, density= baseline: 1.297, variant1: 1.219, variant2: 1.256, variant3: 1.344 g/cm3
m9094
      6012.00c  0.9890  
      6013.00c  0.0110
c"""

materials_uco = """
     92234.00c  3.34179E-03
     92235.00c  1.99636E-01
     92236.00c  1.93132E-04
     92238.00c  7.96829E-01
      6012.00c  0.3217217
      6013.00c  0.0035783
      8016.00c  1.3613
c"""

for cap, particle in capsule_particle.items():
    for stack in range(1, 4):
        for comp in range(1, 5):
            materials += f"""\nc kernel, UCO: density=10.924 g/cm3
m9{cap}{stack}{comp}"""
            materials += materials_uco


#
# Control Drums
#
cycles = [
    '138B', '139A', '139B', '140A',
    '140B', '141A', '142A', '142B',
    '143A', '143B', '144A', '144B',
    '145A'
    ]

useful_lobes = ['ne', 'c', 'se']

# in days
shutdown_duration = [
    15, 95, 15, 14,
    9, 56, 14, 24,
    16, 20, 15, 62
    ]

shutdown_cycle = dict(zip(cycles[:-1], shutdown_duration))

useful_drums = ['ne', 'se']

drum_surfaces = {}
angles = [0, 25, 40, 50, 60, 65, 75, 80, 85, 100, 120, 125, 150]
ne_surfaces = []

surf = f"""c
  981   c/z    44.2436  -6.3119  9.195       $ DRUM E1 AT 0 DEGREES
  982   c/z    30.3697 -17.5600  9.195       $ DRUM E2 AT 0 DEGREES
c """
ne_surfaces.append(surf)
surf = f"""c
  981   c/z   43.4011  -10.2020  9.195       $ DRUM E1 AT 25 DEGREES
  982   c/z   28.6527  -21.1509  9.195       $ DRUM E2 AT 25 DEGREES
c"""
ne_surfaces.append(surf)
surf = f"""c
  981   c/z    43.7261 -12.5803  9.195       $ DRUM E1 AT 40 DEGREES
  982   c/z    28.4203 -23.5400  9.195       $ DRUM E2 AT 40 DEGREES
c"""
ne_surfaces.append(surf)
surf = f"""c
  981   c/z   44.2816  -14.0837  9.195       $ DRUM E1 AT 50 DEGREES
  982   c/z   28.6141  -25.1311  9.195       $ DRUM E2 AT 50 DEGREES
c"""
ne_surfaces.append(surf)
surf = f"""c
  981   c/z    45.0898 -15.4678  9.195       $ DRUM E1 AT 60 DEGREES
  982   c/z    29.0812 -26.6643  9.195       $ DRUM E2 AT 60 DEGREES
c"""
ne_surfaces.append(surf)
surf = f"""c
  981   c/z    45.5812 -16.1018  9.195       $ DRUM E1 AT 65 DEGREES
  982   c/z    29.4132 -27.3945  9.195       $ DRUM E2 AT 65 DEGREES
c"""
ne_surfaces.append(surf)
surf = f"""c
  981   c/z   46.7201  -17.2296  9.195       $ DRUM E1 AT 75 DEGREES
  982   c/z   30.2612  -28.7546  9.195       $ DRUM E2 AT 75 DEGREES
c"""
ne_surfaces.append(surf)
surf = f"""c
  981   c/z    47.3589 -17.7148  9.195       $ DRUM E1 AT 80 DEGREES
  982   c/z    30.7708 -29.3741  9.195       $ DRUM E2 AT 80 DEGREES
c"""
ne_surfaces.append(surf)
surf = f"""c
  981   c/z    48.0375 -18.1425  9.195       $ DRUM E1 AT 85 DEGREES
  982   c/z    31.3325 -29.9467  9.195       $ DRUM E2 AT 85 DEGREES
c"""
ne_surfaces.append(surf)
surf = f"""c
  981   c/z   50.2597  -19.0502  9.195       $ DRUM E1 AT 100 DEGREES
  982   c/z   33.2854  -31.3425  9.195       $ DRUM E2 AT 100 DEGREES
c"""
ne_surfaces.append(surf)
surf = f"""c
  981   c/z    53.4422 -19.3130  9.195       $ DRUM E1 AT 120 DEGREES
  982   c/z    36.3215 -32.3323  9.195       $ DRUM E2 AT 120 DEGREES
c"""
ne_surfaces.append(surf)
surf = f"""c
  981   c/z   54.2370  -19.2044  9.195       $ DRUM E1 AT 125 DEGREES
  982   c/z   37.1199  -32.4099  9.195       $ DRUM E2 AT 125 DEGREES
c"""
ne_surfaces.append(surf)
surf = f"""c
  981   c/z    57.9068 -17.6632  9.195       $ DRUM E1 AT 150 DEGREES
  982   c/z    41.0463 -31.7568  9.195       $ DRUM E2 AT 150 DEGREES
c"""
ne_surfaces.append(surf)

drum_surfaces['ne'] = dict(zip(angles, ne_surfaces))


se_surfaces = []
surf = f"""
  983   c/z    17.5600 -30.3697  9.195       $ DRUM E3 AT 0 DEGREES
  984   c/z     6.3119 -44.2436  9.195       $ DRUM E4 AT 0 DEGREES
c"""
se_surfaces.append(surf)
surf = f"""
  983   c/z   21.1509  -28.6527  9.195       $ DRUM E3 AT 25 DEGREES
  984   c/z   10.2020  -43.4011  9.195       $ DRUM E4 AT 25 DEGREES
c"""
se_surfaces.append(surf)
surf = f"""
  983   c/z    23.5400 -28.4203  9.195       $ DRUM E3 AT 40 DEGREES
  984   c/z    12.5803 -43.7261  9.195       $ DRUM E4 AT 40 DEGREES
c"""
se_surfaces.append(surf)
surf = f"""
  983   c/z   25.1311  -28.6141  9.195       $ DRUM E3 AT 50 DEGREES
  984   c/z   14.0837  -44.2816  9.195       $ DRUM E4 AT 50 DEGREES
c"""
se_surfaces.append(surf)
surf = f"""
  983   c/z    26.6643 -29.0812  9.195       $ DRUM E3 AT 60 DEGREES
  984   c/z    15.4678 -45.0898  9.195       $ DRUM E4 AT 60 DEGREES
c"""
se_surfaces.append(surf)
surf = f"""
  983   c/z    27.3945 -29.4132  9.195       $ DRUM E3 AT 65 DEGREES
  984   c/z    16.1018 -45.5812  9.195       $ DRUM E4 AT 65 DEGREES
c"""
se_surfaces.append(surf)
surf = f"""
  983   c/z   28.7546  -30.2612  9.195       $ DRUM E3 AT 75 DEGREES
  984   c/z   17.2296  -46.7201  9.195       $ DRUM E4 AT 75 DEGREES
c"""
se_surfaces.append(surf)
surf = f"""
  983   c/z    29.3741 -30.7708  9.195       $ DRUM E3 AT 80 DEGREES
  984   c/z    17.7148 -47.3589  9.195       $ DRUM E4 AT 80 DEGREES
c"""
se_surfaces.append(surf)
surf = f"""
  983   c/z    29.9467 -31.3325  9.195       $ DRUM E3 AT 85 DEGREES
  984   c/z    18.1425 -48.0375  9.195       $ DRUM E4 AT 85 DEGREES
c"""
se_surfaces.append(surf)
surf = f"""
  983   c/z   31.3425  -33.2854  9.195       $ DRUM E3 AT 100 DEGREES
  984   c/z   19.0502  -50.2597  9.195       $ DRUM E4 AT 100 DEGREES
c"""
se_surfaces.append(surf)
surf = f"""
  983   c/z    32.3323 -36.3215  9.195       $ DRUM E3 AT 120 DEGREES
  984   c/z    19.3130 -53.4422  9.195       $ DRUM E4 AT 120 DEGREES
c"""
se_surfaces.append(surf)
surf = f"""
  983   c/z   32.4099  -37.1199  9.195       $ DRUM E3 AT 125 DEGREES
  984   c/z   19.2044  -54.2370  9.195       $ DRUM E4 AT 125 DEGREES
c"""
se_surfaces.append(surf)
surf = f"""
  983   c/z    31.7568 -41.0463  9.195       $ DRUM E3 AT 150 DEGREES
  984   c/z    17.6632 -57.9068  9.195       $ DRUM E4 AT 150 DEGREES
c"""
se_surfaces.append(surf)

drum_surfaces['se'] = dict(zip(angles, se_surfaces))

#
# TIME
#
power_df = pd.read_csv('power.csv', index_col="Cumulative Timestep")
cycles_by_timestep = power_df['Cycle'].to_list()
time_interval = power_df["Time Interval(hrs)"].to_numpy()
time_interval_by_cycle = {}
cum_time = {}
prev = 0
for cycle in cycles:
    time_steps = cycles_by_timestep.count(cycle)
    time_interval_by_cycle[cycle] = time_interval[prev:prev+time_steps]
    cum_time[cycle] = np.cumsum(time_interval_by_cycle[cycle])
    prev += time_steps

#
# OSCC
#
oscc_df = pd.read_csv('oscc.csv', index_col="Cumulative Timestep")
oscc = {}
oscc['nw'] = oscc_df["NWOSCC(degrees)"].to_numpy()
oscc['sw'] = oscc_df["SWOSCC(degrees)"].to_numpy()
oscc['ne'] = oscc_df["NEOSCC(degrees)"].to_numpy()
oscc['se'] = oscc_df["SEOSCC(degrees)"].to_numpy()

oscc_by_cycle = {}
prev = 0
for cycle in cycles:
    time_steps = cycles_by_timestep.count(cycle)
    oscc_by_cycle[cycle] = {}
    for key, values in oscc.items():
        oscc_by_cycle[cycle][key] = values[prev:prev+time_steps]
    prev += time_steps

# Plot OSCC positions
for cycle in cycles:
    plt.figure()
    time = np.roll(cum_time[cycle], 1)
    time[0] = 0
    width = cum_time[cycle] - time
    for key, values in oscc_by_cycle[cycle].items():
        plt.step(time, values, where='post', label=key.split('_')[0].upper())
    plt.legend()
    plt.ylabel(r'Rotation angle [$^\circ$]')
    plt.xlabel('Time [h]')
    plt.savefig(f'oscc_cycle_{cycle}')
    plt.close()

# get ave oscc degree by cycle for each group (ne, se)
oscc_surfaces = {}
for cycle, angle_by_group in oscc_by_cycle.items():
    oscc_surfaces[cycle] = """"""
    for group, angle in angle_by_group.items():
        if group in useful_drums:
            ave_angle = (angle * time_interval_by_cycle[cycle]).sum() / cum_time[cycle][-1]
            angle = find_closest_value(angles, ave_angle)
            # print(ave_angle, angle)
            oscc_surfaces[cycle] += drum_surfaces[group][angle]

#
# Neck Shim Rods
#
neck_df = pd.read_csv('neck_shim.csv', index_col="Cumulative Timestep")
neck = {}

rods = [
    "NE 1", "NE 2", "NE 3", "NE 4", "NE 5", "NE 6",
    "SE 1", "SE 2", "SE 3", "SE 4", "SE 5", "SE 6",
    ]
for rod in rods:
    neck[rod] = neck_df[rod].to_numpy()

neck_by_cycle = {}
prev = 0
for cycle in cycles:
    time_steps = cycles_by_timestep.count(cycle)
    neck_by_cycle[cycle] = {}
    for key, values in neck.items():
        neck_by_cycle[cycle][key] = values[prev:prev+time_steps]
    prev += time_steps

# Plot Neck Shim insertion condition
for cycle in cycles:
    plt.figure()
    time = np.roll(cum_time[cycle], 1)
    time[0] = 0
    width = cum_time[cycle] - time
    for key, values in neck_by_cycle[cycle].items():
        plt.step(time, values, where='post', label=key.split('_')[0])
    plt.legend()
    plt.ylabel(r'Insertion condition')
    plt.xlabel('Time [h]')
    plt.savefig(f'neck_cycle_{cycle}')
    plt.close()

neck_materials = {
    0: (10, 1.00276E-1),
    1: (71, 4.55926E-2),
    }

neck_shim = {
    'NE 1': (702, 701, 702),
    'NE 2': (707, 706, 707),
    'NE 3': (712, 711, 712),
    'NE 4': (717, 716, 717),
    'NE 5': (722, 721, 722),
    'NE 6': (727, 726, 727),
    'SE 1': (792, 791, 792),
    'SE 2': (797, 796, 797),
    'SE 3': (802, 801, 802),
    'SE 4': (807, 806, 807),
    'SE 5': (812, 811, 812),
    'SE 6': (817, 816, 817),
}

def get_neck_shim_cells(vals, mat, rod, condition):
    state = 'withdrawn' if condition == 0 else 'inserted'

    neck_cells = f"""c
  {vals[0]}   {mat[0]} {mat[1]:.5e}    {vals[1]}   -{vals[2]}  100  -200        $ {rod} Hf neck shim - {state}
                                    -30    10        $ East Quadrant
c"""
    return neck_cells

ne_cells = {}
se_cells = {}
for cycle, rod_insertion in neck_by_cycle.items():
    ne_cells[cycle] = """"""
    se_cells[cycle] = """"""
    for rod, insertion in rod_insertion.items():
        ave_insertion = (insertion * time_interval_by_cycle[cycle]).sum() / cum_time[cycle][-1]
        condition = int(np.rint(ave_insertion))
        mat = neck_materials[condition]
        vals = neck_shim[rod]

        cell_value = get_neck_shim_cells(vals, mat, rod, condition)
        if rod.split()[-1] != '6':
            cell_value += '\n'

        if 'NE' in rod:
            ne_cells[cycle] += cell_value
        elif 'SE' in rod:
            se_cells[cycle] += cell_value

if 'mcnp' not in os.listdir('./'):
    os.mkdir('mcnp')

filename = {cycle: f'bench_{cycle}' for cycle in cycles}
env = Environment(loader=FileSystemLoader('./'))

for cycle in cycles:
    template = env.get_template('bench.template')
    full_input = template.render(
        cells=cells,
        surfaces=surfaces,
        materials=materials,
        oscc_surfaces=oscc_surfaces[cycle],
        ne_cells=ne_cells[cycle],
        se_cells=se_cells[cycle],
        )

    with open(f'mcnp/{filename[cycle]}', 'w+') as f:
        f.write(full_input)

cells += """\nc
99991 8900 -1.164e-03  (97066:-98000:98045)  -99000 $ Room
99999 0                99000
"""

surfaces += f"""\nc
c Room
99000 rpp  {(-100+25.337):.3f} {(100+25.337):.3f}  {(-100-25.337):.3f} {(100-25.337):.3f}   -2.54000 {(200-2.5):.3f}
"""

moaa_xml = 'mcnp/sdr-agr.i'
with open(moaa_xml, 'w+') as f:
    f.write('AGR PIE MCNP model\nc\nc Cells\n')
    f.write(cells)
    f.write('\nc\nc Surfaces\n')
    f.write(surfaces)
    f.write('\nc\nc Materials\n')
    f.write(materials)
    f.write('\nimp:p   1  880r  0')


# --------------------
#
# --- DEPLETION
#
# --------------------
#
# POWER
#
power = {}
power['nw_lobe_power'] = power_df["NWLobePower(MW)"].to_numpy()
power['ne_lobe_power'] = power_df["NELobePower(MW)"].to_numpy()
power['c_lobe_power'] = power_df["CLobePower(MW)"].to_numpy()
power['sw_lobe_power'] = power_df["SWLobePower(MW)"].to_numpy()
power['se_lobe_power'] = power_df["SELobePower(MW)"].to_numpy()
power['total_power'] = power_df["TotalCorePower(MW)"].to_numpy()

power_by_cycle = {}
prev = 0
for cycle in cycles:
    time_steps = cycles_by_timestep.count(cycle)
    power_by_cycle[cycle] = {}
    for key, values in power.items():
        power_by_cycle[cycle][key] = values[prev:prev+time_steps]
    prev += time_steps

# plot power vs time for all lobes
for cycle in cycles:
    plt.figure()
    time = np.roll(cum_time[cycle], 1)
    time[0] = 0
    for key, values in power_by_cycle[cycle].items():
        if 'total' not in key:
            plt.step(time, values, where='post', label=key.split('_')[0].upper())
    plt.legend()
    plt.ylabel('Power [MW]')
    plt.xlabel('Time [h]')
    plt.savefig(f'power_cycle_{cycle}')
    plt.close()

# get ave power by cycle for each lobe
e_power_by_cyle = {}
for cycle, power_by_lobe in power_by_cycle.items():
    add_power = 0
    for lobe_long, power in power_by_lobe.items():
        lobe = lobe_long.split('_')[0]
        if lobe in useful_lobes:
            ave_power = (power * time_interval_by_cycle[cycle]).sum() / cum_time[cycle][-1]
            add_power += ave_power/3
    e_power_by_cyle[cycle] = add_power

irradiation_cases = """"""
for cycle in cycles:
    time = cum_time[cycle][-1] / 24  # hours -> days
    irradiation_cases += define_irrad_case(filename[cycle], time, e_power_by_cyle[cycle])
    if cycle is not cycles[-1]:
        irradiation_cases += '\n'
        irradiation_cases += define_irrad_case(filename[cycle], shutdown_cycle[cycle], 0)
        irradiation_cases += '\n'

cells = """"""
for cap, particle in capsule_particle.items():
    for stack in range(1, 4):
        for comp in range(1, 5):
            c = int(90000 + cap*1000 + stack*100 + 2*(comp-1)*10)
            cells += f"""\n    cell number: {c+1}<{c+8}<{c+10}<{c+11}"""

print("\nPower History:")
print(irradiation_cases)
print("\nFuel cells:")
print(cells)
