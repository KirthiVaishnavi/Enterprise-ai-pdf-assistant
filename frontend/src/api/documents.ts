import apiRequest from "./client"

export interface DocumentResponse{
    id: number
    filename: string
    user_id: number
    created_at: string
}

export function uploadDocument(file: File):Promise<DocumentResponse> {
  const formData = new FormData()
  formData.append('file', file)

  return apiRequest('/documents/upload', {
    method: 'POST',
    body: formData,
  })
}

export function getDocuments(){
    return apiRequest('/documents')
}