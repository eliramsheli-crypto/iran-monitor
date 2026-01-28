import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import feedparser
from datetime import datetime
import urllib.parse

# הגדרות דף
st.set_page_config(page_title="ניטור הסתברות לתקיפה איראנית", layout="wide")

# כותרת מעודכנת לבקשתך
st.title("🛡️ לוח בקרה מודיעיני - הסתברות לתקיפה איראנית")

# --- פונקציות נתונים וגרפים ---
def get_indicator_data(ticker):
    try:
        # משיכת נתונים ל-7 ימים כדי לייצר גרף מגמה
        data = yf.Ticker(ticker).history(period="7d")
        current = data['Close'].iloc[-1]
        start_val = data['Close'].iloc[0]
        change = ((current - start_val) / start_val) * 100
        return current, change, data['Close']
    except:
        return 0.0, 0.0, []

def plot_sparkline(data, color):
    fig = go.Figure(data=go.Scatter(
        y=data, 
        mode='lines', 
        line=dict(color=color, width=4),
        fill='toself',
        fillcolor=f"rgba{tuple(list(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + [0.1])}"
    ))
    fig.update_layout(
        width=160, height=45,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def create_gauge(title, value, color):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        title = {'text': title, 'font': {'size': 20}},
        gauge = {
            'axis': {'range': [0, 100]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 40], 'color': "#e8f5e9"},
                {'range': [40, 75], 'color': "#fff9c4"},
                {'range': [75, 100], 'color': "#ffebee"}
            ],
            'threshold': {'line': {'color': "black", 'width': 4}, 'value': value}
        }
    ))
    fig.update_layout(height=250, margin=dict(l=30, r=30, t=50, b=20))
    return fig

# --- איסוף נתונים ---
oil_val, oil_chg, oil_hist = get_indicator_data("CL=F")
gold_val, gold_chg, gold_hist = get_indicator_data("GC=F")
vix_val, vix_chg, vix_hist = get_indicator_data("^VIX")
ils_val, ils_chg, ils_hist = get_indicator_data("USDILS=X")

# סריקת חדשות
try:
    feed = feedparser.parse("https://news.google.com/rss/search?q=Iran+Israel+USA+Attack")
    headlines = [post.title for post in feed.entries[:8]]
except:
    headlines = []

# --- חישוב שקלול סבירות ---
news_israel = sum(1 for h in headlines if any(w in h.lower() for w in ["israel", "tel aviv", "strike"]))
news_usa = sum(1 for h in headlines if any(w in h.lower() for w in ["usa", "biden", "base", "pentagon"]))

# שקלול ישראל: בסיס + חדשות + חוזק השקל
score_israel = min(20 + (news_israel * 12) + (20 if ils_chg > 0.5 else 0), 100)
# שקלול ארה"ב: בסיס + חדשות + מחיר הנפט
score_usa = min(15 + (news_usa * 15) + (15 if oil_chg > 1.5 else 0), 100)

# --- תצוגה ---
g_col1, g_col2 = st.columns(2)
with g_col1:
    st.plotly_chart(create_gauge("הסתברות תקיפה נגד ישראל", score_israel, "#FF4B4B"), use_container_width=True)
with g_col2:
    st.plotly_chart(create_gauge("הסתברות תקיפה נגד ארה״ב", score_usa, "#1C83E1"), use_container_width=True)

st.write("---")

# --- רשימת אינדיקטורים מפורטת ---
st.subheader("🔍 אינדיקטורים לשקלול המדדים")
st.markdown("להלן הנתונים המשפיעים על תזוזת המחוגים בלוח הבקרה:")

def draw_row(label, val, unit, chg, hist, color):
    c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
    c1.write(label)
    c2.write(f"**{val:.2f} {unit}**")
    delta_color = "normal" if abs(chg) < 2 else "inverse"
    c3.metric("", "", f"{chg:.2f}%", delta_color=delta_color)
    with c4:
        if len(hist) > 0:
            st.plotly_chart(plot_sparkline(hist, color), config={'displayModeBar': False})

draw_row("🛢️ מחיר נפט (WTI) - אינדיקטור למתח במפרץ", oil_val, "$", oil_chg, oil_hist, "#FF4B4B")
draw_row("💰 שער דולר/שקל - חוסן הכלכלה הישראלית", ils_val, "₪", ils_chg, ils_hist, "#1C83E1")
draw_row("📈 מדד הפחד (VIX) - תנודתיות שו
