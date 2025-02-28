# Conversational Memory Bot: AI-Powered Photo Gallery Assistant

## 📝 Project Overview
The **Conversational Memory Bot** is an AI-powered chatbot designed to revolutionize how users interact with their personal photo galleries.

## 🧠 Technology Stack

- **Backend:** FastAPI
- **Vector Database:** ChromaDB
- **AI Model:** Gemini 2.0 Flash API
- **Frontend:** React
- **Framework:** Retrieval-Augmented Generation (RAG)

## 🛠️ Setup and Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name
```

2. **Create and configure the `.env` file:**
Create a `.env` file in the root directory and add the following variables:
```env
GEMINI_API_KEY=your-gemini-api-key-here
CHROMADB_PATH=path/to/your/chromadb
IMAGE_UPLOAD_DIR=path/to/uploaded/images
```
Make sure to replace `your-gemini-api-key-here` with your actual Gemini 2.0 Flash API key.

3. **Backend Setup (FastAPI):**
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

4. **Frontend Setup (React):**
```bash
cd frontend
npm install
npm start
```

## 🧪 How to Use

1. **Upload images** through the Batch Image Uploader.
2. **Query images** using natural language in the Chat Interface.
3. **View retrieved images** and descriptions in the interactive gallery.
4. **Find similar images** and explore based on visual similarity.

## 🎯 Future Improvements

- **Advanced Tagging:** Automatically assign descriptive keywords.
- **Enhanced Visual Search:** Improve visual similarity using advanced image embeddings.
- **User Feedback:** Allow users to refine search results through interactive feedback.

## 📝 License
This project is licensed under the [MIT License](LICENSE).

---

💡 *Built with love by David and the team.*

