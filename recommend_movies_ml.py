from pyspark.sql import SparkSession
from pyspark.sql.functions import concat_ws, col
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Tạo SparkSession với cấu hình bộ nhớ
spark = SparkSession.builder \
    .appName("MovieRecommendation") \
    .config("spark.driver.memory", "4g") \
    .config("spark.executor.memory", "2g") \
    .getOrCreate()

# Đọc dữ liệu
df = spark.read.csv("movies_dataset/TMDB_movie_dataset_v11.csv", header=True, inferSchema=True, multiLine=True, quote="\"", escape="\"")

# Tiền xử lý
df = df.select("title", "overview", "genres").dropna()
df = df.withColumn("content", concat_ws(" ", col("overview"), col("genres")))

# Lấy mẫu dữ liệu để tránh OOM
sample_df = df.limit(1000).toPandas()
titles = sample_df["title"].tolist()
contents = sample_df["content"].tolist()

# Vector hóa TF-IDF
vectorizer = TfidfVectorizer(stop_words="english")
tfidf_matrix = vectorizer.fit_transform(contents)

# Tính cosine similarity
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
title_to_index = {title.lower(): i for i, title in enumerate(titles)}  # lowercase cho khớp

def recommend_similar_movies_csv(title, top_n=5):
    print(f"🔍 Tìm phim: {title}")
    if not title:
        return "❌ Vui lòng nhập tên phim."

    title = title.lower()
    if title not in title_to_index:
        return f"❌ Không tìm thấy phim '{title}' trong CSV (1000 row mẫu)."

    try:
        idx = title_to_index[title]
        if idx >= len(cosine_sim) or idx < 0:
            return f"❌ Index {idx} vượt ngoài phạm vi ma trận cosine_sim."

        sim_scores = list(enumerate(cosine_sim[idx]))
        if len(sim_scores) < 2:
            return f"❌ Không đủ dữ liệu để gợi ý cho '{title}'."

        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:top_n+1]

        return "\n".join([f"🎬 {titles[i]} ({round(score * 100, 1)}%)" for i, score in sim_scores])
    except IndexError as e:
        return f"❌ Lỗi tính toán gợi ý: {str(e)}. Kiểm tra dữ liệu hoặc index ({idx}/{len(cosine_sim)})."
    except Exception as e:
        return f"❌ Lỗi không xác định: {str(e)}."

# Ghi chú: spark.stop() không cần gọi ở đây nếu bạn dùng liên tục trong Gradio
