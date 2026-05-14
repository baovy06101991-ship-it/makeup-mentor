import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import requests
import json

st.set_page_config(page_title="Makeup Mentor AI", layout="wide")
st.title("Makeup Mentor AI - Tu van my pham")

DEEPSEEK_API_KEY = st.secrets["DEEPSEEK_API_KEY"]

def ask_deepseek(prompt):
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

data = {
    "product_name": ["MAC Chili", "Maybelline 130", "Romand Fudge"],
    "brand": ["MAC", "Maybelline", "Romand"],
    "price": ["750k", "280k", "320k"]
}
df = pd.DataFrame(data)

def get_dominant_color(image):
    img = image.resize((50, 50))
    arr = np.array(img)
    avg = arr.mean(axis=0).mean(axis=0).astype(int)
    return avg[0], avg[1], avg[2]

uploaded = st.file_uploader("Tai anh mau son len", type=["jpg", "png", "jpeg"])

if uploaded:
    img = Image.open(uploaded)
    st.image(img, width=250)
    r, g, b = get_dominant_color(img)
    st.success(f"RGB: {r},{g},{b}")

    if st.button("Tu van AI"):
        with st.spinner("AI dang phan tich..."):
            prompt = f"Mau RGB ({r},{g},{b}) la mau son. Hay tu van mau nay hop voi da nao, loai son phu hop."
            try:
                result = ask_deepseek(prompt)
                st.subheader("Phan hoi tu API (debug):")
                st.json(result)
                if "choices" in result:
                    st.subheader("Tu van AI:")
                    st.write(result["choices"][0]["message"]["content"])
                else:
                    st.error(f"Loi: {result}")
            except Exception as e:
                st.error(f"Loi: {e}")
