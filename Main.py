import streamlit as st

import config
from database import Database

db=Database(config.DB_FILENAME,config.DB_DEBUG)