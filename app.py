import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import requests

st.set_page_config(page_title="Makeup Mentor AI", layout="wide")
st.title("Makeup Mentor AI - Tu van my pham thong minh")

GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

def ask_groq(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

# Du lieu san pham (mo rong)
data = {
    "Son": [
        {"name": "MAC Chili", "brand": "MAC", "price": "750k", "image": "https://picsum.photos/id/1/150/150"},
        {"name": "Maybelline 130", "brand": "Maybelline", "price": "280k", "image": "https://picsum.photos/id/2/150/150"},
        {"name": "Romand Fudge", "brand": "Romand", "price": "320k", "image": "https://picsum.photos/id/3/150/150"},
        {"name": "3CE Velvet", "brand": "3CE", "price": "450k", "image": "https://picsum.photos/id/4/150/150"}
    ],
    "Kem nen": [
        {"name": "Fit Me 120", "brand": "Maybelline", "price": "280k", "image": "https://picsum.photos/id/13/150/150"},
        {"name": "Infallible 130", "brand": "L'Oreal", "price": "380k", "image": "https://picsum.photos/id/14/150/150"},
        {"name": "Studio Fix NC30", "brand": "MAC", "price": "700k", "image": "https://picsum.photos/id/15/150/150"}
    ],
    "Phan phu": [
        {"name": "Laura Mercier", "brand": "Laura Mercier", "price": "950k", "image": "https://picsum.photos/id/19/150/150"},
        {"name": "Innisfree No Sebum", "brand": "Innisfree", "price": "150k", "image": "https://picsum.photos/id/20/150/150"}
    ],
    "Ma hong": [
        {"name": "NARS Orgasm", "brand": "NARS", "price": "600k", "image": "https://picsum.photos/id/24/150/150"},
        {"name": "MAC Peaches", "brand": "MAC", "price": "500k", "image": "https://picsum.photos/id/25/150/150"}
    ]
}

def get_dominant_color(image):
    img = image.resize((50, 50))
    arr = np.array(img)
    avg = arr.mean(axis=0).mean(axis=0).astype(int)
    return avg[0], avg[1], avg[2]

# ==================== GIAO DIEN ====================
# Chon danh muc
category = st.selectbox("Chon danh muc san pham", ["Son", "Kem nen", "Phan phu", "Ma hong"])

# Tu van theo da/moi
st.subheader("Thong tin ca nhan (de tu van chinh xac hon)")
col1, col2 = st.columns(2)
with col1:
    lip_type = st.selectbox("Tinh trang moi", ["Khong biet", "Moi thuong", "Moi kho", "Moi nut ne", "Moi sam mau"])
with col2:
    skin_type = st.selectbox("Loai da", ["Khong biet", "Da thuong", "Da dau", "Da kho", "Da hon hop", "Da nhay cam"])

st.markdown("---")
st.subheader("Tai anh mau son len de phan tich")

uploaded = st.file_uploader("Chon anh (jpg, png)", type=["jpg", "png", "jpeg"])

if uploaded:
    img = Image.open(uploaded)
    st.image(img, caption="Anh cua ban", width=250)
    r, g, b = get_dominant_color(img)
    st.success(f"Mau RGB: {r},{g},{b}")

    if st.button("Tu van AI"):
        with st.spinner("AI dang phan tich..."):
            prompt = f"""
            Mau RGB ({r},{g},{b}) la mau son.
            Tinh trang moi: {lip_type}.
            Loai da: {skin_type}.
            Danh muc: {category}.
            Hay tu van:
            1. Mau nay hop voi nhung ai (mau da, phong cach)?
            2. Loai san pham {category} phu hop?
            3. Goi y 2-3 san pham cu the (ten san pham va thuong hieu) phu hop voi mau nay.
            """
            try:
                result = ask_groq(prompt)
                if "choices" in result and len(result["choices"]) > 0:
                    st.subheader("Tu van AI:")
                    st.write(result["choices"][0]["message"]["content"])
                    
                    # Hien thi san pham goi y
                    st.subheader(f"San pham {category} goi y:")
                    products = data.get(category, [])
                    cols = st.columns(3)
                    for i, product in enumerate(products[:3]):
                        with cols[i % 3]:
                            st.image(product["image"], caption=product["name"], width=120)
                            st.markdown(f"**{product['brand']}**")
                            st.markdown(f"💰 {product['price']}")
                else:
                    st.error(f"Loi API: {result}")
            except Exception as e:
                st.error(f"Loi: {e}")
