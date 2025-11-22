import streamlit as st

def header(title, subtitle):
    st.markdown(
        f"""
        <div class="page-header-card">
            <div class="page-header-title">{title}</div>
            <div class="page-header-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
