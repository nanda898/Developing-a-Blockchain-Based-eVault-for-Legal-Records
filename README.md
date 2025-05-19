# Blockchain-based eVault for Legal Records

A secure document management system that leverages blockchain technology for storing and tracking legal records. The system provides document upload, download capabilities with audit logging functionality.

## Features

- 📤 **Secure Document Upload**
  - Upload documents with owner information and metadata
  - Automatic hash generation for document verification
  - Secure storage in S3-compatible storage

- 📥 **Controlled Document Download**
  - Download documents using unique document IDs
  - Time-limited secure download links (15 minutes)
  - Hash verification for document integrity

- 📋 **Comprehensive Audit Logging**
  - Track all document activities
  - View audit logs per document
  - Access complete system activity log
  - Chronological activity tracking

## System Architecture

### Frontend
- Built with Streamlit for a clean, modern UI
- Responsive web interface
- Multiple functional tabs for different operations

### Backend
- Flask-based REST API
- Secure document storage integration
- DynamoDB tables for document and audit log management

## Setup Instructions

1. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   python app.py
   ```
   The backend server will start on http://localhost:5000

2. **Frontend Setup**
   ```bash
   cd frontend
   pip install -r requirements.txt
   streamlit run app.py
   ```
   The frontend will be accessible at http://localhost:8501

## Usage Guide

### Document Upload
1. Navigate to the Upload tab
2. Enter owner name/ID
3. Add document metadata/description
4. Select file to upload
5. Click Upload button
6. Save the returned Document ID

### Document Download
1. Go to the Download tab
2. Enter the Document ID
3. Click "Get download link"
4. Use the generated link to download (valid for 15 minutes)
5. Verify document integrity using provided hash

### Viewing Audit Logs
- **Per Document**: Use the Audit Logs tab with a specific Document ID
- **System-wide**: Use the All Logs tab to view recent activities

## Security Features

- Blockchain-based document verification
- Temporary download links
- Comprehensive activity logging
- Secure document storage

## Note

This system is designed for managing legal records with a focus on security and auditability. Always ensure proper access controls and security measures are in place when deploying in a production environment.