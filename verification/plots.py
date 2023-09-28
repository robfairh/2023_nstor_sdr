""" Makes plots for publication """
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.cbook import get_sample_data
from matplotlib.ticker import ScalarFormatter


class ScalarFormatterClass(ScalarFormatter):
    def _set_format(self):
        self.format = "%1.2f"


def add_labels(figname):
    '''
    Adds legend to geometry image 'figname'.
    '''
    fuel = mpatches.Patch(color=(1., 0, 1.), label='Fuel')
    shell = mpatches.Patch(color=(1., 1., 0.), label='Shell')
    water = mpatches.Patch(color=(0, 0, 1.), label='Water')

    cwd = os.getcwd()
    fname = get_sample_data(f'{cwd}/{figname}')
    im = plt.imread(fname)
    plt.imshow(im)
    plt.legend(handles=[fuel, shell, water],
               loc="upper right", bbox_to_anchor=(1., 1.), fancybox=True)
    plt.axis('off')
    plt.savefig("toy-problem-b.png", dpi=300, bbox_inches="tight")


def plot_composition_comparison(times, composition_1, composition_2, labels,
                                figname):
    """
    This function plots th etime evolution of two material compositions side
    by side.

    Parameters:
    ----------_
    times: [list of float], timesteps
    composition_X: [dict], {keys: isotopes, values: [list of float]
    labels: [list of str], labels for each composition
    figname: [str], name of the figure to produce
    """
    n_plots = len(composition_1)
    fig, axs = plt.subplots(n_plots)
    fig.tight_layout(pad=2.1)
    for idx, isotope in enumerate(composition_1.keys()):
        axs[idx].plot(
            times, composition_1[isotope], marker='o', label=labels[0])
        axs[idx].plot(
            times, composition_2[isotope], marker='o', label=labels[1])
        yScalarFormatter = ScalarFormatterClass(useMathText=True)
        yScalarFormatter.set_powerlimits((0, 0))
        axs[idx].yaxis.set_major_formatter(yScalarFormatter)
        axs[idx].set_ylabel(f'{isotope.upper()} [g]')
        axs[idx].legend(loc="upper right")
        axs[idx].set_xlabel('Time [months]', fontsize=16)
        axs[idx].set_xlim([times[0], times[-1]])

        diff = (composition_1[isotope]/composition_2[isotope] - 1)*100
        sec_color = 'darkgreen'
        ax2 = axs[idx].twinx()  # second axes sharing the same x-axis
        ax2.plot(times, diff, color=sec_color, marker='o')
        ax2.tick_params(axis='y', labelcolor=sec_color, labelsize=16)
        ax2.ticklabel_format(useOffset=False)
        ax2.set_ylabel('Rel. Diff. [%]', color=sec_color, fontsize=16)

    plt.xlabel('Time [years]')
    plt.savefig(figname, dpi=300, bbox_inches="tight")


def plot_gamma_intens_comparison(x_list, y_list, heat_list, labels,
                                 figure_name):
    """
    x_list: list of float
        contains x location
    y_list: list of float
        contains y location
    heat_list: list of float
        contains heat values
    labels: list of str
        list of labels to be included in figure's title
    figure_name: str
        name of the figure to be plotted
    """
    heat1 = np.array(heat_list[0])
    heat2 = np.array(heat_list[1])
    heat3 = (heat1-heat2)/heat2 * 100

    re_height, re_width = 32, 32  # Real image dimensions
    image_name = 'geometry-zoom.png'

    cwd = os.getcwd()
    image_name = os.path.join(cwd, image_name)
    fname = get_sample_data(image_name)

    plt.figure()
    im = plt.imread(fname)
    # im = im[120:-120, 110:-110, :]

    plt.imshow(im)
    plt.axis('off')

    im_height, im_width, _ = np.shape(im)
    print(f'Image dimensions: {im_height}x{im_width}')
    re_origin = -re_width/2, re_height/2  # Origin location

    for x, y, h1, h2, h3 in zip(x_list, y_list, heat1, heat2, heat3):
        # transform to image system
        xp = -(re_origin[0] - x)
        yp = re_origin[1] - y
        xpp = xp/re_width * im_width
        ypp = yp/re_height * im_height

        plt.text(
            xpp, ypp-15, s=f'{h1:.2e}', fontsize=5, color='white',
            weight='bold', horizontalalignment='center',
            verticalalignment='center', rotation='horizontal')
        plt.text(
            xpp, ypp, s=f'{h2:.2e}', fontsize=5, color='white',
            weight='bold', horizontalalignment='center',
            verticalalignment='center', rotation='horizontal')
        plt.text(
            xpp-2, ypp+15, s=f'{h3:.1f}', fontsize=6, color='white',
            weight='bold', horizontalalignment='center',
            verticalalignment='center', rotation='horizontal')

    title = ""
    title += f'Total {labels[0]}: {heat1.sum():.2e}, '
    title += f'Total {labels[1]}: {heat2.sum():.2e}, '
    title += f'Diff: {((heat1.sum() - heat2.sum())/heat2.sum() * 100):.1f}%'
    plt.title(title, fontsize=8)
    plt.savefig(figure_name, dpi=300, bbox_inches="tight")
    plt.close()


