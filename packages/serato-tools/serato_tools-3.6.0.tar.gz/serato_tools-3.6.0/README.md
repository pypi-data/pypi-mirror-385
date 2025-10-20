## Includes:

- Serato track tag parsing and modification, including cue points, track color, beatgrid, waveform, autogain, etc.
- Serato library database parsing and modification
- Serato crate parsing and modification
- Serato smart crate parsing and rule modification
- Dynamic beatgrid analysis that can be saved to a track's beatgrid.
- Serato USB export that beats Serato's sync by putting all files in 1 folder (without duplicates) and only copying changed files, unlike Serato's sync which takes forever and creates many duplicate file locations

**Currently designed for Python 3.12+. If you would like backwards compatibility with an older version, please reach out!**

## Example uses:

**USB:**
- Export crates (including Smart Crates) to USB. Beats Serato's sync by keeping all files in 1 folder and by comparing files for changes (instead of always copying, like Serato does)

**Tracks:**
- Change hot cue's text (i.e. change to all caps; change "c" to "CHORUS", etc.)
- Set a hot cue's text based on its color (i.e. if RED, set to "EXIT")
- Set a track's color (i.e. if has hot cues, change to BLUE)
- Set a piece of metadata due to a track's color (i.e. if track is green, set "grouping" to "TAGGED") (this is useful since can't create smart crates by track color in Serato)
- Analyze a track's Dynamic Beatgrid and save it to the beatgrid Serato tag.

**Database:**
- Rename a file while changing its location in the database as well, so that it doesn't go missing.
- After changing a track's metadata, modify database values for a specific track so that you don't have to "Reload Id3 Tags" in Serato, the change appears in Serato instantly.

**Crate:**
- Read a crate's tracks
- Remove a track from a crate
- Add a track to a crate
- List available crates

**Smart Crate:**
- Read a smart crate's tracks and rules
- Modify a smart crate's rules
- List available smart crates

_**Code examples are below.**_

# Installation

```cmd
pip install serato-tools
```

The following deps are optional, but **must be installed based on what features you want to use**:

- For getting/modifying track metadata including tags, cue points, beagrid, and waveform, must install `pip install mutagen`
- For viewing a track's waveform, must install `pip install pillow`
- For beatgrid analysis, must install `pip install numpy` and `pip install librosa`

# Examples

### Analyzing and setting a dynamic beatgrid

 Rekordbox has Dynamic Beatgrid Analysis but Serato doesn't. This analyzes a non-consistent BPM across a track, such as a track with live drums, and snaps a beatgrid marker to each beat.

_NOTE: This feature has only been tested on a couple of tracks. Recommend reviewing the resulting beatgrid in Serato— some grid markers may require adjustment. It seems to be working pretty great though!_

```cmd
>>> serato_analyze_beatgrid "Music/Dubstep/Mind Splitter - YAPPIN'.mp3"
```

### Exporting crates to USB

**NOTE: replaces existing crates on flash drive! (but does not delete existing track files) (TODO: ability to merge with existing)**

```cmd
>>> serato_usb_export --drive E --crate_matcher *house* *techno* --root_crate="Dave USB"
```

### Renaming a file and changing its location in the database

This renames the file path, and also changes the path in the database to point to the new filename, so that the renamed file is not missing in the library.

_NOTE: Recommended to make a backup of the database file elsewhere, before modifying via this package, in case an unforseen bug appears._

```python
from serato_tools.database_v2 import DatabaseV2

db = DatabaseV2()
db.rename_track_file(src="5udo - One - Original Mix.mp3", dest="5udo - One.mp3")

```

### Modifying the database file

_NOTE: Recommended to make a backup of the database file elsewhere, before modifying via this package, in case an unforseen bug appears._

