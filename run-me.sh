#!/bin/bash

cd "$(dirname "$0")"
set -ex

# Virtuális környezet létrehozása
if [ ! -f pyvenv.cfg ] ; then
  python -m venv .
fi

# Aktiváljuk a virtuális környezetet
source bin/activate

# Csomagok installálása
if [ -f requirements.txt ] ; then
  pip install -r requirements.txt
fi

# streamlit config
if [ ! -d .streamlit ] ; then
  mkdir .streamlit
fi

if [ ! -f .streamlit/config.toml ] ; then
  streamlit config show > .streamlit/config.toml
fi

currentpath=$(pwd)
servicename="streamlit"
if [ ! -f $servicename ] ; then
  cp $servicename.service.template $servicename.service
fi

sed -i "s|%currentpath%|$currentpath|g" $servicename.service

if [ ! -f /etc/systemd/system/$servicename.service ] ; then
  sudo ln -s "$currentpath/$servicename.service" /etc/systemd/system/$servicename.service
fi

# Restart Service
sudo systemctl daemon-reload
sudo systemctl enable $servicename
sudo systemctl restart $servicename