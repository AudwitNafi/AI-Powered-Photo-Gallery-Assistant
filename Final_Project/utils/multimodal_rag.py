import os
import chromadb
import google.generativeai as genai
from PIL import Image
import json
from datetime import datetime
from typing import List, Dict, Optional
from dotenv import load_dotenv
from chromadb_config import configure_db

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL")
image_collection, desc_collection = configure_db()

system_instruction = "You are a photo gallery assistant. Your responses should assist in retrieving relevant images, describing images, or asking if users want relevant images based on their previous prompts."
model = genai.GenerativeModel(MODEL)
assistant_model = genai.GenerativeModel(MODEL, system_instruction=system_instruction)


def process_query(query: Optional[str] = None, image_path: Optional[str] = None) -> Dict:
    """Handle hybrid queries across both collections"""
    results = {"images": [], "text": []}

    # Parse metadata filters using Gemini
    text_filters = {}
    if query:
        text_model = model
        prompt = f"""Extract from this query: "{query}"
        - date_range (start/end dates as YYYY-MM-DD)
        - location
        Return JSON with those fields. Keep original query as search_text."""

        try:
            response = text_model.generate_content(prompt)
            filters = json.loads(response.text.replace('```json', '').replace('```', ''))
            if filters.get("date_range"):
                text_filters["date"] = {
                    k: v for k, v in filters["date_range"].items() if v
                }
            if filters.get("location"):
                text_filters["location"] = filters["location"].lower()
            query = filters.get("search_text", query)
        except:
            pass

    # Search image collection
    if image_path:
        img_results = image_collection.query(
            query_uris=[image_path],
            where=text_filters,
            n_results=10
        )
        results["images"] = _format_results(img_results, collection_type="images")

    # Search text collection
    if query:
        text_results = desc_collection.query(
            query_texts=[query],
            where=text_filters,
            n_results=10
        )
        results["text"] = _format_results(text_results, collection_type="text")

    return results


def _format_results(results: Dict, collection_type: str) -> List[Dict]:
    """Format results based on collection type"""
    formatted = []
    for ids, distances, metadatas in zip(results["ids"], results["distances"], results["metadatas"]):
        for id, distance, meta in zip(ids, distances, metadatas):
            entry = {
                "id": id,
                "score": float(1 - distance),
                "date": meta["date"],
                "location": meta["location"],
                "type": collection_type
            }
            if collection_type == "text":
                entry["description"] = meta["description"]
                entry["tags"] = meta["tags"].split(", ")
            formatted.append(entry)
    return sorted(formatted, key=lambda x: x["score"], reverse=True)


def generate_response(results: Dict) -> str:
    """Generate unified response using Gemini"""
    text_model = genai.GenerativeModel('gemini-pro')

    context = f"Found {len(results['images'])} visual matches and {len(results['text'])} text matches.\n"

    if results["images"]:
        context += "Visual matches include: "
        context += ", ".join(set([os.path.basename(img['id']) for img in results["images"][:3]])) + "\n"

    if results["text"]:
        context += "Text matches include: "
        context += ", ".join(set([desc['tags'][0] for desc in results["text"][:3]])) + "\n"

    response = text_model.generate_content(
        f"Create a concise summary of these search results: {context}"
    )
    return response.text