import sqlite3
from notanorm import SqliteDb
import streamlit as st

''' Database-related Functions '''

class UserDB:
    def __init__(self, db_file: str):
        self.__db = SqliteDb(db_file)
        self.__db.query("CREATE TABLE IF NOT EXISTS users (username TEXT, \
                password TEXT, userID INTEGER PRIMARY KEY AUTOINCREMENT;") 
        self.__db.query("CREATE TABLE IF NOT EXISTS ledgers (username TEXT, \
                password TEXT, userID INTEGER;") 
        self.__db.close()

    def __user_exists(self, username):
        pass

    def __check_pwd(self, username, password):
        pass
        
    def auth_user(self, username, password):
        if not self.__user_exists(username):
            st.error("Username not found")
            return False
        elif not self.__check_pwd(username, password):
            st.error("Incorrect Password for Given User")
            return False
        else:
            st.success(f"Welcome {username}!")
            return True

    def add_user(self, username, password):
        names = self.parse_names(names)
        self.__db.insert("people", firstname=names[0], 
                       lastname=names[1], status=status)
