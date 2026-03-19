# 🚀 AI-Based Load Testing Framework

An intelligent, adaptive load testing framework that uses machine learning to predict system failures, detect anomalies, and optimize load testing strategies.

## 📋 Overview

This project implements an **AI-driven adaptive load testing system** that combines:
- **Async/Concurrent Testing**: Efficient parallel request handling with `aiohttp`
- **Machine Learning Models**: Gradient Boosting, Random Forest, and Isolation Forest for performance prediction
- **Anomaly Detection**: Identify unusual system behavior during load tests
- **Digital Twin Simulation**: Simulate system behavior under various load conditions
- **REST API**: Flask-based API for note management
- **Interactive Dashboard**: Streamlit-powered UI for visualization and control

## 📁 Project Structure

```
AI_Load_Test/
├── api.py                           # Flask API for note management (CRUD operations)
├── concurrency_test.py              # Core AI-driven load testing logic
├── ui.py                            # Streamlit interactive dashboard
├── baselin.py                       # Baseline testing utilities
├── helper.py                        # Database helper functions
├── populate_db.py                   # Database population utility
├── ai_load_testing_results.csv      # Test results storage
├── requirments.txt                  # Python dependencies
└── __pycache__/                     # Python cache files
```

## 🔧 Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

1. **Clone the repository** (if applicable):
```bash
git clone <repository-url>
cd AI_Load_Test
```

2. **Create a virtual environment**:
```bash
python -m venv env
source env/Scripts/activate  # On Windows
# or
source env/bin/activate      # On macOS/Linux
```

3. **Install dependencies**:
```bash
pip install -r requirments.txt
```

## 🚀 Quick Start

### 1. Populate Database
Initialize the database with test data:
```bash
python populate_db.py
```

### 2. Start the API Server
Run the Flask backend:
```bash
python api.py
```
The API will be available at `http://localhost:5000`

### 3. Launch the Dashboard
Start the Streamlit interactive UI:
```bash
streamlit run ui.py
```
Access the dashboard at `http://localhost:8501`

### 4. Run Load Tests
Execute the load testing framework:
```bash
python concurrency_test.py
```

## 📊 Features

### API Endpoints
- `GET /` - API health check
- `GET /notes` - Retrieve all notes
- `POST /notes` - Create a new note
- `GET /notes/<id>` - Get specific note
- `PUT /notes/<id>` - Update a note
- `DELETE /notes/<id>` - Delete a note

### Load Testing Framework
The `concurrency_test.py` module includes:

- **Async Request Handling**: Concurrent load generation using `aiohttp`
- **Performance Metrics**: Response time, throughput, error rates
- **ML Models**:
  - Gradient Boosting & Random Forest for performance prediction
  - Logistic Regression for failure classification
  - Isolation Forest for anomaly detection
  - Voting Regressor for ensemble predictions

- **Feature Engineering**: Extracts meaningful patterns from load test data
- **Digital Twin Simulation**: Predicts system behavior under various loads
- **Adaptive Thresholding**: Dynamically determines failure points

### Streamlit Dashboard
Interactive visualization featuring:
- Real-time load testing controls
- Performance charts and metrics
- Model predictions and anomaly detection results
- System resource monitoring
- Trial data visualization

## ⚙️ Configuration

Key configuration variables in `concurrency_test.py`:

```python
BASE_URL = ""              # Target API endpoint
NOTES_URL = ""             # Notes API endpoint
START_USERS = 1            # Initial load (concurrent users)
MAX_USERS = 2000           # Maximum load (concurrent users)
TIMEOUT = 5                # Request timeout (seconds)
BATCH_SIZE = 500           # Batch processing size
NUM_TRIALS = 5             # Number of test trials
KFOLD_SPLITS = 5           # K-fold cross-validation splits
```

Update these values based on your testing requirements.

## 📈 Dependencies

Key libraries:
- **Flask** - RESTful API framework
- **Streamlit** - Interactive dashboard
- **aiohttp** - Async HTTP client
- **asyncio** - Asynchronous I/O
- **scikit-learn** - Machine learning models
- **pandas** - Data manipulation and analysis
- **numpy** - Numerical computing
- **matplotlib** - Data visualization
- **psutil** - System and process utilities

See `requirments.txt` for the complete dependency list.

## 📝 Usage Examples

### Running a Load Test
```bash
# Configure BASE_URL and NOTES_URL in concurrency_test.py
python concurrency_test.py
```

### Adding Test Data
```bash
python populate_db.py
```

### Creating Notes via API
```bash
curl -X POST http://localhost:5000/notes \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Note", "description": "Description"}'
```

## 📊 Output

Results are saved to `ai_load_testing_results.csv` with metrics including:
- Concurrent users
- Response times
- Error rates
- Throughput
- System resource usage
- ML model predictions

## 🔍 How It Works

1. **Data Collection**: Gather performance metrics during load tests
2. **Feature Engineering**: Extract relevant features from raw metrics
3. **Model Training**: Train ML models on historical test data
4. **Prediction**: Predict performance under new load conditions
5. **Anomaly Detection**: Identify unusual system behavior
6. **Adaptive Testing**: Adjust load based on predictions and observations
7. **Validation**: Test predictions against actual results

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📄 License

This project is open source and available under the MIT License.

## 📧 Support

For questions or issues, please create an issue in the repository or contact the development team.

---

**Built with ❤️ for intelligent load testing**
