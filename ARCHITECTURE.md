# 🏗️ CarePlan AI - POC Architecture

## Overview

This document describes the technical architecture of the CarePlan AI proof-of-concept. This is a **demo system** designed to showcase LLM-powered care plan generation with human-in-the-loop clinical oversight.

## 🎯 POC Design Principles

### Core Concept
- **Human-in-the-Loop**: All AI-generated care plans require clinician review and approval
- **LLM Integration**: Demonstrates OpenAI GPT integration for care plan generation
- **Role-Based Demo**: Shows different interfaces for patients, clinicians, and administrators
- **Rapid Prototyping**: File-based storage for quick development and testing

## 🔧 Current POC Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│  React Frontend │◄──►│  FastAPI Backend│◄──►│   File Storage  │
│  (Port 3000)    │    │   (Port 8000)   │    │  (JSON Files)   │
│                 │    │                 │    │                 │
└─────────────────┘    └────────┬────────┘    └─────────────────┘
                                │
                       ┌────────▼────────┐
                       │                 │
                       │   OpenAI API    │
                       │  + FAISS Store  │
                       │                 │
                       └─────────────────┘
```

## 🏛️ Implemented Components

### Frontend (React + TypeScript)
**Current Stack:**
- React 18 with TypeScript
- Material-UI (MUI) for UI components
- React Router for navigation
- Axios for API communication

**Implemented Features:**
- Role-based UI for patients, clinicians, and administrators
- Care plan review and approval workflows
- Batch operation interfaces
- Patient data upload and management

**File Structure:**
```
clients/web-ui/src/
├── components/Layout/   # Navigation and page layout
├── pages/              # Main application pages
├── contexts/           # Auth context for user management
├── services/           # API communication layer
└── types/              # TypeScript type definitions
```

### Backend (FastAPI + Python)
**Current Stack:**
- FastAPI for async API
- Pydantic for data validation
- JWT authentication with role-based access
- OpenAI API integration
- FAISS for vector similarity search

**Implemented Services:**
```
app/
├── api/                # API endpoints
│   ├── auth.py        # User authentication
│   ├── batch.py       # Bulk operations
│   ├── mock_data.py   # Demo data endpoints
│   └── review.py      # Care plan review
├── auth/              # JWT authentication
├── models/            # Pydantic data models
├── llm/               # OpenAI integration
└── main.py            # App initialization
```

**Key Features:**
- JWT-based authentication with role validation
- AI-powered care plan generation via OpenAI
- Batch processing for patient data uploads
- Clinical review workflow management

### Data Storage (File-Based POC)
**Current Implementation:**
- JSON files for patient and care plan data
- CSV import/export for batch operations
- Local file system for rapid prototyping
- Mock data for demo purposes

**POC Limitations:**
- No concurrent access control
- Limited query capabilities
- No data persistence guarantees
- Single point of failure

### AI/ML Integration
**OpenAI Integration:**
- GPT models for care plan text generation
- Prompt engineering for medical context
- Response validation and formatting

**Vector Search:**
- FAISS for similarity matching
- Care plan recommendation based on patient similarity
- Medical text embeddings

## 🚀 Deployment

### Local Development
```yaml
# docker-compose.yml
services:
  backend:
    build: .
    ports: ["8000:8000"]
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      
  frontend:
    build: ./clients/web-ui
    ports: ["3000:80"]
    depends_on: [backend]
```

### Production (AWS ECS)
**Current Setup:**
- ECS Fargate for container orchestration
- ECR for Docker image storage
- Application Load Balancer for traffic distribution
- CloudWatch for logging and monitoring
- GitHub Actions for CI/CD

## 🔄 Implemented Workflow

### Care Plan Generation (POC)
```
1. Patient Data Input
   ├── CSV upload via batch operations
   ├── Manual entry through admin UI
   └── Mock data for demonstration

2. Data Processing
   ├── Pydantic validation
   ├── JSON file storage
   └── Batch job tracking

3. AI Generation
   ├── OpenAI API calls
   ├── Prompt-based care plan creation
   └── Response formatting

