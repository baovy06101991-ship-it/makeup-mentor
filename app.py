import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
from groq import Groq
import json
import re

st.set_page_config(page_title="Makeup Mentor AI", layout="wide")

# CSS
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
            temperature=0.9,
            max_tokens=3000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Lỗi: {e}"

def clean_and_parse_json(text):
    """Sửa lỗi JSON thường gặp và parse"""
    # Loại bỏ markdown code blocks
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*$', '', text)
    
    # Sửa lỗi missing closing brackets
    if text.count('{') > text.count('}'):
        text += '}' * (text.count('{') - text.count('}'))
    if text.count('[') > text.count(']'):
        text += ']' * (text.count('[') - text.count(']'))
    
    # Sửa lỗi sai key name (lip_care viết thành líp_care...)
    text = text.replace('líp_care', 'lip_care')
    text = text.replace('"líp_care"', '"lip_care"')
    
    # Thử parse
    try:
        return json.loads(text)
    except:
        # Thử tìm JSON object bằng regex
        match = re.search(r'\{.*\}|\[.*\]', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except:
                pass
        return None

def extract_json_from_text(text):
    """Trích xuất JSON từ văn bản với xử lý lỗi"""
    # Ưu tiên dùng clean_and_parse_json
    data = clean_and_parse_json(text)
    if data:
        return data
    
    # Fallback: tìm JSON block
    json_match = re.search(r'```json\n(.*?)\n```', text, re.DOTALL)
    if json_match:
        return clean_and_parse_json(json_match.group(1))
    
    return None

def get_product_link(product_name, brand):
    query = f"{brand} {product_name}".replace(" ", "%20")
    return f"https://shopee.vn/search?keyword={query}"

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
    "Giá rẻ (dưới 500k)": "dưới 500,000đ",
    "Tầm trung (500k - 1tr)": "từ 500,000đ đến 1,000,000đ",
    "Cao cấp (1tr - 2tr)": "từ 1,000,000đ đến 2,000,000đ"
}[price_range]

st.markdown("---")
st.subheader("📸 Tải ảnh màu son lên để phân tích")

uploaded = st.file_uploader("Chọn ảnh (jpg, png)", type=["jpg", "png", "jpeg"])

if uploaded:
    img = Image.open(uploaded)
    st.image(img, caption="Ảnh của bạn", width=250)
    r, g, b = get_dominant_color(img)
    st.success(f"🎨 Màu RGB: {r}, {g}, {b}")

    if st.button("🔍 Tư vấn chuyên gia"):
        with st.spinner("Chuyên gia AI đang phân tích..."):
            prompt = f"""
BẠN LÀ CHUYÊN GIA TRANG ĐIỂM VỚI 10 NĂM KINH NGHIỆM.
Hãy tư vấn một cách TẬN TÌNH, CHI TIẾT, dựa trên thông tin sau:

- Màu son RGB ({r},{g},{b})
- Tình trạng môi: {lip_type}
- Loại da: {skin_type}
- Danh mục: {category}
- Phân khúc giá: {price_prompt}

YÊU CẦU TƯ VẤN CHUYÊN SÂU:

1. PHÂN TÍCH MÀU SẮC:
   - Màu này thuộc tông nào?
   - Cảm nhận: ấm áp/lạnh, dịu dàng/cá tính?
   - Hợp với màu da nào?
   - Phong cách phù hợp?

2. TƯ VẤN SẢN PHẨM:
   - Gợi ý 3 sản phẩm {category} (tên, thương hiệu, mã màu nếu có, giá, lý do).

3. LỜI KHUYÊN:
   - Dưỡng môi cho {lip_type}
   - Chọn {category} cho da {skin_type}
   - Kết hợp makeup
   - Lưu ý đặc biệt

Trả lời dưới dạng JSON thuần, cấu trúc:
{{
  "color_analysis": {{
    "tone": "",
    "feeling": "",
    "skin_tone_suitable": "",
    "style": ""
  }},
  "products": [
    {{"name": "", "brand": "", "code": "", "price": 0, "reason": ""}}
  ],
  "advice": {{
    "lip_care": "",
    "skin_care": "",
    "makeup_tips": "",
    "note": ""
  }}
}}
- price chỉ ghi số.
- Nếu không biết mã màu, để "không rõ".
"""
            response_text = ask_groq(prompt)
            try:
                data = extract_json_from_text(response_text)
                if not data:
                    st.error("Chuyên gia AI trả về định dạng không đúng.")
                    st.code(response_text[:1000])
                else:
                    st.subheader("💄 Tư vấn chuyên gia:")
                    
                    if "color_analysis" in data:
                        ca = data["color_analysis"]
                        st.markdown(f"**🎨 Tông màu:** {ca.get('tone', 'không rõ')}")
                        st.markdown(f"**💭 Cảm nhận:** {ca.get('feeling', 'không rõ')}")
                        st.markdown(f"**👩 Màu da phù hợp:** {ca.get('skin_tone_suitable', 'không rõ')}")
                        st.markdown(f"**✨ Phong cách:** {ca.get('style', 'không rõ')}")
                    
                    if "advice" in data:
                        adv = data["advice"]
                        st.markdown("---")
                        st.markdown("### 📝 Lời khuyên chuyên sâu:")
                        st.markdown(f"**💋 Dưỡng môi:** {adv.get('lip_care', 'không rõ')}")
                        st.markdown(f"**🧴 Chọn son theo da:** {adv.get('skin_care', 'không rõ')}")
                        st.markdown(f"**🎨 Kết hợp makeup:** {adv.get('makeup_tips', 'không rõ')}")
                        st.markdown(f"**⚠️ Lưu ý:** {adv.get('note', 'không rõ')}")
                    
                    st.markdown("---")
                    st.subheader("🛒 Sản phẩm gợi ý (kèm link mua):")
                    products_list = data.get('products', [])
                    if products_list:
                        cols = st.columns(3)
                        for i, product in enumerate(products_list[:3]):
                            with cols[i % 3]:
                                st.markdown(f"**{product.get('name', 'N/A')}**")
                                st.markdown(f"🏷 {product.get('brand', 'N/A')} | 💰 {product.get('price', 0):,}đ")
                                if product.get('code') and product.get('code') != "không rõ":
                                    st.markdown(f"🔖 Mã màu: {product.get('code')}")
                                st.markdown(f"📝 {product.get('reason', '')}")
                                link = get_product_link(product.get('name', ''), product.get('brand', ''))
                                st.markdown(f"[🛍️ Mua ngay]({link})", unsafe_allow_html=True)
                    else:
                        st.warning("Không có sản phẩm gợi ý.")
            except Exception as e:
                st.error(f"Lỗi xử lý: {e}")
                st.code(response_text[:1500])
