import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
from groq import Groq
import json

st.set_page_config(page_title="Makeup Mentor AI", layout="wide")

# CSS (giữ nguyên)
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #ffe6f0, #ffd6e8, #ffe0f0); background-size: 200% 200%; animation: gradientShift 8s ease infinite; }
    @keyframes gradientShift { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    div[data-testid="column"] { background-color: rgba(255, 255, 255, 0.85); backdrop-filter: blur(2px); border-radius: 20px; padding: 15px; margin: 8px; transition: 0.3s; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
    div[data-testid="column"]:hover { transform: translateY(-5px); box-shadow: 0 12px 20px rgba(0,0,0,0.15); background-color: rgba(255, 255, 255, 0.95); }
    h1 { color: #c2185b; text-shadow: 0 0 5px #ff80ab, 0 0 10px #ffb3c6; animation: titleGlow 3s ease-in-out infinite alternate; }
    @keyframes titleGlow { from { text-shadow: 0 0 2px #ff80ab; } to { text-shadow: 0 0 12px #ff4081; } }
    .stButton button { background: linear-gradient(90deg, #c2185b, #e91e63); color: white; border: none; border-radius: 40px; padding: 10px 28px; font-weight: bold; transition: 0.3s; box-shadow: 0 2px 8px rgba(0,0,0,0.2); }
    .stButton button:hover { transform: scale(1.02); background: linear-gradient(90deg, #e91e63, #f06292); box-shadow: 0 6px 14px rgba(233,30,99,0.4); cursor: pointer; }
    .stFileUploader { border: 2px dashed #e91e63; border-radius: 24px; padding: 12px; transition: 0.2s; }
    .stFileUploader:hover { border-color: #c2185b; background-color: #fff0f3; }
</style>
""", unsafe_allow_html=True)

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
        return f"Lỗi: {e}"

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

def get_dominant_color(image):
    img = image.resize((50, 50))
    arr = np.array(img)
    avg = arr.mean(axis=0).mean(axis=0).astype(int)
    return avg[0], avg[1], avg[2]

category = st.selectbox("📂 Chọn danh mục sản phẩm", ["Son", "Kem nen", "Phan phu", "Ma hong"])

col1, col2 = st.columns(2)
with col1:
    lip_type = st.selectbox("💋 Tình trạng môi", ["Không biết", "Môi thường", "Môi khô", "Môi nứt nẻ", "Môi sậm màu"])
with col2:
    skin_type = st.selectbox("🧴 Loại da", ["Không biết", "Da thường", "Da dầu", "Da khô", "Da hỗn hợp", "Da nhạy cảm"])

price_range = st.radio("💰 Phân khúc giá", ["Giá rẻ (dưới 500k)", "Tầm trung (500k - 1tr)", "Cao cấp (1tr - 2tr)"])
price_prompt = {
    "Giá rẻ (dưới 500k)": "ưu tiên sản phẩm dưới 500,000đ",
    "Tầm trung (500k - 1tr)": "ưu tiên sản phẩm từ 500,000đ đến 1,000,000đ",
    "Cao cấp (1tr - 2tr)": "ưu tiên sản phẩm từ 1,000,000đ đến 2,000,000đ"
}[price_range]

detail_level = st.radio("📝 Độ chi tiết", ["Nhanh (gợi ý chính)", "Chuyên sâu (có mã số, màu cụ thể)"])
detail_prompt = "trả lời ngắn gọn" if "Nhanh" in detail_level else "trả lời chi tiết, có mã sản phẩm cụ thể (nếu biết), mô tả màu chính xác"

st.markdown("---")
st.subheader("📸 Tải ảnh màu son lên để phân tích")

uploaded = st.file_uploader("Chọn ảnh (jpg, png)", type=["jpg", "png", "jpeg"])

if uploaded:
    img = Image.open(uploaded)
    st.image(img, caption="Ảnh của bạn", width=250)
    r, g, b = get_dominant_color(img)
    st.success(f"🎨 Màu RGB: {r}, {g}, {b}")

    if st.button("🔍 Tư vấn AI"):
        with st.spinner("AI đang phân tích..."):
            prompt = f"""
Màu RGB ({r},{g},{b}) là màu son chính.
Tình trạng môi: {lip_type}.
Loại da: {skin_type}.
Danh mục: {category}.
Phân khúc giá: {price_prompt}.
Yêu cầu chi tiết: {detail_prompt}.

QUAN TRỌNG:
- Phải viết đúng tên thương hiệu, đúng mã màu (ví dụ: INTOYOU 302, Romand 23, 3CE 212, MAC Chili, Maybelline 130...).
- Không viết tắt hoặc sai chính tả tên hãng (INTOYOU, không phải INTYOU).
- Mỗi gợi ý phải có: tên sản phẩm + thương hiệu + mã màu (nếu có) + giá + lý do phù hợp.

Hãy tư vấn:
1. Màu này gần với tông màu gì (đỏ cam, hồng đất, cam cháy, nâu hồng...)?
2. Gợi ý 3 sản phẩm {category} cụ thể, **có mã màu hoặc tên màu chính xác**.
3. Đánh giá độ phù hợp với loại da {skin_type} và tình trạng môi {lip_type}.
4. Trả lời bằng tiếng Việt, dễ hiểu, chi tiết.
"""
            advice = ask_groq(prompt)
            st.subheader("💄 Tư vấn AI:")
            st.write(advice)

            st.subheader(f"🛒 Sản phẩm {category} tham khảo (theo phân khúc giá):")
            products_list = products.get(category, [])
            cols = st.columns(3)
            for i, p in enumerate(products_list[:3]):
                with cols[i % 3]:
                    st.markdown(f"**{p['name']}**")
                    st.markdown(f"🏷 {p['brand']} | 💰 {p['price']}")
                    st.markdown(f"[🛍️ Mua ngay]({p['link']})", unsafe_allow_html=True)
