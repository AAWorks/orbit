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
            timestamp TIMESTAMP DEFAULT CURRENT_DATE, buy_in INTEGER, \
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
    
    def __add_entry(self, username, buy_in, buy_out):
        self.__db.insert("ledgers", user=username, buy_in=buy_in, buy_out=buy_out)

    def get_base_ledger(self, username: str) -> pd.DataFrame:
        if len(self.__db.select("ledgers", user=username)) == 0:
            self.__add_entry(username, 0, 0)
    
        sqlledger = [row for row in self.__db.select("ledgers", user=username)]
        df = pd.DataFrame.from_records(sqlledger)
        df = df.rename(columns={"timestamp": "Date",
                                 "buy_in": "Buy In",
                                 "buy_out": "Buy Out",
                                 "entry_id": "ID"})

        df = df.drop("user", axis=1)

        return df
    
    def get_enhanced_ledger(self, username: str) -> pd.DataFrame:
        ledger = self.get_base_ledger(username)
        ledger["Net $"] = ledger["Buy Out"] - ledger["Buy In"]
        ledger['%' + " Gain/Loss"] = ledger["Net $"] / ledger["Buy In"] * 100
        ids = ledger["ID"]
        ledger = ledger.drop("ID", axis=1)
        ledger["ID"] = ids
        return ledger
    
    def get_stats(self, ledger) -> pd.DataFrame:
        handle_0 = sum(ledger["Buy In"])
        if handle_0 == 0:
            handle_0 = 1
        stats = {"Capital Spent": sum(ledger["Buy In"]), 
                 "Capital Earned": sum(ledger["Buy Out"]), 
                 "Gross Profit": sum(ledger["Net $"]), 
                 "% Gain/Loss": sum(ledger["Net $"]) / handle_0 * 100
        }
        return list(stats.keys()), list(stats.values())
    
    def delete_row(self, entry_id):
        self.__db.delete("ledgers", entry_id=entry_id)
        st.success("Row Deleted")
