import sqlite3
from notanorm import SqliteDb
import streamlit as st
import pandas as pd

''' Database-related Functions '''

DB_FILE = "pkr.db"

@st.cache_resource
def db_setup():
    db = SqliteDb(DB_FILE)
    db.query("CREATE TABLE IF NOT EXISTS users (username TEXT, \
                password TEXT);") 
    db.query("CREATE TABLE IF NOT EXISTS ledgers (user TEXT, \
            dt DATETIME DEFAULT CURRENT_DATE, buy_in INTEGER, \
            buy_out INTEGER, entry_id INTEGER PRIMARY KEY AUTOINCREMENT);")
    return db

class UserDB:
    def __init__(self, db):
        self.__db = db

    def __user_exists(self, username: str) -> bool:
        return self.__db.select("users", username=username)

    def __check_pwd(self, username: str, password: str) -> bool:
        to_check = self.__db.select("users", username=username)[0].password
        return password == to_check # Will add bcrypt protection later
        
    def auth_user(self, username: str, password: str):
        if not self.__user_exists(username):
            st.error("Username not found")
        elif not self.__check_pwd(username, password):
            st.error("Incorrect Password for Given User")
        else:
            st.session_state["username"] = username

    def add_user(self, username, password):
        if self.__user_exists(username):
            st.error("Username already exists.")
        else:
            self.__db.insert("users", username=username, password=password)
            st.session_state["username"] = username

class LedgerDB:
    def __init__(self, db):
        self.__db = db
    
    def __add_entry(self, username, buy_in = 0, buy_out = 0):
        self.__db.insert("ledgers", user=username, buy_in=buy_in, buy_out=buy_out)

    def raw_ledgers(self, username):
        self.__add_entry(username)
        ledger = self.__db.select("ledgers")
        return pd.DataFrame(ledger)

    def get_base_ledger(self, username: str) -> pd.DataFrame:
        st.write(self.__db.select("ledgers", user=username))
        if len(self.__db.select("ledgers", user=username)) == 0:
            self.__add_entry(username)
        
        sqlledger = self.__db.select_gen("ledgers", username=username, order_by="dt")
        headers = ["User", "Date", "Buy In", "Buy Out", "entry_id"]
        df = pd.DataFrame(sqlledger, columns=headers)

        st.dataframe(df)
        st.write(df['User'])
        df.drop("User")
        df.drop("entry_id")

        return df
    
    def get_ledger_stats(self, username: str) -> pd.DataFrame:
        ledger = self.get_base_ledger(username)
        stats = pd.DataFrame()
        
        stats["Net $"] = ledger["Buy Out"] - ledger["Buy In"]
        stats['%' + " Earnings"] = stats["Net $"] / ledger["Buy In"]

        return stats
