import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from transformers import pipeline  # type: ignore
import os

# ✅ Set working directory to script location
DATA_DIR = os.path.dirname(os.path.abspath(__file__))

# ✅ Streamlit setup
st.set_page_config(page_title="Chennai Risk Chatbot", page_icon="🧠")
st.title("🧠 Chennai Risk Chatbot")

# ✅ Load Excel files
def load_data():
    try:
        return {
            "accident": pd.read_excel(os.path.join(DATA_DIR, "accident1.xlsx")),
            "air pollution": pd.read_excel(os.path.join(DATA_DIR, "air pollution.xlsx")),
            "crime": pd.read_excel(os.path.join(DATA_DIR, "crime details 1.xlsx")),
            "heat": pd.read_excel(os.path.join(DATA_DIR, "heat.xlsx")),
            "flood": pd.read_excel(os.path.join(DATA_DIR, "flood.xlsx")),
            "population": pd.read_excel(os.path.join(DATA_DIR, "population.xlsx")),
            "riskfactor": pd.read_excel(os.path.join(DATA_DIR, "riskanalysis.xlsx"))
        }
    except FileNotFoundError as e:
        st.error(f"📂 Missing file: {e.filename}")
        st.stop()

data = load_data()

# ✅ Load NLP model (zero-shot classification)
with st.spinner("🔄 Loading NLP model... (may take a minute)"):
    try:
        classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
    except Exception:
        st.error("❌ Error loading NLP model. Ensure internet is available and 'transformers' is installed.")
        st.stop()

# ✅ NLP-based intent detection
def detect_intent(user_input):
    labels = list(data.keys())
    result = classifier(user_input, candidate_labels=labels)
    return result["labels"][0]

# ✅ Friendly AI-style reply generator
def generate_response(user_input, intent):
    greetings = ["hi", "hello", "hey"]
    if any(g in user_input.lower() for g in greetings):
        return "👋 Hello! I'm your Chennai Risk Assistant. Ask me anything about accidents, crime, floods, or more."

    if intent in data:
        return f"Great question! Let's explore **{intent}** risk data in Chennai. You can choose an area below to view more details and a chart."
    
    return "Hmm, I didn't catch that. Can you rephrase or ask about accident, crime, flood, heat, etc.?"

# ✅ Use chat-based UI
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input box
user_input = st.chat_input("Ask anything about Chennai's risks...")

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Detect intent and get dataset
    intent = detect_intent(user_input)
    df = data[intent]

    # Friendly assistant reply
    assistant_msg = generate_response(user_input, intent)
    st.session_state.messages.append({"role": "assistant", "content": assistant_msg})
    with st.chat_message("assistant"):
        st.markdown(assistant_msg)

    # Show data and charts if not just small talk
    if intent in data:
        # Column mapping setup
        zone_column = None
        value_column = None
        color = "gray"

        if intent == "accident":
            zone_column = "Zone / Area"
            value_column = "No. of Cases"
            color = "crimson"
        elif intent == "air pollution":
            zone_column = "Zone / Area"
            value_column = "Avg. Value (µg/m³) or AQI"
            color = "green"
        elif intent == "crime":
            zone_column = "Zone Name"
            value_column = "Total Crimes"
            color = "blue"
        elif intent == "heat":
            zone_column = "Area"
            value_column = "Heatstroke Cases"
            color = "orange"
        elif intent == "flood":
            zone_column = "Area"
            value_column = "People Affected"
            color = "black"
        elif intent == "population":
            zone_column = "Zone Name"
            value_column = "Population"
            color = "purple"
        elif intent == "riskfactor":
            st.dataframe(df)
            st.stop()

        # Process and clean
        df.columns = df.columns.str.strip()
        df[value_column] = pd.to_numeric(df[value_column], errors="coerce")
        df = df.dropna(subset=[zone_column, value_column])

        # Dropdown for zone selection
        zones = df[zone_column].dropna().unique()
        selected_zone = st.selectbox(f"📍 Select {zone_column}:", sorted(zones))
        filtered_data = df[df[zone_column] == selected_zone]
        st.dataframe(filtered_data)

        # Bar chart
        chart_data = df[[zone_column, value_column]].copy()
        chart_data = chart_data.groupby(zone_column).sum().sort_values(value_column, ascending=False)

        fig, ax = plt.subplots(figsize=(12, 6))
        bars = ax.bar(chart_data.index, chart_data[value_column], color=color)
        ax.set_ylabel(value_column)
        ax.set_title(f"{intent.capitalize()} Overview by {zone_column}")
        plt.xticks(rotation=45, ha='right')

        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{int(height)}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom')

        st.pyplot(fig)
