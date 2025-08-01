import os
import csv
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lower
from dotenv import load_dotenv
from tmdb_utils1 import fetch_tmdb_info_only, predict_movie_rating

load_dotenv()

# Tạo SparkSession và đọc file CSV
spark = SparkSession.builder.appName("MovieAnalyzer").getOrCreate()
df = spark.read.option("header", True).option("inferSchema", True) \
    .csv("movies_dataset/TMDB_movie_dataset_v11.csv") \
    .dropna(subset=["title", "genres", "vote_average", "vote_count", "revenue"])


def format_currency(value):
    try:
        return f"${float(value):,.0f}"
    except:
        return "$0"


def get_best_movie_info(title):
    title_lower = title.strip().lower()

    # Lọc trong CSV
    filtered_csv = df.filter(
        (lower(col("title")) == title_lower) &
        (col("vote_count") > 100) &
        (col("revenue") > 0)
    ).orderBy(col("vote_average").desc(), col("vote_count").desc()).limit(1).collect()

    csv_movie = None
    if filtered_csv:
        row = filtered_csv[0]
        csv_movie = {
            "source": "CSV",
            "title": row['title'],
            "genres": row['genres'],
            "vote_average": row['vote_average'],
            "vote_count": row['vote_count'],
            "revenue": format_currency(row['revenue']),
            "predicted_rating": predict_movie_rating({
                "vote_count": float(row['vote_count']),
                "revenue": float(row['revenue']),
                "runtime": 90
            })
        }

    # Lấy từ TMDB
    tmdb_data = fetch_tmdb_info_only(title)
    tmdb_movie = None
    if tmdb_data and isinstance(tmdb_data, dict):
        vote_count = tmdb_data.get("vote_count", 0)
        revenue = tmdb_data.get("revenue", 0)
        runtime = tmdb_data.get("runtime", 90)
        title_tmdb = tmdb_data.get("title", "")
        if title_tmdb and vote_count > 0:
            tmdb_movie = {
                "source": "TMDB",  # ✅ PHẢI có dòng này để phân biệt nguồn
                "title": title_tmdb,
                "genres": ", ".join([g['name'] for g in tmdb_data.get("genres", [])]) or "Không rõ",
                "vote_average": tmdb_data.get("vote_average", 0),
                "vote_count": vote_count,
                "revenue": format_currency(revenue),
                "predicted_rating": predict_movie_rating({
                    "vote_count": float(vote_count),
                    "revenue": float(revenue),
                    "runtime": float(runtime)
                })
            }

    # So sánh và trả kết quả phù hợp
    results = []
    if csv_movie:
        results.append(csv_movie)
    if tmdb_movie:
        results.append(tmdb_movie)

    return results