```python
from serato_tools.database_v2 import DatabaseV2

now = int(time.time())

def modify_uadd(filename: str, prev_val: Any):
    print(f'Serato library change - Changed "date added" to today: {filename}')
    return now

def modify_tadd(filename: str, prev_val: Any):
    return str(now)

def remove_group(filename: str, prev_val: Any):
    return " "

db = DatabaseV2()
# a list of field keys can be found in serato_tools.database_v2
db.modify_file(
    rules=[
        {"field": DatabaseV2.Fields.DATE_ADDED_U, "files": files_set_date, "func": modify_uadd},
        {"field": DatabaseV2.Fields.DATE_ADDED_T, "files": files_set_date, "func": modify_tadd},
        {"field": DatabaseV2.Fields.GROUPING, "func": remove_group}, # all files
    ]
)
```

### Setting track color

```python
from serato_tools.track_cues_v2 import TrackCuesV2, TRACK_COLORS

tags = TrackCuesV2(file)
tags.set_track_color('/Users/Username/Music/Dubstep/Raaket - ILL.mp3',
    TRACK_COLORS["purple"],
    delete_tags_v1=True
    # Must delete delete_tags_v1 in order for track color change to appear in Serato (since we never change tags_v1 along with it (TODO)). Not sure what tags_v1 is even for, probably older versions of Serato. Have found no issues with deleting this, but use with caution if running an older version of Serato.
)
tags.save()
```

### Modifying track metadata / hot cues

```python
from mutagen.id3._frames import TIT1
from serato_tools.track_cues_v2 import TrackCuesV2, CUE_COLORS, TRACK_COLORS
from serato_tools.utils.track_tags import del_geob

def red_fix(prev_val: ValueType):
    if prev_val in [CUE_COLORS["pinkred"], CUE_COLORS["magenta"]]:
        print("Cue close to red, changed to red")
        return CUE_COLORS["red"]

def name_changes(prev_val: ValueType):
    if (not isinstance(prev_val, str)) or prev_val == "":
        return

    # make cue names all caps
    val_caps = prev_val.strip().upper()
    if prev_val != val_caps:
        return val_caps

def set_grouping_based_on_track_color(prev_val: ValueType):
    if prev_val == TRACK_COLORS["limegreen3"]:
        tagfile.tags.setall("TIT1", [TIT1(text="TAGGED")])
    elif prev_val in [ TRACK_COLORS["white"], TRACK_COLORS["grey"], TRACK_COLORS["black"]]:
        tagfile.tags.setall("TIT1", [TIT1(text="UNTAGGED")])

tags = TrackCuesV2(file)
tags.modify_entries(
    {
        "cues": [
            {"field": "color", "func": red_fix},
            {"field": "name", "func": name_changes},
        ],
        "color": [
            {"field": "color", "func": set_grouping_based_on_track_color},
        ],
    },
    delete_tags_v1=True
    # Must delete delete_tags_v1 in order for many tags_v2 changes appear in Serato (since we never change tags_v1 along with it (TODO)). Not sure what tags_v1 is even for, probably older versions of Serato. Have found no issues with deleting this, but use with caution if running an older version of Serato.
)
tags.save()
```

### Listing available crates or smart crates

```python
from serato_tools.crate import Crate
Crate.list_dir()

from serato_tools.smart_crate import SmartCrate
SmartCrate.list_dir()
``` 

### Modifying a SmartCrate Rule

__via command line__

_one crate_
```cmd
>>> serato_smartcrate '/Users/Username/Music/_Serato_/SmartCrates/Dubstep.scrate' --set_rules --grouping UNTAGGED
```

_all crates_
```cmd
>>> serato_smartcrate --all --set_rules --grouping UNTAGGED
```

__via code__

```python
from serato_tools.smart_crate import SmartCrate

crate = SmartCrate('/Users/Username/Music/_Serato_/SmartCrates/Dubstep.scrate')

def modify_rule(rule: SmartCrate.Rule):
    if rule.field != SmartCrate.RULE_FIELD["grouping"]:
        return rule
    rule.set_value(SmartCrate.Fields.RULE_VALUE_TEXT, "UNTAGGED")
    return rule

crate.modify_rules(modify_rule)
crate.save()
```

### Crate details and adding a track

