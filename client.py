import requests
import streamlit as st

def get_llm_response(input):
    url = "http://localhost:8000/agent/invoke"
    
    payload = {"input": input}
    response = requests.post(url, json={'input': payload})

    if response.status_code == 200:
        return response.json()['output']['output']
    else:
        return f"Error: {response.status_code} - {response.text}"
    
st.title("LangServe LLM Client")
input_text = st.text_input("Enter a prompt:")

if input_text:
    response = get_llm_response(input_text)

    st.write(response)