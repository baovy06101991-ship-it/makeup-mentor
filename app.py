import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
from groq import Groq
import json

st.set_page_config(page_title="Makeup Mentor AI", layout="wide")

# ==================== CSS TRANG TRÍ & HIỆU ỨNG ====================
st.markdown("""
<style>
    /* Nền gradient chuyển động */
    .stApp {
        background: linear-gradient(135deg, #ffe6f0, #ffd6e8, #ffe0f0);
        background-size: 200% 200%;
        animation: gradientShift 8s ease infinite;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Card sản phẩm */
    div[data-testid="column"] {
        background-color: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(2px);
        border-radius: 20px;
        padding: 15px;
        margin: 8px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    
    div[data-testid="column"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 20px rgba(0,0,0,0.15);
        background-color: rgba(255, 255, 255, 0.95);
    }
    
    /* Tiêu đề */
    h1 {
        color: #c2185b;
        text-shadow: 0 0 5px #ff80ab, 0 0 10px #ffb3c6;
        animation: titleGlow 3s ease-in-out infinite alternate;
    }
    
    @keyframes titleGlow {
        from { text-shadow: 0 0 2px #ff80ab; }
        to { text-shadow: 0 0 12px #ff4081; }
    }
    
    /* Nút bấm */
    .stButton button {
        background: linear-gradient(90deg, #c2185b, #e91e63);
        color: white;
        border: none;
        border-radius: 40px;
        padding: 10px 28px;
        font-weight: bold;
        transition: 0.3s;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    
    .stButton button:hover {
        transform: scale(1.02);
        background: linear-gradient(90deg, #e91e63, #f06292);
        box-shadow: 0 6px 14px rgba(233,30,99,0.4);
        cursor: pointer;
    }
    
    /* Khung upload */
    .stFileUploader {
        border: 2px dashed #e91e63;
        border-radius: 24px;
        padding: 12px;
        transition: 0.2s;
    }
    .stFileUploader:hover {
        border-color: #c2185b;
        background-color: #fff0f3;
    }
</style>
""", unsafe_allow_html=True)

st.title("💄 Makeup Mentor AI - Tu van my pham & cham soc da")

# ==================== AI ====================
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

# ==================== DU LIEU SAN PHAM ====================
products = {
    "Son": [
        {"name": "MAC Chili", "brand": "MAC", "price": "750,000d", "link": "https://shopee.vn/search?keyword=MAC%20Chili"},
        {"name": "Maybelline 130", "brand": "Maybelline", "price": "280,000d", "link": "https://shopee.vn/search?keyword=Maybelline%20130"},
        {"name": "Romand Fudge", "brand": "Romand", "price": "320,000d", "link": "https://shopee.vn/search?keyword=Romand%20Fudge"}
    ],
    "Kem nen": [
        {"name": "Fit Me 120", "brand": "Maybelline", "price": "280,000d", "link": "https://shopee.vn/search?keyword=Maybelline%20Fit%20Me%20120"},
        {"name": "Infallible 130", "brand": "L'Oreal", "price": "380,000d", "link": "https://shopee.vn/search?keyword=L'Oreal%20Infallible%20130"}
    ],
    "Phan phu": [
        {"name": "Innisfree No Sebum", "brand": "Innisfree", "price": "150,000d", "link": "https://shopee.vn/search?keyword=Innisfree%20No%20Sebum"}
    ],
    "Ma hong": [
        {"name": "NARS Orgasm", "brand": "NARS", "price": "600,000d", "link": "https://shopee.vn/search?keyword=NARS%20Orgasm"}
    ]
}

# ==================== XU LY ANH ====================
def get_dominant_color(image):
    img = image.resize((50, 50))
    arr = np.array(img)
    avg = arr.mean(axis=0).mean(axis=0).astype(int)
    return avg[0], avg[1], avg[2]

# ==================== GIAO DIEN ====================
category = st.selectbox("📂 Chon danh muc san pham", ["Son", "Kem nen", "Phan phu", "Ma hong"])

st.subheader("🧑 Thong tin ca nhan")
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
            # Tu van makeup
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

            # Tu van skincare
            prompt_skincare = f"""
            Dua tren thong tin:
            - Loai da: {skin_type}
            - Tinh trang moi: {lip_type}
            - Mau son: RGB ({r},{g},{b})
            Hay tu van:
            1. Cach chuan bi da truoc khi trang diem.
            2. San pham cham soc da phu hop.
            3. Luu y khi chon son.
            Chi tra loi bang tieng Viet, ngan gon.
            """
            advice_skincare = ask_groq(prompt_skincare)

            st.subheader("💄 Tu van Makeup:")
            st.write(advice_makeup)
            st.subheader("🧴 Tu van Cham soc da:")
            st.write(advice_skincare)

            # Hien thi san pham goi y
            st.subheader(f"🛒 San pham {category} goi y (gia re):")
            products_list = products.get(category, [])
            cols = st.columns(3)
            for i, p in enumerate(products_list[:3]):
                with cols[i % 3]:
                    st.markdown(f"**{p['name']}**")
                    st.markdown(f"🏷 {p['brand']} | 💰 {p['price']}")
                    st.markdown(f"[🛍️ Mua ngay]({p['link']})", unsafe_allow_html=True)
