import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import feedparser
from datetime import datetime
import urllib.parse

# הגדרות דף
st.set_page_config(page_title="ניטור הסתברות לתקיפה איראנית", layout="wide")

st.title("🛡️ לוח בקרה מודיעיני - הסתברות לתקיפה איראנית")

# --- פונקציות נתונים ---
def get_indicator_data(ticker):
    try:
        data = yf.Ticker(ticker).history(period="7d")
        current = data['Close'].iloc[-1]
        start_val = data['Close'].iloc[0]
        change = ((current - start_val) / start_val) * 100
        return current, change, data['Close']
    except:
        return 0.0, 0.0, []

def plot_sparkline(data, color):
    fig = go.Figure(data=go.Scatter(y=data, mode='lines', line=dict(color=color, width=4)))
    fig.update_layout(
        width=150, height=40, margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

# פונקציה מעודכנת להצגת אחוזים במדד
def create_gauge(title, value, color):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        number = {'suffix': "%", 'font': {'size': 40}}, # הוספת סיומת אחוזים
        title = {'text': title, 'font': {'size': 20}},
        gauge = {
            'axis': {'range': [0, 100], 'ticksuffix': "%"}, # אחוזים על השנתות
            'bar': {'color': color},
            'steps': [
                {'range': [0, 30], 'color': "#e8f5e9"},
                {'range': [30, 60], 'color': "#fff9c4"},
                {'range': [60, 100], 'color': "#ffebee"}
            ]
        }
    ))
    fig.update_layout(height=280, margin=dict(l=30, r=30, t=50, b=20))
    return fig

# --- איסוף נתונים ---
oil_val, oil_chg, oil_hist = get_indicator_data("CL=F")
ils_val, ils_chg, ils_hist = get_indicator_data("USDILS=X")
vix_val, vix_chg, vix_hist = get_indicator_data("^VIX")
gold_val, gold_chg, gold_hist = get_indicator_data("GC=F")

# סריקת חדשות ממוקדת
headlines = []
try:
    feed = feedparser.parse("https://news.google.com/rss/search?q=Iran+Israel+USA+Attack+threat")
    headlines = [post.title.lower() for post in feed.entries[:10]]
except: pass

# --- לוגיקת שקלול שמרנית ---
news_israel = sum(2 for h in headlines if "israel" in h or "tel aviv" in h)
threat_israel = sum(5 for h in headlines if "imminent" in h or "retaliate" in h)
market_israel = 15 if ils_chg > 1.2 else 0

# חישוב אחוז סופי (בסיס 15%)
score_israel = min(15 + news_israel + threat_israel + market_israel, 100)

news_usa = sum(2 for h in headlines if "usa" in h or "pentagon" in h)
threat_usa = sum(5 for h in headlines if "base" in h or "navy" in h)
market_usa = 15 if oil_chg > 2.5 else 0

score_usa = min(10 + news_usa + threat_usa + market_usa, 100)

# --- תצוגת המדים ---
col_g1, col_g2 = st.columns(2)
with col_g1:
    st.plotly_chart(create_gauge("הסתברות תקיפה נגד ישראל", score_israel, "#FF4B4B"), use_container_width=True)
with col_g2:
    st.plotly_chart(create_gauge("הסתברות תקיפה נגד ארה״ב", score_usa, "#1C83E1"), use_container_width=True)

st.write("---")
st.subheader("🔍 אינדיקטורים לשקלול המדדים")

def
