# Banking News and Deal Intelligence Engine

An NLP-powered platform for collecting, analyzing, and extracting insights from banking and financial news.

## 🎯 Project Overview

This system collects financial news from multiple sources, processes them using advanced NLP techniques, detects banking deals and trends, and provides a RESTful API and interactive dashboard for intelligence gathering.

## ✨ Features

### ✅ Phase 1: Data Collection & Storage
- **NewsAPI Integration**: Automated collection of financial news
- **Web Scraping**: Reuters, Financial Times, and RSS feed scraping
- **MongoDB Storage**: Efficient storage with indexing and duplicate detection
- **Automated Pipeline**: Scheduled data collection

### ✅ Phase 2: NLP Processing Pipeline
- **Text Preprocessing**: Cleaning, tokenization, lemmatization with NLTK
- **Named Entity Recognition**: Extract companies, people, locations, amounts using spaCy
- **Sentiment Analysis**: Financial sentiment analysis with FinBERT
- **Topic Modeling**: LDA-based topic extraction with Gensim
- **Keyword Extraction**: TF-IDF and RAKE algorithms

### ✅ Phase 3: Deal Intelligence & Analytics
- **Deal Detection**: Automatic detection of M&A, IPO, loans, partnerships
- **Company Relationships**: Network graph analysis with NetworkX
- **Trend Analysis**: Deal volume, value, and sentiment trends
- **Anomaly Detection**: Statistical anomaly detection
- **Alert System**: Real-time alerts for mega deals and significant events

### ✅ Phase 4: API Development
- **RESTful API**: FastAPI-based REST API
- **News Endpoints**: List, search, filter articles
- **Analytics Endpoints**: Sentiment trends, deal statistics
- **Company Endpoints**: Company details, relationships, sentiment history
- **Alert Endpoints**: Alert retrieval and filtering
- **Auto-documentation**: Swagger UI and ReDoc

### 🚧 Phase 5: Dashboard & Visualization (Planned)
- Interactive React dashboard
- Real-time news feed
- Sentiment visualization
- Deal tracking interface
- Company network visualization

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- MongoDB (local or Atlas)
- NewsAPI key ([Get one here](https://newsapi.org/))

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/jitesh523/Banking-News-and-Deal-Intelligence-Engine.git
cd Banking-News-and-Deal-Intelligence-Engine
```

2. **Set up Python environment**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Download spaCy model**
```bash
python -m spacy download en_core_web_sm
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env and add your NewsAPI key and MongoDB URI
```

5. **Start MongoDB** (if running locally)
```bash
mongod --dbpath /path/to/data/db
```

### Running the Application

1. **Collect data (Phase 1)**
```bash
cd backend
python tests/test_phase1.py
```

2. **Process with NLP (Phase 2)**
```bash
python tests/test_phase2.py
```

3. **Run analytics (Phase 3)**
```bash
python tests/test_phase3.py
```

4. **Start the API server**
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

Once the server is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### API Endpoints

#### News Endpoints (`/api/v1/news`)
- `GET /` - List all articles with filtering
- `GET /{article_id}` - Get specific article
- `GET /search/` - Search articles by query
- `GET /trending/` - Get trending news
- `GET /stats/` - Get news statistics

#### Analytics Endpoints (`/api/v1/analytics`)
- `GET /sentiment` - Get sentiment trends
- `GET /topics` - Get topic distribution
- `GET /entities` - Get entity frequency
- `GET /deals` - Get deal statistics
- `GET /dashboard` - Get dashboard summary

#### Companies Endpoints (`/api/v1/companies`)
- `GET /` - List companies
- `GET /{company_name}` - Get company details
- `GET /{company_name}/relationships` - Get company network
- `GET /{company_name}/sentiment` - Get sentiment history
- `GET /network/graph` - Get network graph data

#### Alerts Endpoints (`/api/v1/alerts`)
- `GET /` - Get alerts with filtering
- `GET /summary` - Get alert summary

## 📁 Project Structure

```
Banking-News-and-Deal-Intelligence-Engine/
├── backend/
│   ├── app/
│   │   ├── api/              # API endpoints
│   │   │   ├── news.py
│   │   │   ├── analytics.py
│   │   │   ├── companies.py
│   │   │   └── alerts.py
│   │   ├── core/             # Core configuration
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   └── logging.py
│   │   ├── models/           # Data models
│   │   │   └── article.py
│   │   ├── services/         # Business logic
│   │   │   ├── collector.py
│   │   │   ├── news_api.py
│   │   │   ├── web_scraper.py
│   │   │   ├── storage.py
│   │   │   ├── text_preprocessing.py
│   │   │   ├── ner.py
│   │   │   ├── sentiment.py
│   │   │   ├── topic_modeling.py
│   │   │   ├── keyword_extraction.py
│   │   │   ├── nlp_pipeline.py
│   │   │   ├── deal_detector.py
│   │   │   ├── relationship_mapper.py
│   │   │   ├── trend_analyzer.py
│   │   │   ├── alert_system.py
│   │   │   └── analytics_engine.py
│   │   └── utils/            # Utilities
│   ├── tests/                # Test files
│   │   ├── test_phase1.py
│   │   ├── test_phase2.py
│   │   └── test_phase3.py
│   ├── main.py               # Application entry point
│   └── requirements.txt      # Python dependencies
├── frontend/                 # React dashboard (Phase 5)
├── data/                     # Data storage
├── notebooks/                # Jupyter notebooks
└── .env.example              # Environment template
```

## 🔧 Configuration

Key environment variables in `.env`:

```env
# MongoDB
MONGODB_URI=mongodb://localhost:27017/banking_news_engine
MONGODB_DB_NAME=banking_news_engine

# NewsAPI
NEWS_API_KEY=your_newsapi_key_here

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=your-secret-key

# Frontend
FRONTEND_URL=http://localhost:3000

# Environment
ENVIRONMENT=development
LOG_LEVEL=INFO
```

## 🧪 Testing

Run phase-specific tests:

```bash
# Phase 1: Data Collection
python tests/test_phase1.py

# Phase 2: NLP Processing
python tests/test_phase2.py

# Phase 3: Analytics
python tests/test_phase3.py
```

## 📊 Technology Stack

### Backend
- **Framework**: FastAPI
- **Database**: MongoDB (motor, pymongo)
- **NLP**: spaCy, FinBERT, Gensim, NLTK, Transformers
- **Data Collection**: NewsAPI, BeautifulSoup4, Requests
- **Analytics**: NetworkX, NumPy, scikit-learn
- **Logging**: Loguru

### Frontend (Planned)
- **Framework**: React
- **Visualization**: Recharts/D3.js
- **HTTP Client**: Axios
- **UI**: Material-UI

## 📝 Development Roadmap

- [x] **Phase 1**: Data Collection & Storage
- [x] **Phase 2**: NLP Processing Pipeline
- [x] **Phase 3**: Deal Intelligence & Analytics
- [x] **Phase 4**: API Development
- [ ] **Phase 5**: Dashboard & Visualization

## 🤝 Contributing

This project follows a phased development approach. Each phase is committed to GitHub upon completion.

## 📄 License

MIT License

## 🔗 Resources

- [NewsAPI Documentation](https://newsapi.org/docs)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [spaCy Documentation](https://spacy.io/)
- [FinBERT](https://huggingface.co/ProsusAI/finbert)

---

**Current Status**: Phase 4 Complete ✅ | API Fully Functional

**Repository**: [jitesh523/Banking-News-and-Deal-Intelligence-Engine](https://github.com/jitesh523/Banking-News-and-Deal-Intelligence-Engine)
