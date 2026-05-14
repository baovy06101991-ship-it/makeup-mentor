import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import google.generativeai as genai

st.set_page_config(page_title="Makeup Mentor AI", layout="wide")
st.title("Makeup Mentor AI - Tu van my pham")

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")
    gemini_ok = True
except Exception as e:
    gemini_ok = False
    st.error(f"Loi cau hinh Gemini API: {e}")

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
        if gemini_ok:
            with st.spinner("AI dang phan tich..."):
                prompt = f"Mau RGB ({r},{g},{b}) la mau son. Hay tu van mau nay hop voi da nao, loai son phu hop."
                response = model.generate_content(prompt)
                st.subheader("Tu van AI:")
                st.write(response.text)
        else:
            st.error("Gemini API chua duoc cau hinh hoac key khong hop le.")
