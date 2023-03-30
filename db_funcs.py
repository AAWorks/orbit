import sqlite3
from notanorm import SqliteDb
import streamlit as st

''' Database-related Functions '''

class UserDB:
    @st.cache_resource
    def __init__(self, db_file: str):
        self.__db = SqliteDb(db_file)
        self.__db.query("CREATE TABLE IF NOT EXISTS users (username TEXT, \
                password TEXT, userID INTEGER PRIMARY KEY AUTOINCREMENT;") 
        self.__db.query("CREATE TABLE IF NOT EXISTS ledgers (userID INTEGER, \
                dt DATETIME DEFAULT CURRENT_DATE, buy_in INTEGER, \
                buy_out INTEGER;")

    def get_user_id(self, username: str) -> int:
        return self.__db.select("users", username=username)[0].userID

    def __user_exists(self, username: str) -> bool:
        return self.__db.select("users", username=username)

    def __check_pwd(self, username: str, password: str) -> bool:
        to_check = self.__db.select("users", username=username)[0].password
        return password == to_check # Will add bcrypt protection later
        
    def auth_user(self, username: str, password: StopAsyncIteration):
        if not self.__user_exists(username):
            st.error("Username not found")
        elif not self.__check_pwd(username, password):
            st.error("Incorrect Password for Given User")
        else:
            st.success(f"Welcome {username}!")
            st.session_state["user_id"] = self.get_user_id(username)

    def add_user(self, username, password):
        if self.__user_exists(username):
            st.error("Username already exists.")
        else:
            self.__db.insert("users", username=username, password=password)
            st.session_state["user_id"] = self.get_user_id(username)
