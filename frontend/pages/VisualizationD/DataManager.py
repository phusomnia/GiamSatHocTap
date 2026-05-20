import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

class DataManager:
    def __init__(self, st: st) -> None:
        self.st = st
        pass

    def demo(self):
        x = np.linspace(0, 10, 100)
        y = np.sin(x)

        fig, ax = plt.subplots()
        ax.plot(x, y)
        ax.set_title("Sine Wave")

        self.st.pyplot(fig)