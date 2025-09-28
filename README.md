
# Medical Report Simplifier 
Medical Report Simplifier , Put in your medical report and understand it like never before 


## Table of Contents :
1. [Setup Instructions](#setup-instructions)  
2. [Architecture](#architecture)  
3. [API Examples](#api-examples)  
   - [Summarize Report](#summarize-report)  
   - [Analyze Report](#analyze-report)  
   - [Get Normalized Report](#get-normalized-report)  
   - [Extract Table](#extract-table)  

## Setup Instructions
1.  **Clone the repository:**
    ```bash
    git clone https://github.com/giri3105/Medical_Report_Simplifier.git
    cd Medical_Report_Simplifier
    ```
2.  **Configure Environment Variables:**
    This project requires a Hugging Face API token to function. The repository includes a template file.
    ```bash
    # Create a copy of the example environment file
    cd app
    cp .env_example .env    
    ```
    Now, open the `.env` file with a text editor and replace the placeholder  with your actual Hugging Face token .

3.  **Run in Local:**
    ```bash
    #Run server locally
    uvicorn main:app
    ```

4.  **Run with Docker:**
     Alternatively if you wish to run it with a docker 
    ```bash
    cd ..
    docker compose build 
    docker compose up -d
    ```

4.  **Tunnel thorugh ngrok:**
    Open a new terminal / split terminal  
    ```bash
    ngrok http 8000
    ```
    This will return a https URL which we can further use for API end point testing through cURL commands or Postman 



## Architecture

### High Level Architecture

Routes Available illustrated with the picture

<img width="1920" height="1080" alt="HLD ARCHITECTURE" src="https://github.com/user-attachments/assets/15d6ccab-984d-48d0-9a9e-e4f9ae254932" />


**/summarize/**: Accepts an image of a medical report and returns a brief summary along with normalized data. The summary is generated using a meta LLaMA model via the Hugging Face API.

**/analyze report/**: Provides a more detailed textual analysis of the medical report while enforcing guardrails to prevent giving any medical advice or diagnoses.

**/get_normalized_report/**: Outputs the medical report data in a structured JSON format, including the status of each result—whether it is high, low, or normal.

**/extract table/**: Detects and extracts tables from the report image using a transformer model from Microsoft, then processes each cell with EasyOCR to extract and assemble the text data into JSON format.

### Low Level Architecture

The following image displays a low-level architecture diagram for a multi-stage data processing pipeline, detailing the flow from a raw image to a final, AI-generated summary.

<img width="1920" height="1080" alt="lld architecture" src="https://github.com/user-attachments/assets/dba87d2d-9632-4b13-b630-6cccd2ba5947" />


**Architecture Overview: A Multi-Stage Pipeline**

**Local Processing**: A chain of local models handles the initial heavy lifting—table detection, structure recognition, and OCR—to convert raw images into normalized JSON data.

**Guarded LLM Intelligence**: The structured JSON is then sent as context to an external LLM to generate patient-friendly explanations and summaries, with safety guardrails applied to the output.

**Modular API Design**: Each stage of the pipeline is exposed as a distinct API endpoint, providing excellent modularity for testing and future development.

### Output Guardrail Architecture

<img width="1920" height="1080" alt="GUARDRAIL_ARCHITECTURE" src="https://github.com/user-attachments/assets/814f39ad-d3c0-4144-a41d-6b4780e3edec" />

This guardrail architecture uses two chained AI prompts: one generates a simple lab explanation, and the second validates its safety. If safe ("TRUE"), the explanation is returned; if not ("FALSE"), an error is given.



##API Examples

