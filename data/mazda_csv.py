
# Copyright 2026, fork additions. MIT License (see LICENSE).
#
# Loads the plain CAN-bus CSV logs produced by the companion
# mazda3-telemetry-toolkit project (tools/record_drive.py, against the
# Arduino/ESP32 can_live.ino firmware) -- time,throttle,brake,steering_deg,
# speed,rpm,gear,gear_raw,wheel_fl,wheel_fr,wheel_rl,wheel_rr. There's no
# GPS and no lap-beacon channel, so:
#   - distance comes from integrating 'speed' (see data/distance.py),
#     which works fine without GPS.
#   - the whole file loads as a single lap, since there's nothing to split
#     on. That's enough to compare separate RUNS against each other (open
#     several of these CSVs and pick ref_lap/alt_lap/extra laps from
#     different files) -- just not multiple laps within one recording.

import csv as csv_module
import os
import time
from array import array

from . import base

# (CSV column, display name, units, decimal points, interpolate)
CHANNELS = [
    ('throttle',     'Throttle',  '%',   1, True),
    ('brake',        'Brake',     '%',   1, True), # raw CAN units -> %, same calibration as tools/csv_to_vbo.py
    ('steering_deg', 'Steering',  'deg', 1, True),
    ('speed',        'Speed',     'mph', 1, True),
    ('rpm',          'RPM',       'rpm', 0, True),
    ('gear',         'Gear',      'gear', 0, False),
    ('wheel_fl',     'Wheel FL',  'Hz',  1, True),
    ('wheel_fr',     'Wheel FR',  'Hz',  1, True),
    ('wheel_rl',     'Wheel RL',  'Hz',  1, True),
    ('wheel_rr',     'Wheel RR',  'Hz',  1, True),
]

def MazdaCSV(fname, progress):
    with open(fname, 'rt', encoding='utf-8', newline='') as f:
        total_len = max(0, sum(1 for _ in f) - 1)

    channels = {disp: base.Channel(timecodes=array('d'), values=array('d'),
                                   name=disp, units=units, dec_pts=dec,
                                   interpolate=interp)
               for _col, disp, units, dec, interp in CHANNELS}
    col_to_disp = {col: disp for col, disp, _u, _d, _i in CHANNELS}

    max_tc = 0.
    with open(fname, 'rt', encoding='utf-8', newline='') as f:
        reader = csv_module.DictReader(f)
        for update_count, row in enumerate(reader):
            if (update_count & 4095) == 0 and progress:
                progress(update_count, total_len)
            tc = float(row['time']) * 1000. # seconds -> ms, matches this app's internal convention
            max_tc = tc
            for col, disp in col_to_disp.items():
                v = row.get(col)
                if not v:
                    continue
                val = float(v)
                if col == 'brake':
                    val = max(0.0, min(100.0, val / 100.0))
                channels[disp].timecodes.append(tc)
                channels[disp].values.append(val)

    laps = [base.Lap(0, 0, int(max_tc))]

    # The CSV's own 'time' column is relative (seconds since logging
    # started), with no wall-clock date/time anywhere in the file. The
    # Data dock (ui/datamgr.py) requires 'Log Date'/'Log Time' on every
    # open log to sort and group them, so fall back to the file's own
    # last-modified time -- not exact, but close enough to group/sort runs
    # sensibly, and far better than crashing that dock outright.
    tm = time.localtime(os.path.getmtime(fname))
    metadata = {
        'Log Date': '%02d/%02d/%d' % (tm.tm_mon, tm.tm_mday, tm.tm_year),
        'Log Time': '%02d:%02d:%02d' % (tm.tm_hour, tm.tm_min, tm.tm_sec),
    }
    return base.LogFile(channels, laps, metadata, ['Speed', None, None, None], fname)
