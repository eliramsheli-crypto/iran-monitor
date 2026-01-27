import streamlit as st
import asyncio
import telegram
import yfinance as yf
import pandas as pd
import folium
from streamlit_folium import folium_static
from datetime import datetime
import os

# --- הגדרות אישיות (הפרטים שלך כבר בפנים) ---
TELEGRAM_TOKEN = '1393856180:AAE72TvUWcp12-6omU2cHL5WdKbc2evAF9I'
CHAT_ID = '8005495585'
LOG_FILE = 'security_log.csv'

# --- פונקציות עזר ---
async def send_alert(msg):
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    async with bot:
        await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='Markdown')

def log_to_excel(risk, reasons):
    df = pd.DataFrame([{'Time': datetime.now(), 'Risk': risk, 'Details': ", ".join(reasons)}])
    df.to_csv(LOG_FILE, mode='a', header=not os.path.exists(LOG_FILE), index=False, encoding='utf-8-sig')

# --- ממשק המשתמש (Streamlit) ---
st.set_page_config(page_title="מערכת חיזוי איום איראני", layout="wide")

# סימולציה של נתונים (כאן יבואו ה-APIs שדיברנו עליהם)
risk_score = 42 
active_sites = ["Tehran"]
news_briefs = {"Tehran": "דיווחים על הגברת אבטחה בקריית הממשלה."}

st.title("🛡️ מערכת מודיעין וחיזוי: איראן-ישראל")

col1, col2 = st.columns([1, 2])

with col1:
    st.metric("רמת סיכון משוקללת", f"{risk_score}%")
    if st.button("שלח התראה לטלגרם"):
        asyncio.run(send_alert(f"⚠️ עדכון ידני: רמת סיכון נוכחית {risk_score}%"))
        log_to_excel(risk_score, ["בדיקה ידנית"])
        st.success("נשלח!")

with col2:
    # המפה האינטראקטיבית
    m = folium.Map(location=[32.427, 53.688], zoom_start=5, tiles="CartoDB dark_matter")
    for city, coords in {"Tehran": [35.68, 51.38], "Isfahan": [32.65, 51.66]}.items():
        color = "red" if city in active_sites else "green"
        folium.CircleMarker(coords, radius=10, color=color, fill=True, popup=news_briefs.get(city, "שגרה")).add_to(m)
    folium_static(m)

if os.path.exists(LOG_FILE):
    st.subheader("📋 יומן אירועים אחרונים")
    st.dataframe(pd.read_csv(LOG_FILE).tail(5))