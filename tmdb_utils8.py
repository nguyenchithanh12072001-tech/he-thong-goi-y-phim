import requests
from collections import Counter
import os
from dotenv import load_dotenv

load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"

# Lớp thay thế pandas DataFrame
class SimpleDataFrame:
    def __init__(self, data, columns):
        self.data = data
        self.columns = columns

    def to_markdown(self):
        header = " | ".join(self.columns)
        sep = " | ".join(["---"] * len(self.columns))
        rows = [" | ".join(str(row[col]) for col in self.columns) for row in self.data]
        return "\n".join([header, sep] + rows)

# 1. Thể loại phổ biến
def get_top_genres():
    res = requests.get(f"{BASE_URL}/genre/movie/list?api_key={TMDB_API_KEY}&language=en-US").json()
    genre_map = res.get("genres", [])
    genre_dict = {g["id"]: g["name"] for g in genre_map}

    counts = Counter()
    for page in range(1, 3):  # Giảm từ 6 xuống 2
        res = requests.get(f"{BASE_URL}/movie/popular?api_key={TMDB_API_KEY}&page={page}", timeout=10).json()
        for movie in res.get("results", []):
            for gid in movie.get("genre_ids", []):
                counts[genre_dict.get(gid, "Unknown")] += 1

    data = [{"genre": k, "count": v} for k, v in counts.most_common(10)]
    return SimpleDataFrame(data, ["genre", "count"])

# 2. Năm nhiều phim nhất
def get_top_years():
    counts = Counter()
    for page in range(1, 3):  # Giảm từ 6 xuống 2
        res = requests.get(f"{BASE_URL}/movie/popular?api_key={TMDB_API_KEY}&page={page}", timeout=10).json()
        for movie in res.get("results", []):
            date = movie.get("release_date", "")
            if date:
                year = date[:4]
                counts[year] += 1
    data = [{"year": y, "count": c} for y, c in counts.most_common(10)]
    return SimpleDataFrame(data, ["year", "count"])

# 3. Quốc gia sản xuất
def get_top_countries():
    counts = Counter()
    for page in range(1, 3):  # Giảm từ 6 xuống 2
        res = requests.get(f"{BASE_URL}/movie/popular?api_key={TMDB_API_KEY}&page={page}", timeout=10).json()
        for movie in res.get("results", []):
            detail = requests.get(f"{BASE_URL}/movie/{movie['id']}?api_key={TMDB_API_KEY}", timeout=10).json()
            for c in detail.get("production_countries", []):
                counts[c["name"]] += 1
    data = [{"country": k, "count": v} for k, v in counts.most_common(10)]
    return SimpleDataFrame(data, ["country", "count"])

# 4. Doanh thu trung bình theo thể loại
def get_avg_revenue_by_genre():
    genre_revenue = {}
    genre_count = {}
    for page in range(1, 3):  # Giảm từ 6 xuống 2
        res = requests.get(f"{BASE_URL}/movie/popular?api_key={TMDB_API_KEY}&page={page}", timeout=10).json()
        for movie in res.get("results", []):
            detail = requests.get(f"{BASE_URL}/movie/{movie['id']}?api_key={TMDB_API_KEY}", timeout=10).json()
            rev = detail.get("revenue", 0)
            for g in detail.get("genres", []):
                name = g["name"]
                genre_revenue[name] = genre_revenue.get(name, 0) + rev
                genre_count[name] = genre_count.get(name, 0) + 1
    avg = [{"genre": g, "avg_revenue_million": round(genre_revenue[g]/genre_count[g]/1_000_000, 2)} for g in genre_revenue if genre_count[g] > 0]
    avg.sort(key=lambda x: x["avg_revenue_million"], reverse=True)
    return SimpleDataFrame(avg[:10], ["genre", "avg_revenue_million"])

# 5. Phim từ 2000–2025
def get_movies_2000_2025():
    counts = Counter()
    for page in range(1, 3):  # Giảm từ 10 xuống 2
        res = requests.get(f"{BASE_URL}/movie/popular?api_key={TMDB_API_KEY}&page={page}", timeout=10).json()
        for movie in res.get("results", []):
            date = movie.get("release_date", "")
            if date:
                y = int(date[:4])
                if 2000 <= y <= 2025:
                    counts[y] += 1
    data = [{"year": y, "count": c} for y, c in sorted(counts.items())]
    return SimpleDataFrame(data, ["year", "count"])

# 6. Phim lợi nhuận cao nhất
def get_top_profits():
    movies = []
    for page in range(1, 3):  # Giảm từ 6 xuống 2
        res = requests.get(f"{BASE_URL}/movie/popular?api_key={TMDB_API_KEY}&page={page}", timeout=10).json()
        for movie in res.get("results", []):
            detail = requests.get(f"{BASE_URL}/movie/{movie['id']}?api_key={TMDB_API_KEY}", timeout=10).json()
            rev = detail.get("revenue", 0)
            bud = detail.get("budget", 0)
            profit = rev - bud
            if profit > 0:
                movies.append({"title": detail["title"], "profit": round(profit / 1_000_000, 2)})
    movies.sort(key=lambda x: x["profit"], reverse=True)
    return SimpleDataFrame(movies[:10], ["title", "profit"])

# Cho app3.py truy cập
tmdb_functions = {
    "10 thể loại phim phổ biến": get_top_genres,
    "10 năm có nhiều phim phát hành nhất": get_top_years,
    "10 quốc gia sản xuất nhiều phim nhất": get_top_countries,
    "Doanh thu trung bình theo thể loại": get_avg_revenue_by_genre,
    "Số lượng phim từ 2000 đến 2025": get_movies_2000_2025,
    "Top 10 phim lợi nhuận cao nhất": get_top_profits
}