4. Clinical Review
   ├── Clinician dashboard display
   ├── Manual approval/rejection
   ├── Plan modification capability
   └── Status updates

5. Patient Access
   ├── Approved plans in patient portal
   ├── Status tracking
   └── Progress display
```

## ⚡ Current Performance

### POC Metrics
- **API Response**: < 200ms for most endpoints
- **Care Plan Generation**: 15-30 seconds per plan (OpenAI dependent)
- **File Operations**: Fast for small datasets
- **UI Load**: < 2 seconds initial load

## 🔒 Security (POC Level)

### Current Authentication
- JWT token-based authentication
- Role-based access control (patient/clinician/admin)
- Basic password validation
- Session management

### Security Limitations (POC)
- **File-based storage**: No encryption at rest
- **Demo passwords**: Hardcoded credentials for testing
- **Limited validation**: Basic input sanitization only
- **No audit trail**: Limited logging of user actions

**Note**: This POC is for demonstration only. Production systems require comprehensive security measures.

## 🔧 Technology Choices (POC)

### Why These Technologies?

#### FastAPI
- **Pros**: Fast development, automatic API docs, async support
- **Cons**: Smaller ecosystem than Django
- **POC Rationale**: Quick prototyping with built-in documentation

#### React + TypeScript
- **Pros**: Rich component ecosystem, type safety, familiar to developers
- **Cons**: More setup complexity than plain JavaScript
- **POC Rationale**: Material-UI provides professional healthcare UI components

#### File-Based Storage
- **Pros**: Zero setup, easy to inspect, rapid development
- **Cons**: No scalability, no concurrent access, no reliability
- **POC Rationale**: Fastest way to build functional demo

#### OpenAI API
- **Pros**: State-of-the-art language models, simple integration
- **Cons**: External dependency, costs per API call, rate limits
- **POC Rationale**: Demonstrates LLM capabilities without training custom models

---

## 🏭 Beyond POC: Production Considerations

This POC demonstrates the core concept of LLM-powered care plan generation. For a production healthcare system, consider these approaches:

### Data Architecture
- **PostgreSQL/MySQL**: ACID compliance for clinical data integrity
- **Vector Databases**: Specialized solutions like Pinecone, Weaviate for medical embeddings
- **Data Lakes**: For clinical analytics and research (Snowflake, BigQuery)
- **Caching**: Redis/Memcached for frequently accessed patient data

### AI/ML Infrastructure
- **Model Management**: MLflow, Weights & Biases for model versioning
- **Fine-tuned Models**: Domain-specific models trained on medical literature
- **Model Serving**: Dedicated inference servers (TensorFlow Serving, TorchServe)
- **A/B Testing**: Clinical decision support effectiveness testing

### Security & Compliance
- **HIPAA Compliance**: End-to-end encryption, audit trails, data governance
- **Authentication**: SAML/OIDC integration with hospital systems
- **Zero Trust**: Network segmentation, principle of least privilege
- **Audit Logging**: Immutable logs for all clinical decisions

### Integration & Interoperability
- **EHR Integration**: FHIR R4 compliance for Epic, Cerner, AllScripts
- **HL7 Messaging**: Real-time data exchange with hospital systems
- **API Gateway**: Rate limiting, monitoring, version management
- **Event Streaming**: Kafka for real-time clinical data processing

### Scalability & Reliability
- **Microservices**: Domain-driven decomposition as system grows
- **Container Orchestration**: Kubernetes for production workloads
- **Multi-region**: High availability across geographic regions
- **Monitoring**: Comprehensive observability with Datadog, New Relic

### Regulatory & Clinical
- **FDA Compliance**: If system provides clinical decision support
- **Clinical Validation**: Evidence-based validation of AI recommendations
- **Workflow Integration**: Seamless integration with existing clinical workflows
- **Change Management**: Training and adoption strategies for healthcare teams

**Key Principle**: Healthcare AI systems require extensive validation, regulatory compliance, and clinical integration that goes far beyond a technical proof-of-concept.

