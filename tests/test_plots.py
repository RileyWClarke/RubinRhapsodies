
def test_singlePlotObject():
    from rrhapsodies.configs import INSTRUMENTS
    from rrhapsodies.rr_plotutils import singlePlotObject
    from rrhapsodies.rr_utils import readdata

    data, metadata = readdata()
    objectID, filter, key = 43018203, 'r', 'c_major',
    instrument = INSTRUMENTS[filter],

    singlePlotObject(data, objectID, filter,
                     instrument=instrument, save=False, show=True)

