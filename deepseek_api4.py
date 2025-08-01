import os 
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "deepseek/deepseek-r1-0528:free"
BASE_URL = "https://openrouter.ai/api/v1"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://your-site.com",
    "X-Title": "MovieAnalyzer",
}

def ask_ai_analysis(movie_infos):
    try:
        if len(movie_infos) == 1:
            info = movie_infos[0]
            prompt = f"""
Hãy phân tích phim dưới đây ngắn gọn thôi nhé (bằng cả tiếng Việt và tiếng Anh, không quá 100 từ, càng ngắn gọn càng tốt nhưng đủ ý nhé):

🎬 Tên phim: {info['title']}
🎭 Thể loại: {info['genres']}
⭐ Điểm đánh giá: {info['vote_average']}
📊 Số lượt đánh giá: {info['vote_count']}
💰 Doanh thu: {info['revenue']}
🔮 Dự đoán điểm đánh giá (ước tính): {info['predicted_rating']}

Hãy nêu bật điểm mạnh/yếu, khả năng thành công thương mại và đánh giá tổng quan phim dưới đây ngắn gọn thôi nhé (song ngữ Việt - Anh, không quá 100 từ, càng ngắn gọn càng tốt nhưng đủ ý nhé).
"""
        else:
            info1 = movie_infos[0]
            info2 = movie_infos[1]
            prompt = f"""
Hãy phân tích 2 phim dưới đây ngắn gọn thôi nhé (song ngữ Việt - Anh, không quá 100 từ, càng ngắn gọn càng tốt nhưng đủ ý nhé):

Phim 1:
🎬 Tên phim: {info1['title']}
🎭 Thể loại: {info1['genres']}
⭐ Điểm đánh giá: {info1['vote_average']}
📊 Số lượt đánh giá: {info1['vote_count']}
💰 Doanh thu: {info1['revenue']}
🔮 Dự đoán điểm đánh giá: {info1['predicted_rating']}

Phim 2:
🎬 Tên phim: {info2['title']}
🎭 Thể loại: {info2['genres']}
⭐ Điểm đánh giá: {info2['vote_average']}
📊 Số lượt đánh giá: {info2['vote_count']}
💰 Doanh thu: {info2['revenue']}
🔮 Dự đoán điểm đánh giá: {info2['predicted_rating']}

Phân tích chất lượng, nội dung và tiềm năng thành công của 2 phim dưới đây ngắn gọn thôi nhé (song ngữ Việt - Anh, không quá 100 từ, càng ngắn gọn càng tốt nhưng đủ ý nhé).
"""

        body = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": "Bạn là chuyên gia phân tích phim, trả lời ngắn gọn khoảng 150 từ, càng ngắn gọn càng tốt nhưng đủ ý nhé, song ngữ Việt-Anh."},
                {"role": "user", "content": prompt},
            ],
        }

        response = requests.post(
            f"{BASE_URL}/chat/completions",
            headers=HEADERS,
            json=body,
            timeout=40  # Giới hạn timeout để tránh Gradio bị lỗi
        )
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ Lỗi từ AI: {str(e)}"
