import requests
import os
from dotenv import load_dotenv
from datetime import datetime
from predict_rating_rf import predict_movie_rating_ml  # ✅ Dùng mô hình ML mới

load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"

def fetch_tmdb_info_only(title):
    try:
        print(f"\n🔍 Tìm kiếm phim: {title}")
        search_url = f"{TMDB_BASE_URL}/search/movie"
        search_params = {
            "api_key": TMDB_API_KEY,
            "query": title
        }
        search_resp = requests.get(search_url, params=search_params)
        print("\n🔎 DEBUG TMDB search_movie status:")
        print(search_resp.status_code)
        print("=" * 50)
        print("\n🔎 DEBUG TMDB search_movie raw text:")
        print(search_resp.text[:300])  # log giới hạn
        print("=" * 50)

        if search_resp.status_code != 200:
            return None, None

        search_data = search_resp.json()
        if not search_data.get("results"):
            return None, None

        movie_id = search_data["results"][0]["id"]
        print(f"\n🎯 ID phim đầu tiên: {movie_id}")

        # Lấy chi tiết phim
        details_url = f"{TMDB_BASE_URL}/movie/{movie_id}"
        details_params = {"api_key": TMDB_API_KEY}
        details_resp = requests.get(details_url, params=details_params)

        print("\n🔎 DEBUG TMDB get_movie_details status:")
        print(details_resp.status_code)
        print("=" * 50)
        print("\n🔎 DEBUG TMDB get_movie_details raw text:")
        print(details_resp.text[:300])
        print("=" * 50)

        if details_resp.status_code != 200:
            return None, None

        movie_data = details_resp.json()

        # ✅ Dự đoán bằng mô hình ML
        predicted_score = predict_movie_rating_ml(
            vote_count=movie_data.get("vote_count", 0),
            revenue=movie_data.get("revenue", 0),
            budget=movie_data.get("budget", 0),
            runtime=movie_data.get("runtime", 90) or 90
        )

        return movie_data, predicted_score

    except Exception as e:
        print(f"❌ Lỗi fetch TMDB: {e}")
        return None, None
