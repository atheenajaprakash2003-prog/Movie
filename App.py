import streamlit as st
import pickle
import pandas as pd
import requests

# ---------------- PAGE CONFIG ---------------- #

st.set_page_config(
    page_title="Movie Recommender",
    layout="wide"
)

# ---------------- CUSTOM CSS ---------------- #

st.html("""
<style>

body {
    background-color: #0E1117;
}

.main {
    background-color: #0E1117;
}

.movie-card {
    background-color: #1c1f26;
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 20px;
    transition: 0.3s;
    text-align: center;
}

.movie-card:hover {
    transform: scale(1.03);
    box-shadow: 0px 0px 15px rgba(255,255,255,0.3);
}

.title {
    color: white;
    font-size: 20px;
    font-weight: bold;
}

.rating {
    color: gold;
    font-size: 16px;
}

.genre {
    color: cyan;
    font-size: 14px;
}

.overview {
    color: #d3d3d3;
    font-size: 13px;
}

a {
    text-decoration: none;
    color: #00d4ff;
    font-weight: bold;
}

</style>
""")

# ---------------- LOAD FILES ---------------- #

movies = pickle.load(open('movie_dict.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

# ---------------- TMDB API ---------------- #

API_KEY = "56438adede3ec211246179c85a34a184"

# ---------------- FETCH MOVIE DETAILS ---------------- #

def fetch_movie_details(movie_id):

    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"

    data = requests.get(url)

    data = data.json()

    poster_path = data.get('poster_path', '')

    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path

    return {
        "poster": full_path,
        "rating": data.get('vote_average', 'N/A'),
        "genres": ", ".join(
            [genre['name'] for genre in data.get('genres', [])]
        ),
        "overview": data.get('overview', 'No overview available')
    }

# ---------------- RECOMMEND FUNCTION ---------------- #

def recommend(movie):

    movie_index = movies[movies['title'] == movie].index[0]

    distances = similarity[movie_index]

    movie_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:11]

    recommended_movies = []

    for i in movie_list:

        movie_data = movies.iloc[i[0]]

        movie_id = movie_data["id"]

        details = fetch_movie_details(movie_id)

        recommended_movies.append({
            "title": movie_data.title,
            "poster": details['poster'],
            "rating": details['rating'],
            "genres": details['genres'],
            "overview": details['overview']
        })

    return recommended_movies

# ---------------- SIDEBAR ---------------- #

st.sidebar.title("🎬 Movie Filters")

search_movie = st.sidebar.text_input(
    "🔍 Search Movie"
)

# ---------------- FILTER MOVIES ---------------- #

filtered_movies = movies

if search_movie:

    filtered_movies = filtered_movies[
        filtered_movies['title'].str.contains(
            search_movie,
            case=False
        )
    ]

# ---------------- MAIN TITLE ---------------- #

st.title("🎬 Movie Recommender System")

st.write(
    "Content-Based Recommendation using Machine Learning"
)

# ---------------- SELECT MOVIE ---------------- #

selected_movie = st.selectbox(
    "Choose a movie",
    filtered_movies['title'].values
)

# ---------------- RECOMMEND BUTTON ---------------- #

if st.button("Recommend"):

    recommendations = recommend(selected_movie)

    st.subheader("Recommended Movies")

    cols = st.columns(5)

    for idx, movie in enumerate(recommendations[:10]):

        with cols[idx % 5]:

            st.html(
                f"""
                <div class="movie-card">

                    <img src="{movie['poster']}" width="100%">

                    <br><br>

                    <div class="title">
                        {movie['title']}
                    </div>

                    <br>

                    <div class="rating">
                        ⭐ Rating: {movie['rating']}
                    </div>

                    <br>

                    <div class="genre">
                        🎭 {movie['genres']}
                    </div>

                    <br>

                    <div class="overview">
                        {movie['overview'][:120]}...
                    </div>

                    <br>

                    <a href="https://www.youtube.com/results?search_query={movie['title']} trailer" target="_blank">
                        ▶️ Watch Trailer
                    </a>

                </div>
                """,
            )