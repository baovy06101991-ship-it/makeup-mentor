import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import google.generativeai as genai
import io

st.set_page_config(page_title="Makeup Mentor AI", layout="wide")

# PWA manifest
st.markdown("""
    <link rel="manifest" href="/manifest.json">
    <link rel="apple-touch-icon" href="icon-192.png">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="theme-color" content="#FF5733">
""", unsafe_allow_html=True)

st.title("?? Makeup Mentor AI - Tu van my pham")

# Gemini config (d—ng st.secrets d? b?o m?t)
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")
    gemini_ok = True
except:
    gemini_ok = False
    st.warning("Chua cau hinh Gemini API. Vui long them key vao Secrets.")

# D? li?u s?n ph?m m?u
data = {
    "product_name": ["MAC Chili", "Maybelline 130", "Romand Fudge"],
    "brand": ["MAC", "Maybelline", "Romand"],
    "price": ["750k", "280k", "320k"],
    "image_url": [
        "https://picsum.photos/id/1/150/150",
        "https://picsum.photos/id/2/150/150",
        "https://picsum.photos/id/3/150/150"
    ]
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
    r,g,b = get_dominant_color(img)
    st.success(f"Mau RGB: {r},{g},{b}")
    
    if st.button("Tu van AI"):
        if gemini_ok:
            with st.spinner("AI dang phan tich..."):
                prompt = f"Mau RGB ({r},{g},{b}) la mau son. Hay tu van mau nay hop voi da nao, loai son phu hop."
                response = model.generate_content(prompt)
                st.subheader("Tu van AI:")
                st.write(response.text)
        else:
            st.error("Chua cau hinh Gemini. Hay them API key vao Secrets.")