import streamlit as st

def header_home():
    log_url = "https://cdn-icons-png.flaticon.com/512/5968/5968322.png"

    st.markdown(
        f"""
        <div style='display: flex; align-items: center; flex-direction: column; margin-bottom: 30px; justify-content: center; margin-top: 30px;'>
            <img src='{log_url}' alt='Logo' style='width: 100px; height: 100px;'>
            <h1 style='color: #E0E3FF; text-align: center;'>SNAP<br>CLASS</h1>
        </div>
        """, unsafe_allow_html=True)
    
def header_dashboard():
    log_url = "https://cdn-icons-png.flaticon.com/512/5968/5968322.png"

    st.markdown(
        f"""
        <div style='display: flex; align-items: center;margin-bottom: 30px; justify-content: center; gap: 10px;'>
            <img src='{log_url}' alt='Logo' style='width: 65px; height: 65px;'>
            <h2 style='color: #5865F2; text-align: left;'>SNAP<br>CLASS</h2>
        </div>
        """, unsafe_allow_html=True)
    
    