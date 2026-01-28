import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import feedparser
from datetime import datetime
import urllib.parse

# הגדרות דף - אנונימי לחלוטין
st.set_page_config(page_title="מערכת ניטור סיכונים אזורית", layout="wide")

# כותרת מקצועית ללא שם
st.title("🛡️ לוח בקרה מודיעיני - הסתברות לתקיפה איראנית")

# --- פונקציות עזר ---
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
    fig = go.Figure(data=go.Scatter(y=data, mode='lines', line=dict(color=color, width=3)))
    fig.update_layout(
        width=120, height=35, margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def create_gauge(title, value, color):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        number = {'suffix': "%", 'font': {'size': 25}},
        title = {'text': title, 'font': {'size': 16}},
        gauge = {
            'axis': {'range': [0, 100], 'ticksuffix': "%"},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 35], 'color': "#e8f5e9"},
                {'range': [35, 70], 'color': "#fff9c4"},
                {'range': [70, 100], 'color': "#ffebee"}
            ]
        }
    ))
    # הקטנת הממדים של המדד
    fig.update_layout(height=180, width=250, margin=dict(l=20, r=20, t=40, b=10))
    return fig

# --- איסוף נתונים ---
oil_val, oil_chg, oil_hist = get_indicator_data("CL=F")
ils_val, ils_chg, ils_hist = get_indicator_data("USDILS=X")
vix_val, vix_chg, vix_hist = get_indicator_data("^VIX")
gold_val, gold_chg, gold_hist = get_indicator_data("GC=F")

# סריקת חדשות מורחבת (כולל סייבר והצהרות)
headlines = []
try:
    feed = feedparser.parse("https://news.google.com/rss/search?q=Iran+attack+threat+cyber+missile+retaliation")
    headlines = [post.title.lower() for post in feed.entries[:15]]
except: pass

# --- שקלול סבירות משודרג ---
# מילות מפתח לאינדיקטורים ביטחוניים
cyber_threat = sum(4 for h in headlines if "cyber" in h or "hacking" in h)
rhetoric_threat = sum(4 for h in headlines if "retaliate" in h or "revenge" in h or "warns" in h)
military_threat = sum(6 for h in headlines if "missile" in h or "drone" in h or "launch" in h)

score_israel = min(15 + cyber_threat + rhetoric_threat + military_threat + (15 if ils_chg > 1.0 else 0), 100)
score_usa = min(10 + cyber_threat + rhetoric_threat + (15 if oil_chg > 2.0 else 0), 100)

# --- תצוגה ---
col_g1, col_g2, col_empty = st.columns([1, 1, 1]) # שימוש בעמודה ריקה להקטנת המדדים
with col_g1:
    st.plotly_chart(create_gauge("הסתברות נגד ישראל", score_israel, "#FF4B4B"))
with col_g2:
    st.plotly_chart(create_gauge("הסתברות נגד ארה״ב", score_usa, "#1C83E1"))

st.write("---")
st.subheader("🔍 אינדיקטורים וניטור נתונים")

def draw_row(label, val, unit, chg, hist, color):
    c1, c2, c3, c4 = st.columns([3, 1.5, 1.5, 1.5])
    c1.write(label)
    c2.write(f"**{val:.2f} {unit}**")
    c3.write(f"{'📈' if chg > 0 else '📉'} {chg:.2f}%")
    with c4:
        if len(hist) > 0:
            st.plotly_chart(plot_sparkline(hist, color), config={'displayModeBar': False})

draw_row("🛢️ מחירי אנרגיה (נפט WTI)", oil_val, "$", oil_chg, oil_hist, "#FF4B4B")
draw_row("💵 יציבות מטבע (USD/ILS)", ils_val, "₪", ils_chg, ils_hist, "#1C83E1")
draw_row("📉 תנודתיות שווקים (VIX)", vix_val, "pts", vix_chg, vix_hist, "#FFA500")
draw_row("🛡️ רטוריקה וסייבר (ניתוח חדשות)", (cyber_threat + rhetoric_threat), "pts", 0.0, [], "#9C27B0")

st.caption(f"זמן עדכון מערכת: {datetime.now().strftime('%H:%M:%S')} (UTC+2)")
