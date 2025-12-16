# RAG-Powered Chatbot with Document Support

![Python](https://img.shields.io/badge/Python-3.11-blue) ![Django](https://img.shields.io/badge/Django-5.2-green) ![REST](https://img.shields.io/badge/DRF-API-orange) ![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## Project Overview
This project is a **RAG (Retrieval-Augmented Generation) chatbot** that allows users to upload documents (PDF, DOCX, TXT), ask questions, and receive AI-generated answers based on their personal documents. Chat history is stored for user reference, and background tasks can automatically clean old messages.  

**Key Features:**
- User registration and JWT-based authentication.
- Upload and process documents for context-aware responses.
- AI-powered chat using **LLaMA-3.1 Instruct model**.
- Retrieval of relevant document sections via **Chroma vector store**.
- Scheduled background tasks: deleting old chat history, sending verification emails.

---

## Technologies Used
- **Backend:** Django 5, Django REST Framework  
- **Authentication:** JWT via `djangorestframework-simplejwt`  
- **AI/ML:** LLaMA-3.1 via HuggingFace Endpoint, embeddings via `sentence-transformers/all-MiniLM-L6-v2`  
- **Vector Store:** Chroma (`langchain-chroma`)  
- **Database:** SQLite (default; can switch to PostgreSQL/MySQL in production)  
- **Task Scheduler:** APScheduler  
- **Email:** SMTP for verification emails  

---

## Architecture and Design Decisions

### 1. RAG Pipeline Integration
The **RAG pipeline** combines document retrieval with AI response generation:  
- **Document Retrieval:** Uploaded documents are split into chunks and stored in a vector database (Chroma).  
- **Query:** User questions are embedded and matched to document chunks.  
- **AI Response:** Retrieved chunks are fed as context to the LLaMA-3.1 model to generate informed answers.

### 2. Database & Model Structure
- **UserDocument:** Stores uploaded files with metadata (`title`, `processed`, `chunk_count`).  
- **ChatHistory:** Logs user queries and AI responses.  
- **Rationale:** Keeps user data isolated and enables efficient retrieval for the RAG system.

### 3. User Authentication
- **JWT Authentication:** Users register/login using username and password.  
- **Security Measures:**  
  - Passwords are hashed using Django's built-in `PBKDF2` algorithm.  
  - JWT tokens are used for stateless authentication.  
  - Verification emails ensure email ownership.

### 4. AI Response Generation
1. The RAG pipeline retrieves the top-K relevant document chunks.  
2. Chunks are formatted into a context string.  
3. LLaMA-3.1 generates a response using the context and the user question.  
4. Sources from retrieved documents are attached for transparency.

### 5. Scheduled Background Tasks
Implemented via **APScheduler**:
- **Delete Old Chat History:** Runs every 30 days (configurable; 5 min for testing).  
- **Send Verification Emails:** Triggered after user registration.

### 6. Testing Strategies
- Unit testing for serializers, views, and models.  
- Manual testing using Swagger/Redoc for API endpoints.  
- Functional testing of chat queries with different document sets.  
- Verification of background tasks in development mode.

### 7. External Services
- **HuggingFace API:** For LLaMA-3.1 model inference.  
- **Chroma Vector Store:** For document embeddings and retrieval.  
- **SMTP Server:** For sending verification emails.

### 8. Future Enhancements
- Real-time knowledge base updates.  
- Multi-user chat sessions with personalized RAG pipelines.  
- Integration with other LLMs or custom embeddings.  
- More document types (HTML, Markdown, CSV).  

---

## API Documentation

| Endpoint             | Method | Description |
|---------------------|--------|-------------|
| `/register/`        | POST   | User signup |
| `/login/`           | POST   | JWT login |
| `/api/token/refresh/` | POST | Refresh JWT token |
| `/upload/`          | POST   | Upload a document (PDF, DOCX, TXT) |
| `/chat/`            | POST   | Send a question to AI |
| `/chat-history/`    | GET    | Retrieve user’s chat history |

> Each endpoint includes summary and description in Swagger/Redoc. Below given: 

## 1. User Signup
**Endpoint:** `POST /register/`  

**Description:** Register a new user account. A verification email will be sent after successful registration.  

**Request Body:**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "SecurePass123",
  "confirm_password": "SecurePass123"
}
```

**Success Response (201):**
```json
{
  "detail": "Registration successful. Please check your email."
}
```

**Error Response (400):**
```json
{
  "email": ["A user with that email already exists."],
  "confirm_password": ["Passwords don't match."]
}
```

## 2. User Login
**Endpoint:** `POST /login/`  

**Description:** Authenticate user and retrieve JWT tokens (access and refresh). Accepts either username or email. 

**Request Body:**
```json
{
  "username_or_email": "johndoe",
  "password": "SecurePass123"
}
```

**Success Response (201):**
```json
{
  "refresh": "<refresh_token>",
  "access": "<access_token>",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com"
  }
}
```

**Error Response (400):**
```json
{
  "non_field_errors": ["Invalid username/email or password"]
}
```

## 3. Refresh JWT Token
**Endpoint:** `POST /refresh/`  

**Description:** Refresh the access token using a valid refresh token.

**Request Body:**
```json
{
  "refresh": "<refresh_token>"
}
```

**Success Response (201):**
```json
{
  "access": "<new_access_token>"
}
```

**Error Response (400):**
```json
{
  "detail": "Token is invalid or expired"
}
```

## 4. Upload Document
**Endpoint:** `POST /upload/`  

**Description:** Upload a document (PDF, DOCX, TXT) for RAG processing. Maximum file size: 10MB.

**Header:**
```bash
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

