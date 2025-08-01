from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date, year

# Khởi tạo SparkSession
spark = SparkSession.builder \
    .appName("Movies Analysis Step 2") \
    .getOrCreate()

# Đọc dữ liệu
df = spark.read.csv("movies_dataset/TMDB_movie_dataset_v11.csv", header=True, inferSchema=True)

# Chuyển release_date thành kiểu ngày
df = df.withColumn("release_date", to_date(col("release_date"), "yyyy-MM-dd"))

# Thêm cột năm phát hành
df = df.withColumn("release_year", year(col("release_date")))

# Đổi kiểu budget & revenue
df = df.withColumn("budget", col("budget").cast("long")) \
       .withColumn("revenue", col("revenue").cast("long"))

# Xóa những dòng thiếu dữ liệu quan trọng
df = df.dropna(subset=["title", "release_date", "budget", "revenue", "vote_average"])

# In schema + dữ liệu mẫu
df.printSchema()
df.select("title", "release_year", "budget", "revenue", "vote_average").show(5)
