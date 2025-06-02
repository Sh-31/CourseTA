import shutil
import uuid
import os
from fastapi import APIRouter, File, UploadFile, HTTPException
from tools.pdf_extractor_tool import extract_text_from_pdf, save_extracted_text
from tools.transcript_tool import transcript_loader

router = APIRouter()
ASSETS_DIR = "assets"

@router.post("/upload_file/")
async def upload_file_api(file: UploadFile = File(...)):
    """
    Handles both PDF and audio/video file uploads, extracts text or transcription,
    and saves both in the 'assets' directory organized by a unique ID.
    """
    print(f"Received file upload: {file.filename}")
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded.")

    file_id = str(uuid.uuid4())
    file_dir = os.path.join(ASSETS_DIR, file_id)
    os.makedirs(file_dir, exist_ok=True)

    file_path = os.path.join(file_dir, file.filename)
    text_path = os.path.join(file_dir, "extracted_text.txt")
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        content_type = file.content_type.lower() if file.content_type else ""
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        print(f"Processing file: {file.filename}, Content-Type: {content_type}, Extension: {file_ext}")
        
        # Process based on file type
        if content_type == "application/pdf" or file_ext == ".pdf":
            print(f"Processing as PDF: {file_path}")
            extracted_documents = extract_text_from_pdf(file_path)
            save_extracted_text(extracted_documents, text_path)
            print("PDF text extraction complete")

        elif (content_type.startswith("audio/") or 
              content_type.startswith("video/") or 
              file_ext in [".mp3", ".mp4", ".wav", ".avi", ".mov", ".mkv", ".flv"]):
            print(f"Processing as audio/video: {file_path}")
            transcription = transcript_loader(file_path)
            with open(text_path, "w", encoding="utf-8") as f:
                f.write(transcription)
            print("Audio/Video transcription complete")

        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {content_type or file_ext}. Only PDF, audio, or video files are allowed."
            )

        return {
            "message": "File processed successfully",
            "id": file_id,
            "text_path": text_path,
            "original_file_path": file_path
        }
        
    except Exception as e:
        if os.path.exists(file_dir): # Clean up the directory if an error occurs
            shutil.rmtree(file_dir)
        error_msg = f"An error occurred during file processing: {str(e)}"
        print(f"ERROR: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)
    
    finally:
        file.file.close()
