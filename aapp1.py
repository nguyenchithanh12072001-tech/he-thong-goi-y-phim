import os
import re
import gradio as gr
from tmdb_utils3 import fetch_tmdb_info_only
import requests

# ==============================
# Config OpenRouter API
# ==============================
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY") or "sk-or-..."  # <-- cập nhật bằng .env
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MODEL_ID = "deepseek/deepseek-r1-0528:free"

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://your-site.com",
    "X-Title": "MovieAI",
}

def ask_openrouter_ai(title, genres, vote_average, vote_count, revenue):
    prompt = f"""
Dựa trên dữ liệu phim sau:
- Tên: {title}
- Thể loại: {genres}
- Điểm TMDB: {vote_average}/10
- Số lượt đánh giá: {vote_count}
- Doanh thu: {revenue}

Bạn hãy đánh giá lại điểm TMDB cho phim này, và đưa ra 3 lý do vì sao bạn chấm điểm như vậy. Mỗi lý do không quá 100 từ, càng ngắn gọn càng tốt.

Viết bằng cả tiếng Việt và tiếng Anh.
"""
    body = {
        "model": MODEL_ID,
        "messages": [
            {"role": "system", "content": "Bạn là chuyên gia phân tích phim song ngữ (Việt - Anh)."},
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

def clean_unicode(text):
    return re.sub(r'[\ud800-\udfff]', '', text)

def format_movie_info(movie_data, predicted_score):
    if not movie_data:
        return "❌ Không tìm thấy thông tin phim.", "", "", 0.0, 0, 0

    title = movie_data.get("title", "Không rõ")
    genres = ", ".join([g["name"] for g in movie_data.get("genres", [])]) or "Không rõ"
    vote = movie_data.get("vote_average", 0.0)
    vote_count = movie_data.get("vote_count", 0)
    revenue = movie_data.get("revenue", 0)

    info = f"""🎬 Tên phim: {title}
🎭 Thể loại: {genres}
⭐ Điểm TMDB: {vote:.2f}""" if vote > 0 else "⭐ Điểm TMDB: Chưa có"
    info += f"\n📊 Số lượt đánh giá: {vote_count}" if vote_count > 0 else "\n📊 Số lượt đánh giá: Chưa có"
    info += f"\n💰 Doanh thu: ${revenue:,}" if revenue > 0 else "\n💰 Doanh thu: Chưa có"

    info += f"\n🔮 Dự đoán điểm đánh giá: {predicted_score}/10" if predicted_score > 0 else "\n🔮 Dự đoán điểm đánh giá: Không thể dự đoán"

    return info, title, genres, vote, vote_count, revenue

def chat_with_ai(title):
    movie_data, prediction = fetch_tmdb_info_only(title)
    info, title, genres, vote, vote_count, revenue = format_movie_info(movie_data, prediction)
    ai_analysis = ask_openrouter_ai(title, genres, vote, vote_count, revenue)
    return clean_unicode(info), clean_unicode(ai_analysis)

# ==============================
# Gradio UI
# ==============================
with gr.Blocks(title="🎥 Movie AI Assistant") as demo:
    gr.Markdown("## 🎬 AI Dự đoán & Phân tích Phim Song ngữ 🇻🇳🇺🇸")
    with gr.Row():
        with gr.Column(scale=1):
            movie_input = gr.Textbox(label="🎯 Nhập tên phim")
            submit_btn = gr.Button("🚀 Dự đoán & Phân tích")
        with gr.Column(scale=2):
            output_info = gr.Textbox(label="📊 Thông tin & Dự đoán", lines=8)
            output_ai = gr.Textbox(label="🧠 Phân tích AI Song ngữ", lines=15)

    submit_btn.click(fn=chat_with_ai, inputs=movie_input, outputs=[output_info, output_ai])

# ✅ Mở cổng nội bộ & chia sẻ qua Gradio Live
demo.launch(server_name="0.0.0.0", share=True)