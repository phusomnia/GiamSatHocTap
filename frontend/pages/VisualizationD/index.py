import streamlit as st
from .DataManager import DataManager

def render(self):
    st.set_page_config(page_title="Visualization Dashboard", layout="wide")
    st.title("Visualization Dashboard")

    data_manager = DataManager(st)
    data_manager.demo()
