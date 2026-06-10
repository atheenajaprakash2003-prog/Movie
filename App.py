import streamlit as st
import pickle
import pandas as pd
import requests

# ─────────────────────────────────────────
#  PAGE CONFIG  (must be first Streamlit call)
# ─────────────────────────────────────────
st.set_page_config(
    page_title="The Hollywood Archive",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────
#  SESSION STATE  –  controls landing vs app
# ─────────────────────────────────────────
if "started" not in st.session_state:
    st.session_state.started = False

# ─────────────────────────────────────────
#  SHARED CSS  (fonts + resets)
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Outfit:wght@300;400;500;600;700&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background-color: #0A0A0F !important;
    color: white !important;
}
[data-testid="stHeader"]  { display: none !important; }
[data-testid="stSidebar"] { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }
.block-container {
    padding-top: 0 !important;
    padding-bottom: 0 !important;
    max-width: 100% !important;
}
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #0A0A0F; }
::-webkit-scrollbar-thumb { background: #FF2D2D; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
#  DATA LOADING  (cached)
# ─────────────────────────────────────────
@st.cache_resource
def load_data():
    movies = pickle.load(open('movie_dict.pkl', 'rb'))
    similarity = pickle.load(open('similarity.pkl', 'rb'))
    if isinstance(movies, dict):
        movies = pd.DataFrame(movies)
    return movies, similarity

movies, similarity = load_data()

# ─────────────────────────────────────────
#  TMDB API
# ─────────────────────────────────────────
API_KEY = "56438adede3ec211246179c85a34a184"

@st.cache_data(show_spinner=False)
def fetch_movie_details(movie_id):
    try:
        # Primary: fetch by TMDB id
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
        r = requests.get(url, timeout=8)
        data = r.json()

        poster_path = data.get('poster_path') or ''

        # Fallback 1: try /images endpoint if no poster_path returned
        if not poster_path:
            img_url = f"https://api.themoviedb.org/3/movie/{movie_id}/images?api_key={API_KEY}"
            img_r = requests.get(img_url, timeout=8)
            img_data = img_r.json()
            posters = img_data.get('posters', [])
            if posters:
                poster_path = posters[0].get('file_path', '')

        # Fallback 2: search by title if still no poster
        if not poster_path:
            title = data.get('title') or data.get('original_title', '')
            if title:
                search_url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={requests.utils.quote(title)}&language=en-US"
                s_r = requests.get(search_url, timeout=8)
                s_data = s_r.json()
                results = s_data.get('results', [])
                for res in results:
                    if res.get('poster_path'):
                        poster_path = res['poster_path']
                        break

        poster = ("https://image.tmdb.org/t/p/w500" + poster_path) if poster_path else ""
        genres = ", ".join([g['name'] for g in data.get('genres', [])])
        rating = data.get('vote_average', 'N/A')
        overview = data.get('overview', 'No overview available.')
        return {"poster": poster, "rating": rating, "genres": genres, "overview": overview}
    except Exception:
        return {"poster": "", "rating": "N/A", "genres": "Unknown", "overview": "Details unavailable."}

def fetch_poster_by_title(title):
    """Last-resort: search TMDB by title and grab first poster."""
    try:
        search_url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={requests.utils.quote(title)}&language=en-US"
        res = requests.get(search_url, timeout=8).json().get('results', [])
        for r in res:
            if r.get('poster_path'):
                return "https://image.tmdb.org/t/p/w500" + r['poster_path']
    except Exception:
        pass
    return ""

def recommend(movie_title):
    idx = movies[movies['title'] == movie_title].index[0]
    distances = similarity[idx]
    ranked = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:11]
    results = []
    for i, score in ranked:
        row = movies.iloc[i]
        details = fetch_movie_details(int(row['id']))
        # If still no poster after all TMDB id-based attempts, search by title
        if not details['poster']:
            details['poster'] = fetch_poster_by_title(str(row['title']))
        results.append({
            "title":      row['title'],
            "poster":     details['poster'],
            "rating":     details['rating'],
            "genres":     details['genres'],
            "overview":   details['overview'],
            "similarity": round(float(score) * 100, 1)
        })
    return results

FALLBACK = "https://placehold.co/300x450/161B22/FF2D2D?text=No+Poster"


