import streamlit as st
import regex as re
from db_funcs import UserDB

DB_FILE = "pkr.db"

def streamlit_setup():
    st.set_page_config(layout="wide", page_title="Orbit", page_icon=":spades:")
    st.title('Welcome to Orbit:spades:')
    st.sidebar.success("Just Keep Gambling.")

streamlit_setup()