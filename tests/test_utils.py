

import numpy as np
import numpy.testing as npt
import pytest


def test_make_c_major():
    from sonifyFED import sonify
    x = np.linspace(1, 4, 7, endpoint=True)
    y = np.linspace(1, 2, 7, endpoint=True)
    data = list(zip(x, y))
    converted_c_data = sonify.convert_to_key(data, 'c_major', number_of_octaves=1)
    x, y_in_c = zip(*converted_c_data)

    assert (36, 38, 40, 41, 43, 45, 47) == y_in_c


def test_make_f_lydian():
    from sonifyFED import sonify
    x = np.linspace(1, 4, 7, endpoint=True)
    y = np.linspace(1, 2, 7, endpoint=True)
    data = list(zip(x, y))
    converted_c_data = sonify.convert_to_key(data, 'f_major_lydian', number_of_octaves=1)
    x, y_in_c = zip(*converted_c_data)

    assert (41, 43, 45, 47, 48, 50, 52) == y_in_c


def test_rescale_flux():
    from sonifyFED import sonify as sonify
    from rrhapsodies.rr_utils import rescalenotes

    # check get_scaled_value
    npt.assert_array_almost_equal(np.arange(1, 2, 0.1),
                                  sonify.core.get_scaled_value(np.arange(1, 11), 1, 11, 1, 2), decimal=4)

    # check rescalenotes
    keynotes = list(zip(*sonify.convert_to_key(list(zip(range(7), range(7))),
                                               'c_major', number_of_octaves=1)))[1]
    print(keynotes)
    startindx, endindx = rescalenotes(np.array([1, 2, 3, 4, 5]), (0, 6), keynotes)
    print(startindx, endindx)
    if endindx <= -1:
        notes_in_key = keynotes[startindx:endindx]
    else:
        notes_in_key = keynotes[startindx:]
    print(keynotes, notes_in_key)
    npt.assert_array_equal(keynotes[1:-1],
                           notes_in_key)
    return


def test_get_data():
    from rrhapsodies.rr_utils import readdata
    data, metadata = readdata()
    for c in ['object_id', 'mjd', 'passband', 'flux', 'flux_err']:
        assert c in data.columns
    assert 'object_id' in metadata.columns
    for o in data.object_id.unique():
        assert o in metadata.object_id.values


def test_numbers2notes():
    from rrhapsodies.configs import numbers2notes
    print(numbers2notes(0, 100))


def test_getrange():
    from rrhapsodies.rr_utils import getrange
    from rrhapsodies.rr_utils import readdata

    data, _ = readdata()
    objectID = 43018203
    objFiltered = data[data["object_id"] == objectID]
    minflux, maxflux = getrange(objFiltered)
    objFiltered.flux.min()
    print(minflux, maxflux)

    npt.assert_equal(minflux, objFiltered.flux.min())
    npt.assert_equal(maxflux, objFiltered.flux.max())


def test_scaling():
    from sonifyFED.sonify.core import key_name_to_notes
    from rrhapsodies.rr_utils import rescalenotes

    minflux, maxflux = 0, 10
    fluxValue = np.arange(2, 10)

    # testing C_major key with 1 octave
    print("testing C_major key with 1 octave")
    keynotes = key_name_to_notes('c_major', octave_start=1, number_of_octaves=1)
    rescaled = rescalenotes(fluxValue, (minflux, maxflux), keynotes)
    if rescaled[1] < -1:
        keynotes = keynotes[rescaled[0]:rescaled[1] + 1]
    else:
        keynotes = keynotes[rescaled[0]:]
    npt.assert_equal(keynotes[0], 38)
    npt.assert_equal(keynotes[-1], 47)

    # testing F_major_lydian key with 2 octaves
    print("testing F_major_lydian key with 2 octaves")
    keynotes = key_name_to_notes('f_major_lydian', octave_start=1, number_of_octaves=2)
    rescaled = rescalenotes(fluxValue, (minflux, maxflux), keynotes)
    if rescaled[1] < -1:
        keynotes = keynotes[rescaled[0]:rescaled[1] + 1]
    else:
        keynotes = keynotes[rescaled[0]:]

    npt.assert_equal(keynotes[0], 47)
    npt.assert_equal(keynotes[-1], 64)

def test_getIDs():
    from rrhapsodies.rr_utils import getIDs
    from rrhapsodies.rr_utils import readdata
    data, metadata = readdata()
    assert 43018203 in getIDs(data, metadata, "SNe").values
    assert 43018203 in getIDs(data, metadata, "SNIbc").values
    assert 2677 in getIDs(data, metadata, "EB").values