# ══════════════════════════════════════════════════════════════════════════
#  LANDING PAGE
# ══════════════════════════════════════════════════════════════════════════
if not st.session_state.started:

    st.markdown("""
    <style>
    .landing-wrap {
        min-height: 100vh;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: 60px 24px 80px;
        background:
            radial-gradient(ellipse 90% 55% at 50% 0%,   rgba(255,45,45,0.14) 0%, transparent 65%),
            radial-gradient(ellipse 60% 40% at 80% 85%,  rgba(0,200,255,0.06) 0%, transparent 60%),
            #0A0A0F;
    }
    .screen-frame {
        width: min(660px, 94vw);
        background: #0E0E16;
        border: 1px solid rgba(255,255,255,0.09);
        border-radius: 20px;
        overflow: hidden;
        box-shadow:
            0 0 0 1px rgba(255,45,45,0.12),
            0 40px 100px rgba(0,0,0,0.65),
            0 0 80px rgba(255,45,45,0.07);
    }
    .screen-topbar {
        display: flex; align-items: center; gap: 7px;
        padding: 11px 18px;
        background: rgba(255,255,255,0.03);
        border-bottom: 1px solid rgba(255,255,255,0.06);
    }
    .dot { width:11px; height:11px; border-radius:50%; }
    .dot-r{background:#FF5F57;} .dot-y{background:#FEBC2E;} .dot-g{background:#28C840;}
    .topbar-url {
        font-family:'Outfit',sans-serif; font-size:12px;
        color:rgba(255,255,255,0.25); margin-left:8px;
        letter-spacing:1.2px;
    }
    .screen-inner { padding: 52px 44px 44px; }
    .landing-eyebrow {
        display: inline-flex; align-items: center; gap: 8px;
        background: rgba(255,45,45,0.1);
        border: 1px solid rgba(255,45,45,0.22);
        border-radius: 100px; padding: 5px 16px; margin-bottom: 26px;
        font-family:'Outfit',sans-serif; font-size:11px; font-weight:600;
        letter-spacing:2.5px; text-transform:uppercase; color:#FF2D2D;
    }
    .e-dot { width:6px;height:6px;border-radius:50%;background:#FF2D2D; animation:blink 1.8s infinite; }
    @keyframes blink{0%,100%{opacity:1;}50%{opacity:0.25;}}
    .landing-title {
        font-family:'Bebas Neue',sans-serif;
        font-size: clamp(44px, 9vw, 82px);
        line-height:0.88; letter-spacing:5px; color:white; margin-bottom:8px;
        text-shadow: 0 0 60px rgba(255,45,45,0.25);
    }
    .landing-title .red { color:#FF2D2D; }
    .landing-tagline {
        font-family:'DM Sans',sans-serif; font-size:15px; font-weight:300;
        color:rgba(255,255,255,0.42); line-height:1.7; margin-bottom:36px;
    }
    .landing-tagline b { color:rgba(0,229,255,0.8); font-weight:500; }
    .feat-list {
        display:flex; flex-wrap:wrap; gap:9px; justify-content:center; margin-bottom:38px;
    }
    .feat-pill {
        display:flex; align-items:center; gap:7px;
        background:rgba(255,255,255,0.04);
        border:1px solid rgba(255,255,255,0.08);
        border-radius:100px; padding:7px 14px;
        font-family:'Outfit',sans-serif; font-size:12px;
        color:rgba(255,255,255,0.58); white-space:nowrap;
    }
    .screen-footer {
        padding:13px 44px;
        border-top:1px solid rgba(255,255,255,0.06);
        display:flex; align-items:center; justify-content:space-between;
        background:rgba(0,0,0,0.2);
    }
    .sf-left  { font-family:'Outfit',sans-serif; font-size:11px; color:rgba(255,255,255,0.2); letter-spacing:1px; }
    .sf-right { font-family:'Outfit',sans-serif; font-size:11px; color:rgba(0,229,255,0.45);  letter-spacing:1px; }

    /* landing button */
    [data-testid="stButton"] > button {
        background: linear-gradient(135deg, #FF2D2D 0%, #AA0000 100%) !important;
        color: white !important; border: none !important;
        border-radius: 10px !important; padding: 14px 56px !important;
        font-family: 'Outfit', sans-serif !important;
        font-size: 15px !important; font-weight: 700 !important;
        letter-spacing: 2px !important; text-transform: uppercase !important;
        box-shadow: 0 8px 36px rgba(255,45,45,0.38) !important;
        transition: all 0.25s !important;
    }
    [data-testid="stButton"] > button:hover {
        transform: translateY(-3px) scale(1.03) !important;
        box-shadow: 0 18px 56px rgba(255,45,45,0.58) !important;
    }
    </style>

    <div class="landing-wrap">
      <div class="screen-frame">
        <div class="screen-topbar">
          <div class="dot dot-r"></div>
          <div class="dot dot-y"></div>
          <div class="dot dot-g"></div>
          <span class="topbar-url">thehollywoodarchive.app</span>
        </div>
        <div class="screen-inner">
          <div class="landing-eyebrow">
            <span class="e-dot"></span>
            Content-Based Movie Recommender
          </div>
          <div class="landing-title">THE<br><span class="red">HOLLYWOOD</span><br>ARCHIVE</div>
          <div class="landing-tagline">
            Discover films you will love through <b>AI similarity matching</b><br>
            powered by machine learning and the TMDB database
          </div>
          <div class="feat-list">
            <div class="feat-pill">🎯 Personalized Picks</div>
            <div class="feat-pill">🤖 ML Similarity Engine</div>
            <div class="feat-pill">⭐ Live TMDB Ratings</div>
            <div class="feat-pill">▶️ Trailer Links</div>
            <div class="feat-pill">🎭 Genre Intelligence</div>
            <div class="feat-pill">🔍 Smart Search</div>
          </div>
        </div>
        <div class="screen-footer">
          <span class="sf-left">Hollywood Archive © 2026</span>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    _, mid, _ = st.columns([2, 1, 2])
    with mid:
        if st.button("▶  Enter The Archive", use_container_width=True):
            st.session_state.started = True
            st.rerun()

    st.stop()


# ══════════════════════════════════════════════════════════════════════════
#  MAIN APP
# ══════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 80% 50% at 50% -5%, rgba(255,45,45,0.10) 0%, transparent 60%),
        #0A0A0F !important;
}

/* NAVBAR */
.navbar {
    position: sticky; top:0; z-index:1000;
    display:flex; align-items:center; justify-content:space-between;
    padding: 0 52px; height: 64px;
    background: rgba(10,10,15,0.88);
    backdrop-filter: blur(22px);
    border-bottom: 1px solid rgba(255,255,255,0.07);
}
.nav-logo {
    font-family:'Bebas Neue',sans-serif;
    font-size:21px; letter-spacing:3px; color:white;
}
.nav-logo span { color:#FF2D2D; }
.nav-links { display:flex; gap:26px; list-style:none; margin:0; padding:0; }
.nav-links li {
    font-family:'Outfit',sans-serif; font-size:12px; font-weight:500;
    letter-spacing:1.5px; text-transform:uppercase;
    color:rgba(255,255,255,0.38); cursor:default;
}
.nav-links li.active { color:white; }
.nav-pill {
    background: rgba(255,45,45,0.12);
    border: 1px solid rgba(255,45,45,0.28);
    border-radius:100px; padding:5px 16px;
    font-family:'Outfit',sans-serif; font-size:11px; font-weight:600;
    letter-spacing:1.5px; text-transform:uppercase; color:#FF2D2D;
}

/* HERO */
.hero {
    padding: 68px 52px 52px;
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
}
.hero-eyebrow {
    display:inline-flex; align-items:center; gap:8px;
    background:rgba(255,45,45,0.08);
    border:1px solid rgba(255,45,45,0.2);
    border-radius:100px; padding:5px 16px; margin-bottom:20px;
    font-family:'Outfit',sans-serif; font-size:11px; font-weight:600;
    letter-spacing:2.5px; text-transform:uppercase; color:#FF2D2D;
}
.h-dot { width:6px;height:6px;border-radius:50%;background:#FF2D2D; animation:blink 1.8s infinite; }
@keyframes blink{0%,100%{opacity:1;}50%{opacity:0.25;}}
.hero-title {
    font-family:'Bebas Neue',sans-serif;
    font-size: clamp(68px,10vw,130px);
    line-height:0.88; letter-spacing:6px; color:white; margin-bottom:10px;
    text-align: center;
    text-shadow: 0 0 100px rgba(255,45,45,0.45), 0 0 200px rgba(255,45,45,0.15);
}
.hero-title .red { color:#FF2D2D; }
.hero-sub {
    font-family:'DM Sans',sans-serif; font-size:16px; font-weight:300;
    color:rgba(255,255,255,0.42); max-width:530px; line-height:1.65;
    text-align: center;
}
.hero-sub b { color:rgba(0,229,255,0.78); font-weight:500; }

/* SECTION DIVIDER */
.sdiv {
    display:flex; align-items:center; gap:18px;
    padding:0 52px; margin-bottom:34px;
}
.sdiv-line { flex:1; height:1px; background:linear-gradient(90deg,transparent,rgba(255,255,255,0.08),transparent); }
.sdiv-lbl {
    font-family:'Outfit',sans-serif; font-size:11px; font-weight:600;
    letter-spacing:3px; text-transform:uppercase; color:rgba(255,255,255,0.2);
}

/* RESULTS HEADER */
.res-hdr { padding:0 52px 30px; }
.res-title {
    font-family:'Bebas Neue',sans-serif;
    font-size:44px; letter-spacing:3px; color:white; margin-bottom:4px;
}
.res-title span { color:#FF2D2D; }
.res-sub { font-family:'DM Sans',sans-serif; font-size:13px; color:rgba(255,255,255,0.3); }

/* MOVIE CARD */
.movie-card {
    background: rgba(22,27,34,0.82);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius:16px; overflow:hidden;
    transition: transform 0.3s cubic-bezier(.34,1.4,.64,1), box-shadow 0.3s, border-color 0.3s;
    backdrop-filter: blur(8px);
}
.movie-card:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 24px 60px rgba(0,0,0,0.55), 0 0 0 1px rgba(255,45,45,0.2), 0 0 40px rgba(255,45,45,0.1);
    border-color: rgba(255,45,45,0.2);
}
.poster-wrap { position:relative; aspect-ratio:2/3; overflow:hidden; }
.poster-wrap img { width:100%; height:100%; object-fit:cover; display:block; transition:transform 0.4s; }
.movie-card:hover .poster-wrap img { transform:scale(1.06); }
.poster-overlay {
    position:absolute; inset:0;
    background:linear-gradient(0deg,rgba(10,10,15,0.95) 0%,transparent 52%);
}
.sim-badge {
    position:absolute; top:10px; right:10px;
    background:linear-gradient(135deg,#FF2D2D,#900);
    color:white; font-family:'Outfit',sans-serif;
    font-size:10px; font-weight:700;
    padding:3px 10px; border-radius:100px; letter-spacing:0.4px;
}
.card-body { padding:14px 14px 15px; }
.c-title {
    font-family:'Outfit',sans-serif; font-size:13px; font-weight:700; color:white;
    margin-bottom:6px; line-height:1.3;
    white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
}
.c-rating { font-family:'Outfit',sans-serif; font-size:12px; color:#FFD700; font-weight:600; margin-bottom:4px; }
.c-genre  {
    font-family:'Outfit',sans-serif; font-size:10px; color:rgba(0,229,255,0.72);
    letter-spacing:0.3px; margin-bottom:8px;
    white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
}
.c-overview {
    font-family:'DM Sans',sans-serif; font-size:11px; color:rgba(255,255,255,0.36);
    line-height:1.55; margin-bottom:12px;
    display:-webkit-box; -webkit-line-clamp:3; -webkit-box-orient:vertical; overflow:hidden;
}
.trailer-btn {
    display:block; text-align:center;
    background:rgba(255,45,45,0.1);
    border:1px solid rgba(255,45,45,0.25);
    border-radius:8px; padding:9px;
    font-family:'Outfit',sans-serif; font-size:11px; font-weight:700;
    letter-spacing:1.2px; text-transform:uppercase;
    color:#FF2D2D !important; text-decoration:none !important;
    transition: background 0.2s, color 0.2s;
}
.trailer-btn:hover { background:#FF2D2D !important; color:white !important; text-decoration:none !important; }

/* streamlit column padding */
[data-testid="column"] { padding: 5px !important; }

/* selectbox + text input */
[data-testid="stSelectbox"] > div > div {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 12px !important;
    color: white !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 14px !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
[data-testid="stSelectbox"] > div > div:focus-within,
[data-testid="stSelectbox"] > div > div:hover {
    border-color: #FF2D2D !important;
    box-shadow: 0 0 0 3px rgba(255,45,45,0.1) !important;
}
[data-testid="stSelectbox"] label {
    font-family:'Outfit',sans-serif !important; font-size:11px !important;
    font-weight:600 !important; letter-spacing:2px !important;
    text-transform:uppercase !important; color:rgba(255,255,255,0.3) !important;
}
[data-testid="stTextInput"] input {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 12px !important;
    color: white !important; font-family:'Outfit',sans-serif !important; font-size:14px !important;
}
[data-testid="stTextInput"] input:focus {
    border-color:#FF2D2D !important;
    box-shadow:0 0 0 3px rgba(255,45,45,0.1) !important;
}
[data-testid="stTextInput"] label {
    font-family:'Outfit',sans-serif !important; font-size:11px !important;
    font-weight:600 !important; letter-spacing:2px !important;
    text-transform:uppercase !important; color:rgba(255,255,255,0.3) !important;
}

/* recommend button */
[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #FF2D2D, #AA0000) !important;
    color: white !important; border: none !important;
    border-radius: 12px !important; padding: 14px 36px !important;
    font-family:'Outfit',sans-serif !important; font-size:13px !important;
    font-weight:700 !important; letter-spacing:1.5px !important;
    text-transform:uppercase !important;
    box-shadow: 0 8px 32px rgba(255,45,45,0.32) !important;
    transition: all 0.25s !important;
}
[data-testid="stButton"] > button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 16px 48px rgba(255,45,45,0.52) !important;
}

/* FOOTER */
.footer {
    padding:28px 52px; margin-top:56px;
    border-top:1px solid rgba(255,255,255,0.06);
    display:flex; align-items:center; justify-content:space-between;
}
.footer-brand { font-family:'Bebas Neue',sans-serif; font-size:18px; letter-spacing:2px; color:white; }
.footer-brand span { color:#FF2D2D; }
.footer-meta { font-family:'DM Sans',sans-serif; font-size:11px; color:rgba(255,255,255,0.2); }
</style>
""", unsafe_allow_html=True)

