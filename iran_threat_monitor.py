import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import feedparser
from datetime import datetime
import urllib.parse

# הגדרות דף
st.set_page_config(page_title="מערכת ניטור איומים - אלירם", layout="wide")

st.title("🛡️ לוח בקרה מודיעיני: אלירם")

# --- פונקציות עזר ---
def create_gauge(title, value, color):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        title = {'text': title, 'font': {'size': 24}},
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 1},
            'bar': {'color': color},
            'bgcolor': "white",
            'steps': [
                {'range': [0, 40], 'color': "rgba(0, 255, 0, 0.3)"},
                {'range': [40, 75], 'color': "rgba(255, 255, 0, 0.3)"},
                {'range': [75, 100], 'color': "rgba(255, 0, 0, 0.3)"}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': value
            }
        }
    ))
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
    return fig

def get_latest_news():
    try:
        feed = feedparser.parse("https://news.google.com/rss/search?q=Iran+Israel+USA+Attack")
        return [post.title for post in feed.entries[:8]]
    except:
        return []

# --- איסוף וחישוב נתונים ---
headlines = get_latest_news()

# חישוב סבירות נגד ישראל
score_israel = 20
if any(word in h.lower() for h in headlines for word in ["israel", "tel aviv", "jerusalem"]): score_israel += 30
if any(word in h.lower() for h in headlines for word in ["attack", "missile", "strike"]): score_israel += 25

# חישוב סבירות נגד ארה"ב
score_usa = 15
if any(word in h.lower() for h in headlines for word in ["usa", "biden", "american", "pentagon"]): score_usa += 35
if any(word in h.lower() for h in headlines for word in ["red sea", "base", "retaliation"]): score_usa += 20

# וידוא שהציון לא עובר 100
score_israel = min(score_israel, 100)
score_usa = min(score_usa, 100)

# --- תצוגת המדים ---
col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(create_gauge("סבירות תקיפה נגד ישראל", score_israel, "red"), use_container_width=True)

with col2:
    st.plotly_chart(create_gauge("סבירות תקיפה נגד ארה״ב", score_usa, "blue"), use_container_width=True)

st.write("---")

# --- מידע נוסף ---
c1, c2 = st.columns([1, 2])
with c1:
    st.subheader("📰 כותרות שנסרקו")
    for h in headlines[:5]:
        st.caption(f"• {h}")

with c2:
    st.subheader("📲 שיתוף סטטוס")
    share_msg = f"🛡️ *דו״ח איומים - אלירם*\n🇮🇱 סבירות נגד ישראל: {score_israel}%\n🇺🇸 סבירות נגד ארה״ב: {score_usa}%"
    wa_link = f"https://api.whatsapp.com/send?text={urllib.parse.quote(share_msg)}"
    st.markdown(f'<a href="{wa_link}" target="_blank"><button style="background-color: #25D366; color: white; padding: 15px; border: none; border-radius: 10px; width: 100%; cursor: pointer; font-weight: bold;">שתף את המדדים בוואטסאפ 💬</button></a>', unsafe_allow_html=True)

st.caption(f"המערכת מנטרת אינדיקטורים בזמן אמת | מיקום שרת: באר שבע | {datetime.now().strftime('%H:%M:%S')}")
