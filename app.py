from flask import Flask, render_template, request, jsonify
import requests
import random

app = Flask(__name__)

# TMDB API Configuration - REPLACE WITH YOUR ACTUAL API KEY
TMDB_API_KEY = '258d4f7582b4928874c54d84fecf53ec'
TMDB_BASE_URL = 'https://api.themoviedb.org/3'
TMDB_IMAGE_BASE_URL = 'https://image.tmdb.org/t/p'

# Beautiful Purple & Electric Color Scheme
BEAUTIFUL_COLORS = {
    'primary': '#8A2BE2',      # Electric Purple
    'secondary': '#4B0082',    # Indigo
    'accent': '#FF00FF',       # Magenta
    'background': '#0A0A1A',   # Dark Blue-Black
    'card_bg': '#1A1A2F',      # Dark Purple
    'text_light': '#FFFFFF',
    'text_muted': '#B8B8D1',
    'electric_blue': '#00FFFF', # Cyan
    'violet': '#9400D3',       # Dark Violet
    'neon_pink': '#FF1493'     # Deep Pink
}

def get_tmdb_data(endpoint, params=None):
    """Helper function to fetch data from TMDB API"""
    if params is None:
        params = {}
    params['api_key'] = TMDB_API_KEY
    params['language'] = 'en-US'
    
    try:
        response = requests.get(f"{TMDB_BASE_URL}/{endpoint}", params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching from TMDB: {e}")
        return None

def get_featured_movies():
    """Get featured movies for the main banner"""
    data = get_tmdb_data('movie/popular', {'page': 1})
    if data and 'results' in data:
        return random.sample(data['results'], min(5, len(data['results'])))
    return []

def get_popular_movies():
    """Get currently popular movies"""
    return get_tmdb_data('movie/popular')

def get_top_rated_movies():
    """Get top rated movies"""
    return get_tmdb_data('movie/top_rated')

def get_now_playing_movies():
    """Get now playing movies"""
    return get_tmdb_data('movie/now_playing')

def get_upcoming_movies():
    """Get upcoming movies"""
    return get_tmdb_data('movie/upcoming')

def get_movie_details(movie_id):
    """Get detailed information about a specific movie"""
    return get_tmdb_data(f'movie/{movie_id}')

def get_movie_credits(movie_id):
    """Get cast information for a movie"""
    return get_tmdb_data(f'movie/{movie_id}/credits')

def get_movie_trailer(movie_id):
    """Get trailer for a movie"""
    data = get_tmdb_data(f'movie/{movie_id}/videos')
    if data and 'results' in data:
        trailers = [video for video in data['results'] 
                   if video['site'] == 'YouTube' and video['type'] in ['Trailer', 'Teaser']]
        if trailers:
            return f"https://www.youtube.com/embed/{trailers[0]['key']}"
    return None

@app.route('/')
def home():
    """Main home page with beautiful layout"""
    # Get different categories of movies
    popular_data = get_popular_movies()
    top_rated_data = get_top_rated_movies()
    now_playing_data = get_now_playing_movies()
    upcoming_data = get_upcoming_movies()
    featured_movies = get_featured_movies()
    
    return render_template('home.html', 
                         popular_movies=popular_data.get('results', [])[:20] if popular_data else [],
                         top_rated_movies=top_rated_data.get('results', [])[:20] if top_rated_data else [],
                         now_playing_movies=now_playing_data.get('results', [])[:20] if now_playing_data else [],
                         upcoming_movies=upcoming_data.get('results', [])[:20] if upcoming_data else [],
                         featured_movies=featured_movies,
                         colors=BEAUTIFUL_COLORS,
                         image_base_url=f"{TMDB_IMAGE_BASE_URL}/w500")

@app.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    """Movie details page"""
    movie = get_movie_details(movie_id)
    if not movie:
        return "Movie not found", 404
    
    credits = get_movie_credits(movie_id)
    trailer_url = get_movie_trailer(movie_id)
    
    cast = credits.get('cast', [])[:10] if credits else []
    
    return render_template('movie_detail.html',
                         movie=movie,
                         cast=cast,
                         trailer_url=trailer_url,
                         colors=BEAUTIFUL_COLORS,
                         image_base_url=f"{TMDB_IMAGE_BASE_URL}/w500")

@app.route('/search')
def search():
    """Search for movies"""
    query = request.args.get('q', '')
    if query:
        search_data = get_tmdb_data('search/movie', {'query': query})
        movies = search_data.get('results', []) if search_data else []
    else:
        movies = []
    
    return render_template('search.html',
                         movies=movies,
                         query=query,
                         colors=BEAUTIFUL_COLORS,
                         image_base_url=f"{TMDB_IMAGE_BASE_URL}/w500")

if __name__ == '__main__':
    app.run(debug=True)