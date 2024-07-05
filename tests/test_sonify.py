import numpy as np
import numpy.testing as npt
import pytest


def test_play_c_major():
    from sonifyFED import sonify

    x = np.linspace(1, 4, 7, endpoint=True)
    y = np.linspace(1, 2, 7, endpoint=True)
    data = list(zip(x, y))
    converted_c_data = sonify.convert_to_key(data, 'c_major', number_of_octaves=1)
    x, y_in_c = zip(*converted_c_data)

    sonify.play_midi_from_data(list(zip(x, y_in_c)), track_type='single', key='c_major',
                               number_of_octaves=1)
    assert y_in_c[0] == 36
    assert y_in_c[-1] == 47

    # adding the high C
    sonify.play_midi_from_data(list(zip(np.linspace(1, 4, 8, endpoint=True),
                                        np.concatenate([y_in_c, [y_in_c[-1] + 1]]))),
                               track_type='single')


def test_play_chromatic_scale():
    import sonifyFED.sonify.core as sonify

    x = np.linspace(1, 8, 12, endpoint=True)
    y = np.linspace(1, 2, 12, endpoint=True)
    data = list(zip(x, y))
    converted_c_data = sonify.convert_to_key(data, 'chromatic', number_of_octaves=1)
    x, y_in_c = zip(*converted_c_data)
    npt.assert_array_equal(y_in_c, np.arange(41, 53).astype(int))
    sonify.play_midi_from_data(list(zip(x, y_in_c)), track_type='single',
                               number_of_octaves=1)


def test_change_volume():
    from sonifyFED import sonify

    x = np.linspace(1, 4, 7, endpoint=True)
    y = np.linspace(1, 2, 7, endpoint=True)
    data = list(zip(x, y))
    converted_c_data = sonify.convert_to_key(data, 'c_major', number_of_octaves=1)
    x, y_in_c = zip(*converted_c_data)

    sonify.play_midi_from_data(list(zip(x, y_in_c)), track_type='single', key='c_major',
                               number_of_octaves=1, volume=[np.linspace(30, 100, 7, endpoint=True).astype(int)])
    sonify.play_midi_from_data(list(zip(x, y_in_c)), track_type='single', key='c_major',
                               number_of_octaves=1, volume=[np.linspace(30, 100, 7, endpoint=True)[::-1].astype(int)])


def test_play_f_major_lydian():
    from sonifyFED import sonify

    x = np.linspace(1, 4, 7, endpoint=True)
    y = np.linspace(1, 2, 7, endpoint=True)
    data = list(zip(x, y))
    converted_c_data = sonify.convert_to_key(data, 'f_major_lydian', number_of_octaves=1)
    x, y_in_c = zip(*converted_c_data)

    sonify.play_midi_from_data(list(zip(x, y_in_c)), track_type='single')
    assert y_in_c[0] == 41
    assert y_in_c[-1] == 52

    sonify.play_midi_from_data(list(zip(np.linspace(1, 4, 8, endpoint=True),
                                        np.concatenate([y_in_c, [y_in_c[-1] + 1]]))),
                               track_type='single')


def test_play_instruments():
    from sonifyFED import sonify
    from rrhapsodies.configs import INSTRUMENTS, FILTERS, TRANSPOSITIONS
    from rrhapsodies.rr_utils import transpose

    x = np.linspace(1, 4, 7, endpoint=True)
    y = np.linspace(1, 2, 7, endpoint=True)

    data = list(zip(x, y))

    for i in range(6):
        f = FILTERS[i]
        converted_c_data = sonify.convert_to_key([INSTRUMENTS[f]] + data,
                                                 'c_major', number_of_octaves=1)
        x, y_in_c = zip(*converted_c_data[1:])
        print(INSTRUMENTS[f])
        notes = transpose(np.concatenate([y_in_c, [y_in_c[-1] + 1]]), down=False,
                          intervals=TRANSPOSITIONS[f])
        sonify.play_midi_from_data([INSTRUMENTS[f]] +
                                   list(zip(np.linspace(1, 4, 8, endpoint=True), notes)),
                                   track_type='single')


