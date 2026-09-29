import { useState, useEffect, useRef } from "react"
import { uploadDocument, type DocumentResponse, getDocuments } from "../api/documents"
import { useNavigate } from "react-router-dom"

function Dashboard(){
    const [file,setFile]=useState<File|null>(null)
    const [document,setDocument]=useState<DocumentResponse|null>(null)
    const [uploading, setUploading]=useState(false)
    const [uploadError, setUploadError]=useState('')
    const [documents, setDocuments]=useState<DocumentResponse[]>([])
    const fileInputRef=useRef<HTMLInputElement|null>(null)
    const navigate=useNavigate()

    async function handleUpload(){
        if(!file){
            return
        }
        setUploading(true)
        setUploadError('')
        try{
            const response=await uploadDocument(file)
            setDocument(response)
            setDocuments((previous)=>[response,...previous])
            setFile(null)

            if (fileInputRef.current) {
                fileInputRef.current.value = ''
            }
        }
        catch{
            setUploadError('Upload failed. Please try again.')
        }
        finally{
            setUploading(false)
        }
    }  

    useEffect(()=>{
        async function loadDocuments(){
            const response=await getDocuments()
            setDocuments(response)
        }
        loadDocuments()
    },[])

    return( 
    <div className="dashboard">
        <h1 className="page-title"> Dashboard</h1>

        <div className="documents-section">
            <h2>Your Documents</h2>

            <div className="document-list">
                {documents.length === 0 ? (
                    <p className="empty-state">
                        No documents yet. Upload a PDF to get started.
                    </p>
                ) :(documents.map((doc) => (
                    <div className="document-card"
                        key={doc.id} 
                        onClick={()=>
                            {
                                navigate('/chat',{ state: {document: doc} })
                            }}
                    >
                        <p>{doc.filename}</p>
                    </div>
                )))}
            </div>
        </div>

        <div className="upload-section">
            <h2>Upload a PDF</h2>

            <input 
                ref={fileInputRef} 
                type="file" 
                accept=".pdf"
                onChange={(event)=>{
                    setFile(event.target.files?.[0] ?? null)
                }}
            />

            <button onClick={handleUpload} disabled={!file||uploading}>
                {uploading? 'Uploading...':'Upload PDF'}
            </button>

            {document && <p>Uploaded: {document.filename} </p>}
            {uploadError && <p>{uploadError}</p>}
        </div>

    </div>
    )
}
export default Dashboard