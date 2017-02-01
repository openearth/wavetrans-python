import os
import docopt
import logging
from wavetrans import get_transmitted_spectrum


def wavetrans():
    '''wavetrans : creates SWAN spectrum shoreward of barrier

    Usage:
        wavetrans <sp1file_in> <tabfile> <sp1file_out> [--closed] [--ix=NUM] [--verbose=LEVEL]

    Positional arguments:
        sp1file_in         SWAN spectrum file seaward of barrier
        tabfile            SWAN tabular file seaward of barrier
        sp1file_out        resulting SWAN spectrum file shoreward of barrier

    Options:
        -h, --help         show this help message and exit
        --closed           assume barrier doors are closed
        --ix=NUM            location index in SWAN files
        --verbose=LEVEL    write logging messages [default: 20]

    '''

    arguments = docopt.docopt(wavetrans.__doc__)

    # initialize file logger
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)-15s %(name)-8s %(levelname)-8s %(message)s',
                        filename='%s.log' % os.path.splitext(arguments['<sp1file_in>'])[0])

    # initialize console logger
    console = logging.StreamHandler()
    console.setLevel(int(arguments['--verbose']))
    console.setFormatter(logging.Formatter('%(levelname)-8s %(message)s'))
    logging.getLogger('').addHandler(console)

    # run script
    if arguments['--ix']:
        ix = int(arguments['--ix'])
    else:
        ix = 0
        
    get_transmitted_spectrum(arguments['<sp1file_in>'],
                             arguments['<tabfile>'],
                             arguments['<sp1file_out>'],
                             closed=arguments['--closed'],
                             ix=ix)

    
if __name__ == '__main__':
    wavetrans()
    
