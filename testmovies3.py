from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col
from pyspark.sql.types import ArrayType, StringType
import json

# Tạo SparkSession
spark = SparkSession.builder.appName("Movie Genres Extraction").getOrCreate()

# Đọc dữ liệu
df = spark.read.csv("movies_dataset/TMDB_movie_dataset_v11.csv", header=True, inferSchema=True)

# Định nghĩa UDF để trích xuất tên thể loại từ chuỗi JSON
def extract_genres(genre_str):
    if genre_str:
        return [g.strip() for g in genre_str.split(",")]
    else:
        return []


extract_genres_udf = udf(extract_genres, ArrayType(StringType()))
df = df.withColumn("genre_names", extract_genres_udf(col("genres")))


# Hiển thị kết quả
df.select("title", "genres", "genre_names").show(10, truncate=False)

