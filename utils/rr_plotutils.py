
import matplotlib.pyplot as plt
from . import configs
import numpy as np


def setax2ticks(ax):
    ax2 = ax.twinx()
    ax2.set_ylabel('notes')

    ticks = np.array(np.array(ax.get_yticks()).astype(int))
    ax2.set_yticks(ticks, [configs.numbers2notes(ticks[0], ticks[-1])[t] for t in ticks])


def plotlc(objFiltered, ax, filter=None, instruments=None):
    filts = configs.FILTERS
    if instruments is None:
        instruments = configs.INSTRUMENTS
    if filter is not None:
        assert isinstance(filter, str), "the filter should be a single character string"

    for i, f in enumerate(filts):
        # select data from object
        # select the i-th bandpass
        objP = objFiltered[objFiltered["passband"].isin([i])]
        timeValue = objP["mjd"]
        fluxValue = objP["flux"]
        fluxerrValue = objP["flux_err"]

        # choose color black for all but the specific filter chosen
        if filter is None:
            plt.errorbar(timeValue, fluxValue, yerr=fluxerrValue,
                         marker='o', color=configs.ugrizyC_cb[f], alpha=0.7,
                         linestyle='none', label=f + ': ' + instruments[f])

        else:
            color = configs.ugrizyC_cb[f] if f == filter else 'k'
            # set transparency if the filter is not the chosen one
            alpha = 1 if f == filter else 0.2

            ax.errorbar(timeValue, fluxValue, yerr=fluxerrValue, marker='o', color=color,
                        linestyle='none', label=f, alpha=alpha)


def singlePlotObject(data, objectID, filter, key,
                     instrument=None, save=False, show=True):
    """ plots a single band from a Plasticc object:
    arguments:
    objectID: int: the PLAsTiCC object id
    filter: char: a character corresponding to a photometric filter as defined in FILTERS
    instrument: string: a musical instrument available in the SonifyFED library configurations (default is 'violin')
    save: bool: if True saves the plot as a png file (default True)
    """

    # creates a figure
    fig, ax = plt.subplots(1, 1, figsize=(10, 3.5))
    filts = configs.FILTERS
    objFiltered = data[data["object_id"].isin([objectID])]
    assert filter in filts, "ERROR: your filter argument must be 'u', 'g', 'r', 'i', 'z', or 'y'"

    plotlc(objFiltered, ax, filter=filter)

    title = 'Object ID: {}, filter: {}, key: {}, '.format(objectID, filter, key)
    if instrument:
        title = title + 'instrument: {}'.format(instrument)
    plt.title(title)
    plt.legend(fontsize=8, loc='upper left', ncol=2)

    plt.xlabel("Modified Julian Date (days)")
    plt.ylabel("Flux")
    setax2ticks(ax)
    if show:
        plt.show()
    if save:
        plt.savefig('ID{}_filter{}}.png'.format(objectID, filter), dpi=300, bbox_inches='tight')

    return fig, ax


def multiPlotObject(data, objectID, instruments,
                    save=False, show=True):

    """ plots a multi band object from a Plasticc object:
    arguments:
    objectID: int: the PLAsTiCC object id
    instruments: list or array: a list of strings indicating musical instrument
                available in the SonifyFED library configurations
    save: bool: if True saves the plot as a png file (default True)
    """
    fig, ax = plt.subplots(1, 1, figsize=(10, 3.5))
    objFiltered = data[data["object_id"].isin([objectID])]

    plotlc(objFiltered, ax, filter=None, instruments=instruments)

    title = 'Object: {} '.format(objectID)

    plt.title(title)
    plt.legend(fontsize=8, loc='upper left', ncol=2)

    plt.xlabel("Modified Julian Date (days)")
    plt.ylabel("Flux")
    setax2ticks(ax)
    if show:
        plt.show()

    if save:
        plt.savefig('ID{}_multi.png'.format(objectID), dpi=300, bbox_inches='tight')

    return fig, ax