```

**Request Body:**
```bash
file: <binary file>
```

**Success Response (201):**
```json
{
  "id": 1,
  "title": "my_document",
  "file": "/media/documents/my_document.pdf",
  "uploaded_at": "2025-12-16T10:30:00Z",
  "processed": true,
  "chunk_count": 25
}

```

**Error Response (400):**
```json
{
  "file": ["Only .pdf, .txt, .docx files are allowed"]
}

```

## 5. Chat with RAG
**Endpoint:** `POST /chat/`  

**Description:** Send a question and receive an AI-generated response based on uploaded documents.

**Header:**
```bash
Authorization: Bearer <access_token>
Content-Type: application/json

```

**Request Body:**
```json
{
  "question": "What is the main topic of my document?",
  "chat_history": []
}

```

**Success Response (201):**
```json
{
  "question": "What is the main topic of my document?",
  "answer": "Based on your uploaded documents, the main topic discusses ...",
  "sources": [
    {
      "title": "my_document.pdf",
      "type": "personal_document"
    }
  ]
}


```

**Error Response (400):**
```json
{
  "answer": "No relevant documents found.",
  "sources": []
}

```

## 6. Get Chat History
**Endpoint:** `GET /chat-history/`  

**Description:** Retrieve the logged-in user's chat history (last 50 conversations).

**Header:**
```bash
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "question": "What is the main topic of my document?",
  "chat_history": []
}

```

**Success Response (201):**
```json
[
  {
    "id": 1,
    "query": "What is the main topic?",
    "response": "The main topic is about ...",
    "created_at": "2025-12-16T10:35:00Z"
  },
  {
    "id": 2,
    "query": "Tell me more about section 2",
    "response": "Section 2 covers ...",
    "created_at": "2025-12-16T10:36:00Z"
  }
]

```

**Error Response (400):**
```json
{
  "detail": "Authentication credentials were not provided."
}


```


---

## Setup Instructions

1. Clone the repository:
```bash
git clone https://github.com/mrh-rafi-18/drf-rag-chatbot.git
cd drf-rag-chatbot
```
2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate  
```


3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure .env file with environment variables:
```bash
HUGGINGFACEHUB_API_TOKEN="your_huggingface_api_token_here"
EMAIL="your_email_here"
EMAIL_PASSWORD="your_email_password_here"
```

5. Make migrations and migrate:

```bash
python manage.py makemigrations
python manage.py migrate
```

6. Run the development server:
```bash
python manage.py runserver
```


## Background Task Setup

Background tasks run automatically using **APScheduler** when the server starts.

- **Delete old chat history**: Configurable by days/hours/minutes in `tasks.py`.
- **Send verification email**: Triggered after user registration.

## Deployment Notes

- Set `DEBUG=False` in production.
- Use **Gunicorn** or **Daphne** for ASGI deployment.
- Store vector database inside the project.

```bash
VECTOR_STORE_BASE_DIR = os.path.join(BASE_DIR, "chroma_vectorstore")

```
