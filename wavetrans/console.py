import os
import docopt
import logging
from wavetrans import get_transmitted_spectrum


def wavetrans():
    '''wavetrans : creates SWAN spectrum shoreward of barrier

    Usage:
        wavetrans <spcfile> <outpath> [--closed] [--door=NUM] [--verbose=LEVEL]

    Positional arguments:
        spcfile            SWAN spectrum file seaward of barrier
        outpath            resulting SWAN spectrum file shoreward of barrier

    Options:
        -h, --help         show this help message and exit
        --closed           assume barrier doors are closed
        --door=NUM         location index in SWAN files
        --verbose=LEVEL    write logging messages [default: 20]

    '''

    arguments = docopt.docopt(wavetrans.__doc__)

    # initialize file logger
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)-15s %(name)-8s %(levelname)-8s %(message)s',
                        filename='%s.log' % os.path.splitext(arguments['<spcfile>'])[0])

    # initialize console logger
    console = logging.StreamHandler()
    console.setLevel(int(arguments['--verbose']))
    console.setFormatter(logging.Formatter('%(levelname)-8s %(message)s'))
    logging.getLogger('').addHandler(console)

    # run script
    if arguments['--door']:
        door = int(arguments['--door'])
    else:
        door = None
        
    get_transmitted_spectrum(arguments['<spcfile>'],
                             arguments['<outpath>'],
                             closed=arguments['--closed'],
                             door=door)

    
if __name__ == '__main__':
    wavetrans()
    