# ── NAVBAR ──
st.markdown("""
<nav class="navbar">
  <div class="nav-logo">THE <span>HOLLYWOOD</span> ARCHIVE</div>
  <ul class="nav-links">
    <li class="active">Home</li>
    <li>Genres</li>
    <li>Trending</li>
    <li>Top Actors</li>
    <li><span class="nav-pill">Recommender</span></li>
  </ul>
</nav>
""", unsafe_allow_html=True)

# ── HERO ──
st.markdown(f"""
<div class="hero">
  <div class="hero-eyebrow"><span class="h-dot"></span>Content-Based Movie Recommender</div>
  <div class="hero-title">THE<br><span class="red">HOLLYWOOD</span><br>ARCHIVE</div>
  <div class="hero-sub">
    Discover films you will love using <b>machine learning similarity analysis</b><br>
    across {len(movies):,} Hollywood titles — powered by the TMDB database.
  </div>
</div>
""", unsafe_allow_html=True)

# ── SELECT + SEARCH + BUTTON ──
st.markdown('<div style="padding: 0 44px 44px;">', unsafe_allow_html=True)

col_search, col_select, col_btn = st.columns([1.1, 2.2, 0.9])

with col_search:
    search_query = st.text_input("🔍  Search title", placeholder="e.g. Inception…")

