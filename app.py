import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import cv2
import mediapipe as mp
from groq import Groq
import json
import re

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

st.title("💄 Makeup Mentor AI - Tu van my pham thong minh")

# Khởi tạo MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, min_detection_confidence=0.5)

# Chỉ số điểm mốc trên khuôn mặt (MediaPipe)
# Môi: 61-76 (viền môi ngoài), 78-82 (viền môi trong)
# Mắt trái: 33, 133, 157, 158, 159, 160, 161, 173
# Mắt phải: 362, 263, 387, 386, 385, 384, 398
# Má trái: vùng xung quanh điểm 234, 93, 132
# Má phải: vùng xung quanh điểm 454, 323, 361

LIP_INDICES = list(range(61, 69)) + list(range(70, 76)) + [78, 80, 82, 84, 86, 88, 90, 92]
LEFT_EYE_INDICES = [33, 133, 157, 158, 159, 160, 161, 173]
RIGHT_EYE_INDICES = [362, 263, 387, 386, 385, 384, 398]
LEFT_CHEEK_INDICES = [234, 93, 132, 127, 205]
RIGHT_CHEEK_INDICES = [454, 323, 361, 356, 435]

def get_roi_region(image, landmarks, indices, margin=20):
    """Trích xuất vùng ảnh dựa trên các điểm mốc"""
    h, w = image.shape[:2]
    points = []
    for idx in indices:
        if idx < len(landmarks):
            x = int(landmarks[idx].x * w)
            y = int(landmarks[idx].y * h)
            points.append([x, y])
    
    if len(points) < 3:
        return None
    
    points = np.array(points, dtype=np.int32)
    x_min = max(0, points[:, 0].min() - margin)
    x_max = min(w, points[:, 0].max() + margin)
    y_min = max(0, points[:, 1].min() - margin)
    y_max = min(h, points[:, 1].max() + margin)
    
    return image[y_min:y_max, x_min:x_max]

def get_dominant_color_from_roi(roi):
    """Lấy màu chủ đạo từ vùng ảnh"""
    if roi is None or roi.size == 0:
        return None
    # Chuyển đổi sang RGB để xử lý
    if len(roi.shape) == 3:
        roi_rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
    else:
        roi_rgb = roi
    # Resize để tính nhanh
    small = cv2.resize(roi_rgb, (50, 50))
    avg = small.mean(axis=0).mean(axis=0).astype(int)
    return avg[0], avg[1], avg[2]

def analyze_face(image):
    """Phân tích khuôn mặt: phát hiện, xác định vùng và màu sắc"""
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(image_rgb)
    
    if not results.multi_face_landmarks:
        return None
    
    landmarks = results.multi_face_landmarks[0].landmark
    
    # Trích xuất từng vùng
    lip_roi = get_roi_region(image, landmarks, LIP_INDICES, margin=10)
    left_eye_roi = get_roi_region(image, landmarks, LEFT_EYE_INDICES, margin=15)
    right_eye_roi = get_roi_region(image, landmarks, RIGHT_EYE_INDICES, margin=15)
    left_cheek_roi = get_roi_region(image, landmarks, LEFT_CHEEK_INDICES, margin=25)
    right_cheek_roi = get_roi_region(image, landmarks, RIGHT_CHEEK_INDICES, margin=25)
    
    # Lấy màu chủ đạo từng vùng
    lip_color = get_dominant_color_from_roi(lip_roi)
    left_eye_color = get_dominant_color_from_roi(left_eye_roi)
    right_eye_color = get_dominant_color_from_roi(right_eye_roi)
    left_cheek_color = get_dominant_color_from_roi(left_cheek_roi)
    right_cheek_color = get_dominant_color_from_roi(right_cheek_roi)
    
    # Trung bình màu mắt (trái + phải)
    eye_color = None
    if left_eye_color and right_eye_color:
        eye_color = (
            (left_eye_color[0] + right_eye_color[0]) // 2,
            (left_eye_color[1] + right_eye_color[1]) // 2,
            (left_eye_color[2] + right_eye_color[2]) // 2
        )
    elif left_eye_color:
        eye_color = left_eye_color
    elif right_eye_color:
        eye_color = right_eye_color
    
    # Trung bình màu má
    cheek_color = None
    if left_cheek_color and right_cheek_color:
        cheek_color = (
            (left_cheek_color[0] + right_cheek_color[0]) // 2,
            (left_cheek_color[1] + right_cheek_color[1]) // 2,
            (left_cheek_color[2] + right_cheek_color[2]) // 2
        )
    elif left_cheek_color:
        cheek_color = left_cheek_color
    elif right_cheek_color:
        cheek_color = right_cheek_color
    
    return {
        "lip_color": lip_color,
        "eye_color": eye_color,
        "cheek_color": cheek_color
    }

# Khởi tạo Groq client
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=GROQ_API_KEY)

def ask_groq(prompt):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,
            max_tokens=1500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Lỗi: {e}"

def get_product_link(product_name, brand):
    query = f"{brand} {product_name}".replace(" ", "%20")
    return f"https://shopee.vn/search?keyword={query}"

