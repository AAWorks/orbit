import streamlit as st
import regex as re
from db_funcs import UserDB

DB_FILE = "pkr.db"

class Auth:
    def __init__(self):
        st.set_page_config(layout="wide")
        st.title('Welcome to Orbit:diamonds:')
        self.user = st.text_input("Username (No special characters)")
        self.pwd = st.text_input("Password (Minimum eight characters, \
                                at least one uppercase letter, \
                                 one lowercase letter, one number \
                                 and one special character)")
        self.user_db = UserDB(DB_FILE)

    def __check_inputs(self):
        pwd_reqs = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])\
            [A-Za-z\d@$!%*?&]{8,}$"
        return re.match(pwd_reqs, self.pwd) and self.user.isalnum()

    def authorize(self):
        if not self.__check_inputs():
            st.error("Username or Password don't meet specifications.")
        else:
            self.user_db.auth_user(self.user, self.pwd):    
    
    def register(self):
        if not self.__check_inputs():
            st.error("Username or Password don't meet specifications.")
        else:
            self.user_db.add_user(self.user, self.pwd)

auth = Auth()
st.button("Log In", use_container_width=True, on_click=auth.authorize)
st.button("Register with Orbit", use_container_width=True, on_click=auth.register)
