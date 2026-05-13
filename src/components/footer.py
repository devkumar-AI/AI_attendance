import streamlit as st

def footer_home():
    log_url = "https://cdn-icons-png.flaticon.com/512/5968/5968322.png"

    st.markdown(
        """
        <div style="margin-top:2rem; display: flex; gap:6px; justify-content: center; align-items: center;">
        <p style="color: white; text-align: center; font-weight: bold;">Made with 💖 by </p>
        <img src='{log_url}' alt='Logo' style='max-height:25px;'>
        </div>
        """, unsafe_allow_html=True)
    

def footer_dashboard():
    log_url = "https://cdn-icons-png.flaticon.com/512/5968/5968322.png"

    st.markdown(
        """
        <div style="margin-top:2rem; display: flex; gap:6px; justify-content: center; align-items: center;">
        <p style="color: black; text-align: center; font-weight: bold;">Made with 💖 by </p>
        <img src='{log_url}' alt='Logo' style='max-height:25px;'>
        </div>
        """, unsafe_allow_html=True)