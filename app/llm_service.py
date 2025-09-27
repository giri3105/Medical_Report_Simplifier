import os
import json
import requests
import re

# Corrected, safer prompt for generation
GENERATION_COLANG = '''template generate_explanation {
  role system
  content """
You are a helpful medical assistant. Your task is to explain lab results in simple language that a general person can understand.
- Focus ONLY on explaining what the result means in a simple way.
- Avoid technical terms and alarming tones.
- Keep each explanation short and clear.
- Do NOT provide any medical advice or recommendations.
- Do NOT mention any medicine names.
- YOUR FINAL OUTPUT MUST BE A VALID JSON OBJECT WITH A SINGLE KEY "explanations" WHICH CONTAINS A LIST OF STRINGS.
  """
}
'''

# Corrected, clearer prompt for validation
VALIDATION_COLANG = '''template validate_explanation {
  role system
  content """
You are an AI safety validator. Your only task is to answer with TRUE or FALSE based on the following rules:
- Check if there is any abuse.
- Check if there is any harmful or dangerous advice.
- No complex medical terms 
- Check if there is any misinformation or misleading content.
- Check if the result is hallucinated or fabricated.
- Answer with only the single word "TRUE" if the text is safe and follows the rules mentioned above, otherwise answer with only the single word "FALSE".
  """
}
'''

# --- Setup (Assumes API_KEY is set in environment or hardcoded safely) ---
API_KEY = os.getenv("HF_TOKEN", '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')
API_URL = "https://router.huggingface.co/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def query_llm(payload):
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    response.raise_for_status()
    return response.json()

def extract_json(text: str) -> dict:
    start = text.find('{')
    end = text.rfind('}') + 1
    if start == -1 or end == 0:
        raise ValueError("No JSON object found in the response text.")
    return json.loads(text[start:end])

def extract_prompt(template_str):
    match = re.search(r'content\s+"""(.*?)"""', template_str, re.DOTALL)
    return match.group(1).strip() if match else ""

def get_llm_summary(abnormal_lab_results: dict) -> dict:
    gen_sys_prompt = extract_prompt(GENERATION_COLANG)
    val_sys_prompt = extract_prompt(VALIDATION_COLANG)

    user_prompt = f"""Here are my abnormal lab results in JSON format:
{json.dumps(abnormal_lab_results, indent=2)}

Please provide the simple explanations in the required JSON format."""

    # Generation payload
    gen_payload = {
        "messages": [
            {"role": "system", "content": gen_sys_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "model": "meta-llama/Llama-3.1-8B-Instruct"
    }

    try:
        # Query for generation
        gen_response = query_llm(gen_payload)
        gen_content = gen_response["choices"][0]["message"]["content"]
        summary_json = extract_json(gen_content)

        # Validation payload
        val_payload = {
            "messages": [
                {"role": "system", "content": val_sys_prompt},
                {"role": "user", "content": json.dumps(summary_json, indent=2)}
            ],
            "model": "meta-llama/Llama-3.1-8B-Instruct"
        }

        val_response = query_llm(val_payload)
        verdict = val_response["choices"][0]["message"]["content"].strip().upper()
        
        if verdict == "TRUE":
            return summary_json
        else:
            return {"error": "Generated explanation failed validation guardrail."}
            
    except Exception as e:
        return {"error": f"An error occurred in the pipeline: {e}"}


# Add this new function to your llm_service.py file

def parse_text_to_structured_json(plain_text: str) -> dict:
    """
    Uses an LLM to parse unstructured lab report text into a structured JSON object.
    """
    system_prompt = """You are an automated data extraction service. Your sole function is to read unstructured lab report text and convert it into a structured JSON object.

Follow these rules:
1.  For each parameter, extract its result and reference range.
2.  Calculate a "status" by comparing the result to the range ("Normal", "High", "Low"). If a range is ambiguous or missing, the status is "Undetermined".
3.  The final response MUST be ONLY the valid JSON object, starting with `{` and ending with `}`. Do not include any conversational text, explanations, or markdown fences.

---
**EXAMPLE**

**INPUT TEXT:**

pH: 7.38 (7.350 - 7.450)
ck + : 6.0 mrol/l (3.5 - 5.5)
cLac: 1.8 mmolfl (0.5 - 1.6)
**EXPECTED OUTPUT:**

**CORRECT JSON OUTPUT:**

{
    "0": {
        "parameter": "pH",
        "results": "7.38",
        "range": "7.350 - 7.450",
        "status": "Normal"
    },
    "1": {
        "parameter": "ck +",
        "results": "6.0",
        "range": "3.5 - 5.5 mrol/l",
        "status": "High"
    },
    "2": {
        "parameter": "cLac",
        "results": "1.8",
        "range": "0.5 - 1.6 mmolfl",
        "status": "High"
    }
}

---
"""

    user_prompt = f"""Please extract the data from the following lab report text:
{plain_text}"""

    print("Parsing plain text with LLM...")
    # This calls the same query_llm function you already have
    response = query_llm({
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "model": "meta-llama/Llama-3.1-8B-Instruct"
    })
    print(response)
    try:
        # 1. Get the full content string (your code was correct)
        content_string = response["choices"][0]["message"]["content"]

        # 2. Find the start and end of the JSON object within the string
        json_start_index = content_string.find('{')
        json_end_index = content_string.rfind('}') + 1

        if json_start_index != -1 and json_end_index != 0:
            # 3. Slice the string to get only the JSON part
            json_substring = content_string[json_start_index:json_end_index]
            
            # 4. Parse the clean JSON substring
            extracted_json = json.loads(json_substring)
            
            return extracted_json
        else:
            print("Error: Could not find a JSON object in the response content.")

    except (KeyError, IndexError, json.JSONDecodeError) as e:
        print(f"An error occurred while parsing the response: {e}")