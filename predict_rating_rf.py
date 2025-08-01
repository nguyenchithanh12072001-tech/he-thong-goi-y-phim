from pyspark.sql import SparkSession, Row
from pyspark.ml.regression import RandomForestRegressionModel
from pyspark.ml.feature import VectorAssembler

# Khởi tạo SparkSession
spark = SparkSession.builder \
    .appName("PredictMovieRating") \
    .config("spark.driver.memory", "4g") \
    .getOrCreate()

# Load mô hình RandomForest đã lưu
model = RandomForestRegressionModel.load("rf_model_only")

# Assemble lại input features
assembler = VectorAssembler(inputCols=["vote_count", "revenue", "budget", "runtime"], outputCol="features")

def predict_movie_rating_ml(vote_count, revenue, budget, runtime):
    data = [Row(
        vote_count=float(vote_count),
        revenue=float(revenue),
        budget=float(budget),
        runtime=float(runtime)
    )]
    df = spark.createDataFrame(data)
    df = assembler.transform(df)
    prediction = model.transform(df).collect()[0].prediction
    return round(prediction, 2)
