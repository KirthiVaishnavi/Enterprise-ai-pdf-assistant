from fastapi import HTTPException, status
import pymupdf

def extract_pages(file_bytes)->list:
    try:
        pdf_document=pymupdf.open(stream=file_bytes, filetype="pdf")
    
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid PDF file"
            )
    
    try:
        pages=[]
        
        for page_number, page in enumerate(pdf_document,start=1):
            text=page.get_text().strip()
            if not text:
                continue
            pages.append({
                    "page_number":page_number,
                    "text":text
                }) 
             
        return pages
    
    finally:
        pdf_document.close()
    