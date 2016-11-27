#!/usr/bin/env python
import re
import sys

in_file = sys.argv[1]
out_file = sys.argv[2]

avg_sample_rate = 794.0
avg_sample_period = 1/avg_sample_rate

decimal_regex = "[0-9]*.[0-9]*"
patterns = [
    ("start", re.compile("__main__ - INFO - starting ({0}) Amps, starting ({0}) Volts".format(decimal_regex)), 0.0, avg_sample_period),
    ("during", re.compile("__main__ - INFO - current draw is ({0}) Amps, voltage draw is ({0}) Volts".format(decimal_regex)), 0.0, avg_sample_period),
    ("looking", re.compile("__main__ - INFO - Looking for markers..."), 0.0, 0.5),
    ("parallel", re.compile("__main__ - INFO - Turning parallel to marker"), 2.0, 0.0),
    ("perpendicular", re.compile("__main__ - INFO - Moving to be perpendicular to marker"), 2.0, 0.0)
]

with open(in_file) as inp, open(out_file, "w") as outp:
    outp.write("t,V,I,type\n")
    t = 0
    for line in inp:
        for sample_type, pattern, before_duration, after_duration in patterns:
            parsed = pattern.match(line)
            if parsed is not None:
                groups = parsed.groups()
                if len(groups) == 2:
                    i, v = groups
                    t += before_duration
                    outp.write("{0},{1},{2},{3}\n".format(t, v, i, sample_type))
                    t += after_duration
                    break
                else:
                    t += before_duration
                    outp.write("{0},0.0,0.0,{1}\n".format(t, sample_type))
                    t += after_duration
