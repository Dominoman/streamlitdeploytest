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
servicename="streamlit.service"
if [ ! -f $servicename ] ; then
  cp $servicename.template $servicename
fi

sed -i "s|%currentpath%|$currentpath|g" $servicename

if [ ! -f /etc/systemd/system/$servicename ] ; then
  print "xxx"
  # sudo ln -s "$currentpath/$servicename" /etc/systemd/system/$servicename
fi