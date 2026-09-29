import apiRequest from './client'

export interface ConversationResponse {
  id: number
  user_id: number
  document_id: number
  created_at: string
}

export function createConversation(
  documentId: number
): Promise<ConversationResponse> {
  return apiRequest('/conversations/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      document_id: documentId,
    }),
  })
}

export function getConversations(): Promise<ConversationResponse[]> {
  return apiRequest('/conversations/')
}