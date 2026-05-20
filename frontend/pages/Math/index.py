import streamlit as st
import numpy as np
import os
import matplotlib.pyplot as plt
from .components.MathFundamentals import MathFundamentals

def render():
    st.title("Mathematics & Image Analysis")
    
    # Add the Math Fundamentals component
    MathFundamentals()