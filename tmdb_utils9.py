import os
import requests
from dotenv import load_dotenv

# Load biến môi trường từ file .env
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

# ✅ Hàm tìm phim theo tên từ TMDB
def search_movies_by_name_tmdb(name_query, top_n=3):
    try:
        if not TMDB_API_KEY:
            return "❌ TMDB_API_KEY không hợp lệ hoặc chưa được thiết lập."

        url = "https://api.themoviedb.org/3/search/movie"
        params = {
            "api_key": TMDB_API_KEY,
            "query": name_query,
            "include_adult": False,
            "language": "en-US"
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json().get("results", [])[:top_n]

        if not data:
            return f"❌ Không tìm thấy phim tên '{name_query}' trên TMDB."

        return "\n".join([
    f"🎬 {m['title']} ({m.get('release_date', 'N/A')[:4]}) — ⭐ {m['vote_average']}/10"
    for m in data
])

    except requests.exceptions.HTTPError as e:
        return f"❌ Lỗi TMDB khi tìm theo tên: {e}"
    except Exception as e:
        return f"❌ Lỗi không xác định khi tìm theo tên: {e}"


# ✅ Hàm tìm phim theo thể loại từ TMDB
def search_movies_by_genre_tmdb(genre_query, top_n=3):
    try:
        if not TMDB_API_KEY:
            return "❌ TMDB_API_KEY không hợp lệ hoặc chưa được thiết lập."

        # Lấy danh sách thể loại
        genre_list_url = "https://api.themoviedb.org/3/genre/movie/list"
        genre_list_resp = requests.get(genre_list_url, params={"api_key": TMDB_API_KEY, "language": "en-US"})
        genre_list_resp.raise_for_status()
        genre_map = {g["name"].lower(): g["id"] for g in genre_list_resp.json().get("genres", [])}

        genre_id = genre_map.get(genre_query.lower())
        if not genre_id:
            return f"❌ TMDB không tìm thấy thể loại '{genre_query}'."

        # Tìm phim thuộc thể loại
        discover_url = "https://api.themoviedb.org/3/discover/movie"
        params = {
            "api_key": TMDB_API_KEY,
            "with_genres": genre_id,
            "sort_by": "vote_average.desc",
            "vote_count.gte": 50,
            "language": "en-US"
        }
        r = requests.get(discover_url, params=params)
        r.raise_for_status()
        data = r.json().get("results", [])[:top_n]

        if not data:
            return f"❌ Không có phim nào thuộc thể loại '{genre_query}' trên TMDB."

        return "\n".join([f"🎬 {m['title']} — ⭐ {m['vote_average']}/10" for m in data])
    except requests.exceptions.HTTPError as e:
        return f"❌ Lỗi TMDB thể loại: {e}"
    except Exception as e:
        return f"❌ Lỗi không xác định khi tìm theo thể loại: {e}"
