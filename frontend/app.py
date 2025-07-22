import streamlit as st
import os
import requests
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Chat@Code", layout = "wide")

st.title("Chat With your COde")

with st.sidebar:
    st.header("Function Reference")
    st.write("Functions will be listed here")

user_query = st.text_input("Ask a question about the code:")

if user_query:
    with st.spinner("Thinking..."):
        try:
            response = requests.post(
                url = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000/query"),
                json={"query": user_query}
            )
            if response.status_code == 200:
                result = response.json()
                st.markdown("### Answer:") 
                st.write(result["answer"])
            else:
                st.error("Error from backend")
        except Exception as e:
            st.error(f"Failed to connect to backend {e}")