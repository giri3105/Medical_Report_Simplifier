from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image
from model import TableExtractor # Import your class from model.py
from llm_service import get_llm_summary ,parse_text_to_structured_json

print("Starting API server...")
app = FastAPI()

extractor = TableExtractor()

@app.post("/extract-table/")
async def extract_table_from_image(file: UploadFile = File(...)):

    try:
        # We need to read the file content into a PIL Image
        image = Image.open(file.file).convert("RGB")
        
        # Call the method on your single, pre-loaded extractor instance
        extracted_data = extractor.extract_table(image)

        # Convert integer keys to strings for valid JSON
        

        return JSONResponse(content=extracted_data)

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/get-normalized-report/")
async def get_nomalized_report(file: UploadFile = File(...)):
    try:
        # We need to read the file content into a PIL Image
        image = Image.open(file.file).convert("RGB")
        
        # Call the method on your single, pre-loaded extractor instance
        normalized_report = extractor.process_image(image,confidence_threshold=0.5)

        # Convert integer keys to strings for valid JSON

        return JSONResponse(content=normalized_report)

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    
@app.post("/analyze-report/")
async def analyze_report_endpoint(
    # FIX 1: Parameters are now optional (None is the default) to avoid a 422 error.
    file: UploadFile = File(None, description="An image file of the lab report."),
    text_input: str = Form(None, description="The plain text content of a lab report.")
):
    # These checks are now meaningful because the inputs are optional.
    if not file and not text_input:
        raise HTTPException(status_code=400, detail="You must provide either an image file or a text_input.")
    
    if file and text_input:
        raise HTTPException(status_code=400, detail="Please provide either an image file or a text_input, not both.")

    try:
        structured_data = {}
        
        # --- Image Path ---
        if file:
            print("Processing image input...")
            image = Image.open(file.file).convert("RGB")
            # Step 1: The extractor's full pipeline should produce the final normalized report
            structured_data = extractor.process_image(image, confidence_threshold=0.5)
            

        # --- Text Path ---
        elif text_input:
            print("Processing text input...")
            # FIX 2: Removed `await` because parse_text_to_structured_json is a regular function.
            structured_data = parse_text_to_structured_json(text_input)
            print(structured_data)

        # --- FIX 3: Unified Logic for Summarization ---
        # Both paths now feed their structured_data into this common logic block.
        
        # Step 2: Filter the normalized report for abnormal results
        abnormal_results = {
            key: row for key, row in structured_data.items()
            if isinstance(row, dict) and row.get("status") != "Normal"
        } 
        
        if not abnormal_results:
            return {"summary": "All results are within the normal range."}
        
        # Step 3: Pass ONLY the abnormal results to the summarizer
        final_summary = get_llm_summary(abnormal_results)
        
        return JSONResponse(content=final_summary)

    except Exception as e:
        # This will now catch any errors from the entire pipeline
        return JSONResponse(status_code=500, content={"error": str(e)})


