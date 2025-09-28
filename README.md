
# Medical Report Simplifier 
This AI-powered backend service simplifies medical reports, converting both typed and scanned inputs into patient-friendly explanations. It ensures accurate, normalized results and prevents hallucination via robust OCR error handling and guarded LLM summarization.


## Table of Contents :
1. [Setup Instructions](#setup-instructions)  
2. [Architecture](#architecture)  
3. [API Examples](#api-examples)  
   - [Summarize Report](#summarize-report)  
   - [Analyze Report](#analyze-report)  
   - [Get Normalized Report](#get-normalized-report)  
   - [Extract Table](#extract-table)  

## Setup Instructions
1.  **Clone the repository and install dependencies:**
    ```bash
    git clone https://github.com/giri3105/Medical_Report_Simplifier.git
    cd Medical_Report_Simplifier
    pip install -r requirements.txt
    ```
2.  **Configure Environment Variables:**
    This project requires a Hugging Face API token to function. The repository includes a template file. Quick Link for getting Access Token :([Link](https://huggingface.co/docs/hub/security-tokens)) 
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

<img width="1920" height="1080" alt="HLD ARCHITECTURE" src="https://github.com/user-attachments/assets/3810db4c-011e-428a-bce9-8683bc420777" />


**/summarize/**: Accepts an image of a medical report and returns a brief summary along with normalized data. The summary is generated using a meta LLaMA model via the Hugging Face API.

**/analyze report/**: Provides a more detailed textual analysis of the medical report while enforcing guardrails to prevent giving any medical advice or diagnoses.

**/get_normalized_report/**: Outputs the medical report data in a structured JSON format, including the status of each result—whether it is high, low, or normal.

**/extract table/**: Detects and extracts tables from the report image using a transformer model from Microsoft, then processes each cell with EasyOCR to extract and assemble the text data into JSON format.

### Low Level Architecture

The following image displays a low-level architecture diagram for a multi-stage data processing pipeline, detailing the flow from a raw image to a final, AI-generated summary.

<img width="1920" height="1080" alt="lld architecture" src="https://github.com/user-attachments/assets/6d839b4b-c84e-4bb0-9764-9852519a74c5" />


**Architecture Overview: A Multi-Stage Pipeline**

**Local Processing**: A chain of local models handles the initial heavy lifting—table detection, structure recognition, and OCR—to convert raw images into normalized JSON data.

**Guarded LLM Intelligence**: The structured JSON is then sent as context to an external LLM to generate patient-friendly explanations and summaries, with safety guardrails applied to the output.

**Modular API Design**: Each stage of the pipeline is exposed as a distinct API endpoint, providing excellent modularity for testing and future development.

### Output Guardrail Architecture

This guardrail architecture uses two chained AI prompts: one generates a simple lab explanation, and the second validates its safety. If safe ("TRUE"), the explanation is returned; if not ("FALSE"), an error is given.

<img width="1920" height="1080" alt="GUARDRAIL_ARCHITECTURE" src="https://github.com/user-attachments/assets/9089e3ef-8945-4dc2-a0d8-ac56044f5ee4" />



## API Examples

For Easy testing / validation I have given a `demo.ipynb` in the github repo `~/app/demo.ipynb` where you can test it quickly .
**DISCLAIMER** Keep the server(app) running and update URL and path before testing using the demo file


## Summarize Report
**cURL command**

Replace the `http://127.0.0.1:8000` with the URL from ngrok and `path_of_sample_report` by the actual path of sample_report that is provided in GitHub
```bash
curl --location 'http://127.0.0.1:8000/summarize/' \
--form 'file=@"path_of_sample_report"'
```

**Postman**

Select `POST` request with URL `{https://url_from_ngrok or localhost}/summarize/` and choose `Body` -> `form-data` -> Type **file** in `Key` -> `File` in dropdown -> choose the file (sample_report) for `Value`

Sample given : 
<img width="756" height="249" alt="sample_post_man_request" src="https://github.com/user-attachments/assets/73843381-d3bd-4050-8916-10559dd61f61" />

## Analyze Report
**cURL command**

Replace the `http://127.0.0.1:8000` with the URL from ngrok and `path_of_sample_report` by the actual path of sample_report that is provided in GitHub
```bash
curl --location 'http://127.0.0.1:8000/analyze-report/' \
--form 'file=@"path_of_sample_report"'
```

**Postman**

Same as before but change the route to `/analyze-report/`

## Get Normalized Report
**cURL command**

Replace the `http://127.0.0.1:8000` with the URL from ngrok and `path_of_sample_report` by the actual path of sample_report that is provided in GitHub
```bash
curl --location 'http://127.0.0.1:8000/get-normalized-report/' \
--form 'file=@"path_of_sample_report"'
```

**Postman**

Same as before but change the route to `/get-normalized-report/`

## Extract Table
**cURL command**

Replace the `http://127.0.0.1:8000` with the URL from ngrok and `path_of_sample_report` by the actual path of sample_report that is provided in GitHub
```bash
curl --location 'http://127.0.0.1:8000/extract-table/' \
--form 'file=@"path_of_sample_report"'
```

**Postman**

Same as before but change the route to `/extract-table/`

## To use Text Input : 
**cURL command:**

Replace the `http://127.0.0.1:8000` with the URL from ngrok 

``` bash 
curl --location 'http://127.0.0.1:8000/summarize/' \
--form 'text_input="Patient Report: Complete Blood Count (CBC)
Haemoglobin Estimation: 15.3 g/dl (Reference: 11.1 - 14.1)
Total Leukocyte Count (TLC): 9.9 K/uL (Reference: 6 - 18)
Platelet Count: 107 K/uL (Reference: 200 - 550)
RBC Count (Red Blood Cell): 5.33 10^6/µL (Reference: 4.1 - 5.3)
PCV (Haematocrit): 44.5 % (Reference: 30 - 40)
Mean Corpuscular Volume (MCV): 83.4 fl (Reference: 68 - 84)
Neutrophils: 68 % (Reference: 20 - 65)"'
```

**Postman:**

Sample Image :
<img width="756" height="249" alt="sample_post_man_request_text" src="https://github.com/user-attachments/assets/cdb53389-37aa-479e-a189-27fc3163c017" />

Paste the sample text in the Value column 

Sample Text : 

```txt
Patient Report: Complete Blood Count (CBC)
Haemoglobin Estimation: 15.3 g/dl (Reference: 11.1 - 14.1)
Total Leukocyte Count (TLC): 9.9 K/uL (Reference: 6 - 18)
Platelet Count: 107 K/uL (Reference: 200 - 550)
RBC Count (Red Blood Cell): 5.33 10^6/µL (Reference: 4.1 - 5.3)
PCV (Haematocrit): 44.5 % (Reference: 30 - 40)
Mean Corpuscular Volume (MCV): 83.4 fl (Reference: 68 - 84)
Neutrophils: 68 % (Reference: 20 - 65)
```
