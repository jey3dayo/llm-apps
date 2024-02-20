import streamlit as st
import json
import openai
from pydantic import BaseModel, Field
import io
import os
from PIL import Image
from stability_sdk import client as stability_client
from constants import DEFAULT_MODEL

StabilityApiModel = "stable-diffusion-xl-1024-v1-0"


class Ingredient(BaseModel):
    ingredient: str = Field(description="材料", examples=["鶏もも肉"])
    quantity: str = Field(description="分量", examples=["300g"])
    # score: str = Field(description="価格", examples=["300円"])


class Recipe(BaseModel):
    ingredients: list[Ingredient]
    instructions: list[str] = Field(
        description="手順", examples=[["材料を切ります。", "材料を炒めます。"]]
    )
    in_english: str = Field(sescription="英語の料理名")


OUTPUT_RECIPE_FUNCTION = {
    "name": "output_recipe",
    "description": "レシピを出力する",
    "parameters": Recipe.schema(),
}

PROMPT_TEMPLATE = """料理のレシピを考えてください。

料理名: {dish}
"""

st.title("レシピ生成AI")

dish = st.text_input(label="料理名")

if dish:
    with st.spinner(text="生成中..."):
        messages = [
            {
                "role": "user",
                "content": PROMPT_TEMPLATE.format(dish=dish),
            },
        ]

        response = openai.ChatCompletion.create(
            model=DEFAULT_MODEL,
            messages=messages,
            functions=[OUTPUT_RECIPE_FUNCTION],
            function_call={"name": OUTPUT_RECIPE_FUNCTION["name"]},
        )

        response_message = response["choices"][0]["message"]
        function_call_args = response_message["function_call"]["arguments"]

        recipe = json.loads(function_call_args)

        st.write("## 材料")
        st.table(recipe["ingredients"])

        # ## 以下の形式のマークダウンの文字列を作成して表示
        #
        # ## 手順
        # 1. 材料を切ります。
        # 2. 材料を炒めます。
        instruction_markdown = "## 手順\n"
        for i, instruction in enumerate(recipe["instructions"], start=1):
            instruction_markdown += f"{i}. {instruction}\n"

        st.write(instruction_markdown)

        stability_api = stability_client.StabilityInference(
            key=os.environ["STABILITY_KEY"],
            engine=StabilityApiModel,
        )

        answers = stability_api.generate(
            prompt=recipe["in_english"],
            height=512,
            width=512,
            samples=1,
        )

        for resp in answers:
            for artifact in resp.artifacts:
                if artifact.finish_reason == stability_client.generation.FILTER:
                    st.warning("画像を生成できませんでした。")
                if artifact.type == stability_client.generation.ARTIFACT_IMAGE:
                    img = Image.open(io.BytesIO(artifact.binary))
                    st.image(img, caption="料理の画像", use_column_width=True)
                    # st.image(image, caption="料理の画像", use_column_width=True)
