
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

<img width="1920" height="1080" alt="HLD ARCHITECTURE" src="https://github.com/user-attachments/assets/d45e4720-f5c0-469c-8194-4ea9946f94e7" />


flowchart TD
    %% INPUT
    A[TEXT INPUT<br><img src="https://via.placeholder.com/40" width="40"/>]

    %% MODELS
    M1[microsoft/table-transformer-detection<br/>MODEL]
    M2[microsoft/table-structure-recognition<br/>MODEL]
    M3[Cell_Localization & EasyOCR]

    %% PROCESSING NODES
    B[Localized Table in the .png]
    C[Localized Columns and Cells]
    D[JSON Structured Data of the Image]
    E[Normalized JSON Data]
    F[Explanation in Natural Language (JSON format)]
    G[Summary with Normalized Data]

    %% ENDPOINTS
    EP1[/extract-table/]
    EP2[/get-normalized-report/]
    EP3[/analyze-report/]
    EP4[/summarize/]

    %% FLOW
    A -->|Input| M1 --> B
    A --> M2 --> C
    A --> M3 --> D
    B --> D
    C --> D

    %% Extract table endpoint
    D --> EP1

    %% Normalization
    D -->|Normalization Function| E --> EP2

    %% Hugging Face API for explanation
    E -->|HF API model: meta-llama/Llama-3.1-8B-Instruct| F --> EP3

    %% Hugging Face API for summary
    F -->|HF API model: meta-llama/Llama-3.1-8B-Instruct| G --> EP4