with col_select:
    filtered = movies.copy()
    if search_query.strip():
        mask = filtered['title'].str.contains(search_query.strip(), case=False, na=False)
        filtered = filtered[mask]
        if filtered.empty:
            filtered = movies.copy()
            st.warning("No match — showing all movies.")
    selected_movie = st.selectbox("Choose a movie", filtered['title'].values)

with col_btn:
    st.markdown("<div style='margin-top:28px;'>", unsafe_allow_html=True)
    run = st.button("⚡  Recommend", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ── FEATURE CHIPS ──
st.markdown("""
<div style="display:flex;gap:10px;flex-wrap:wrap;padding:0 52px 52px;">
  <div style="display:flex;align-items:center;gap:7px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:100px;padding:7px 15px;font-family:'Outfit',sans-serif;font-size:12px;color:rgba(255,255,255,0.52);">🎯 Cosine Similarity</div>
  <div style="display:flex;align-items:center;gap:7px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:100px;padding:7px 15px;font-family:'Outfit',sans-serif;font-size:12px;color:rgba(255,255,255,0.52);">🤖 ML-Powered Engine</div>
  <div style="display:flex;align-items:center;gap:7px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:100px;padding:7px 15px;font-family:'Outfit',sans-serif;font-size:12px;color:rgba(255,255,255,0.52);">⭐ Live TMDB Ratings</div>
  <div style="display:flex;align-items:center;gap:7px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:100px;padding:7px 15px;font-family:'Outfit',sans-serif;font-size:12px;color:rgba(255,255,255,0.52);">▶️ Trailer Previews</div>
  <div style="display:flex;align-items:center;gap:7px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:100px;padding:7px 15px;font-family:'Outfit',sans-serif;font-size:12px;color:rgba(255,255,255,0.52);">🎭 Genre Filtering</div>
  <div style="display:flex;align-items:center;gap:7px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:100px;padding:7px 15px;font-family:'Outfit',sans-serif;font-size:12px;color:rgba(255,255,255,0.52);">🔍 Smart Search</div>
</div>
""", unsafe_allow_html=True)

# ── RECOMMENDATION RESULTS ──
if run:
    with st.spinner("🎬  Fetching recommendations from TMDB…"):
        try:
            recs = recommend(selected_movie)
        except Exception as e:
            st.error(f"Error generating recommendations: {e}")
            st.stop()

    st.markdown(f"""
    <div class="sdiv">
      <div class="sdiv-line"></div>
      <div class="sdiv-lbl">Your Recommendations</div>
      <div class="sdiv-line"></div>
    </div>
    <div class="res-hdr">
      <div class="res-title">SIMILAR <span>FILMS</span></div>
      <div class="res-sub">Based on: {selected_movie} &nbsp;·&nbsp; Top {len(recs)} matches from {len(movies):,} titles</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="padding: 0 44px;">', unsafe_allow_html=True)

    # Row 1 – cards 0–4
    cols1 = st.columns(5)
    for idx in range(min(5, len(recs))):
        m = recs[idx]
        poster = m['poster'] if m['poster'] else FALLBACK
        turl = f"https://www.youtube.com/results?search_query={m['title'].replace(' ', '+')}+official+trailer"
        with cols1[idx]:
            st.markdown(f"""
            <div class="movie-card">
              <div class="poster-wrap">
                <img src="{poster}" alt="{m['title']}" onerror="this.src='{FALLBACK}'">
                <div class="poster-overlay"></div>
                <div class="sim-badge">▲ {m['similarity']}%</div>
              </div>
              <div class="card-body">
                <div class="c-title" title="{m['title']}">{m['title']}</div>
                <div class="c-rating">⭐ {m['rating']}</div>
                <div class="c-genre">{m['genres'] or 'Drama'}</div>
                <div class="c-overview">{m['overview'][:160]}…</div>
                <a class="trailer-btn" href="{turl}" target="_blank">▶ Watch Trailer</a>
              </div>
            </div>
            """, unsafe_allow_html=True)

    if len(recs) > 5:
        st.markdown("<br>", unsafe_allow_html=True)
        cols2 = st.columns(5)
        for idx in range(5, min(10, len(recs))):
            m = recs[idx]
            poster = m['poster'] if m['poster'] else FALLBACK
            turl = f"https://www.youtube.com/results?search_query={m['title'].replace(' ', '+')}+official+trailer"
            with cols2[idx - 5]:
                st.markdown(f"""
                <div class="movie-card">
                  <div class="poster-wrap">
                    <img src="{poster}" alt="{m['title']}" onerror="this.src='{FALLBACK}'">
                    <div class="poster-overlay"></div>
                    <div class="sim-badge">▲ {m['similarity']}%</div>
                  </div>
                  <div class="card-body">
                    <div class="c-title" title="{m['title']}">{m['title']}</div>
                    <div class="c-rating">⭐ {m['rating']}</div>
                    <div class="c-genre">{m['genres'] or 'Drama'}</div>
                    <div class="c-overview">{m['overview'][:160]}…</div>
                    <a class="trailer-btn" href="{turl}" target="_blank">▶ Watch Trailer</a>
                  </div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ── FOOTER ──
st.markdown("""
<div class="footer">
  <div class="footer-brand">THE <span>HOLLYWOOD</span> ARCHIVE</div>
  <div class="footer-meta">Content-Based Recommender &nbsp;·&nbsp; Machine Learning &nbsp;·&nbsp; TMDB API</div>
</div>
""", unsafe_allow_html=True)