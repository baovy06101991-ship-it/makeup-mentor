import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
from groq import Groq
import json

st.set_page_config(page_title="Makeup Mentor AI", layout="wide")
st.title("Makeup Mentor AI - Tu van my pham thong minh")

GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=GROQ_API_KEY)

def ask_groq_with_search(prompt):
    """Gọi Groq với tool web_search để tìm kiếm thông tin sản phẩm"""
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            tools=[{
                "type": "function",
                "function": {
                    "name": "web_search",
                    "description": "Tìm kiếm thông tin sản phẩm mỹ phẩm, giá cả, hình ảnh trên web"
                }
            }],
            tool_choice="auto",
            temperature=0.7
        )
        return response
    except Exception as e:
        # Fallback nếu web search không hoạt động
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response

# Du lieu san pham co ban (de backup)
data = {
    "Son": [
        {"name": "MAC Chili", "brand": "MAC", "price": "750k"},
        {"name": "Maybelline 130", "brand": "Maybelline", "price": "280k"},
        {"name": "Romand Fudge", "brand": "Romand", "price": "320k"}
    ],
    "Kem nen": [
        {"name": "Fit Me 120", "brand": "Maybelline", "price": "280k"},
        {"name": "Infallible 130", "brand": "L'Oreal", "price": "380k"}
    ],
    "Phan phu": [
        {"name": "Laura Mercier", "brand": "Laura Mercier", "price": "950k"}
    ],
    "Ma hong": [
        {"name": "NARS Orgasm", "brand": "NARS", "price": "600k"}
    ]
}

def get_dominant_color(image):
    img = image.resize((50, 50))
    arr = np.array(img)
    avg = arr.mean(axis=0).mean(axis=0).astype(int)
    return avg[0], avg[1], avg[2]

# ==================== GIAO DIEN ====================
category = st.selectbox("Chon danh muc san pham", ["Son", "Kem nen", "Phan phu", "Ma hong"])

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
        with st.spinner("AI dang phan tich va tim kiem san pham..."):
            prompt = f"""
            Mau RGB ({r},{g},{b}) la mau son can tu van.
            Tinh trang moi: {lip_type}.
            Loai da: {skin_type}.
            Danh muc: {category}.
            
            Hay lam cac viec sau:
            1. Tim kiem tren web cac san pham {category} co mau tuong tu voi RGB ({r},{g},{b}).
            2. Lay ten san pham, thuong hieu, gia va link hinh anh (neu co).
            3. Tu van mau nay hop voi loai da va tinh trang moi nao.
            
            Chi tra loi bang tieng Viet, ngan gon xuc tich.
            """
            
            try:
                response = ask_groq_with_search(prompt)
                st.subheader("Tu van AI:")
                st.write(response.choices[0].message.content)
                
                # Neu response co tool_calls (web search results)
                if hasattr(response.choices[0].message, 'tool_calls') and response.choices[0].message.tool_calls:
                    st.subheader("Ket qua tim kiem truc tiep:")
                    for tool_call in response.choices[0].message.tool_calls:
                        if tool_call.function.name == "web_search":
                            args = json.loads(tool_call.function.arguments)
                            st.info(f"🔍 Da tim kiem: {args.get('query', '')}")
                            
            except Exception as e:
                st.error(f"Loi: {e}")
                # Fallback: hien thi san pham co san
                products = data.get(category, [])
                if products:
                    st.subheader(f"San pham {category} goi y (tu du lieu co san):")
                    for p in products[:3]:
                        st.write(f"- {p['name']} ({p['brand']}): {p['price']}")
