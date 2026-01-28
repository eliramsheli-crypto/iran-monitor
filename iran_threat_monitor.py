import streamlit as st
import yfinance as yf
import pandas as pd
import folium
from streamlit_folium import folium_static
from datetime import datetime
import urllib.parse

# הגדרות דף
st.set_page_config(page_title="מערכת ניטור איומים - אלירם", layout="wide")

st.title("🛡️ לוח בקרה מודיעיני: איראן - ישראל")

# פונקציה ליצירת קישור וואטסאפ ללא מספר מוגדר (פותח בחירת איש קשר)
def get_whatsapp_link(message):
    encoded_msg = urllib.parse.quote(message)
    # שימוש ב-send ללא מספר טלפון פותח את רשימת אנשי הקשר של המשתמש
    return f"https://api.whatsapp.com/send?text={encoded_msg}"

# נתוני אמת - מחיר נפט
def get_oil_price():
    try:
        oil = yf.Ticker("CL=F")
        return oil.history(period="1d")['Close'].iloc[-1]
    except:
        return 80.0

oil_price = get_oil_price()

# ממשק המשתמש
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📊 מדדים קריטיים")
    st.metric("מחיר חבית נפט (WTI)", f"${oil_price:.2f}")
    
    st.write("---")
    st.subheader("📲 שיתוף דיווח")
    st.write("לחץ על הכפתור כדי לשלוח את הנתונים הנוכחיים לוואטסאפ שלך:")
    
    # בניית הודעת הדיווח
    alert_text = (
        f"🛡️ *דיווח ממערכת הניטור של אלירם*\n"
        f"--- --- --- ---\n"
        f"📈 מחיר נפט: ${oil_price:.2f}\n"
        f"⏰ זמן עדכון: {datetime.now().strftime('%H:%M')}\n"
        f"📍 המערכת פועלת כעת מבאר שבע"
    )
    
    wa_link = get_whatsapp_link(alert_text)
    
    # כפתור וואטסאפ מעוצב
    st.markdown(f'''
        <a href="{wa_link}" target="_blank">
            <button style="
                background-color: #25D366;
                color: white;
                padding: 15px 25px;
                border: none;
                border-radius: 10px;
                width: 100%;
                cursor: pointer;
                font-weight: bold;
                font-size: 18px;">
                שתף דיווח ב-WhatsApp 💬
            </button>
        </a>
    ''', unsafe_allow_html=True)
    
    st.info("לחיצה על הכפתור תפתח את הוואטסאפ ותאפשר לך לבחור את עצמך או קבוצה לשליחת הדיווח.")

with col2:
    st.subheader("🗺️ מפת פריסה ואיומים")
    m = folium.Map(location=[32.427, 53.688], zoom_start=5, tiles="CartoDB dark_matter")
    folium.CircleMarker([35.68, 51.38], radius=10, color="red", fill=True, popup="טהרן").add_to(m)
    folium_static(m)

st.caption(f"זמן שרת: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
