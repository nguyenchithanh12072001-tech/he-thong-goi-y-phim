import os
import requests
from dotenv import load_dotenv

# Load biến môi trường từ .env
load_dotenv()

# Cấu hình thông số API cho DeepSeek qua OpenRouter
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MODEL_ID = "deepseek/deepseek-r1-0528:free"

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://your-site.com",  # Có thể chỉnh sửa domain bạn
    "X-Title": "MovieAI",
}

def ask_ai_for_similar_movies(movie_name):
    prompt = f"""
Tui đang tìm kiếm phim có tên là "{movie_name}", ông đưa tui 3 phim có tên như vậy được đánh giá cao nhất đi, chỉ cần liệt kê tên phim và điểm, không cần phân tích gì cả.
"""
    body = {
        "model": MODEL_ID,
        "messages": [
            {"role": "system", "content": "Bạn là trợ lý AI chuyên gợi ý phim theo tên, trả lời ngắn gọn."},
            {"role": "user", "content": prompt},
        ],
    }

    try:
        response = requests.post(
            f"{OPENROUTER_BASE_URL}/chat/completions",
            headers=HEADERS,
            json=body,
            timeout=60
        )
        result = response.json()
        if "choices" in result:
            return result["choices"][0]["message"]["content"]
        else:
            return f"❌ Lỗi từ OpenRouter:\n{result}"
    except Exception as e:
        return f"❌ Lỗi khi gọi AI:\n{str(e)}"


def ask_ai_for_genre_movies(genre_name):
    prompt = f"""
Tui đang tìm kiếm phim thuộc thể loại "{genre_name}", ông đưa tui 3 phim nổi bật nhất thuộc thể loại đó được đánh giá cao, chỉ cần liệt kê tên phim và điểm, không cần phân tích gì cả.
"""
    body = {
        "model": MODEL_ID,
        "messages": [
            {"role": "system", "content": "Bạn là trợ lý AI chuyên gợi ý phim theo thể loại, trả lời ngắn gọn."},
            {"role": "user", "content": prompt},
        ],
    }

    try:
        response = requests.post(
            f"{OPENROUTER_BASE_URL}/chat/completions",
            headers=HEADERS,
            json=body,
            timeout=60
        )
        result = response.json()
        if "choices" in result:
            return result["choices"][0]["message"]["content"]
        else:
            return f"❌ Lỗi từ OpenRouter:\n{result}"
    except Exception as e:
        return f"❌ Lỗi khi gọi AI:\n{str(e)}"
