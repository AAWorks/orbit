import streamlit as st
import regex as re
import pandas as pd
import numpy as np
import plotly.express as px
from db_funcs import db_setup, UserDB, LedgerDB, VisDB
import datetime
import altair as alt

DB_FILE = "pkr.db"

def streamlit_setup():
    st.set_page_config(page_title="Variance", page_icon=":diamonds:")
    st.sidebar.success("Interative Poker Ledger")
    if "username" in st.session_state:
        st.title(f"{st.session_state['username']}'s Ledger")
    else:
        st.title('Ledger:clubs:')

def drop_table_indices():
    hide_table_row_index = """
            <style>
            thead tr th:first-child {display:none}
            tbody th {display:none}
            </style>
            """
    st.markdown(hide_table_row_index, unsafe_allow_html=True)

class Auth:
    def __init__(self, db):
        self.user_db = UserDB(db)

    def __check_inputs(self, user, pwd):
        pwd_reqs = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
        return re.match(pwd_reqs, pwd) and user.replace(" ", "").isalnum()

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
        self.__ledger_db = LedgerDB(db)
        self.__username = username

    def __add_entry(self):
        with st.form(key='add'):
            col1, col2, col3 = st.columns(3)
            date = col1.date_input(
                "Date of Entry",
                datetime.date.today())
            buy_in = col2.text_input("Buy In $")
            buy_out = col3.text_input("Buy Out $")
            add = st.form_submit_button(label='Add', use_container_width=True)
        if add:
            self.__ledger_db.add_row(self.__username, buy_in, buy_out, date)

    def __update_entry(self):
        with st.form(key='update'):
            col0, col1, col2, col3 = st.columns(4)
            date = col1.date_input("Date of Entry")
            rowid = col0.text_input("Entry ID")
            buy_in = col2.text_input("Buy In $")
            buy_out = col3.text_input("Buy Out $")
            update = st.form_submit_button(label='Update', use_container_width=True)
        if update:
            self.__ledger_db.update_row(rowid, buy_in, buy_out, date)

    def __drop_entry(self):
        with st.form(key='drop'):
            rowid = st.text_input("Entry ID")
            drop = st.form_submit_button(label='Drop', use_container_width=True)
        if drop:
            self.__ledger_db.delete_row(rowid)

    def __display_stats(self, ledger: pd.DataFrame):
        _, col1, _, col2, _, col3, _ = st.columns([3,4,1,4,1,4,2])
        headers, stats = self.__ledger_db.get_stats(ledger)
        col1.metric(headers[0], "${:0.2f}".format(stats[0]))
        col2.metric(headers[1], "${:0.2f}".format(stats[1]))
        col3.metric(headers[2], "${:0.2f}".format(stats[2]), "{:0.2f}%".format(stats[3]))

    def display(self):
        ledger = self.__ledger_db.get_enhanced_ledger(self.__username)
        self.__display_stats(ledger)
        table = ledger.style.format({"Buy In": '${:.2f}', "Buy Out": '${:.2f}',
                                      "PnL": '${:.2f}', "% Change": "{0:+g}%"},
                                      na_rep="N/A", precision=2)
        st.dataframe(table, use_container_width=True)

    def update(self):
        st.button("Refresh Ledger", use_container_width=True)
        with st.expander("Add Ledger Entry"):
            self.__add_entry()
        with st.expander("Update Ledger Entry"):
            self.__update_entry()
        with st.expander("Remove Ledger Entry"):
            self.__drop_entry()

class Visualize:
    def __init__(self, db, username):
        self.__db = LedgerDB(db)
        self.__graphs = VisDB(db)
        self.__username = username

    def graph_datevspnl(self):
        ledger = self.__db.get_enhanced_ledger(self.__username)
        data = self.__graphs.get_date_pnl(ledger)
        fig = px.line(data, x='Date', y="B) Profit")
        st.plotly_chart(fig)
        data = data.drop("Date", axis=1)
        st.bar_chart(data, use_container_width=True)

if __name__ == "__main__":
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
        log, graph = st.tabs(["Log", "Graph"])
        user = st.session_state["username"]
        ledger = Ledger(db, user)
        vis = Visualize(db, user)
        with log:
            ledger.display()
            ledger.update()
        with graph:
            vis.graph_datevspnl()