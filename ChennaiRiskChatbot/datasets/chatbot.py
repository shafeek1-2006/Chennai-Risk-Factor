import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="🧠 Chennai Risk Chatbot", layout="centered")

st.title("🧠 Chennai Risk Chatbot")
st.markdown("""
Ask me anything about the risk factors in **Chennai areas**, including:
- 🚧 Accident  
- 🌫️ Air Pollution  
- 🕵️ Crime  
- 🌊 Flood  
- 🔥 Heat  
- 👥 Population

_Type your question below like:_
- "What is the air pollution level in T. Nagar?"
- "How risky is Adyar based on crime and flood?"
""")

# Load Excel file from your provided path
DATA_PATH = r"C:\Users\SHAFEEK RAHMAN.R\OneDrive\Desktop\ChennaiRiskChatbot\datasets\ChennaiRiskData.xlsx"

@st.cache_data
def load_data():
    df = pd.read_excel(DATA_PATH)
    df.columns = [col.lower().strip() for col in df.columns]
    return df

df = load_data()

def get_response(question):
    # Identify area from question
    location = None
    for area in df['area']:
        if area.lower() in question.lower():
            location = area
            break

    if not location:
        return "❌ Sorry, I couldn't find the area you're asking about. Please try a different area name."

    # Get data for the matched location
    row = df[df['area'] == location].iloc[0]
    info = {col: row[col] for col in df.columns if col != 'area'}

    # Prepare a friendly markdown response
    response = f"✅ **Risk data for {location}:**\n\n"
    for key, value in info.items():
        response += f"- **{key.title()}**: {value}\n"
    return response

# Input box
query = st.text_input("💬 Type your question here:")

# Show response
if query:
    with st.spinner("🤖 Thinking..."):
        result = get_response(query)
        st.markdown(result)
