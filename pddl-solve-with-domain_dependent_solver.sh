#!/bin/bash

DDS=./ricochet-robot-solver/target/release/ricli

length=$(./pddl-to-domaindepsol.py $1 | ./ricochet-robot-solver/target/release/ricli)

echo Plan length: $length

