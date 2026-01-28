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

# --- פונקציה ליצירת קישור וואטסאפ ---
def send_whatsapp_msg(phone, message):
    # מקודד את ההודעה לפורמט של קישור אינטרנט
    encoded_msg = urllib.parse.quote(message)
    link = f"https://wa.me/{phone}?text={encoded_msg}"
    return link

# --- נתוני אמת ---
def get_oil_price():
    try:
        oil = yf.Ticker("CL=F")
        return oil.history(period="1d")['Close'].iloc[-1]
    except:
        return 80.0

oil_price = get_oil_price()

# --- ממשק המשתמש ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📊 מדדים קריטיים")
    st.metric("מחיר חבית נפט (WTI)", f"${oil_price:.2f}")
    
    st.write("---")
    st.subheader("📲 דיווח מהיר")
    
    # כאן תכניס את מספר הטלפון שלך בפורמט בינלאומי (ללא ה-+ בהתחלה)
    # למשל: 972501234567
    # במקום המספר, אנחנו מושכים אותו מהכספת
my_phone = st.secrets["MY_PHONE_NUMBER"] # <--- שנה למספר שלך
    
    alert_text = f"⚠️ עדכון אבטחה מלוח הבקרה:\nרמת סיכון נוכחית נבדקה.\nמחיר נפט: ${oil_price:.2f}\nזמן: {datetime.now().strftime('%H:%M')}"
    
    wa_link = send_whatsapp_msg(my_phone, alert_text)
    
    # יצירת כפתור שנראה כמו קישור לוואטסאפ
    st.markdown(f'''
        <a href="{wa_link}" target="_blank">
            <button style="
                background-color: #25D366;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                width: 100%;">
                שלח דיווח ל-WhatsApp 💬
            </button>
        </a>
    ''', unsafe_allow_ Harris=True)

with col2:
    st.subheader("🗺️ מפת פריסה ואיומים")
    m = folium.Map(location=[32.427, 53.688], zoom_start=5, tiles="CartoDB dark_matter")
    folium.CircleMarker([35.68, 51.38], radius=10, color="red", fill=True, popup="טהרן").add_to(m)
    folium_static(m)

st.caption(f"זמן עדכון אחרון: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
