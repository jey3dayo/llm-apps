import streamlit as st
import openai
from constants import DEFAULT_MODEL

st.title("simple chat")

user_message = st.text_input(label="どうした？")

if user_message:
    completion = openai.ChatCompletion.create(
        model=DEFAULT_MODEL,
        temperature=0,
        # max_tokens=100,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_message},
        ],
    )

    st.write(completion)
