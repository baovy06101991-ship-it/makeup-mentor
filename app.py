import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
from groq import Groq
import json

st.set_page_config(page_title="Makeup Mentor AI", layout="wide")
st.title("💄 Makeup Mentor AI - Tu van my pham & cham soc da")

GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=GROQ_API_KEY)

def ask_groq(prompt):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Loi: {e}"

# Du lieu san pham (co link mua hang)
products = {
    "Son": [
        {"name": "MAC Chili", "brand": "MAC", "price": "750,000d", "link": "https://shopee.vn/search?keyword=MAC%20Chili"},
        {"name": "Maybelline 130", "brand": "Maybelline", "price": "280,000d", "link": "https://shopee.vn/search?keyword=Maybelline%20130"},
        {"name": "Romand Fudge", "brand": "Romand", "price": "320,000d", "link": "https://shopee.vn/search?keyword=Romand%20Fudge"},
        {"name": "3CE Velvet", "brand": "3CE", "price": "450,000d", "link": "https://shopee.vn/search?keyword=3CE%20Velvet"}
    ],
    "Kem nen": [
        {"name": "Fit Me 120", "brand": "Maybelline", "price": "280,000d", "link": "https://shopee.vn/search?keyword=Maybelline%20Fit%20Me%20120"},
        {"name": "Infallible 130", "brand": "L'Oreal", "price": "380,000d", "link": "https://shopee.vn/search?keyword=L'Oreal%20Infallible%20130"},
        {"name": "Studio Fix NC30", "brand": "MAC", "price": "700,000d", "link": "https://shopee.vn/search?keyword=MAC%20Studio%20Fix%20NC30"}
    ],
    "Phan phu": [
        {"name": "Laura Mercier", "brand": "Laura Mercier", "price": "950,000d", "link": "https://shopee.vn/search?keyword=Laura%20Mercier%20Powder"},
        {"name": "Innisfree No Sebum", "brand": "Innisfree", "price": "150,000d", "link": "https://shopee.vn/search?keyword=Innisfree%20No%20Sebum"}
    ],
    "Ma hong": [
        {"name": "NARS Orgasm", "brand": "NARS", "price": "600,000d", "link": "https://shopee.vn/search?keyword=NARS%20Orgasm"},
        {"name": "MAC Peaches", "brand": "MAC", "price": "500,000d", "link": "https://shopee.vn/search?keyword=MAC%20Peaches"}
    ]
}

def get_dominant_color(image):
    img = image.resize((50, 50))
    arr = np.array(img)
    avg = arr.mean(axis=0).mean(axis=0).astype(int)
    return avg[0], avg[1], avg[2]

# ==================== GIAO DIEN ====================
category = st.selectbox("📂 Chon danh muc san pham", ["Son", "Kem nen", "Phan phu", "Ma hong"])

st.subheader("🧑 Thong tin ca nhan (de tu van chinh xac hon)")
col1, col2 = st.columns(2)
with col1:
    lip_type = st.selectbox("💋 Tinh trang moi", ["Khong biet", "Moi thuong", "Moi kho", "Moi nut ne", "Moi sam mau"])
with col2:
    skin_type = st.selectbox("🧴 Loai da", ["Khong biet", "Da thuong", "Da dau", "Da kho", "Da hon hop", "Da nhay cam"])

st.markdown("---")
st.subheader("📸 Tai anh mau son len de phan tich")

uploaded = st.file_uploader("Chon anh (jpg, png)", type=["jpg", "png", "jpeg"])

if uploaded:
    img = Image.open(uploaded)
    st.image(img, caption="Anh cua ban", width=250)
    r, g, b = get_dominant_color(img)
    st.success(f"🎨 Mau RGB: {r}, {g}, {b}")

    if st.button("🔍 Tu van AI"):
        with st.spinner("AI dang phan tich..."):
            # 1. Tu van makeup
            prompt_makeup = f"""
            Mau RGB ({r},{g},{b}) la mau son.
            Tinh trang moi: {lip_type}.
            Loai da: {skin_type}.
            Danh muc: {category}.
            
            Hay tu van:
            1. Mau nay hop voi ai (mau da, phong cach)?
            2. Loai san pham {category} phu hop?
            3. Goi y 2-3 san pham gia re (200k-500k) phu hop.
            Chi tra loi bang tieng Viet, ngan gon.
            """
            advice_makeup = ask_groq(prompt_makeup)
            
            # 2. Tu van cham soc da
            prompt_skincare = f"""
            Dua tren thong tin:
            - Loai da: {skin_type}
            - Tinh trang moi: {lip_type}
            - Mau son da chon: RGB ({r},{g},{b})
            
            Hay tu van:
            1. Cach chuan bi da truoc khi trang diem (duong am, kem lot).
            2. San pham cham soc da phu hop voi loai da nay (sua rua mat, kem duong, kem chong nang).
            3. Luu y khi chon son cho tinh trang moi nay.
            Chi tra loi bang tieng Viet, ngan gon, thuc te.
            """
            advice_skincare = ask_groq(prompt_skincare)
            
            # Hien thi ket qua
            st.subheader("💄 Tu van Makeup:")
            st.write(advice_makeup)
            
            st.subheader("🧴 Tu van Cham soc da:")
            st.write(advice_skincare)
            
            # Hien thi san pham goi y (co link mua)
            st.subheader(f"🛒 San pham {category} goi y (gia re):")
            products_list = products.get(category, [])
            cols = st.columns(3)
            for i, p in enumerate(products_list[:3]):
                with cols[i % 3]:
                    st.markdown(f"**{p['name']}**")
                    st.markdown(f"🏷 {p['brand']} | 💰 {p['price']}")
                    st.markdown(f"[🛍️ Mua ngay]({p['link']})", unsafe_allow_html=True)
