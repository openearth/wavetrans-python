# wavetrans-python
Little tool to apply wave transmission through a barrier to a SWAN wave spectrum file. Currently only supports the Eastern Scheldt barrier.

# usage

```
wavetrans : creates SWAN spectrum shoreward of barrier

    Usage:  
        wavetrans <spcfile> <outpath> [--closed] [--door=NUM] [--verbose=LEVEL]

    Positional arguments:
        spcfile            SWAN spectrum file seaward of barrier
        outpath            resulting SWAN spectrum file shoreward of barrier

    Options:
        -h, --help         show this help message and exit
        --closed           assume barrier doors are closed
        --door=NUM         location index in SWAN files
        --verbose=LEVEL    write logging messages
```
