import streamlit as st
import regex as re
from db_funcs import UserDB

class Auth:
    def __init__(self):
        st.set_page_config(layout="wide")
        st.title('Welcome to Orbit:diamonds:')
        self.user = st.text_input("Username (No special characters)")
        self.pwd = st.text_input("Password (Minimum eight characters, \
                                at least one uppercase letter, \
                                 one lowercase letter, one number \
                                 and one special character)")
        self.user_db = UserDB()

    def __check_inputs(self):
        pwd_reqs = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
        return re.match(pwd_reqs, self.pwd) and self.user.isalnum()

    def authorize(self):
        if not self.__check_inputs():
            st.error("Username or Password don't meet specifications.")
        elif self.user_db.auth_user(self.user, self.pwd):
            # session
            pass


auth = Auth()
st.button("Log In", use_container_width=True, on_click=auth.authorize)
st.button("Register with Orbit", use_container_width=True, on_click=auth.register)
