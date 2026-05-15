import streamlit as st
from base64 import b64encode
from pathlib import Path


def get_logo_url():
    logo_path = Path(__file__).resolve().parents[1] / "images" / "Dev_kumar_logo.png"
    return f"data:image/png;base64,{b64encode(logo_path.read_bytes()).decode()}"

def footer_home():
    log_url = get_logo_url()

    st.markdown(
        f"""
        <div style="margin-top:2rem; display: flex; gap:6px; justify-content: center; align-items: center;">
        <p style="color: white; text-align: center; font-weight: bold;">Made with 💖 by Dev Kumar</p>
        <img src='{log_url}' alt='Logo' style='max-height:25px; margin-top:-15px;'>
        </div>
        """, unsafe_allow_html=True)
    

def footer_dashboard():
    log_url = get_logo_url()

    st.markdown(
        f"""
        <div style="margin-top:2rem; display: flex; gap:6px; justify-content: center; align-items: center;">
        <p style="color: black; text-align: center; font-weight: bold;">Made with 💖 by Dev Kumar</p>
        <img src='{log_url}' alt='Logo' style='max-height:25px; margin-top:-15px;'>
        </div>
        """, unsafe_allow_html=True)
