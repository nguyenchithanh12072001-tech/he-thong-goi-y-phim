import gradio as gr
from csv_search import search_movies_by_name_csv, search_movies_by_genre_csv
from tmdb_utils9 import search_movies_by_name_tmdb, search_movies_by_genre_tmdb
from deepseek_api6 import ask_ai_for_similar_movies, ask_ai_for_genre_movies

# Hàm xử lý tìm kiếm
def unified_movie_search(query, mode):
    if not query:
        return "❌ Nhập tên hoặc thể loại phim", "", ""

    if mode == "Tên phim":
        csv_result = search_movies_by_name_csv(query)
        tmdb_result = search_movies_by_name_tmdb(query)
        ai_result = ask_ai_for_similar_movies(query)
    else:
        csv_result = search_movies_by_genre_csv(query)
        tmdb_result = search_movies_by_genre_tmdb(query)
        ai_result = ask_ai_for_genre_movies(query)

    return csv_result, tmdb_result, ai_result

# Tạo Gradio UI
with gr.Blocks(title="🎬 Gợi ý & Tìm kiếm phim nâng cao") as demo:
    gr.Markdown("## 🔍 Tìm kiếm phim theo **Tên** hoặc **Thể loại** từ CSV + TMDB + AI")

    with gr.Row():
        with gr.Column(scale=1):
            query_input = gr.Textbox(label="🎯 Nhập tên hoặc thể loại phim", placeholder="Ví dụ: Avatar hoặc Action")
            mode_radio = gr.Radio(["Tên phim", "Thể loại phim"], value="Tên phim", label="🛠️ Chế độ tìm kiếm")
            submit_btn = gr.Button("🚀 Tìm kiếm")

        with gr.Column(scale=2):
            csv_output = gr.Textbox(label="📁 Kết quả từ CSV", lines=8)
            tmdb_output = gr.Textbox(label="🌐 Kết quả từ TMDB", lines=8)
            ai_output = gr.Textbox(label="🤖 Gợi ý từ AI", lines=10)

    # Kết nối logic
    submit_btn.click(
        fn=unified_movie_search,
        inputs=[query_input, mode_radio],
        outputs=[csv_output, tmdb_output, ai_output]
    )

# Chạy server Gradio
if __name__ == "__main__":
    print("✅ Đang khởi chạy Gradio...")
    demo.launch(server_name="0.0.0.0", share=True, debug=True, inbrowser=False)
