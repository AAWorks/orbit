import sqlite3
from notanorm import SqliteDb
import streamlit as st
import pandas as pd
import numpy as np
import regex as re
import datetime

''' Database-related Functions '''

DB_FILE = "pkr.db"

@st.cache_resource
def db_setup():
    db = SqliteDb(DB_FILE)
    db.query("CREATE TABLE IF NOT EXISTS users (username TEXT, \
                password TEXT);") 
    db.query("CREATE TABLE IF NOT EXISTS ledgers (user TEXT, \
            timestamp TIMESTAMP DEFAULT CURRENT_DATE, buy_in FLOAT, \
            buy_out FLOAT, entry_id INTEGER PRIMARY KEY AUTOINCREMENT);")
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
    
    def __add_entry(self, username, buy_in, buy_out, date):
        self.__db.insert("ledgers", user=username, buy_in=buy_in, buy_out=buy_out, timestamp=date)

    def get_base_ledger(self, username: str) -> pd.DataFrame:
        if len(self.__db.select("ledgers", user=username)) == 0:
            yesterday = datetime.date.today() - datetime.timedelta(days = 1)
            self.__add_entry(username, 0, 0, yesterday)
    
        sqlledger = [row for row in self.__db.select("ledgers", user=username)]
        df = pd.DataFrame.from_records(sqlledger)
        df = df.rename(columns={"timestamp": "Date",
                                 "buy_in": "Buy In",
                                 "buy_out": "Buy Out",
                                 "entry_id": "Entry"})

        df = df.drop("user", axis=1)

        return df
    
    def get_enhanced_ledger(self, username: str) -> pd.DataFrame:
        ledger = self.get_base_ledger(username)
        ledger['Date'] = pd.to_datetime(ledger['Date']).dt.date
        ledger = ledger.sort_values(by='Date')
        ledger["PnL ($)"] = ledger["Buy Out"] - ledger["Buy In"]
        ledger["RoI (%)"] = ledger["PnL ($)"] / ledger["Buy In"] * 100
        ids = ledger["Entry"]
        ledger = ledger.drop("Entry", axis=1)
        ledger["Entry"] = ids
        return ledger
    
    def __get_current_playstreak(self, ledger):
        start_date = datetime.date.today() - datetime.timedelta(days = 1)
        dates = pd.to_datetime(ledger['Date'])[::-1]
        dates = [date.date() for date in dates.sort_values(ascending=False)]
        count = 0
        while len(dates) > 0 and start_date == dates.pop(0):
            count += 1
            start_date -= datetime.timedelta(days = 1)
        return count

    def get_stats(self, ledger) -> pd.DataFrame:
        count = self.__get_current_playstreak(ledger)
        handle_0 = sum(ledger["Buy In"])
        if handle_0 == 0:
            handle_0 = 1
        stats = {"Capital Spent": sum(ledger["Buy In"]), 
                 "Revenue": sum(ledger["Buy Out"]), 
                 "Total PnL": sum(ledger["PnL ($)"]), 
                 "Total Growth": sum(ledger["PnL ($)"]) / handle_0 * 100,
                 "Current Play Streak": count
        }
        return stats
    
    def __check_buy_inputs(self, buy_in, buy_out):
        return (buy_in and buy_out and re.match("^\d*(\.\d{0,2})?$", buy_in) 
                and re.match("^\d*(\.\d{0,2})?$", buy_out))

    def __entry_exists(self, entry_id: str, username: str):
        if not isinstance(entry_id, int):
            return False
        return self.__db.select("ledgers", entry_id=int(entry_id), user=username)

    def add_row(self, username, buy_in: str, buy_out: str, date):
        if self.__check_buy_inputs(buy_in, buy_out):    
            self.__add_entry(username, float(buy_in), float(buy_out), date)
            st.success("Entry Added")
        else:
            st.error("Inputs must be a proper monetary amount.")

    def update_row(self, entry_id: str, buy_in: str, buy_out: str, date, username):
        if self.__entry_exists(entry_id, username) and self.__check_buy_inputs(buy_in, buy_out):
            self.__db.update("ledgers", entry_id=int(entry_id), 
                             buy_in=float(buy_in), buy_out=float(buy_out), timestamp=date)
            st.success("Entry Updated")
        else:
            st.error("Entry must exist and buy inputs must be numerical.")
    
    def delete_row(self, entry_id: str, username):
        if self.__entry_exists(entry_id, username):
            self.__db.delete("ledgers", entry_id=int(entry_id))
            st.success("Entry Deleted")
        else:
            st.error("Entry not found.")

class Analytics:
    def __init__(self, db):
        self.__db = db

    def pnl_by_date(self, ledger):
        resultants = pd.DataFrame()
        resultants['Date'] = pd.to_datetime(ledger['Date'])
        net = [0]
        for val in ledger["PnL ($)"]:
            net.append(net[-1] + val)
        resultants["Total PnL (Profits & Losses)"] = net[1:]
        return resultants.sort_values(by='Date')
    
    def net_by_entry(self, ledger):
        resultants = pd.DataFrame()
        profit, loss = [], []
        for val in ledger["PnL ($)"]:
            if val == 0:
                pass
            elif val > 0:
                profit.append(val)
                loss.append(0)
            else:
                profit.append(0)
                loss.append(val)
        
        resultants["    "] = [0] * len(profit)
        resultants["A) Profit"] = profit
        resultants["B) Loss"] = loss
        resultants["Significant Entries"] = range(1, len(profit) + 1)

        return resultants
