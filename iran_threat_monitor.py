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

def create_gauge(title, value, color):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        title = {'text': title, 'font': {'size': 18}},
        gauge = {
            'axis': {'range': [0, 100]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 30], 'color': "#e8f5e9"},
                {'range': [30, 60], 'color': "#fff9c4"},
                {'range': [60, 100], 'color': "#ffebee"}
            ]
        }
    ))
    fig.update_layout(height=230, margin=dict(l=20, r=20, t=50, b=20))
    return fig

# --- איסוף נתונים ---
oil_val, oil_chg, oil_hist = get_indicator_data("CL=F")
ils_val, ils_chg, ils_hist = get_indicator_data("USDILS=X")
vix_val, vix_chg, vix_hist = get_indicator_data("^VIX")
gold_val, gold_chg, gold_hist = get_indicator_data("GC=F")

# סריקת חדשות ממוקדת יותר
headlines = []
try:
    feed = feedparser.parse("https://news.google.com/rss/search?q=Iran+Israel+USA+Attack+threat+imminent")
    headlines = [post.title.lower() for post in feed.entries[:10]]
except: pass

# --- לוגיקת שקלול מעודכנת (כיול מחדש) ---
# ישראל
base_israel = 15 # רמת מתח בסיסית באזור
news_israel = sum(2 for h in headlines if "israel" in h or "tel aviv" in h)
threat_israel = sum(5 for h in headlines if "imminent" in h or "launch" in h or "retaliate" in h)
market_israel = 15 if ils_chg > 1.5 else 0 # השפעת פיחות השקל

score_israel = min(base_israel + news_israel + threat_israel + market_israel, 100)

# ארה"ב
base_usa = 10
news_usa = sum(2 for h in headlines if "usa" in h or "pentagon" in h or "biden" in h)
threat_usa = sum(5 for h in headlines if "base" in h or "red sea" in h)
market_usa = 15 if oil_chg > 3.0 else 0 # השפעת זינוק בנפט

score_usa = min(base_usa + news_usa + threat_usa + market_usa, 100)

# --- תצוגה ---
col_g1, col_g2 = st.columns(2)
with col_g1:
    st.plotly_chart(create_gauge("הסתברות תקיפה נגד ישראל", score_israel, "#FF4B4B"), use_container_width=True)
with col_g2:
    st.plotly_chart(create_gauge("הסתברות תקיפה נגד ארה״ב", score_usa, "#1C83E1"), use_container_width=True)

st.write("---")
st.subheader("🔍 אינדיקטורים לשקלול המדדים")

def draw_row(label, val, unit, chg, hist, color):
    c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
    c1.write(label)
    c2.write(f"**{val:.2f} {unit}**")
    c3.write(f"{'📈' if chg > 0 else '📉'} {chg:.2f}%")
    with c4:
        if len(hist) > 0:
            st.plotly_chart(plot_sparkline(hist, color), config={'displayModeBar': False})

draw_row("מחיר נפט (WTI)", oil_val, "$", oil_chg, oil_hist, "#FF4B4B")
draw_row("שער דולר/שקל", ils_val, "₪", ils_chg, ils_hist, "#1C83E1")
draw_row("מדד הפחד (VIX)", vix_val, "pts", vix_chg, vix_hist, "#FFA500")
draw_row("מחיר הזהב", gold_val, "$", gold_chg, gold_hist, "#FFD700")

st.caption(f"מיקום: באר שבע | זמן עדכון: {datetime.now().strftime('%H:%M:%S')}")
