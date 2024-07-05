# defining the bandpasses for all functions
import importlib
import pandas as pd
from sonifyFED import sonify as sonify
from .rr_plotutils import *
from . import configs as configs

importlib.reload(configs)
importlib.reload(sonify)


def getrange(obj):
    maxflux = obj.flux.max()
    minflux = obj.flux.min()
    return minflux, maxflux


def transpose(notes, down=False, interval=5, intervals=1):
    if isinstance(notes, list):
        notes = np.array(notes)
    assert isinstance(notes, np.ndarray), "must pass a list or a 1D array of notes"
    assert len(notes.shape) == 1, "notes muse be a 1d list or array"
    sign = -1 if down else 1
    return notes + sign * interval * intervals  # transpose by n intervals, each of n notes in the scale (default 5)


def readdata(path=None, root=None):
    if path is None:
        from utils.configs import DATA_PATH as path
    if root is None:
        root = path["path"]
    try:
        data = pd.read_csv(root + path["data"])
        metadata = pd.read_csv(root + "/" + path["metadata"])
    except FileNotFoundError:
        data = pd.read_csv("../" + root + path["data"])
        metadata = pd.read_csv("../" + root + "/" + path["metadata"])

    return data, metadata


def rescalenotes(fluxValue, minmaxflux, keynotes):
    minflux, maxflux = minmaxflux
    fullrange = maxflux - minflux
    keynotesrange = len(keynotes)
    startindx = int(np.round((fluxValue.min() - minflux) / (fullrange / keynotesrange)))
    endindx = int(np.round((maxflux - fluxValue.max()) / (fullrange / keynotesrange)))
    return startindx, -endindx


def prep_sonification(x_points, y_points, key=configs.KEY, filter=None,
                      noctaves=configs.NOCT, t_min=1, t_max=15,
                      transposing=True, rescaling=None, plot=False):
    if plot:
        ax = plt.figure(figsize=(10, 3)).add_subplot()
        plt.plot(x_points, y_points, '.')
    transposition = 0
    if transposing:
        if filter is None:
            transposition = 0
        else:
            transposition = configs.TRANSPOSITIONS[filter]

    # time axis manipulation
    normalized_x = sonify.core.scale_list_to_range(x_points, new_min=t_min, new_max=t_max)

    quantized_x = sonify.quantize_x_value(normalized_x, steps=0.5)
    assert len(normalized_x) == len(x_points)
    # flux axis normalization
    data = list(zip(quantized_x, y_points))
    normed_data = sonify.core.convert_to_key(data, key,  number_of_octaves=noctaves, minmaxvalue=rescaling)

    _, normalized_y = zip(*normed_data)
    assert len(normalized_y) == len(y_points)
    if transposing:
        normalized_y = transpose(np.array(normalized_y), intervals=transposition)

    normed_data = list(zip(quantized_x, normalized_y))
    if plot:
        setax2ticks(ax)
        plt.show()

    return normed_data


def gettrack(x, y, filter, key, minmaxflux, transposing=False,
             rescaled=False, noctaves=configs.NOCT):
    # rescale the notes range to enable proper normalization
    rescaling = None
    keynotes = sonify.core.key_name_to_notes(key, number_of_octaves=noctaves)
    if rescaled:
        rescaling = rescalenotes(y, minmaxflux, keynotes)

    return prep_sonification(x, y, key=key, filter=filter,
                             transposing=transposing, rescaling=rescaling,
                             noctaves=noctaves, plot=False)


def singleSonification(data, objectID, filter, instrument=None, key=None,
                       noctaves=configs.NOCT,
                       transposing=False, rescaled=False,
                       save=False, plot=False, diagonsticplots=False, colab=False, verbose=True):
    if key is None:
        key = configs.KEY
    filters = configs.FILTERS
    assert filter in filters, "ERROR: your filter argument must be 'u', 'g', 'r', 'i', 'z', or 'y'"
    if instrument is None:
        instrument = configs.INSTRUMENTS[filter]

    objFiltered = data[data["object_id"] == objectID]
    objP = objFiltered[objFiltered["passband"].isin([configs.passband[filter]])]

    timeValue = objP["mjd"].values
    fluxValue = objP["flux"].values
    fluxErr = objP["flux_err"].values
    normed_data = gettrack(timeValue, fluxValue, filter, key, getrange(objFiltered),
                           noctaves=noctaves, transposing=transposing, rescaled=rescaled)
    if plot:
        print("now plotting")
        singlePlotObject(data, objectID, filter, key,
                         instrument=instrument, save=False, show=False)

        plt.savefig('{}/ID{}_{}.png'.format(configs.OUTDIR, objectID, filter), dpi=300, bbox_inches='tight')
        plt.show()
    if diagonsticplots:
        ax = plt.figure().add_subplot()
        plt.plot(timeValue, list(zip(*normed_data))[0], '.')
        plt.xlabel("MJD")
        plt.ylabel("note time")
        ax.plot([0, 1], [0, 1], transform=ax.transAxes)
        plt.show()
        ax = plt.figure().add_subplot()
        plt.plot(fluxValue, list(zip(*normed_data))[1], '.')
        plt.xlabel("flux")
        plt.ylabel("note")
        ax.plot([0, 1], [0, 1], transform=ax.transAxes)
        plt.show()

    volume = np.clip(1.0 / fluxErr * 400, 30, 80).astype(int)

    sonify.play_midi_from_data([instrument] + normed_data, track_type='single',
                               volume=[volume], colab=colab, verbose=verbose)
    if save and not colab:
        audiofname = '{}/ID{}_{}.wav'.format(configs.OUTDIR, objectID, filter,
                                             instrument.replace(' ', '_'), key.replace(' ', '_'))
        import subprocess
        subprocess.check_output('cp soundclip.wav {}'.format(audiofname), shell=True)