if __name__ == "__main__":

    add_labels('geometry.png')

    times = np.arange(0, 13)
    print(f'Irradiation times in months: {times}')

    x_list = []
    y_list = []
    for i in range(8):
        for j in range(8):
            x_list.append(-14 + i*4)
            y_list.append(14 - j*4)

    # arf-ref vs arf-uni
    labels = ['universes', 'reference', '', '', 'Time [h]']

    # composition comparison
    composition_1 = {
        'U235': np.array([
            20250., 20220., 20180., 20140.,
            20110., 20070., 20030., 19990.,
            19960., 19920., 19880., 19850.,
            19850.]),
        'U238': np.array([
            243600., 243600., 243600., 243600.,
            243600., 243500., 243500., 243500.,
            243500., 243500., 243500., 243500.,
            243500.])
        }

    composition_2 = {
        'U235': np.array([
            20254.8, 20218.1, 20181., 20142.5,
            20106.4, 20068.8, 20031.6, 19994.6,
            19957.6, 19919.7, 19883.8, 19846.4,
            19846.4]),
        'U238': np.array([
            243584., 243584., 243584., 243580.,
            243568., 243552., 243540., 243532.,
            243524., 243520., 243504., 243501.,
            243501.])
        }
    plot_composition_comparison(times, composition_1, composition_2,
                                labels, 'moaa-ref-uni-composition-time-b')

    # gamma instens comparison
    gamma_intens_1 = [3.66757215e+17/64] * 64
    gamma_intens_2 = [
        3.78282560e+15, 4.24821846e+15, 4.87648778e+15, 5.23745438e+15,
        5.24514824e+15, 4.89147642e+15, 4.26304267e+15, 3.80788793e+15,
        4.23849755e+15, 4.96794429e+15, 5.83682743e+15, 6.31249631e+15,
        6.31050999e+15, 5.83617432e+15, 4.98360940e+15, 4.24448113e+15,
        4.89432377e+15, 5.84049038e+15, 6.88610823e+15, 7.43023905e+15,
        7.45395273e+15, 6.90411021e+15, 5.84589721e+15, 4.88832843e+15,
        5.22932103e+15, 6.30212743e+15, 7.41826268e+15, 8.02750487e+15,
        8.03890482e+15, 7.43833521e+15, 6.28243319e+15, 5.23614017e+15,
        5.23994895e+15, 6.29352323e+15, 7.43622385e+15, 8.03257040e+15,
        8.03802778e+15, 7.45773520e+15, 6.30820281e+15, 5.24563267e+15,
        4.88887716e+15, 5.85369118e+15, 6.91035805e+15, 7.43411542e+15,
        7.44395531e+15, 6.88551842e+15, 5.86229423e+15, 4.90650021e+15,
        4.25311704e+15, 4.98297392e+15, 5.83711733e+15, 6.30288854e+15,
        6.2978697e+15, 5.84785465e+15, 5.00507706e+15, 4.27039361e+15,
        3.78749190e+15, 4.24557950e+15, 4.91670513e+15, 5.24708260e+15,
        5.22616494e+15, 4.90080232e+15, 4.25429956e+15, 3.80020207e+15,
    ]

    heat_list = [gamma_intens_1, gamma_intens_2]
    plot_gamma_intens_comparison(x_list, y_list, heat_list, labels[:2],
                                 'moaa-ref-uni-gamma-intens-b')
