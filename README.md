# Medical_Report_Simplifier
Medical Report Simplifier , Put in your medical report and understand it like never before 

## Table of Contents  
1. [Setup Instructions](#setup-instructions)  
2. [Architecture](#architecture)  
3. [API Examples](#api-examples)  
   - [Summarize Report](#summarize-report)  
   - [Analyze Report](#analyze-report)  
   - [Get Normalized Report](#get-normalized-report)  
   - [Extract Table](#extract-table)  

---

## Setup Instructions  

### 1. Clone the repository  


# Medical_Report_Simplifier
Medical Report Simplifier , Put in your medical report and understand it like never before 

Setup Instruction :

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


    ```
Now use the URL provided by ngrok or `http://localhost:8000` for testing API end points 

make it a proper readme.md file and i also want table of contents with Setup Instruction that is this , then ar
