# 🎬 CineMatch AI - Hollywood Movie Recommendation System

An intelligent **Content-Based Movie Recommendation System** built using **Machine Learning**, **Natural Language Processing (NLP)**, and **Streamlit**. The application recommends Hollywood movies based on content similarity by analyzing movie metadata such as genres, cast, crew, keywords, and overview.

The project utilizes the **TMDB 5000 Movies Dataset** and **Cosine Similarity** to provide accurate movie recommendations through an interactive and modern web interface.

---

## 📌 Features

- 🎥 Hollywood Movie Recommendations
- 🤖 Content-Based Recommendation Engine
- 🧠 NLP-Based Feature Extraction
- 📊 Cosine Similarity Algorithm
- 🔍 Search Movies Instantly
- ⭐ Movie Ratings
- 🎭 Genre Information
- 🖼 Movie Posters via TMDB API
- ▶ Watch Trailer Button
- 📈 Similarity Score Display
- 🌙 Modern Dark Theme UI
- 💻 Interactive Streamlit Dashboard

---

## 🛠 Technologies Used

- Python
- Streamlit
- Pandas
- NumPy
- Scikit-learn
- Requests
- Pickle
- HTML & CSS
- TMDB API

---

## 🤖 Machine Learning Concepts

- Content-Based Filtering
- Natural Language Processing (NLP)
- Bag of Words
- CountVectorizer
- Cosine Similarity
- Feature Engineering
- Text Preprocessing

---

## 📂 Project Structure

```text
CineMatch-AI/
│
├── app.py
├── model.py
├── movie_dict.pkl
├── similarity.pkl
├── tmdb_5000_movies.csv
├── tmdb_5000.csv
├── requirements.txt
├── README.md
└── assets/
```

---

## 📊 Dataset

The project uses the **TMDB 5000 Movies Dataset**, containing movie titles, genres, keywords, cast, crew, overviews, ratings, and release information.

---

## ⚙️ Workflow

1. Load movie and credits datasets.
2. Merge datasets using movie titles.
3. Extract genres, keywords, cast, crew, and overview.
4. Create a combined **tags** feature.
5. Apply NLP preprocessing.
6. Convert text into vectors using **CountVectorizer**.
7. Compute **Cosine Similarity**.
8. Recommend the top similar Hollywood movies.

---

## 📈 Evaluation

- Cosine Similarity Score
- Precision@K
- Recall@K

---

## ▶️ Installation

```bash
git clone https://github.com/your-username/CineMatch-AI.git
cd CineMatch-AI
pip install -r requirements.txt
streamlit run app.py
```

---

## 📦 Requirements

```text
streamlit
pandas
numpy
scikit-learn
requests
```

---

## 🚀 Future Enhancements

- Hybrid Recommendation System
- User Authentication
- Voice Search
- Watchlist
- Sentiment Analysis
- Personalized Profiles

---

## 👩‍💻 Author

**Atheena Jayaprakash**

Data Science | Machine Learning | Deep Learning | Artificial Intelligence

---

## 📄 License

This project is for educational and learning purposes.

⭐ If you found this project useful, consider giving it a star on GitHub!
