import streamlit as st
import openai
from pydantic import BaseModel, Field
from langchain.chat_models import ChatOpenAI
from langchain.chains import create_tagging_chain_pydantic
from constants import DEFAULT_MODEL


class Attribute(BaseModel):
    language: str = Field(description="言語", enum=["ja", "en"])
    tags: list[str] = Field(description="タグ", examples=["python", "streamlit"])


st.title("タグ付け")

text = st.text_area(label="タグ付けするテキスト")

if text:
    with st.spinner("タグ付け中..."):
        llm = ChatOpenAI(model=DEFAULT_MODEL)
        chain = create_tagging_chain_pydantic(Attribute, llm)
        attr = chain.run(text)
        st.write(attr.dict())
