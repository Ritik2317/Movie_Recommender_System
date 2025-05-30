import pickle
import streamlit as st
import requests
import pandas as pd
import time

similarity = pickle.load(open('similarity.pkl', 'rb'))
movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

# Retry logic added
def fetch_poster(movie_id, retries=3, delay=1):
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?{api_key=}'# Create your account of TMDB and generate your API key and paste it.
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('poster_path'):
                    return "https://image.tmdb.org/t/p/w500" + data['poster_path']
                else:
                    return "https://via.placeholder.com/500x750?text=No+Poster"
            else:
                print(f"Failed status code: {response.status_code}")
        except Exception as e:
            print(f"[Attempt {attempt+1}] Error fetching poster for {movie_id}: {e}")
            time.sleep(delay * (2 ** attempt))  # exponential backoff
    return "https://via.placeholder.com/500x750?text=Fetch+Error"

@st.cache_data
def get_movie_recommendations(movie):
    movie_index = movies[movies['original_title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_posters = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        title = movies.iloc[i[0]].original_title
        poster = fetch_poster(movie_id)

        recommended_movies.append(title)
        recommended_posters.append(poster)

    return recommended_movies, recommended_posters

# UI
st.title("🎬 Movie Recommender System")

selected_movie = st.selectbox(
    'Which movie have you just watched?',
    movies['original_title'].values
)

if st.button('Recommend'):
    recommendations, posters = get_movie_recommendations(selected_movie)
    cols = st.columns(5)
    for idx, col in enumerate(cols):
        with col:
            st.text(recommendations[idx])
            st.image(posters[idx])
