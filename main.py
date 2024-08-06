import fitz  # PyMuPDF
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import re
import os 

app = FastAPI()


def extract_text_with_positions(pdf_path):
    print("iNside positions")
    doc = fitz.open(pdf_path)
    text_positions = []
    for page in doc:
        for block in page.get_text("blocks"):
            if block[6] == 0:  # Text blocks
                text_positions.append({
                    'text': block[4].strip(),
                    'bbox': block[:4]  # (x0, y0, x1, y1)
                })
    doc.close()
    return text_positions

def extract_text_from_positions(text_positions):
    text = ""
    for i in text_positions:
        text+=i["text"]+" "
    return text

@app.post("/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    pdf_path = f"./{file.filename}"
    try:
        # Save the uploaded file
        with open(pdf_path, "wb") as f:
            f.write(await file.read())

        # Extract text positions and draw rectangles
        print("PDF Input Done")
        text_positions = extract_text_with_positions(pdf_path)
        print("Posititons done ",text_positions)
        aggregated_text = extract_text_from_positions(text_positions)
        print("Posititons done ",aggregated_text)

        # Cleanup files
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

        return JSONResponse(content={"text": aggregated_text , "TextPositions":text_positions})
        

    except Exception as e:
        # Ensure files are cleaned up on error
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        return JSONResponse(content={"error": str(e)}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    