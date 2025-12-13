# Banking News and Deal Intelligence Engine

An NLP-powered platform for collecting, analyzing, and extracting insights from banking and financial news.

## 🎯 Project Overview

This system collects financial news from multiple sources, processes them using advanced NLP techniques, detects banking deals and trends, and provides an interactive dashboard for intelligence gathering.

## 📋 Features

### Phase 1: Data Collection & Storage ✅
- NewsAPI integration for financial news
- Web scraping from Reuters, Financial Times, and RSS feeds
- MongoDB storage with efficient indexing
- Automated data collection pipeline
- Duplicate detection and handling

### Phase 2: NLP Processing Pipeline (Coming Soon)
- Named Entity Recognition (companies, people, amounts)
- Financial sentiment analysis with FinBERT
- Topic modeling with LDA
- Keyword extraction

### Phase 3: Deal Intelligence & Analytics (Coming Soon)
- Automatic deal detection and classification
- Company relationship mapping
- Trend analysis
- Alert system for significant events

### Phase 4: API Development (Coming Soon)
- RESTful API with FastAPI
- Search and filtering capabilities
- Authentication and rate limiting

### Phase 5: Dashboard & Visualization (Coming Soon)
- Interactive React dashboard
- Real-time news feed
- Sentiment visualization
- Deal tracking interface

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- MongoDB (local or Atlas)
- NewsAPI key ([Get one here](https://newsapi.org/))

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd Banking-News-and-Deal-Intelligence-Engine
```

2. **Set up Python environment**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env and add your NewsAPI key and MongoDB URI
```

4. **Start MongoDB** (if running locally)
```bash
mongod --dbpath /path/to/data/db
```

### Running the Application

1. **Test data collection (Phase 1)**
```bash
cd backend
python tests/test_phase1.py
```

2. **Start the API server**
```bash
cd backend
python main.py
```

The API will be available at `http://localhost:8000`

## 📁 Project Structure

```
Banking-News-and-Deal-Intelligence-Engine/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Core configuration
│   │   ├── models/       # Data models
│   │   ├── services/     # Business logic
│   │   └── utils/        # Utilities
│   ├── tests/            # Test files
│   ├── main.py           # Application entry point
│   └── requirements.txt  # Python dependencies
├── frontend/             # React dashboard (Phase 5)
├── data/                 # Data storage
├── notebooks/            # Jupyter notebooks for analysis
└── .env.example          # Environment template
```

## 🔧 Configuration

Key environment variables in `.env`:

```env
MONGODB_URI=mongodb://localhost:27017/banking_news_engine
NEWS_API_KEY=your_newsapi_key_here
API_HOST=0.0.0.0
API_PORT=8000
```

## 📊 API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🧪 Testing

Run Phase 1 tests:
```bash
cd backend
python tests/test_phase1.py
```

## 📝 Development Roadmap

- [x] **Phase 1**: Data Collection & Storage
- [ ] **Phase 2**: NLP Processing Pipeline
- [ ] **Phase 3**: Deal Intelligence & Analytics
- [ ] **Phase 4**: API Development
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

---

**Current Status**: Phase 1 Complete ✅