# ==================== GIAO DIỆN CHÍNH ====================
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
st.subheader("📸 Tải ảnh chân dung lên (chụp rõ mặt)")

uploaded = st.file_uploader("Chọn ảnh (jpg, png)", type=["jpg", "png", "jpeg"])

if uploaded:
    img = Image.open(uploaded)
    st.image(img, caption="Ảnh của bạn", width=300)
    
    # Chuyển ảnh sang OpenCV format
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    
    # Phân tích khuôn mặt
    with st.spinner("Đang phân tích khuôn mặt và màu sắc..."):
        face_analysis = analyze_face(img_cv)
    
    if face_analysis is None:
        st.error("❌ Không phát hiện khuôn mặt trong ảnh. Vui lòng chọn ảnh chụm mặt rõ ràng!")
    else:
        # Hiển thị kết quả phân tích màu
        st.success("✅ Đã phát hiện khuôn mặt và phân tích màu sắc!")
        
        col_a, col_b, col_c = st.columns(3)
        if face_analysis.get("lip_color"):
            r,g,b = face_analysis["lip_color"]
            col_a.markdown(f"**💋 Màu môi:** RGB({r},{g},{b})")
            col_a.markdown(f'<div style="width:100%; height:30px; background-color:rgb({r},{g},{b}); border-radius:10px;"></div>', unsafe_allow_html=True)
        if face_analysis.get("cheek_color"):
            r,g,b = face_analysis["cheek_color"]
            col_b.markdown(f"**💗 Màu má:** RGB({r},{g},{b})")
            col_b.markdown(f'<div style="width:100%; height:30px; background-color:rgb({r},{g},{b}); border-radius:10px;"></div>', unsafe_allow_html=True)
        if face_analysis.get("eye_color"):
            r,g,b = face_analysis["eye_color"]
            col_c.markdown(f"**👁️ Màu mắt:** RGB({r},{g},{b})")
            col_c.markdown(f'<div style="width:100%; height:30px; background-color:rgb({r},{g},{b}); border-radius:10px;"></div>', unsafe_allow_html=True)
        
        if st.button("🔍 Tư vấn AI"):
            with st.spinner("AI đang phân tích và tư vấn..."):
                # Xây dựng prompt dựa trên phân tích
                prompt = f"""
Bạn là chuyên gia trang điểm. Dựa trên phân tích khuôn mặt, hãy tư vấn:

Loại da: {skin_type}
Tình trạng môi: {lip_type}
Phân khúc giá: {price_prompt}
"""

                if face_analysis.get("lip_color"):
                    r,g,b = face_analysis["lip_color"]
                    prompt += f"\nMàu môi RGB({r},{g},{b}) - màu này gần với tông màu gì?"

                if face_analysis.get("cheek_color"):
                    r,g,b = face_analysis["cheek_color"]
                    prompt += f"\nMàu má RGB({r},{g},{b}) - tông màu da tự nhiên?"

                if face_analysis.get("eye_color"):
                    r,g,b = face_analysis["eye_color"]
                    prompt += f"\nMàu mắt RGB({r},{g},{b}) - gợi ý màu mắt phù hợp."

                prompt += f"""
Danh mục: {category}.

QUAN TRỌNG:
- Gợi ý 3 sản phẩm {category} phù hợp với màu môi, màu da, màu mắt.
- Mỗi sản phẩm có: tên, thương hiệu, mã màu (nếu có), giá, lý do.
- Trả lời bằng tiếng Việt, chi tiết.
- Định dạng JSON thuần:
{{
  "color_tone": "tông màu chính",
  "advice": "lời khuyên chi tiết",
  "products": [
    {{"name": "...", "brand": "...", "code": "...", "price": 0, "reason": "..."}},
    {{...}},
    {{...}}
  ]
}}
"""
                response_text = ask_groq(prompt)
                
                try:
                    # Trích xuất JSON từ response
                    json_match = re.search(r'```json\n(.*?)\n```', response_text, re.DOTALL)
                    if json_match:
                        data = json.loads(json_match.group(1))
                    else:
                        data = json.loads(response_text)
                    
                    st.subheader("💄 Tư vấn AI:")
                    st.write(f"**Tông màu:** {data.get('color_tone', 'không rõ')}")
                    st.write(data.get('advice', ''))
                    
                    st.subheader("🛒 Sản phẩm gợi ý:")
                    cols = st.columns(3)
                    for i, product in enumerate(data.get('products', [])[:3]):
                        with cols[i % 3]:
                            st.markdown(f"**{product.get('name', 'N/A')}**")
                            st.markdown(f"🏷 {product.get('brand', 'N/A')} | 💰 {product.get('price', 0):,}đ")
                            if product.get('code') and product.get('code') != "không rõ":
                                st.markdown(f"🔖 Mã màu: {product.get('code')}")
                            st.markdown(f"📝 {product.get('reason', '')}")
                            link = get_product_link(product.get('name', ''), product.get('brand', ''))
                            st.markdown(f"[🛍️ Mua ngay]({link})", unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Lỗi xử lý: {e}")
                    st.code(response_text)
