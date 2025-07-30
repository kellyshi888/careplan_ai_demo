# 🩺 CarePlan AI - LLM-Powered Care Plan Generation

*A demo and proof-of-concept for using Large Language Models to generate personalized care plans with human-in-the-loop clinical oversight*

[![CI/CD Pipeline](https://github.com/your-username/careplan-ai/workflows/CarePlan%20AI%20CI/CD%20Pipeline/badge.svg)](https://github.com/your-username/careplan-ai/actions)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18+-61DAFB.svg)](https://reactjs.org/)

## 🎯 What This Demonstrates

This proof-of-concept showcases how Large Language Models can assist healthcare providers in generating personalized care plans while maintaining essential clinical oversight. The system demonstrates a **human-in-the-loop approach** where AI generates initial care plans that require clinician review and approval before implementation.

## 🔍 Key Features

### Core Capabilities
- **AI-Powered Generation**: Uses OpenAI GPT models to create initial care plans from patient data
- **Clinical Review Workflow**: All AI-generated plans require clinician approval before activation
- **Batch Processing**: Demonstrates scalable processing of multiple patient records
- **Role-Based Access**: Separate interfaces for patients, clinicians, and administrators

### Demo Workflow
1. **Patient Data Input**: Upload patient information via CSV or manual entry
2. **AI Generation**: LLM processes patient data to create initial care plans
3. **Clinical Review**: Clinicians review, modify, and approve AI-generated plans
4. **Patient Access**: Approved plans become available in patient portal

## 🏗️ Technical Stack

**Frontend**: React + TypeScript + Material-UI  
**Backend**: FastAPI + Python + Pydantic  
**AI/ML**: OpenAI GPT + FAISS Vector Search  
**Infrastructure**: Docker + AWS ECS

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed technical specifications and system design.
