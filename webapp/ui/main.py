import streamlit as st
import requests


URL = "http://127.0.0.1:4444/"



context = st.text_input("Enter Context")
question = st.text_input("Enter Question")

payload = {
    "context": context,
    "question": question
}

answer = requests.post(URL, json=payload)

if answer.status_code == 200:
    print(eval(answer.content))
    answer = eval(answer.content)["answer"]
    st.write(answer)