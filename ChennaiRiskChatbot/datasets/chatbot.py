import streamlit as st
import pandas as pd
import os

# Set page config
st.set_page_config(page_title="🧠 Chennai Risk Chatbot", layout="centered")

# Title and description
st.title("🧠 Chennai Risk Chatbot")
st.write("Hi, I’m your Chennai Risk Assistant! 🤖 Ask me about:")
st.markdown("- 🚗 **Accidents**\n- 🌫️ **Air Pollution**\n- 🚨 **Crime**\n- 🌊 **Floods**\n- 🌡️ **Heat**\n- 🧑‍🤝‍🧑 **Population**\n- ⚠️ **Risk Factor**")

# Set base path
base_path = "datasets"

# Load datasets
@st.cache_data
def load_data():
    try:
        data = {
            "accident": pd.read_excel(os.path.join(base_path, "accident1.xlsx")),
            "air pollution": pd.read_excel(os.path.join(base_path, "air pollution.xlsx")),
            "crime": pd.read_excel(os.path.join(base_path, "crime details 1.xlsx")),
            "flood": pd.read_excel(os.path.join(base_path, "flood.xlsx")),
            "heat": pd.read_excel(os.path.join(base_path, "heat.xlsx")),
            "population": pd.read_excel(os.path.join(base_path, "population.xlsx")),
            "riskfactor": pd.read_excel(os.path.join(base_path, "riskanalysis.xlsx"))
        }
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

data_files = load_data()

# Function to get reply from data
def get_reply(user_input):
    user_input_lower = user_input.lower()

    if "accident" in user_input_lower:
        df = data_files["accident"]
        return f"Here’s a snapshot of accident data:\n\n{df.head().to_markdown()}"

    elif "air" in user_input_lower or "pollution" in user_input_lower:
        df = data_files["air pollution"]
        return f"Here’s air pollution data:\n\n{df.head().to_markdown()}"

    elif "crime" in user_input_lower:
        df = data_files["crime"]
        return f"Here’s crime data for Chennai:\n\n{df.head().to_markdown()}"

    elif "flood" in user_input_lower:
        df = data_files["flood"]
        return f"Flood data overview:\n\n{df.head().to_markdown()}"

    elif "heat" in user_input_lower:
        df = data_files["heat"]
        return f"Heat data snapshot:\n\n{df.head().to_markdown()}"

    elif "population" in user_input_lower:
        df = data_files["population"]
        return f"Population details:\n\n{df.head().to_markdown()}"

    elif "risk" in user_input_lower or "riskfactor" in user_input_lower:
        df = data_files["riskfactor"]
        return f"Risk factor insights:\n\n{df.head().to_markdown()}"

    elif "hi" in user_input_lower or "hello" in user_input_lower:
        return "Hello there! 👋 How can I help you analyze Chennai's risk data?"

    elif "how to stay safe" in user_input_lower:
        return "✅ Stay updated on alerts\n✅ Avoid risky areas\n✅ Follow city guidelines\n✅ Analyze local data to plan better."

    else:
        return "Sorry, I couldn't understand that. Please ask about accident, air pollution, crime, flood, heat, population, or risk factors."

# Chat interaction
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("Type your question here 👇", placeholder="e.g., Show me Chennai crime data")
    submitted = st.form_submit_button("Ask")

if submitted and user_input:
    reply = get_reply(user_input)
    st.session_state.chat_history.append(("You", user_input))
    st.session_state.chat_history.append(("Bot", reply))

# Display chat history
for sender, message in st.session_state.chat_history:
    if sender == "You":
        st.markdown(f"**🧑 You:** {message}")
    else:
        st.markdown(f"**🤖 Bot:** {message}")
