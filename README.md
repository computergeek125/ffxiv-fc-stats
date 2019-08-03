# ffxiv-fc-stats

Parser based on XIVAPI for creating a histogram of character levels in a free company for Final 
Fantasy XIV

## Initial setup

When cloning, you will need to do a `git clone --recursive` to ensure to pick up the XIVAPI 
submodule.  To make this program work, I had to modify the API library.  This is temporary, I'll PR
the library with my changes when I'm done here.  If the upstrem module is updated and I forgot about
this, just delete the submodule from the filesystem and the program should pick up that it has to 
use the system version of XIVAPI.py.

To install requisite libraries, run `pip3 install -r requirements.txt`.  For GUI support (and I 
haven't finished direct image write so you kind of need it right now), you'll also need the 
`tkinter` python package.  In Ubuntu, this can be installed with `apt install python3-tkinter`.
Without that, matplotlib crashes with a cryptic `agg`-related error message when the program tries
to show a graph onscreen.

To prime the config, copy `config.default.json` to `config.json`.  If you're using an API key, put 
that in the `api-key` line.  The others are (what I hope to be) sane defaults.

To run the program at its most basic level, run `./ffxiv-fc-stats.py -i <id>` where `<id>` is the ID
of a free company from Lodestone.  You can find this in the URL if you go to the page in a web
browser.  At this time, the utility does not support searching by FC or character name, but support
for that is coming soon(tm)!

The program will assume your python interpreter is named `python3`.  If that is not true you'll need
to run the program like `my-python-interpreter-name ./ffxiv-fc-stats.py ...`

## Parameters:

```shell
usage: ffxiv-fc-stats.py [-h] [-c CONFIG] -i ID [-o OUT]
                         [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Config to use
  -i ID, --id ID        ID of the Free Company to query
  -o OUT, --out OUT     filename to write to. If none, will attempt use GUI
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --log {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Set the logging level
```

- `-h`/`--help`: as it says, prints out the help.  This is generated with `argparse` at this time
- `-c`/`--config`: if you have more than one config file, this will tell the program which one to 
use.  If it's omitted, the program will assume a default of `config.json`
- `-i`/`--id`: the Lodestone ID of the Free Company you are trying to scan.  You can find this in 
the URL bar when you go to the FC's page on Lodestone by searching or clicking from a character info
page.
- `-o`/`--out`: don't use this it's not written yet and ignored.
- `-l`/`--log`: This will pass one of the indicated log levels to the Python logging subsystem.
It will also affect the log levels of compatible libraries, such as Matplotlib and XIVAPI.py

## `config.json`

- `api-key`: Put your API key here. If this is an empty string, the program will pass said empty 
string to the API, which _should_ allow it to run without a key.  I think.  If it's null, the 
program should remap it to be an empty string. (if it doesn't that a bug)
- `rate-limit`: This is how many requests the program should make against the API within 
`rate-limit-window`.  Once it hits that limit, it will sleep for `rate-limit-window` seconds and 
continue.
- `rate-limit-window`: value in seconds that describes the slice of time the `rate-limit` exists for
- `mpl-style`: this is passed directly to Matplotlib's style string.  More Matplotlib styling to
come for the future!

## Environmental notes

My test environment is Windows Subsystem for Linux with Ubuntu, so _in theory_ that means it works 
on native Linux as well.  I didn't write any system-level code (that I remember), so _in theory_ it 
should also work on native Windows python and macOS python.

I'm using Python 3.6.8, but it should work in most versions of the Python 3.x.x series.  I don't
expect to ever need to use Python 2.x.x series with this unless someone can give me a REALLY good
reason to.