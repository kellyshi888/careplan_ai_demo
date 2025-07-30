# CarePlan AI - Setup Guide

This guide walks you through setting up the CarePlan AI POC system locally with sample data.

> **Architecture Overview**: See [ARCHITECTURE.md](ARCHITECTURE.md) for system design and technical details.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 16+
- Poetry (for Python dependency management)
- Git

### 1. Backend Setup

Choose one of the following installation methods:

#### Option A: Using pip (Recommended)
```bash
# Navigate to the project directory
cd careplan_ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your OpenAI API key and other settings
```

#### Option B: Using Poetry
```bash
# Navigate to the project directory
cd careplan_ai

# Install Poetry if not already installed
pip install poetry

# Install dependencies
poetry install --no-root

# Activate virtual environment
poetry shell

# Set up environment variables
cp .env.example .env
# Edit .env with your OpenAI API key and other settings
```

### 2. Generate Sample Healthcare Data

```bash
# Run the data seeding script
python scripts/run_seeding.py
```

This will generate:
- 100 synthetic patient records
- Patient intake data
- EHR records with diagnoses, lab results, and vital signs
- Sample care plans
- Mock data for the web UI

### 3. Start the FastAPI Backend

```bash
# Start the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Mock Data Info**: http://localhost:8000/api/mock/data-info

### 4. Frontend Setup

```bash
# Navigate to the web UI directory
cd clients/web-ui

# Install Node.js dependencies
npm install

# Start the React development server
npm start
```

The web application will be available at:
- **Patient Portal**: http://localhost:3000

## 🏥 Sample Healthcare Dataset

The system uses synthetic healthcare data based on the Kaggle healthcare dataset structure:

### Data Sources
- **Original Dataset**: https://www.kaggle.com/datasets/prasad22/healthcare-dataset
- **Generated Data**: 100 synthetic patients with realistic medical conditions
- **Privacy**: All data is completely synthetic - no real patient information

### Medical Conditions Included
- **Type 2 Diabetes** - With medications like Metformin, lab results (HbA1c), symptoms
- **Hypertension** - Blood pressure monitoring, ACE inhibitors
- **Arthritis** - Joint pain symptoms, anti-inflammatory medications
- **Asthma** - Respiratory symptoms, inhalers
- **Obesity** - Weight management, lifestyle interventions
- **Cancer** - Various treatment protocols, monitoring

### Data Structure
Each patient has:
- **Demographics**: Age, gender, blood type
- **Medical History**: Past and current conditions
- **Medications**: Current prescriptions with dosages
- **Lab Results**: Recent test results with normal/abnormal flags
- **Vital Signs**: Blood pressure, heart rate, temperature, etc.
- **Care Plans**: AI-generated personalized treatment recommendations

## 🌐 Web UI Features

### Patient Dashboard
- **Health Overview**: Key metrics and trends
- **Current Medications**: Active prescriptions
- **Upcoming Appointments**: Scheduled healthcare visits
- **Health Trends**: Interactive charts showing progress over time

### Medical History
- **Timeline View**: Chronological medical events
- **Diagnoses**: Current and past conditions with ICD-10 codes
- **Lab Results**: Comprehensive laboratory data with reference ranges
- **Vital Signs**: Historical vital sign measurements
- **Medications**: Current and past prescriptions

### Care Plans
- **Active Plans**: Current personalized care recommendations
- **Treatment Actions**: Specific medications, diagnostics, lifestyle changes
- **Goals**: Short-term and long-term health objectives
- **Progress Tracking**: Visual progress indicators
- **Educational Resources**: Patient education materials

## 🧪 Testing the System

### API Documentation
Once the backend is running, access the interactive API docs at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc


### Demo Workflow
1. Generate fresh sample data: `python scripts/run_seeding.py`
2. Start backend: `uvicorn app.main:app --reload`
3. Start frontend: `cd clients/web-ui && npm start`
4. Open http://localhost:3000 and test the demo

## 🐳 Docker Alternative

### Quick Docker Setup (Alternative to Local Setup)
```bash
# Build and start all services
docker-compose up --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

This runs the same demo but in containers instead of local development servers.

## 🧪 Demo Testing

### Demo Users
Test the system with these pre-configured accounts:

| Role | Email | Password | What to Test |
|------|--------|----------|--------------|
| **Patient** | `john.doe@email.com` | `patient123` | View care plans, medical history, dashboard |
| **Clinician** | `dr.garcia@hospital.com` | `doctor123` | Review/approve AI-generated care plans |
| **Admin** | `admin@hospital.com` | `admin123` | Upload patient data, batch operations |

## 🔍 Troubleshooting

### Common Issues

**Backend won't start**
- Check Python version (3.11+ required)
- Verify OpenAI API key in `.env` file
- Install dependencies: `pip install -r requirements.txt`

**Frontend build errors**
- Check Node.js version (16+ required)
- Clear cache: `npm cache clean --force`
- Reinstall: `rm -rf node_modules && npm install`

**No sample data showing**
- Run data generation: `python scripts/run_seeding.py`
- Check if backend is accessible at http://localhost:8000/health

**Can't login**
- Use demo credentials above
- Verify backend is running and accessible
- Check browser console for API errors

### Getting Help
- Check the backend logs in your terminal
- Visit http://localhost:8000/docs for API status
- Review [ARCHITECTURE.md](ARCHITECTURE.md) for technical details

