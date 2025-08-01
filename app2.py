import gradio as gr
from tmdb_utils7 import get_best_movie_info
from deepseek_api4 import ask_ai_analysis


def analyze_movie(title):
    if not title:
        return "❌ Vui lòng nhập tên phim.", "", "", ""

    movie_infos = get_best_movie_info(title)
    if not movie_infos:
        return "❌ Không tìm thấy phim trong cả CSV và TMDB.", "", "", ""

    csv_info_str = "(Không có thông tin từ CSV)"
    tmdb_info_str = "(Không có thông tin từ TMDB)"

    for info in movie_infos:
        print("🔍 DEBUG INFO:", info)  # 👈 để kiểm tra nếu vẫn lỗi
        source = info.get("source", "").strip().upper()
        info_str = f"🎬 Tên phim: {info['title']}\n🎭 Thể loại: {info['genres']}\n⭐ Điểm đánh giá: {info['vote_average']}\n📊 Số lượt đánh giá: {info['vote_count']}\n💰 Doanh thu: {info['revenue']}"

        if source == "CSV":
            csv_info_str = info_str
        elif source == "TMDB":
            tmdb_info_str = info_str

    result = ask_ai_analysis(movie_infos)
    return result, csv_info_str, tmdb_info_str, title



with gr.Blocks(title="🎬 Phân tích phim bằng AI") as demo:
    gr.Markdown("## 🧠 Phân tích phim bằng AI (CSV + TMDB + DeepSeek)")
    with gr.Row():
        with gr.Column(scale=1):
            movie_input = gr.Textbox(label="🎬 Nhập tên phim để phân tích", placeholder="Nhập tên phim tại đây...")
            submit_btn = gr.Button("🚀 Phân tích phim")
        with gr.Column(scale=2):
            movie_title_display = gr.Textbox(label="🎞️ Tên phim bạn nhập", interactive=False)
            csv_output = gr.Textbox(label="📁 Thông tin phim từ CSV", lines=6, interactive=False)
            tmdb_output = gr.Textbox(label="🎞️ Thông tin phim từ TMDB", lines=6, interactive=False)
            ai_output = gr.Textbox(label="🤖 Phân tích từ AI", lines=20)

    submit_btn.click(fn=analyze_movie, inputs=[movie_input], outputs=[ai_output, csv_output, tmdb_output, movie_title_display])

demo.launch(server_name="0.0.0.0", share=True)
