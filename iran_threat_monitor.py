import streamlit as st
import yfinance as yf
import folium
from streamlit_folium import folium_static
from datetime import datetime
import urllib.parse
import feedparser

# הגדרות דף
st.set_page_config(page_title="מערכת ניטור איומים - אלירם", layout="wide")

st.title("🛡️ לוח בקרה מודיעיני: איראן - ישראל")

# --- פונקציות נתונים ---
def get_market_data(ticker):
    try:
        data = yf.Ticker(ticker)
        return data.history(period="1d")['Close'].iloc[-1]
    except:
        return 0.0

def get_latest_news():
    # סריקת כותרות מרויטרס (חדשות עולם)
    feed = feedparser.parse("https://qz.com/feed") # דוגמה למקור חדשות פתוח
    headlines = [post.title for post in feed.entries[:5]]
    return headlines

# משיכת נתונים
oil_price = get_market_data("CL=F")
gold_price = get_market_data("GC=F")
vix_index = get_market_data("^VIX")
news_headlines = get_latest_news()

# חישוב רמת סיכון
risk_score = 15
keywords = ["Iran", "Attack", "Israel", "Missile", "Conflict", "Threat"]
found_keywords = [word for word in keywords if any(word.lower() in h.lower() for h in news_headlines)]

risk_score += (len(found_keywords) * 15) # כל מילת מפתח מעלה את הסיכון
if oil_price > 85: risk_score += 20
if vix_index > 22: risk_score += 20

# --- ממשק המשתמש ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📊 אינדיקטורים וסיכונים")
    st.metric("מחיר נפט (WTI)", f"${oil_price:.2f}")
    st.metric("מדד הפחד (VIX)", f"{vix_index:.2f}")
    
    st.write("---")
    st.subheader("📰 כותרות אחרונות (סריקת מילים)")
    for h in news_headlines:
        st.write(f"• {h}")
    
    st.write("---")
    st.subheader("⚠️ הערכת סבירות נוכחית")
    if risk_score < 40:
        st.success(f"רמת סיכון: נמוכה ({risk_score}%)")
    elif risk_score < 75:
        st.warning(f"רמת סיכון: בינונית - כוננות מוגברת ({risk_score}%)")
    else:
        st.error(f"רמת סיכון: גבוהה - חשש מיידי ({risk_score}%)")

    # כפתור שיתוף וואטסאפ
    alert_text = f"🛡️ *עדכון אבטחה - אלירם*\nסבירות תקיפה: {risk_score}%\nנפט: ${oil_price:.2f}\nזמן: {datetime.now().strftime('%H:%M')}"
    wa_link = f"https://api.whatsapp.com/send?text={urllib.parse.quote(alert_text)}"
    st.markdown(f'<a href="{wa_link}" target="_blank"><button style="background-color: #25D366; color: white; padding: 10px; border: none; border-radius: 5px; width: 100%; cursor: pointer;">שתף סטטוס בוואטסאפ 💬</button></a>', unsafe_allow_html=True)

with col2:
    st.subheader("🗺️
