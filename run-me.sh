#!/bin/bash

cd "$(dirname "$0")"
set -ex

# Virtuális környezet létrehozása
if [ ! -f pyvenv.cfg ] ; then
  python -m venv .
fi

# Aktiváljuk a virtuális környezetet
source bin/activate

# Config.py létrehozása, ha nincs
if [ ! -f config.py ] ; then
  cp config.py.template config.py
fi

# Csomagok installálása
if [ -f requirements.txt ] ; then
  pip install -r requirements.txt
fi

# streamlit config
currentpath=$(pwd)
username=$(whoami)
servicename="streamlit"
groupname=$(id -gn)

if [ ! -f $servicename ] ; then
  cp $servicename.service.template $servicename.service
  sed -i "s|%currentpath%|$currentpath|g; s|%username%|$username|g; s|%groupname%|$groupname|g" $servicename.service
fi

if [ ! -f /etc/systemd/system/$servicename.service ] ; then
  sudo ln -s "$currentpath/$servicename.service" /etc/systemd/system/$servicename.service
fi

# Restart Service
sudo systemctl daemon-reload
sudo systemctl enable $servicename
sudo systemctl restart $servicename