from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image
from model import TableExtractor # Import your class from model.py
from llm_service import get_llm_summary ,parse_text_to_structured_json, summarize

print("Starting API server...")
app = FastAPI()

extractor = TableExtractor()

@app.post("/extract-table/")
async def extract_table_from_image(file: UploadFile = File(...)):       # EXTRACT TABLE FROM IMAGE

    try:
        image = Image.open(file.file).convert("RGB")
        
        extracted_data = extractor.extract_table(image)

        return JSONResponse(content=extracted_data)

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/get-normalized-report/")
async def get_nomalized_report(file: UploadFile = File(...)):       # GET NORMALIZED REPORT FROM IMAGE
    try:

        image = Image.open(file.file).convert("RGB")
        normalized_report = extractor.process_image(image,confidence_threshold=0.5)
        return JSONResponse(content=normalized_report)

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    
@app.post("/analyze-report/")
async def analyze_report_endpoint(
    file: UploadFile = File(None, description="An image file of the lab report."),
    text_input: str = Form(None, description="The plain text content of a lab report.")
):
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
            structured_data = extractor.process_image(image, confidence_threshold=0.5)
            

        # --- Text Path ---
        elif text_input:
            print("Processing text input...")
            structured_data = parse_text_to_structured_json(text_input)


        abnormal_results = {
            key: row for key, row in structured_data['data'].items()
            if isinstance(row, dict) and row.get("status") != "Normal"
        } 
        if not abnormal_results:
            return {"summary": "All results are within the normal range."}
        
        final_summary = get_llm_summary(abnormal_results)
        
        return JSONResponse(content=final_summary)

    except Exception as e:
        # This will now catch any errors from the entire pipeline
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/summarize/")
async def summarizer(
    file: UploadFile = File(None, description="An image file of the lab report."),
    text_input: str = Form(None, description="The plain text content of a lab report.")
):
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
            structured_data = extractor.process_image(image, confidence_threshold=0.5)
            

        # --- Text Path ---
        elif text_input:
            print("Processing text input...")
            structured_data = parse_text_to_structured_json(text_input)
            print(structured_data)


        abnormal_results = {
            key: row for key, row in structured_data['data'].items()
            if isinstance(row, dict) and row.get("status") != "Normal"
        } 
        
        if not abnormal_results:
            return {"summary": "All results are within the normal range."}
        
        analyzed_report = get_llm_summary(abnormal_results)
        final_summary = summarize(analyzed_report, structured_data)
        return JSONResponse(content=final_summary)

    except Exception as e:
        # This will now catch any errors from the entire pipeline
        return JSONResponse(status_code=500, content={"error": str(e)})
