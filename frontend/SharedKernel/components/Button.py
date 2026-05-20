import streamlit as st

def Button(label, on_click=None, key="btn"):
    # Custom CSS for the button
    st.markdown("""
    <style>
    div.stButton > button:first-child {
        padding: 10px 16px;
        border-radius: 00px;
        border: none;
        background: linear-gradient(135deg, #4f46e5, #7c3aed);
        color: white;
        font-weight: 600;
        cursor: pointer;
        transition: 0.2s;
    }
    div.stButton > button:first-child:hover {
        transform: scale(1.05);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Use st.button with custom styling
    if st.button(label, key=key):
        if on_click:
            on_click()