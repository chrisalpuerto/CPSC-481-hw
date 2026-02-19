# CPSC 481
# HW 1
# TOPIC 4: Stance A: Predictable (The agent stops/logs errors when logic is unclear).

"""
NAMES:

Christopher Alpuerto - Prompter, Architect
Andrew Mankin
Nathaniel Obeso

"""

"""
Basketball Video Analysis AI Agent

This module implements an AI agent that leverages Google's Gemini/Vertex AI to analyze
basketball videos. The agent accepts a video input (via GCS URI) along with a customizable
prompt and performs intelligent analysis of the video content.

How it works:
1. The agent initializes a connection to Google's Vertex AI service with the Gemini model.
2. A video file (stored in Google Cloud Storage) is passed to the model along with a prompt.
3. The Gemini model processes the video and returns a structured analysis of basketball shots,
   including player identification, shot type, location, timing, result, and form analysis.

Error Handling Philosophy:
- The agent is designed to fail gracefully and log meaningful error messages.
- When the agent encounters unclear logic or unexpected states, it halts execution,
  logs the error with context, and returns a structured error response.
- This ensures that failures are traceable and do not result in silent corruption of results.

Dependencies:
- google.genai: Google's Generative AI SDK for Vertex AI integration
- logging: Python's standard logging module for error tracking
"""

import json
from google.genai import types
import google.genai as genai
import logging
from prompts import prompt

class VideoAnalysisError(Exception):
    pass
class InvalidVideoError(Exception):
    pass
class InvalidCredentialsError(Exception):
    pass


prompt = prompt()

def vertex_summarize(gcs_uri, analysis_choice="regular"):
    try:
        vertex_client = genai.Client(
            vertexai=True,
            project="project-01",
            location="us-central1",
            http_options=types.HttpOptions(timeout=600000)
        )
        print(f"VERTEX SUMMARIZATION: ANALYSIS CHOICE: {analysis_choice}")
    except InvalidCredentialsError as e:
        # AGENT HALT: Credentials are invalid or missing - the agent cannot authenticate
        # with Vertex AI. Logs the error and returns immediately to prevent unauthorized access attempts.
        logging.error(f"Invalid credentials error: {e}")
        return {"error": e}
    try:
        prompt_use = prompt
        if analysis_choice == "pro":
            print("VERTEX: Using PRO analysis prompt (all parameters)")
            prompt_use = prompt()
        else:
            print("VERTEX: Using REGULAR analysis prompt (shot outcomes only)")
        max_retries = 2
        for attempt in range(max_retries):
            logging.info(f"DEBUG: Vertex summarize, attempt {attempt+1}")
            model = "gemini-2.5-flash"
            prompt = prompt_use
            response = vertex_client.models.generate_content(
                model=model,
                contents=[
                    prompt,
                    types.Part.from_uri(
                        file_uri = gcs_uri,
                        mime_type = "video/mp4"
                    ),
                ],
            )
            logging.info(f"VERTEX: Response received.")
            break
            
        print(type(response))
        text_response = response.text
        raw_text = getattr(response, "text", None)
        if not raw_text:
            try:
                raw_text = response.candidates[0].content.parts[0].text
            except Exception as e:
                # AGENT HALT: Gemini/Vertex returned a response but it contains no extractable text.
                # This indicates unclear or malformed output from the model. The agent stops here
                # and returns an error rather than proceeding with empty/invalid data.
                return {"ok": False, "error": f"VERTEX: No text in Gemini response: {e}"}
        clean_text = raw_text.strip() # return output as a string for now
        print("VERTEX RAW GEMINI OUTPUT:", raw_text)
        try:
            return json.loads(clean_text)
        except json.JSONDecodeError as e:
            # AGENT FALLBACK: The model returned valid text but not in JSON format.
            # Rather than halting, the agent logs the parsing failure and returns the raw text.
            # This allows downstream consumers to still use the unstructured response.
            logging.info(f"(VERTEX_SUMMARIZE): Failed to parse Gemini output as JSON: {e} ")
            return clean_text
        
    except FileNotFoundError:
        # AGENT HALT: The specified video file does not exist at the given GCS URI.
        # The agent cannot proceed without a valid video input. Logs the missing file
        # path and returns an error to inform the caller of the invalid input.
        logging.error(f"ERROR: file not found: {str(e)}")
        return {"ok": False, "error": f"VERTEX: File not found: {gcs_uri}"}
    except VideoAnalysisError:
        # AGENT HALT: Vertex/Gemini encountered an error while processing the video content.
        # This may occur due to video corruption, unsupported format, or model limitations.
        # The agent stops and logs the error to help diagnose the analysis failure.
        logging.error(f"ERROR: error analyzing video: {str(e)}")
        return {"ok": False, "error": e}
    except InvalidVideoError:
        # AGENT HALT: The video input is invalid (e.g., inappropriate content, wrong format,
        # or content that violates usage policies). The agent refuses to proceed with invalid
        # videos and logs the rejection for audit purposes.
        logging.error(f"ERROR: invalid video input: {str(e)}")
        return {"ok": False, "error": e}
    except Exception as e:
        # AGENT HALT: Catch-all for any unexpected errors not handled by specific exceptions.
        # When the agent encounters unknown/unclear error states, it stops execution immediately,
        # logs the full error details for debugging, and returns a structured error response.
        # This prevents the agent from continuing in an undefined state.
        logging.error(f"ERROR: general error: {str(e)}")
        return {"ok": False, "error": e}

def main():
    # gcs uri placeholder, may replace with real gcs uri later
    gcs_uri = "gcs://..."
    res = vertex_summarize(gcs_uri)
    print(f"Gemini API analysis complete: {res}")

if __name__ == "main":
    main()