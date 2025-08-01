import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv

load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

def search_similar_movies_tmdb(movie_name, top_n=5):
    if not TMDB_API_KEY:
        return "❌ TMDB_API_KEY chưa được cấu hình trong .env."

    session = requests.Session()
    retry_strategy = Retry(total=3, backoff_factor=1)
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)

    try:
        print(f"🔍 Gửi yêu cầu TMDB với key: {TMDB_API_KEY[:5]}...")  # Debug một phần key
        search_url = "https://api.themoviedb.org/3/search/movie"
        search_params = {"api_key": TMDB_API_KEY, "query": movie_name}
        search_resp = session.get(search_url, params=search_params, timeout=10)
        print(f"🔎 Status code search: {search_resp.status_code}")
        print(f"🔎 Response text: {search_resp.text[:200]}")  # Log một phần phản hồi

        if search_resp.status_code != 200:
            return f"❌ Lỗi TMDB search (status: {search_resp.status_code}) - {search_resp.text[:100]}"

        results = search_resp.json().get("results", [])
        if not results:
            return f"❌ Không tìm thấy phim tên '{movie_name}' trên TMDB."

        movie_id = results[0]["id"]
        print(f"🎯 ID phim: {movie_id}")

        similar_url = f"https://api.themoviedb.org/3/movie/{movie_id}/similar"
        sim_resp = session.get(similar_url, params={"api_key": TMDB_API_KEY}, timeout=10)
        print(f"🔎 Status code similar: {sim_resp.status_code}")
        print(f"🔎 Response text similar: {sim_resp.text[:200]}")

        if sim_resp.status_code != 200:
            return f"❌ Lỗi TMDB similar (status: {sim_resp.status_code}) - {sim_resp.text[:100]}"

        sim_movies = sim_resp.json().get("results", [])[:top_n]
        if not sim_movies:
            return f"❌ Không có phim tương tự với '{movie_name}' trên TMDB."

        return "\n".join([f"🎬 {m['title']} — ⭐ {round(m['vote_average'], 2)}/10" for m in sim_movies])
    except Exception as e:
        return f"❌ Lỗi TMDB gợi ý: {str(e)}"
    finally:
        session.close()