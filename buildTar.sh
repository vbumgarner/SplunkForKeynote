#!/bin/sh

cd ..
COPYFILE_DISABLE=true tar --exclude=".*" --exclude="Keynote/local/*" --exclude="Keynote/lookups/*_data.csv" --exclude="*.pyc" -cvzf Keynote.spl Keynote

