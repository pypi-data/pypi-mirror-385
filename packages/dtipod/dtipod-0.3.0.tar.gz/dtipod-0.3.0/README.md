# dtipod

This program is a podcatcher in the style of "do_the_internet.sh",
found on Gemini (the Smolweb protocol, not the other thing) and
[popularized by Ploum](https://ploum.net/2021-11-19-offlinetools.html).
The name `dtipod` is directly derived from "`d`o `t`he `i`nternet".

## Installation

### System requirements

- `curl`
- `python3` (tested with 3.12)
- `pipx` (optional, but simplifies installation a lot)

### Cloning the repo

```shell
git clone https://git.sr.ht/~mbuechse/dtipod
cd dtipod
```

### Installation proper

Pros can install this Python program into a virtualenv of choice using `setup.py`;
alternatively, the recommended way is to use `pipx` and then install like so:

```shell
$ pipx install .
```
## Usage

The program is quite boring, as it's supposed to be:

```shell
# import subscriptions from OPML file
dtipod import ~/Downloads/antennapod-feeds-2025-08-30.opml

# add new subscription
dtipod import-url https://overpopulationpodcast.libsyn.com/rss

# show detailed contents of inbox (Markdown style)
dtipod inbox

# fetch and parse RSS for all subscriptions
dtipod update

# show all feeds w/some description
dtipod feeds --long | less -S

# show 25 most recent episodes w/some description
dtipod episodes --long | less -S

# show 3 most recent episodes per feed
dtipod list | less -S

# download 3 episodes given by hashid
dtipod download 6bbc2994 87095be6 79650141

# clear inbox (whatever I don't want to download)
dtipod clear
```

Note: all fetching/downloading is implemented using `curl --parallel`.

## Copyright and License

Copyright 2025 Matthias Büchse.

dtipod is free software: you can redistribute it and/or modify it under the terms of the
GNU General Public License as published by the Free Software Foundation, either version 3
of the License, or (at your option) any later version.

dtipod is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with dtipod.
If not, see <https://www.gnu.org/licenses/>.
