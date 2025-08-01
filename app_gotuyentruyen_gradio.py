import gradio as gr
from recommend_movies_ml import recommend_similar_movies_csv
from tmdb_utils9 import search_similar_movies_tmdb

def combined_recommendation(movie_name):
    csv_result = recommend_similar_movies_csv(movie_name)
    tmdb_result = search_similar_movies_tmdb(movie_name)

    return csv_result, tmdb_result

with gr.Blocks(title="Gợi ý phim tương tự (ML + TMDB)") as interface:
    gr.Markdown("## 🎬 Gợi ý phim tương tự bằng Machine Learning và TMDB")
    with gr.Row():
        movie_input = gr.Textbox(label="Nhập tên phim bạn muốn tìm tương tự", placeholder="Inception")
    with gr.Row():
        btn = gr.Button("🔍 Gợi ý phim")
    with gr.Row():
        output_csv = gr.Textbox(label="📁 Gợi ý từ dữ liệu CSV + ML (TF-IDF)", lines=6)
        output_tmdb = gr.Textbox(label="🌐 Gợi ý từ TMDB API", lines=6)

    btn.click(fn=combined_recommendation, inputs=movie_input, outputs=[output_csv, output_tmdb])

if __name__ == "__main__":
    print("✅ Sẵn sàng gợi ý phim...")
    interface.launch(share=True, debug=True, inbrowser=True)

