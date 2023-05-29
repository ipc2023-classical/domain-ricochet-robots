#!/bin/bash

CLINGO=/opt/clingo/v5.6.2/bin/clingo

$CLINGO --opt-mode=opt --quiet=1,0,0 -V10 "$1" asp-2015/encoding.asp 2>&1 | tee tmp.clingo.log

plan=$(cat tmp.clingo.log | grep -o 'go([a-z]\+,\(east\|west\|south\|north\),[0-9]\+)')

echo Plan: $plan
echo Plan length: $(echo "$plan" | wc -l)

rm -f tmp.clingo.log
