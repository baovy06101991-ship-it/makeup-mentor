import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
from groq import Groq
import json
import re

# ==================== CẤU HÌNH TRANG ====================
st.set_page_config(page_title="Makeup Mentor AI", layout="wide")

# ==================== CSS & HEADER ====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Playfair Display', 'Times New Roman', 'Segoe UI', Arial, sans-serif;
    }
    
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
    
    /* Gradient chạy ngang */
    @keyframes gradientMove {
        0% { background-position: 100% 0%; }
        100% { background-position: 0% 0%; }
    }
    
    .app-header {
        text-align: center;
        padding: 25px 20px;
        margin-bottom: 30px;
        background: linear-gradient(135deg, #c2185b, #e91e63);
        border-radius: 35px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.15);
    }
    
    /* Logo chạy màu */
    .logo-text {
        font-size: 2.8rem;
        font-weight: 600;
        font-style: italic;
        letter-spacing: 1px;
        margin-bottom: 5px;
        background: linear-gradient(90deg, #8B0000, #B22222, #CD5C5C, #A0522D, #800080, #4B0082, #2E8B57);
        background-size: 200% 100%;
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        animation: gradientMove 5s linear infinite;
    }
    .logo-ai {
        font-size: 1.4rem;
        font-weight: 600;
        letter-spacing: 4px;
        background: linear-gradient(90deg, #8B0000, #B22222, #CD5C5C, #A0522D, #800080, #4B0082, #2E8B57);
        background-size: 200% 100%;
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        animation: gradientMove 5s linear infinite;
    }
    .logo-tagline {
        font-size: 0.85rem;
        margin-top: 10px;
        letter-spacing: 1px;
        background: linear-gradient(90deg, #8B0000, #B22222, #CD5C5C, #A0522D, #800080, #4B0082, #2E8B57);
        background-size: 200% 100%;
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        animation: gradientMove 5s linear infinite;
    }
    
    /* Áp dụng hiệu ứng cho các thành phần khác */
    label, .stMarkdown, .stSelectbox, .stRadio, .stFileUploader, div[data-testid="column"] {
        background: linear-gradient(90deg, #8B0000, #B22222, #CD5C5C, #A0522D, #800080, #4B0082, #2E8B57);
        background-size: 200% 100%;
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        animation: gradientMove 5s linear infinite;
        font-weight: 500;
    }
    
    /* Loại trừ phần nội dung AI tư vấn */
    .ai-advice, .ai-advice * {
        background: none !important;
        -webkit-background-clip: unset !important;
        background-clip: unset !important;
        color: #2c3e50 !important;
        animation: none !important;
    }
    
    .stButton button {
        background: linear-gradient(90deg, #c2185b, #e91e63);
        color: white;
        border: none;
        border-radius: 40px;
        padding: 10px 28px;
        font-weight: 600;
        transition: 0.3s;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        font-size: 1rem;
    }
    .stButton button:hover {
        transform: scale(1.02);
        background: linear-gradient(90deg, #e91e63, #f06292);
        box-shadow: 0 6px 14px rgba(233,30,99,0.4);
        cursor: pointer;
    }
    
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
    
    .stSelectbox label, .stRadio label, .stColumns label {
        font-weight: 500;
        font-size: 1rem;
    }
    
    div[data-testid="column"] {
        background-color: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(2px);
        border-radius: 20px;
        padding: 15px;
        margin: 8px;
        transition: 0.3s;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    div[data-testid="column"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 20px rgba(0,0,0,0.15);
        background-color: rgba(255, 255, 255, 0.95);
    }
</style>

<div class="app-header">
    <div class="logo-text">Makeup Mentor</div>
    <div class="logo-ai">AI</div>
    <div class="logo-tagline">Trợ lý trang điểm & chăm sóc da thông minh</div>
</div>
""", unsafe_allow_html=True)

# ==================== KHỞI TẠO GROQ CLIENT ====================
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=GROQ_API_KEY)

def ask_groq(prompt):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,
            max_tokens=3000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Lỗi: {e}"

def extract_json_from_text(text):
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*$', '', text)
    if text.count('{') > text.count('}'):
        text += '}' * (text.count('{') - text.count('}'))
    if text.count('[') > text.count(']'):
        text += ']' * (text.count('[') - text.count(']'))
    try:
        return json.loads(text)
    except:
        match = re.search(r'\{.*\}|\[.*\]', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except:
                pass
        return None

def get_product_link(product_name, brand):
    query = f"{brand} {product_name}".replace(" ", "%20")
    return f"https://shopee.vn/search?keyword={query}"

def get_dominant_color(image):
    img = image.resize((50, 50))
    arr = np.array(img)
    avg = arr.mean(axis=0).mean(axis=0).astype(int)
    return avg[0], avg[1], avg[2]

# ==================== GIAO DIỆN CHÍNH ====================
category = st.selectbox("📂 Chọn danh mục sản phẩm", ["Son", "Kem nen", "Phan phu", "Ma hong", "Serum duong da"])

col1, col2 = st.columns(2)
with col1:
    lip_type = st.selectbox("💋 Tình trạng môi", ["Không biết", "Môi thường", "Môi khô", "Môi nứt nẻ", "Môi sậm màu"])
with col2:
    skin_type = st.selectbox("🧴 Loại da", ["Không biết", "Da thường", "Da dầu", "Da khô", "Da hỗn hợp", "Da nhạy cảm"])

price_range = st.radio("💰 Phân khúc giá", ["Giá rẻ (dưới 500k)", "Tầm trung (500k - 1tr)", "Cao cấp (1tr - 2tr)"])
price_prompt = {
    "Giá rẻ (dưới 500k)": "dưới 500,000đ",
    "Tầm trung (500k - 1tr)": "từ 500,000đ đến 1,000,000đ",
    "Cao cấp (1tr - 2tr)": "từ 1,000,000đ đến 2,000,000đ"
}[price_range]

st.markdown("---")

# Hướng dẫn chụp ảnh
st.markdown("""
### 📸 Hướng dẫn chụp ảnh để có kết quả chính xác nhất:
| Bạn cần tư vấn về... | Hãy chụp cận... |
|----------------------|------------------|
| 🔴 **Màu son** | Vùng môi (tránh để mắt và da xung quanh) |
| 🟠 **Màu mắt / phấn mắt** | Vùng mắt |
| 🟡 **Màu má hồng** | Vùng má |
| 🟢 **Lông mày** | Vùng lông mày |
| 🔵 **Kem nền / phấn phủ** | Vùng má hoặc cằm (da sạch, không makeup) |
| 🟣 **Serum / dưỡng da** | Vùng má (da sạch) |
""")

st.subheader("📸 Tải ảnh lên để phân tích")

uploaded_file = st.file_uploader("📁 Chọn ảnh từ thư viện", type=["jpg", "png", "jpeg"], key="file_uploader")

if uploaded_file is not None:
    img = Image.open(uploaded_file)
    st.image(img, caption="Ảnh của bạn", width=250)
    r, g, b = get_dominant_color(img)
    st.success(f"🎨 Màu RGB: {r}, {g}, {b}")

    if st.button("🔍 Tư vấn chuyên gia"):
        with st.spinner("Chuyên gia AI đang phân tích..."):
            prompt = f"""
BẠN LÀ CHUYÊN GIA TRANG ĐIỂM VÀ CHĂM SÓC DA.
QUAN TRỌNG: Người dùng đang cần tư vấn về DANH MỤC: {category}. 

Thông tin:
- Màu RGB ({r},{g},{b}) là màu tham khảo
- Tình trạng môi: {lip_type} (chỉ áp dụng cho Son)
- Loại da: {skin_type}
- Danh mục: {category}
- Phân khúc giá: {price_prompt}

YÊU CẦU TƯ VẤN:

1. PHÂN TÍCH MÀU SẮC (nếu là makeup):
   - Tông màu, cảm nhận, phong cách

2. TƯ VẤN SẢN PHẨM {category}:
   - Gợi ý 3 sản phẩm cụ thể (tên, thương hiệu, giá, lý do)
   - Với Serum: gợi ý theo loại da {skin_type}, thành phần phù hợp

3. LỜI KHUYÊN:
   - Cách chọn cho da {skin_type}
   - Cách sử dụng (nếu là Serum)
   - Lưu ý

Trả lời dưới dạng JSON:
{{
  "color_analysis": {{
    "tone": "tông màu",
    "style": "phong cách"
  }},
  "products": [
    {{"name": "tên", "brand": "thương hiệu", "price": 0, "reason": "lý do"}}
  ],
  "advice": {{
    "selection_tips": "cách chọn",
    "usage": "cách dùng (nếu có)",
    "note": "lưu ý"
  }}
}}
"""
            response_text = ask_groq(prompt)
            try:
                data = extract_json_from_text(response_text)
                if not data:
                    st.error("Chuyên gia AI trả về định dạng không đúng.")
                    st.code(response_text[:1000])
                else:
                    st.markdown('<div class="ai-advice">', unsafe_allow_html=True)
                    st.subheader(f"💄 Tư vấn chuyên gia về {category}:")
                    
                    if "color_analysis" in data:
                        ca = data["color_analysis"]
                        if ca.get('tone'):
                            st.markdown(f"**🎨 Tông màu:** {ca.get('tone')}")
                        if ca.get('style'):
                            st.markdown(f"**✨ Phong cách:** {ca.get('style')}")
                    
                    if "advice" in data:
                        adv = data["advice"]
                        st.markdown("---")
                        st.markdown("### 📝 Lời khuyên:")
                        st.markdown(f"**💡 Cách chọn:** {adv.get('selection_tips', 'không rõ')}")
                        if adv.get('usage'):
                            st.markdown(f"**🕒 Cách dùng:** {adv.get('usage')}")
                        st.markdown(f"**⚠️ Lưu ý:** {adv.get('note', 'không rõ')}")
                    
                    st.markdown("---")
                    st.subheader(f"🛒 Sản phẩm {category} gợi ý (kèm link mua):")
                    products_list = data.get('products', [])
                    if products_list:
                        cols = st.columns(3)
                        for i, product in enumerate(products_list[:3]):
                            with cols[i % 3]:
                                st.markdown(f"**{product.get('name', 'N/A')}**")
                                st.markdown(f"🏷 {product.get('brand', 'N/A')} | 💰 {product.get('price', 0):,}đ")
                                st.markdown(f"📝 {product.get('reason', '')}")
                                link = get_product_link(product.get('name', ''), product.get('brand', ''))
                                st.markdown(f"[🛍️ Mua ngay]({link})", unsafe_allow_html=True)
                    else:
                        st.warning("Không có sản phẩm gợi ý.")
                    st.markdown('</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Lỗi: {e}")
                st.code(response_text[:1500])
