import streamlit as st
import regex as re
import pandas as pd
from db_funcs import db_setup, UserDB, LedgerDB

DB_FILE = "pkr.db"

def streamlit_setup():
    st.set_page_config(page_title="Variance", page_icon=":spades:")
    st.sidebar.success("Interative Poker Ledger")
    if "username" in st.session_state:
        st.title(f"{st.session_state['username']}'s Ledger:clubs:")
    else:
        st.title('Ledger:clubs:')

class Auth:
    def __init__(self, db):
        self.user_db = UserDB(db)

    def __check_inputs(self, user, pwd):
        pwd_reqs = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
        return re.match(pwd_reqs, pwd) and user.isalnum()

    def authorize(self, user, pwd):
        if not self.__check_inputs(user, pwd):
            st.error("Username or Password don't meet specifications.")
        else:
            self.user_db.auth_user(user, pwd) 
    
    def register(self, user, pwd):
        if not self.__check_inputs(user, pwd):
            st.error("Username or Password don't meet specifications.")
        else:
            self.user_db.add_user(user, pwd)
    
class Ledger:
    def __init__(self, db, username):
        self.__db = LedgerDB(db)
        #st.dataframe(self.__db.raw_ledgers(username))
        self.__username = username
        self.__ledger = self.__db.get_base_ledger(username)
        self.__stats = self.__db.get_ledger_stats(username)

    def display(self):
        st.columns([3, 2])
        st.experimental_data_editor(self.__ledger)
        st.dataframe(self.__stats)

    def update(self):
        pass

streamlit_setup()
db = db_setup()
if "username" not in st.session_state:
    with st.form(key='authy'):
        st.write("Sign In to View Personal Ledger")
        username = st.text_input("Username (No special characters)")
        password = st.text_input("Password (8+ characters, \
                                1+ uppercase letters, \
                                1+ lowercase letters, 1+ numbers \
                                and 1+ special character)")
        login = st.form_submit_button(label='Log In', use_container_width=True)
        register = st.form_submit_button(label='Register', use_container_width=True)
    auth = Auth(db)
    if login:
        auth.authorize(username, password)
    elif register:
        auth.register(username, password)
else:
    ledger = Ledger(db, st.session_state["username"])
    ledger.display()