
# never-forget/extraction_engine.py
# Core Extraction Engine for the Never-Forget Memory System

import json
import os
from scripts.total_recall_search import total_recall_search # Assuming this is available in the path

def extract_memory(raw_chat_data: dict, search_queries: list) -> str:
    """
    Orchestrates the retrieval and extraction process.

    :param raw_chat_data: The original raw message metadata and content.
    :param search_queries: A list of queries derived from the raw chat data.
    :return: JSON string containing structured memory artifacts.
    """
    print(f"--- Starting Extraction Engine for chat_id: {raw_chat_data.get('chat_id')} ---")
    
    # 1. Execute Retrieval (Using the defined tool)
    print("Executing total-recall-search for context...")
    try:
        # In a real implementation, this would handle pagination/batches
        search_results = total_recall_search(query=search_queries[0], maxResults=5, includeTools=True)
        print("Retrieval complete.")
    except Exception as e:
        print(f"ERROR: Total recall search failed: {e}")
        search_results = []

    # 2. LLM Extraction and Structuring (This is where the prompt logic goes)
    # We use a comprehensive prompt that includes the raw data, the search results,
    # and demands a specific JSON structure.
    
    extraction_prompt = f"""
    You are the Never-Forget Memory Extraction Agent. Your task is to synthesize
    all provided context into structured, permanent memories.

    CONTEXT:
    - Raw Chat Data: {json.dumps(raw_chat_data)}
    - Search Results (Artifacts): {search_results}

    INSTRUCTIONS:
    1. Analyze the conversation flow to identify discrete, actionable 'facts', 'decisions', and 'learnings'.
    2. Use the search results to enrich the raw chat data.
    3. STRICTLY output a single JSON object matching the required schema. Do not include any preamble or explanation outside the JSON block.

    REQUIRED JSON SCHEMA:
    {{
      "metadata": {{
        "source_chat_id": "string",
        "source_timestamp": "string",
        "summary_key": "string (a brief, unique descriptor for this memory block)"
      }},
      "memory_entries": [
        {{
          "type": "fact" | "decision" | "learning" | "task",
          "summary": "A concise, single-sentence summary.",
          "details": "A detailed paragraph expanding on the summary, citing sources if possible.",
          "source_references": ["Source 1", "Source 2"] 
        }}
        // ... more entries
      ]
    }}
    """
    
    print("Sending data to LLM for structured extraction...")
    # Placeholder for the actual LLM call
    # result = llm_call(prompt=extraction_prompt, model="opus") 
    
    # For simulation purposes, we return a mock structured JSON
    mock_json = {
      "metadata": {
        "source_chat_id": raw_chat_data.get('chat_id'),
        "source_timestamp": raw_chat_data.get('timestamp'),
        "summary_key": "Initial Never-Forget Engine Run"
      },
      "memory_entries": [
        {
          "type": "learning",
          "summary": "The process requires synthesizing raw chat data with external artifacts for accurate memory formation.",
          "details": "The engine successfully integrated the simulated total-recall-search output with the conversational context provided.",
          "source_references": ["Search Result 1 (Simulated)"]
        }
      ]
    }

    return json.dumps(mock_json, indent=2)

if __name__ == "__main__":
    # Example Usage Simulation (Mocking Inputs)
    mock_raw_data = {
        "chat_id": "telegram:8755120444",
        "message_id": "22915",
        "sender_id": "8755120444",
        "sender": "Bob Reilly",
        "timestamp": "Wed 2026-05-13 17:58 EDT"
    }
    
    # Note: The search query must be derived from the chat context, 
    # e.g., a key topic from the conversation.
    mock_queries = ["Never-forget memory system implementation details", "Project_Never_Forget_Core.md"]
    
    extracted_json = extract_memory(mock_raw_data, mock_queries)
    
    print("\n--- Extraction Complete (JSON Output) ---\n")
    print(extracted_json)

# Next steps:
# 1. Test this script with real, streamed conversation chunks.
# 2. Refine the LLM prompt to handle ambiguity and conflicting sources.
# 3. Integrate error handling and rate limit management.
