# utils/ui.py
import streamlit as st

def header(title, subtitle=None):
    st.markdown(f"<h2 style='margin-bottom:-10px;'>{title}</h2>", unsafe_allow_html=True)
    if subtitle:
        st.caption(subtitle)

