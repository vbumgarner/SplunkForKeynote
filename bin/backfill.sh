#!/bin/sh

../../../../bin/splunk cmd python ../../../../bin/fill_summary_index.py -app Keynote -name "*" -et -21day@day -lt @h -dedup true -auth admin:5plunkRules -sleep 2 -j 5

