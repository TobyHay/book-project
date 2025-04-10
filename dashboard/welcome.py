'''A script that creates a Streamlit dashboard using book data from the RDS'''
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import pandas as pd
import streamlit as st
import altair as alt
import psycopg2

# Streamlit code heree
