# ... your existing imports ...
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import random
from difflib import get_close_matches
import plotly.express as px
import streamlit as st
import mysql.connector

# MySQL connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="sqlsr@123",
    database="chennai_chatbot"
)
cursor = conn.cursor()

# ✅ Step 4 - Function to store user & bot messages
def log_chat(user_input, bot_response):
    query = "INSERT INTO chat_history (user_input, bot_response, timestamp) VALUES (%s, %s, NOW())"
    cursor.execute(query, (user_input, bot_response))
    conn.commit()



st.set_page_config(page_title="Chennai Risk Chatbot AI", page_icon="🧠", layout="wide")

# 💡 Custom styles
st.markdown("""
    <style>
        .big-font {
            font-size:24px !important;
        }
        .highlight {
            color: #FF4B4B;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# 🔁 Session state initialization
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if "messages" not in st.session_state:
    st.session_state.messages = []

# 🤖 Fallback response
def get_bot_response(user_input):
    responses = [
        "Thanks for your question!",
        "I'm still learning about this area.",
        "Interesting query. Give me a moment!",
        "Please elaborate more.",
        "Let me pull up the relevant data..."
    ]
    return random.choice(responses)

# 🗂️ Sidebar - Chat History from MySQL
st.sidebar.title("🗂️ Chat History")

try:
    cursor.execute("SELECT id, user_input, bot_response, timestamp FROM chat_history ORDER BY id DESC LIMIT 20")
    chats = cursor.fetchall()
    if chats:
        for cid, utext, btext, ts in chats:
            st.sidebar.markdown(f"🕒 {ts.strftime('%d %b %Y %I:%M %p')}")
            st.sidebar.markdown(f"**You**: {utext}")
            st.sidebar.markdown(f"**Bot**: {btext}")
            st.sidebar.markdown("---")
    else:
        st.sidebar.info("No previous chats found.")
except Exception as e:
    st.sidebar.error(f"Error loading history: {e}")


# 🏷️ Title and description
st.title("🤖 Chennai AI Risk Chatbot")
st.markdown("<p class='big-font'>Ask about <span class='highlight'>accidents, pollution, crime, heat, flood, population, or risk factors</span>.</p>", unsafe_allow_html=True)

# 🥒 Current date and time
st.markdown(f"🕒 {datetime.now().strftime('%A, %d %B %Y | %I:%M %p')}")


# 📊 Load datasets
accident_df = pd.read_excel("accident.xlsx")
air_df = pd.read_excel("air_pollution.xlsx")
crime_df = pd.read_excel("crime_details.xlsx")
heat_df = pd.read_excel("heat.xlsx")
flood_df = pd.read_excel("flood.xlsx")
population_df = pd.read_excel("population.xlsx")
Riskfactor_df = pd.read_excel("riskanalysis.xlsx")

# 🧹 Clean column names
for df in [accident_df, air_df, crime_df, heat_df, flood_df, population_df, Riskfactor_df]:
    df.columns = df.columns.str.strip()

def bar_chart(df, x_col, y_col, title, color):
    fig = px.bar(df, x=x_col, y=y_col, title=title, color_discrete_sequence=[color])
    st.plotly_chart(fig)


def show_overall_summary(df, zone_col, y_col, title, color):
    st.subheader(f"📊 {title} Overview")
    if zone_col not in df.columns:
        st.warning(f"⚠️ Column '{zone_col}' not found in the data!")
        st.write(df.head())  # fallback
    else:
        st.dataframe(df)
        bar_chart(df, zone_col, y_col, f"Zone-wise {title}", color)


# ✍️ Name input first
if st.session_state.user_name == "":
    name_input = st.text_input("Enter your name to begin:")
    if name_input:
        st.session_state.user_name = name_input
        st.success(f"Hi {name_input}, welcome to the Chennai Risk Analyzer!")
else:
    st.markdown(f"👋 Hello, **{st.session_state.user_name}**! Ask me anything about Chennai risk data.")

    for idx, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

            mtype = msg.get("type", None)
            key_suffix = f"_{idx}"

            def bar_chart(df, x_col, y_col, title, color):
                df[y_col] = pd.to_numeric(df[y_col], errors="coerce")
                df = df.dropna(subset=[x_col, y_col])
                chart_data = df[[x_col, y_col]].copy()
                chart_data = chart_data.groupby(x_col).sum().sort_values(y_col, ascending=False)

                fig, ax = plt.subplots(figsize=(12, 6))
                bars = ax.bar(chart_data.index, chart_data[y_col], color=color)
                ax.set_ylabel(y_col)
                ax.set_title(title)
                plt.xticks(rotation=45, ha='right')

                for bar in bars:
                    height = bar.get_height()
                    ax.annotate(f'{int(height)}',
                                xy=(bar.get_x() + bar.get_width() / 2, height),
                                xytext=(0, 3),
                                textcoords="offset points",
                                ha='center', va='bottom')

                st.pyplot(fig)

            def extract_zone_from_query(query, zones):
                words = query.lower().split()
                matched = get_close_matches(' '.join(words), zones, n=1, cutoff=0.6)
                if matched:
                    return matched[0]
                for word in words:
                    matched = get_close_matches(word, zones, n=1, cutoff=0.7)
                    if matched:
                        return matched[0]
                return None

            def zone_data(df, zone_col, title, key_suffix=""):
                if zone_col not in df.columns:
                    st.warning(f"⚠️ Column '{zone_col}' not found in the data!")
                    return

                zones = [z.lower() for z in df[zone_col].dropna().unique()]
                user_query = st.session_state.messages[-1]["content"]
                zone = extract_zone_from_query(user_query, zones)

                if zone:
                    st.write(f"📍 Showing {title.lower()} data for **{zone.title()}**")
                    st.dataframe(df[df[zone_col].str.lower() == zone])
                else:
                    selected_zone = st.selectbox(f"📍 Select Zone ({title}):", sorted(df[zone_col].dropna().unique()), key=title + key_suffix)
                    st.success(f"Showing {title.lower()} data for *{selected_zone}*")
                    st.dataframe(df[df[zone_col] == selected_zone])

            if mtype == "accident":
                zone_data(accident_df, "Zone", "Accidents", key_suffix)
                bar_chart(accident_df, "Zone", "No. of Cases", "Zone-wise Accident Cases", 'crimson')

            elif mtype == "pollution":
                zone_col = "Zone" if "Zone" in air_df.columns else "Zone / Area"
                val_col = "Avg. Value (µg/m³) or AQI"
                zone_data(air_df, zone_col, "Air Pollution", key_suffix)
                bar_chart(air_df, zone_col, val_col, "Zone-wise Air Pollution Levels", 'grey')

            elif mtype == "crime":
                zone_data(crime_df, "Zone Name", "Crime", key_suffix)
                bar_chart(crime_df, "Zone Name", "Total Crimes", "Zone-wise Crime Rates", 'blue')

            elif mtype == "heat":
                zone_data(heat_df, "Area", "Heat", key_suffix)
                bar_chart(heat_df, "Area", "Heatstroke Cases", "Zone-wise Heatstroke Cases", 'orange')

            elif mtype == "flood":
                zone_data(flood_df, "Area", "Flood", key_suffix)
                bar_chart(flood_df, "Area", "People Affected", "Zone-wise Flood Impact", 'black')

            elif mtype == "population":
                zone_data(population_df, "Zone Name", "Population", key_suffix)
                bar_chart(population_df, "Zone Name", "Population", "Zone-wise Population Distribution", 'purple')

            elif mtype == "risk":
                zones = Riskfactor_df["Area"].dropna().unique()
                selected_zone = st.selectbox("📍 Select Zone (Risk Factors):", sorted(zones), key="risk_" + key_suffix)
                st.success(f"Showing risk data for *{selected_zone}*")
                st.dataframe(Riskfactor_df[Riskfactor_df["Area"] == selected_zone])

                melted_df = Riskfactor_df.melt(
                    id_vars=["Area"],
                    value_vars=["Accident", "Air Pollution", "Flood", "Heat", "Crime", "Population"],
                    var_name="Risk Type",
                    value_name="Level"
                )

                fig, ax = plt.subplots(figsize=(14, 6))
                pivot_df = melted_df.pivot(index="Area", columns="Risk Type", values="Level")
                pivot_df.plot(kind="bar", ax=ax, colormap="coolwarm", edgecolor='black')

                plt.title("Risk Factor Levels by Zone")
                plt.xlabel("Zone")
                plt.ylabel("Risk Level (1=Low, 2=Medium, 3=High)")
                plt.xticks(rotation=45, ha='right')
                plt.legend(title="Risk Type", bbox_to_anchor=(1.05, 1), loc='upper left')
                plt.tight_layout()
                st.pyplot(plt)

    user_input = st.chat_input("Type your query here...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        query = user_input.lower()
        bot_reply = ""
        reply_type = None

        if "accident" in query or "hospital" in query:
         bot_reply = "You asked about accident-related risks in Chennai."
         reply_type = "accident"
         show_overall_summary(accident_df, "Zone", "No. of Cases", "Accidents", 'crimson')

        elif "pollution" in query or "air" in query or "aqi" in query:
         bot_reply = "Looking up air pollution levels across Chennai."
         reply_type = "pollution"
         zone_col = "Zone" if "Zone" in air_df.columns else "Zone / Area"
         show_overall_summary(air_df, zone_col, "Avg. Value (µg/m³) or AQI", "Air Pollution", 'grey')

        elif "crime" in query or "theft" in query or "robbery" in query:
            bot_reply = "Retrieving crime statistics across zones."
            reply_type = "crime"
            show_overall_summary(crime_df, "Zone Name", "Total Crimes", "Crime", 'blue')

        elif "heat" in query or "temperature" in query or "hot" in query:
            bot_reply = "Fetching heat-related health reports."
            reply_type = "heat"
            show_overall_summary(heat_df, "Area", "Heatstroke Cases", "Heat", 'orange')

        elif "flood" in query or "rain" in query or "water" in query:
            bot_reply = "Loading flood impact reports zone-wise."
            reply_type = "flood"
            show_overall_summary(flood_df, "Area", "People Affected", "Flood", 'black')

        elif "population" in query or "people" in query or "density" in query:
            bot_reply = "Analyzing population distribution across zones."
            reply_type = "population"
            show_overall_summary(population_df, "Zone Name", "Population", "Population", 'purple')

        elif "risk" in query:
            bot_reply = "Showing combined risk levels zone-wise."
            reply_type = "risk"

        st.session_state.messages.append({
            "role": "assistant",
            "content": bot_reply,
            "type": reply_type
        })
                # ✅ Save to database
        log_chat(user_input, bot_reply)

        st.session_state.chat_history.append({"user": user_input, "bot": bot_reply})
        st.rerun()