def multiSonification(data, objectID, instruments=None, key=None,
                      transposing=False, rescaled=False, noctaves=configs.NOCT,
                      drone="gliss", drone_vol=50, drum=None,
                      save=False, plot=True, colab=False, verbose=True):

    if key is None:
        key = configs.KEY
    if instruments is None:
        instruments = configs.INSTRUMENTS
    filts = configs.FILTERS
    objFiltered = data[data["object_id"].isin([objectID])]
    multiDataWIntsruments = []
    volume = []
    for f in filts:
        objP = objFiltered[objFiltered["passband"].isin([configs.passband[f]])]
        timeValue = objP["mjd"].values
        fluxValue = objP["flux"].values
        fluxErr = objP["flux_err"].values
        normed_data = gettrack(timeValue, fluxValue, f, key, getrange(objFiltered), noctaves=noctaves,
                               transposing=transposing, rescaled=rescaled)
        multiDataWIntsruments.append([instruments[f]] + normed_data)
        thisvolume = np.clip(np.log(1e4 / fluxErr) * 10,
                             None, 100).astype(int)
        #if f in ['u', 'g', 'r', 'i']:
        #    thisvolume = np.ones_like(fluxErr).astype(int)
        volume.append(thisvolume)

    if plot:
        print("now plotting")
        multiPlotObject(data, objectID, instruments,
                        save=False, show=True)
        plt.savefig('{}/ID{}.png'.format(configs.OUTDIR, objectID), dpi=300, bbox_inches='tight')
        plt.show()

    if drone is not None:
        assert drone in ["gliss", "step"], 'Current drone options are glissando "gliss" and step "step"'
        if drone == "gliss":
            from .rr_sounds import drone_glissando_2
            track_drone, track_base = drone_glissando_2()
        elif drone == "step":
            from .rr_sounds import drone
            track_drone, track_base = drone()

        multiDataWIntsruments.append(['voice oohs'] + track_drone)
        multiDataWIntsruments.append(['voice oohs'] + track_base)
        # sonify.play_midi_from_data(list(zip(quantized_x, dronenote)), track_type='single')
        volume.append([drone_vol] * len(track_drone))
        volume.append([drone_vol] * len(track_drone))
    if drum is not None:
        from .rr_sounds import drum_beat
        track_drum1, track_drum2 = drum_beat(drum)
        multiDataWIntsruments.append([drum] + track_drum1)
        volume.append([20] * len(track_drone))
        multiDataWIntsruments.append([drum] + track_drum2)
        volume.append([60] * len(track_drone))
    sonify.play_midi_from_data(multiDataWIntsruments, track_type='multiple',
                               volume=volume, colab=colab, verbose=verbose)

    if save and not colab:
        audiofname = '{}/ID{}_{}.wav'.format(configs.OUTDIR, objectID, key.replace(' ', '_'))
        import subprocess
        subprocess.check_output('cp soundclip.wav {}'.format(audiofname), shell=True)


def getIDs(data, dataMETA, objtype):
    assert objtype in ["SNIbc", "SNe", "EB"], "can only look for SNIbc, SN3, EB, use appropriate string"
    if objtype in ["SNe", "SNIbc"]:
        ids = list(configs.SNids.keys())
        if objtype == "SNIbc":
            val_list = list(configs.SNids.values())
            position = val_list.index('SNIbc')
            ids = [ids[position]]
    else:
        ids = [16]
    return dataMETA[dataMETA["true_target"].isin(ids)].object_id #find the SNe Ibc in the metadata: target 62
