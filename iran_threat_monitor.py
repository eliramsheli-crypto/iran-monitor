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
def get_data(ticker):
    try:
        data = yf.Ticker(ticker)
        return data.history(period="1d")['Close'].iloc[-1]
    except:
        return 0.0

def get_latest_news():
    # סריקת כותרות מ-World News
    feed = feedparser.parse("https://news.google.com/rss/search?q=Iran+Israel+Attack")
    return [post.title for post in feed.entries[:5]]

# משיכת נתונים
oil = get_data("CL=F")      # נפט
gold = get_data("GC=F")     # זהב
vix = get_data("^VIX")      # מדד הפחד
ils = get_data("USDILS=X") # שער הדולר/שקל
ta35 = get_data("TA35.TA") # בורסת תל אביב

headlines = get_latest_news()

# חישוב רמת סיכון מורכב
risk_score = 10
# בדיקת כותרות
keywords = ["Immediate", "Escalation", "Retaliation", "Launch", "Alert"]
found_keywords = [w for w in keywords if any(w.lower() in h.lower() for h in headlines)]
risk_score += (len(found_keywords) * 15)

# בדיקת מדדים כלכליים
if ils > 3.75: risk_score += 15  # שקל נחלש
if vix > 25: risk_score += 20    # פחד עולמי עולה
if oil > 90: risk_score += 15    # נפט מזנק

# --- ממשק המשתמש ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📊 מדדים ואינדיקטורים")
    
    # תצוגה בשתי עמודות פנימיות
    m1, m2 = st.columns(2)
    m1.metric("נפט (WTI)", f"${oil:.2f}")
    m2.metric("דולר/שקל", f"₪{ils:.3f}")
    m1.metric("מדד הפחד", f"{vix:.2f}")
    m2.metric("זהב", f"${gold:.1f}")
    
    st.write("---")
    st.subheader("📰 ניתוח כותרות בזמן אמת")
    for h in headlines:
        st.caption(f"• {h}")
    
    st.write("---")
    st.subheader("⚠️ סבירות תקיפה משוקללת")
    if risk_score < 30:
        st.success(f"רמת סיכון: שגרה ({risk_score}%)")
    elif risk_score < 65:
        st.warning(f"רמת סיכון: כוננות גבוהה ({risk_score}%)")
    else:
        st.error(f"רמת סיכון: חשש למתקפה מיידית ({risk_score}%)")

    # כפתור שיתוף
    share_msg = f"🛡️ *סטטוס מודיעיני - אלירם*\nסבירות תקיפה: {risk_score}%\nשער הדולר: ₪{ils:.3f}\nמחיר נפט: ${oil:.2f}"
    st.markdown(f'<a href="https://api.whatsapp.com/send?text={urllib.parse.quote(share_msg)}" target="_blank"><button style="background-color: #25D366; color: white; padding: 12px; border: none; border-radius: 8px; width: 100%; cursor: pointer; font-weight: bold;">שתף דיווח בוואטסאפ 💬</button></a>', unsafe_allow_html=True)

with col2:
    st.subheader("🗺️ מפת פריסה ואיומים")
    m = folium.Map(location=[32.427, 53.688], zoom_start=5, tiles="CartoDB dark_matter")
    # טהראן
    folium.CircleMarker([35.68, 51.38], radius=10, color="red", fill=True, popup="מרכזי שליטה").add_to(m)
    # בסיסי טילים במערב
    folium.Circle([34.34, 47.09], radius=70000, color="orange", fill=True, popup="אזור שיגור טקטי").add_to(m)
    folium_static(m)

st.caption(f"המערכת מנתחת נתוני שוק וחדשות גלובליים | באר שבע | {datetime.now().strftime('%d/%m/%Y %H:%M')}")
