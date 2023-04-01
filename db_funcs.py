import sqlite3
from notanorm import SqliteDb
import streamlit as st

''' Database-related Functions '''

DB_FILE = "pkr.db"

@st.cache_resource
def db_setup():
    db = SqliteDb(DB_FILE)
    db.query("CREATE TABLE IF NOT EXISTS users (username TEXT, \
                password TEXT);") 
    db.query("CREATE TABLE IF NOT EXISTS ledgers (user TEXT, \
            dt DATETIME DEFAULT CURRENT_DATE, buy_in INTEGER, \
            buy_out INTEGER);")
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
