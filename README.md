# Medical_Report_Simplifier
Medical Report Simplifier , Put in your medical report and understand it like never before 

Setup Instruction :
1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/giri3105/Medical_Report_Simplifier.git](https://github.com/giri3105/Medical_Report_Simplifier.git)
    cd Medical_Report_Simplifier
    ```
2.  **Configure Environment Variables:**
    This project requires a Hugging Face API token to function. The repository includes a template file.
    ```bash
    # Create a copy of the example environment file
    cp .env.example .env
    ```
    Now, open the `.env` file with a text editor and replace the placeholder `"hf_YOUR_TOKEN_HERE"` with your actual Hugging Face token.

3.  **Run in Local:**
   ```bash
    # Run in Local 
    uvicorn main:app 
    ```
