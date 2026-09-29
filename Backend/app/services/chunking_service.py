from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunk_pages(pages:list, chunk_size=600, overlap=100):
    chunks=[]
    
    splitter= RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap
        )
    
    for page in pages:
        page_number=page["page_number"]
        text=page["text"]
        
        page_chunks=splitter.split_text(text)
        
        for chunk_index, chunk_text in enumerate(page_chunks):
            chunk={
                "page_number":page_number,
                "chunk_index":chunk_index,
                "text":chunk_text
            }
            
            chunks.append(chunk)
        
    return chunks