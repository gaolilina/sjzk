#!/bin/sh
python generate.py

python activity
python competition.py
python forum.py
python team.py
python user.py
python admin_user.py

rm activity
rm competition.py
rm forum.py
rm team.py
rm user.py
rm admin_user.py