```python
from serato_tools.crate import Crate

crate = Crate('/Users/Username/Music/_Serato_/Subcrates/Dubstep.crate')

print(crate)
# OUTPUT:
#
# Crate containing 81 tracks:
# Music/Dubstep/Saka - backitup.mp3
# Music/Dubstep/Mind Splitter - YAPPIN'.mp3
# Music/Dubstep/Flozone - DO IT.mp3
# Music/Dubstep/Evalution - Throw It Back.mp3
# ...

crate.print()
# OUTPUT:
#
# [   ('vrsn', 1.0/Serato ScratchLive Crate),
#     ('osrt', [('brev', b'\x00')]),
#     ('ovct', [('tvcn', 'key'), ('tvcw', '0')]),
#     ('ovct', [('tvcn', 'artist'), ('tvcw', '0')]),
#     ('ovct', [('tvcn', 'song'), ('tvcw', '0')]),
#     ('ovct', [('tvcn', 'bpm'), ('tvcw', '0')]),
#     ('ovct', [('tvcn', 'playCount'), ('tvcw', '0')]),
#     ('ovct', [('tvcn', 'length'), ('tvcw', '0')]),
#     ('ovct', [('tvcn', 'added'), ('tvcw', '0')]),
#     (   'otrk',
#         [   (   'ptrk',
#                 'Music/Dubstep/Flozone - Candy Paint')]),
#     (   'otrk',
#         [   (   'ptrk',
#                 'Music/Dubstep/Mind Splitter - LISTEN TO ME')]),
#     ('otrk', [('ptrk', 'Music/Dubstep/Flozone - DO IT')]),
# ...


# Example: Add a track to the crate and save it as a new crate
crate.add_track('/Users/Username/Music/Dubstep/Chozen - I Wanna Dance.mp3')
crate.save_to_file('/Users/Username/Music/Dubstep/New Crate.crate')
```

### Smart Crate details (TODO: modification)

```python
from serato_tools.smart_crate import SmartCrate

s_crate = Crate('/Users/Username/Music/_Serato_/SmartCrates/Dubstep.scrate')
print(s_crate)
```

# Serato Tags

Original writeup on Serato GEOB tag discoveries: [blog post](https://homepage.ruhr-uni-bochum.de/jan.holthuis/posts/reversing-seratos-geob-tags)

| GEOB Tag                                     | Research Progress | Contents                                                                        | Script File                                  |
| -------------------------------------------- | ----------------- | ------------------------------------------------------------------------------- | -------------------------------------------- |
| [`Serato Analysis`](docs/serato_analysis.md) | Done              | Serato version information                                                      |
| [`Serato Autotags`](docs/serato_autotags.md) | Done              | BPM and Gain values                                                             | [`track_autotags.py`](src/track_autotags.py) |
| [`Serato BeatGrid`](docs/serato_beatgrid.md) | Mostly done       | Beatgrid Markers                                                                | [`track_beatgrid.py`](src/track_beatgrid.py) |
| [`Serato Markers2`](docs/serato_markers2.md) | Mostly done       | Hotcues, Saved Loops, etc.<br>_(The main one used in newer versions of Serato)_ | [`track_cues_v2.py`](src/track_cues_v2.py)   |
| [`Serato Markers_`](docs/serato_markers_.md) | Mostly done       | Hotcues, Saved Loops, etc.<br>_(Old, not used in newer versions of Serato)_     | [`track_cues_v1.py`](src/track_cues_v1.py)   |
| [`Serato Offsets_`](docs/serato_offsets_.md) | _Not started_     | ???                                                                             |
| [`Serato Overview`](docs/serato_overview.md) | Done              | Waveform data                                                                   | [`track_waveform.py`](src/track_waveform.py) |

The different file/tag formats that Serato uses to store the information are documented in [`docs/fileformats.md`](docs/fileformats.md), a script to dump the tag data can be found at [`track_tagdump.py`](src/track_tagdump.py).

# Sources

- Serato track file tag parsing and modification from https://github.com/Holzhaus/serato-tags , which appears to be no longer maintained
- Serato crate parsing and modification from https://github.com/sharst/seratopy
- Dynamic beatgrid analysis from [https://github.com/heyitsmass/audio](https://github.com/heyitsmass/audio/blob/master/audio/beat_grid.py)

# Contributing

If you want a new feature, or have a bug fix, please put in a PR!
