#!/bin/sh
# Name ..... : unittest.sh
# Object ... : Launch unit tests software on Unix-like systems
# Parameters : -s to display stdout
# See python3 -m pytest -h for more options
# Author ... : MAILLARD Thierry (TMD)
# Date ..... : 1/7/2019
# Modif .... : 14/02/2018 : parameters allowed and transmitted to pytest
# Prerequisite : Pytest installed
#   sudo python3 -m pip install -U pytest
#  -k 'not global'

echo "Début des tests unitaires  ..."
python3 -m pytest  unittest $*