def test_prep_sonification():
    from rrhapsodies.rr_utils import prep_sonification

    x_points, y_points = np.arange(7), np.arange(7)
    key = 'c_major'
    noctaves = 1
    t_min, t_max = 1, 13

    print("basic test 1 octave no transpose no rescale")
    track = prep_sonification(x_points, y_points, key=key,
                              noctaves=noctaves, t_min=t_min, t_max=t_max,
                              transposing=False, rescaling=None)
    npt.assert_array_equal(np.array([(1.0, 36), (3., 38), (5., 40),
                                     (7., 41), (9., 43), (11., 45), (13., 47)]),
                           track)

    print("test transpose")
    track = prep_sonification(x_points, y_points, key=key,
                              noctaves=noctaves, t_min=t_min, t_max=t_max, filter='g',
                              transposing=True, rescaling=None)
    npt.assert_array_equal(np.array([(1.0, 41), (3.0, 43), (5.0, 45),
                                     (7.0, 46), (9., 48), (11., 50), (13., 52)]),
                           track)

    print("test rescale")
    track = prep_sonification(x_points, y_points, key=key,
                              noctaves=noctaves, t_min=t_min, t_max=t_max,
                              filter='r', transposing=False, rescaling=[1, -2])

    npt.assert_array_equal(np.array([(1.0, 38), (3., 38), (5., 40),
                                     (7.0, 40), (9.0, 41), (11, 43), (13.0, 43)]),
                           track)

    print("test change min max time")
    track = prep_sonification(x_points, y_points, key=key,
                              noctaves=noctaves, t_min=2, t_max=14,
                              filter='r',
                              transposing=False, rescaling=[1, -2])
    print(track)

    npt.assert_array_equal(np.array([(2.0, 38), (4., 38), (6., 40),
                                     (8.0, 40), (10., 41), (12, 43), (14.0, 43)]),
                           track)


def test_gettrack(plot=False):
    from sonifyFED.sonify import core as sonify
    from rrhapsodies.rr_utils import gettrack, readdata, getrange
    from rrhapsodies import configs as configs
    from pylab import plt

    t = np.linspace(1, 4, 8)
    f = np.arange(8)

    track = gettrack(t, f, 'i', 'c_major', (1, 10), noctaves=1,
                     transposing=False, rescaled=False)

    sonify.play_midi_from_data(track, track_type='single')

    track = gettrack(t, f, 'r', 'c_major', (1, 10), noctaves=1,
                     transposing=True, rescaled=False)
    print(track)

    sonify.play_midi_from_data(track, track_type='single')

    track = gettrack(t, f, 'r', 'c_major', (-10, 20), noctaves=1,
                     transposing=True, rescaled=True)
    print(track)

    sonify.play_midi_from_data(track, track_type='single')

    data, _ = readdata()
    objFiltered = data[data["object_id"] == 43018203]

    objP = objFiltered[objFiltered["passband"].isin([configs.passband['r']])]

    track = gettrack(objP["mjd"].values, objP["flux"].values, 'r', 'c_major',
                     getrange(objFiltered), noctaves=1, transposing=True, rescaled=True)

    t, n = list(zip(*track))
    t = np.array(t)

    if plot:
        fig, ax = plt.subplots(2, 1)

        ax[0].plot(objP["mjd"].values, objP["flux"].values, '-')
        ax[0].plot(objP["mjd"].values, objP["flux"].values, '.')
        plt.ylabel("flux")

        ax[1].plot(t, n, '-')
        ax[1].plot(t, n, '.')
        plt.xlabel("time/tempo")
        plt.ylabel("note")
        plt.show()

        plt.plot(objP["mjd"].values, t, '.')
        plt.xlabel("MJD")
        plt.ylabel("note start")
        plt.show()

        plt.plot(objP["flux"].values, n, '.')
        plt.xlabel("flux")
        plt.ylabel("note")
        plt.show()

    sonify.play_midi_from_data(track, track_type='single')


def test_drone():
    from rrhapsodies.rr_sounds import drone
    import sonifyFED.sonify.core as sonify
    track_drone, track_base = drone(PLOT=False)
    multiDataWIntsruments = [['voice oohs'] + track_drone,
                             ['voice oohs'] + track_base]
    # sonify.play_midi_from_data(list(zip(quantized_x, dronenote)), track_type='single')
    sonify.play_midi_from_data(multiDataWIntsruments, track_type='multiple',
                               volume=[[40]*len(track_drone), [40]*len(track_drone)])


def test_drone_glissando():
    from rrhapsodies.rr_sounds import drone_glissando
    import sonifyFED.sonify.core as sonify
    track_drone, track_base = drone_glissando(PLOT=False)
    multiDataWIntsruments = [['voice oohs'] + track_drone,
                             ['voice oohs'] + track_base]
    sonify.play_midi_from_data(multiDataWIntsruments, track_type='multiple',
                               volume=[[80] * len(track_drone), [80] * len(track_base)])


def test_drum():
    import sonifyFED.sonify.core as sonify
    from sonifyFED.sonify.constants import PERCUSSION
    import sys
    x = np.linspace(1, 2, 4, endpoint=True)
    y = np.linspace(1, 2, 4, endpoint=True)
    data = list(zip(x, y))
    #for p in PERCUSSION:
        #print(p, flush=True)

    sonify.play_midi_from_data(['crash cymbal 1'] + data, track_type='single', key='c_major',
                               number_of_octaves=1)