FILTERS = ['u', 'g', 'r', 'i', 'z', 'y']
passband = {'u': 0,
            'g': 1,
            'r': 2,
            'i': 3,
            'z': 4,
            'y': 5}

ugrizyC_cb = {'u': "#E69F00", 'g': "#56B4E9",
              'r': "#009E73", 'i': "#F0E442",
              'z': "#0072B2", 'y': "#D55E00"}  # colorblind-compliant palette

INSTRUMENTS = {'u': 'flute',
               'g': 'trumpet',
               'r': 'violin',
               'i': 'cello',
               'z': 'bassoon',
               'y': 'french horn'}

KEY = 'f_major_lydian'

DATA_PATH = {"path": "data/",
             "data": "plasticc_train_lightcurves.csv.gz",
             "metadata": "plasticc_train_metadata.csv.gz",
             }

# inits of interval for transposition
TRANSPOSITIONS = {'u': 2,
                  'g': 1,
                  'r': 0,
                  'i': -1,
                  'z': -2,
                  'y': -3}

OUTDIR = "view/"

NOCT = 6

drone_base = 36  # 24 #130.8128Hz   C3
drone_low = 41  # 29 #174.6141Hz F3
drone_high = 44  # 31 #195.9977   G3


def numbers2notes(mindata, maxdata):
    import sonifyFED.sonify as sonify
    import numpy as np

    notenumbers = {i+36: '/'.join(note) for i, note in enumerate(sonify.constants.NOTES)}
    for i in range(np.array(list(notenumbers.keys())).min() - 1, mindata - 1, -1):
        notenumbers[i] = notenumbers[i + 12]
    for i in range(np.array(list(notenumbers.keys())).max() + 1, maxdata + 1):
        notenumbers[i] = notenumbers[i - 12]

    return notenumbers

SNids = {42: "SNII",
         52: "SNIax",
         62: "SNIbc",
         67: "SNIa-91bg",
         64: "KN",
         90: "SNIa",
         95: "SLSN-1"}