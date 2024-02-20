import streamlit as st

st.title("AIアシスタント")

input = st.text_input(label="何を依頼しますか？")

if input:
    with st.spinner("考え中..."):
        st.write("スケジュールを登録しました！")
