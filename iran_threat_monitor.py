import streamlit as st
import asyncio
import telegram
import yfinance as yf
import pandas as pd
import folium
from streamlit_folium import folium_static
from datetime import datetime
import os

# --- משיכת פרטים מאובטחים מהגדרות השרת ---
# במקום הטוקן עצמו, אנחנו משתמשים במפתחות סודיים
try:
    TELEGRAM_TOKEN = st.secrets["TELEGRAM_TOKEN"]
    CHAT_ID = st.secrets["CHAT_ID"]
except Exception:
    st.error("שגיאה: חסרים מפתחות אבטחה (Secrets) בהגדרות המערכת.")
    st.stop()

LOG_FILE = 'security_log.csv'

async def send_alert(msg):
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    async with bot:
        await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='Markdown')

def log_to_excel(risk, reasons):
    df = pd.DataFrame([{'Time': datetime.now(), 'Risk': risk, 'Details': ", ".join(reasons)}])
    df.to_csv(LOG_FILE, mode='a', header=not os.path.exists(LOG_FILE), index=False, encoding='utf-8-sig')

st.set_page_config(page_title="מערכת חיזוי איום איראני", layout="wide")

st.title("🛡️ מערכת מודיעין וחיזוי: איראן-ישראל")

# נתונים לדוגמה (ניתן להוסיף כאן את ה-APIs)
risk_score = 42 
active_sites = ["Tehran"]
news_briefs = {"Tehran": "דיווחים על הגברת אבטחה בקריית הממשלה."}

col1, col2 = st.columns([1, 2])

with col1:
    st.metric("רמת סיכון משוקללת", f"{risk_score}%")
    if st.button("שלח התראה לטלגרם"):
        asyncio.run(send_alert(f"⚠️ עדכון מהשרת: רמת סיכון נוכחית {risk_score}%"))
        st.success("ההתראה נשלחה מהענן!")

with col2:
    m = folium.Map(location=[32.427, 53.688], zoom_start=5, tiles="CartoDB dark_matter")
    for city, coords in {"Tehran": [35.68, 51.38], "Isfahan": [32.65, 51.66]}.items():
        color = "red" if city in active_sites else "green"
        folium.CircleMarker(coords, radius=10, color=color, fill=True, popup=news_briefs.get(city, "שגרה")).add_to(m)
    folium_static(m)
