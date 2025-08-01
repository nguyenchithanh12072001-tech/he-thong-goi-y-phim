import gradio as gr
from tmdb_utils8 import tmdb_functions
from deepseek_api5 import ask_ai_summary
from csv_stats import stats_functions
from pyspark.sql import SparkSession

# Khởi tạo SparkSession với bộ nhớ lớn hơn
spark = SparkSession.builder \
    .appName("CSVStats") \
    .config("spark.driver.memory", "8g") \
    .config("spark.executor.memory", "8g") \
    .getOrCreate()

# Mapping tiếng Việt -> tiếng Anh cho prompt AI
stat_mapping = {
    "10 thể loại phim phổ biến": "top 10 genres",
    "10 năm có nhiều phim phát hành nhất": "top 10 years",
    "10 quốc gia sản xuất nhiều phim nhất": "top 10 countries",
    "Doanh thu trung bình theo thể loại": "average revenue by genre",
    "Số lượng phim từ 2000 đến 2025": "movie count from 2000 to 2025",
    "Top 10 phim lợi nhuận cao nhất": "top 10 most profitable movies"
}

options = list(stat_mapping.keys())

def analyze(stat_choice):
    csv_result = "[CSV ERROR] Không thể truy xuất."
    tmdb_result = "[TMDB ERROR] Không thể truy xuất."
    ai_result = "[AI ERROR] Không thể phân tích."

    # CSV
    try:
        csv_func = stats_functions[stat_choice]
        csv_result = csv_func(spark)  # Truyền spark vào
    except Exception as e:
        csv_result = f"[CSV ERROR] {e}"

    # TMDB
    try:
        tmdb_df = tmdb_functions[stat_choice]()
        tmdb_result = tmdb_df.to_markdown()
    except Exception as e:
        tmdb_result = f"[TMDB ERROR] {e}"

    # AI
    try:
        prompt = f"Xuất ra bảng cho tui {stat_mapping[stat_choice]} với 2 cột: cột đầu là 'genre' hoặc 'year' hoặc 'country' tùy theo thống kê, cột thứ hai là 'avg_revenue_million' hoặc 'count' hoặc 'profit' tùy theo thống kê. Chỉ cần dữ liệu bảng, không cần code, giải thích, hoặc phân tích gì thêm."
        ai_result = ask_ai_summary(prompt)
    except Exception as e:
        ai_result = f"[AI ERROR] {e}"

    return csv_result, tmdb_result, ai_result

with gr.Blocks(title="📊 Thống kê phim từ CSV, TMDB và phân tích từ AI") as demo:
    gr.Markdown("## 📊 Thống kê phim từ CSV, TMDB và phân tích từ AI")

    stat_dropdown = gr.Dropdown(choices=options, label="Chọn loại thống kê", value=options[0])
    analyze_btn = gr.Button("📌 Phân tích ngay")

    with gr.Row():
        csv_out = gr.Textbox(label="📄 Kết quả từ CSV", lines=15)
        tmdb_out = gr.Textbox(label="🎬 Kết quả từ TMDB", lines=15)
        ai_out = gr.Textbox(label="🤖 Kết quả từ AI", lines=15)

    analyze_btn.click(fn=analyze, inputs=[stat_dropdown], outputs=[csv_out, tmdb_out, ai_out])

demo.launch(server_name="0.0.0.0", share=True)