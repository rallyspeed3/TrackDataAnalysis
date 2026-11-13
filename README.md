# Track Data Analysis (fork)

This is a personal fork of [racer-coder/TrackDataAnalysis](https://github.com/racer-coder/TrackDataAnalysis)
by Scott Smith -- all credit for the original design and implementation
goes to him. This fork exists because the upstream project hasn't seen
updates in a while; changes here are AI-assisted (built with Claude) and
not reviewed by someone with deep knowledge of the codebase, so treat
them accordingly. No PRs or issues are being filed upstream for this
work -- if you want the original, use the link above.

### Changes in this fork

- Fixed a `loadfile` crash (`ValueError: Invalid value for mpv parameter`)
  when playing video on modern libmpv (>= 0.38.0), which changed the
  `loadfile` command's argument order ([`ui/mpv.py`](ui/mpv.py)).
- Made the RaceLogic `.vbo` parser tolerant of files missing a
  `[laptiming]` section, a `height` channel, or a full `[channel units]`
  list, instead of crashing on `KeyError`/`IndexError`
  ([`data/racelogic.py`](data/racelogic.py)).
- Added keyboard shortcuts for video playback: Space to play/pause,
  Left/Right arrow to step back/forward one frame
  ([`ui/video.py`](ui/video.py)).
- Added independent data/video sync markers, so you can mark the same
  real-world moment in each even before they're aligned, then compute
  the offset from the pair:
  - `M` / `Shift+M` / `[` / `]`: add / remove nearest / jump to
    prev-next **data** marker (placed in the data's own timeline).
  - `V` / `Shift+V` / `Ctrl+[` / `Ctrl+]`: same, but for a **video**
    marker (placed at the video's own raw playback position).
  - `Ctrl+M`: "Sync video to data using markers" -- sets
    `video_alignment` from the nearest data marker and nearest video
    marker to where you currently are.
  - Data markers are solid orange, video markers are dashed cyan, both
    shown on the graph and the video alignment slider, and both are
    saved with your workspace ([`ui/video.py`](ui/video.py),
    [`ui/timedist.py`](ui/timedist.py), [`ui/state.py`](ui/state.py)).
  - Each pane's right-click menu only shows what's actually relevant
    to it: the graph's menu has the data marker actions, the video's
    menu has the video marker actions and "Sync video to data using
    markers" -- not both crammed into one menu.
  - Added "Sync alt lap to ref lap using markers" (`Ctrl+Shift+M`,
    graph menu) -- the same idea as syncing video to data, but for
    aligning two *logs* against each other. Useful as a GPS-free
    "start/finish line": drop a data marker on the same real-world
    moment in each run's log (the ref lap's and the alt lap's), and
    this computes the alt lap's offset from that pair, matching
    whichever display mode (time or distance) the graph is
    currently in. Also fixed marker rendering to use the same
    position formula `paintGraph` actually draws channel traces with
    -- markers were using a different (lap-relative) conversion, so
    after syncing, the data visibly snapped into alignment but a
    marker barely moved, making it look stuck
    ([`ui/timedist.py`](ui/timedist.py)).
- Added "Split channels by log (stacked)" (graph right-click menu) --
  instead of overlaying each compared lap's same channel on one row
  in different colors, stacks them as separate rows (ref's Throttle,
  alt's Throttle, ref's Brake, alt's Brake, ...), sharing a Y-axis
  scale per channel so sibling rows stay comparable, with the shared
  cursor crossing all of them at once. Each row keeps its channel's
  own color (the same one "Edit channel..." sets, right-click a
  channel's name) instead of flattening every channel in a lap to
  that lap's color -- once each row is already labeled R:/A:, there's
  no need to do that just to tell the logs apart
  ([`ui/timedist.py`](ui/timedist.py)).
- Added "Stack videos vertically" (video right-click menu) for the
  ref/alt video comparison view, as an alternative to the default
  side-by-side layout. Each video now also has a small "Reference" /
  "Alternate" label above it either way, so it's clear which is
  which ([`ui/video.py`](ui/video.py)).
- Added "Reference lap color..." / "Alternate lap color..." (graph
  right-click menu) to customize the colors used for ref/alt
  throughout the app (graphs, Data dock, lift & coast, XY scatter --
  it's one shared setting, not per-graph), persisted in config.ini
  ([`ui/state.py`](ui/state.py), [`ui/timedist.py`](ui/timedist.py),
  [`gui.py`](gui.py)).
- Added a custom background image ("wallpaper") for the worksheet
  canvas behind your panes -- right-click the empty canvas area ->
  "Set background image..." (or "Clear background image" to go back
  to the default checkerboard). Scales to fill the canvas and is
  dimmed so panes on top stay readable; persisted in config.ini, with
  a missing/moved file just falling back quietly
  ([`ui/components.py`](ui/components.py)).
- Added a loader for the plain CAN-bus CSV logs produced by the
  companion mazda3-telemetry-toolkit project (no GPS, no lap-beacon
  channel). Distance comes from integrating the 'speed' channel, so
  it works fine without GPS; each file loads as a single lap, which
  is enough to compare separate *runs* against each other (open
  several CSVs and pick ref/alt/extra laps from different files, via
  the Data dock's R/A columns -- see "Comparing runs" below) -- just
  not multiple laps within one recording. Also added `*.csv` to the
  File > Open dialog's file-type filter (it has its own list,
  separate from the file-extension-to-loader mapping) and gave these
  logs a usable `Log Date`/`Log Time` (from the file's own
  last-modified time, since the CSV has no wall-clock timestamp
  anywhere) -- the Data dock requires both on every open log to sort
  and group them, and crashed populating itself without them
  ([`data/mazda_csv.py`](data/mazda_csv.py), [`ui/datamgr.py`](ui/datamgr.py)).
- Renamed the right-click "Cut" action on any pane (graph, video,
  etc.) to "Remove", and added "Minimize", which hides the pane and
  drops a small labeled tab at the bottom of the window; click the tab
  to bring it back. The tab always stays on top of other panes, and
  minimized state is saved with your workspace
  ([`ui/components.py`](ui/components.py)).
- The track map can now be panned (click and drag) and zoomed
  (scroll wheel, centered on the cursor) independently of the graph's
  own time/distance selection, instead of always auto-fitting to it.
  Right-click "Reset map view" to go back to auto-fit. The track
  outline and current-section outline colors are also customizable
  via right-click ("Track outline color...", "Current section
  color..."), and persist across restarts ([`ui/map.py`](ui/map.py)).
- Fixed the video-marker line on the main graph going stale while
  manually dragging the video alignment slider -- it only refreshed
  on the next unrelated repaint instead of live, during the drag
  ([`ui/video.py`](ui/video.py)).

## Comparing runs (works without GPS)

Open each run's file (File > Open, or drag onto the window -- multiple
files at once is fine). The **Data** dock (left sidebar tab) lists every
open log grouped by date, with a lap under each; its **R** / **A** / **3**
columns pick which lap is the reference, the alternate (comparison), and
extra overlay laps, respectively -- across *any* open logs, not just laps
within one file. Once picked, graphs show both aligned by distance, and
"Show Time Slip" (right-click a graph) adds the gap-time trace between
them. This is distance-based, not GPS-based, so it works the same whether
your logs have GPS or not -- see `data/mazda_csv.py` for a CAN-only
example, where distance comes from integrating the speed channel instead.

By default both laps' Throttle (say) overlay on one row, in different
colors. Right-click a graph and check **"Split channels by log
(stacked)"** to instead stack them as separate rows -- ref's Throttle,
alt's Throttle, ref's Brake, alt's Brake, and so on -- each pair sharing
the same scale so they're directly comparable, with the shared cursor
moving across all of them at once. Each row keeps Throttle's/Brake's own
color (right-click a channel's name -> "Edit channel..." to change it),
rather than painting everything in that lap the same color.

Each run's own lap "starts" wherever its logging happened to start,
though, which usually isn't the same real-world point for two separate
recordings. If that leaves the two runs visibly offset on the graph: pick
a moment that's identifiable in *both* runs (the start line, a hard brake
into a landmark corner, whatever stands out), place a data marker there
in each (`M`), then **"Sync alt lap to ref lap using markers"**
(`Ctrl+Shift+M`). That's the GPS-free equivalent of a start/finish line.

## Motivation

Every data acquisition tool comes with their own software, so why make another tool?

- High DPI Support.  Most tools don't enable High DPI support and thus
  are scaled and look horrible on a modern display.  You can override
  this in Windows, and Motec i2 actually mostly works in this mode but
  still has some edge cases that don't render properly.  AiM
  RaceStudio 2 and 3 work very badly if you override scaling.

- Responsive UI.  Motec i2 is mostly responsive while AiM RaceStudio 2
  and 3 are quite sluggish: when dragging the cursor, the values for
  the channels update very slowly.

- Cross platform.  There should be a native tool for Windows, Linux, and Mac OSX.

- Video support.  Motec supports video files but playback was very
  choppy for a 1080p/60 video on a new 2024 laptop.  AiM only supports
  video files from SmartyCam.

### Alternatives

| Feature | MoTeC i2 | AiM RaceStudio | GEMS Data Analysis | Track Attack | Race Capture |
| --- | --- | --- | --- | --- | --- |
| High DPI support | almost | no | YES | almost | YES |
| Responsive UI | YES | no | YES | YES | YES |
| Video support | Pro (but didn't work for me) | only smartycam | Pro version | Premium version | YES |
| Cross platform | no | no | no | Windows + Mac | YES |
| Many data formats | CSV (Pro) | no | no | YES | no |

- [Aim_2_MoTeC](https://github.com/ludovicb1239/Aim_2_MoTeC) will
  convert AiM DRK and XRK files to a MoTeC LD file that enables i2 Pro
  features.  If i2 works for you this may be a more robust solution.
  It only works on Windows, but then again, i2 only works on Windows.
- [RCP2GEMS](https://github.com/autosportlabs/RCP2GEMS/) will convert
  AutoSport Labs log files (a form of CSV) to another form of CSV that
  GEMS can read.

## Features

- Native high dpi support - fonts are sized by dpi/scaling.  Most
  lines are still drawn at a single pixel though which still looks
  good on a black background.

- Responsive UI - channel search, cursor drag, switching worksheets,
  resizing all respond very quickly, even when dealing with 2 hour
  logs at 100Hz on a 10+ year old computer (i5-2500 with integrated
  graphics running 1600x1200).

- Cross platform (Windows 10+, Ubuntu 22.04+, Mac Arm)

- Opens AiM XRK, MoTeC LD, ECUMaster ADULOG and EMUPROLOG, Autosport
  Lab LOG, RaceLogic VBOX, Race Technology RUN, MegaLogViewer MLG, and
  iRacing IBT files natively.

- Time/distance graph with overlaying channels, drag and drop channel
  support (for reordering the view), zoom in/out, pan, multiple laps
  with individual lap offsets, and time slip.

- Channel values report with simple, concise search (type `o p` for oil pressure).

- GPS map with optional satellite background for line comparison.

- Video from almost anything can be included.  Playback is kept
  synchronized even in distance mode by speeding up/slowing down
  playback of the alternate lap.

- Configurable workspace layout, with cut/copy/paste.

- Math channels.

- Database that caches metadata from your sessions for easy lookup.

### Future (aka missing) features

- Track editor for defining sections
- Various channel graphs (bar, steering, histogram, etc)
- Various reports (channel min/max/average, sector comparison, etc)

## Installation (from binary)

Windows x86_64/Arm and Mac Arm images can be found at
[Releases](https://github.com/racer-coder/TrackDataAnalysis/releases).

On Windows, it will install a start menu shortcut for "Track Data
Analysis" (just press the windows key and start typing Track).

## Installation (from source)

Track Data Analysis relies on the `PySide6` package for the UI.  This
precludes Windows versions before 10.

### Linux / Ubuntu

Track Data Analysis is developed and tested on Ubuntu 22.04.  You can
use the built in packages for most things except `glfw`, which you'll
have to install via `pip3`.  Later versions of Ubuntu have switched to
`python3.11` as the default, which is fine as long as the PySide2
package is available.  If you're installing PySide2 via `pip3`, then
you'll want to stick to `python3.10` or older.

Ubuntu 22.04:
```
sudo apt install python3-pyside2.qtwidgets python3-numpy libmpv1
pip3 install dacite glfw pyyaml # Ubuntu 23.04+ has apt package python3-pyglfw
python3 setup.py build_ext --inplace
```

You should then be able to run the program using either of the following:

```
./gui.py
python3.10 gui.py
```

### Windows 8+

You'll want to get Python 3.10 directly from
[python.org](https://www.python.org/downloads/release/python-31011/).
You should probably get the 'Windows installer (64-bit)'.  Do not use
the version of python from the Microsoft app store; I haven't tried it
but I have read enough that makes me think it won't work right.

Assuming that Python is in your path, you can then install the
Python package requirements with:
```
pip install -r requirements.txt
```

You will need to manually install [libmpv](https://sourceforge.net/projects/mpv-player-windows/files/libmpv/);
I typically put `libmpv-2.dll` under the `ui/` directory as that is
added to the path automatically.

You should then be able to run the program using:

```
python3 gui.py
```

### Mac Arm (and probably Intel?)

Mac is a little tricky; PySide2 is not technically supported on Mac
Arm machines, but it is available on [Homebrew](https://brew.sh/).
However, they make it a little difficult, and it will only show up
under Python3.10, so you need to make sure to specify that when
running various commands.

```
brew install pyside@2
brew link pyside@2
brew install mpv
pip3.10 install dacite glfw numpy pyyaml
python3.10 setup.py build_ext --inplace
```

Then you should be able to run the program with either:
```
./gui.py
python3.10 ./gui.py
```

## Basic introduction

### UI

The window is made up of components (graphs, videos, etc) and docks
(anything activated by a button on the left side of the screen).  The
dock windows can be attached to the UI on either the left side or
right side of the component area.  Docks are shown on all
worksheets, while components are specific to a worksheet.

### Components

Components have a context menu (right click), along with a top level
menu which is basically the same thing.  Components can be removed by
'Cut' and duplicated using 'Copy' / 'Paste'.  Actions such as enabling
time slip or linking video happen through component menus.  New
components can be added using the 'Add' menu.

### Worksheets / Workbooks / Workspaces

Each worksheet has it's own collection of graphs.  You can easily
switch between worksheets within a workbook by selecting the
corresponding tab on top.  You can select different workbooks using
the drop down.  Use the Layout menu to change the worksheet / workbook
organization.  The collection of workbooks is stored in the current
workspace; use the File menu to open/save workspaces.  Generally I
would assume most users will only use a single workspace, or maybe one
per car.

### Data

Log files are opened via File menu, and laps are generally selected
through the Data dock.  There should always be a single reference lap
selected.  There can be an alternate lap selected (for components that
only support two comparisons, such as video, this will be the one
given preference).  There can be a number of extra laps selected
though the UI can get pretty busy with a lot of laps selected.  Use
the data menu adjust parameters relating to laps.  NOTE that
Time/Distance is a per-worksheet parameter!

### Time/Distance Graphs

Channels can be added using either the Channels dock or the Values
dock.  Double click on the channel to add and it will by default be
added to a subgraph that has the same units, otherwise a new subgraph
will be created.  To always add to a new subgraph, hold down Ctrl
while double clicking.  Channels can be rearranged on the graph using
drag and drop: dropping onto a channel will put the dragged channel
after it.  Dropping onto the bottom half of a subgraph will insert a
new subgraph for that channel.

### Video

You can load any video file, but currently only one video file can be
associated with a log file.  Typically to align a video I will open
the first two laps, put the cursor at the start of the lap, enable
'Set video alignment' (right click on video), then drag the bottom
slider until the video lines up (the top timecode is session time, the
bottom timecode is video time).  Both videos should look roughly like
they're in the same spot.

### Satellite Maps

You'll need an API key from [MapTiler](https://www.maptiler.com/) to
get satellite maps.  A free account should work just fine and you
don't need to give them a credit card.  Once your account is created
navigate to [API Keys](https://cloud.maptiler.com/account/keys/) to
copy your key, then go to File/Preferences to set it.  You can always
disable the satellite background by right clicking on the map.

## Changelog

- 0.4.1
  - Fix important usability bugs in 0.4.0
- 0.4.0
  - Initial math expression support
  - 4x faster AiM XRK file processing.
  - Allow specifying 'last used' instead of 'interpolate' for channels (for gear, status, etc)
- 0.3.3
  - Significantly (50%) faster AiM XRK file processing.
  - Add handling for interpolated vs previous values in graphs
- 0.3.2
  - Context menu for worksheet tabs (new/rename/delete/duplicate/etc)
  - Parse some metadata from iRacing files for use in db
  - Fix bug in parsing some iRacing files
  - Allow * in channel search
- 0.3.1
  - iRacing IBT support
  - Automatic GPS lap insert for AiM files
  - Small bug fixes
- 0.3.0
  - Add automatic scanning of directories for quick access to old log files.
  - Add ability to diplay metadata from log files (venue/driver/etc)
- 0.2.0
  - Mac/Arm support
  - Channel editor to set units, decimals places, and color
  - Basic units support.  Fixes distance calculation when speed is not m/s.
  - Fix MoTeC beacon support
  - Fix Autosport Labs lap counter
