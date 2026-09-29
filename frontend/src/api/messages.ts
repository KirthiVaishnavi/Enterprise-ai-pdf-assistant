import apiRequest from './client'

export interface MessageResponse {
    id: number
    conversation_id: number
    role: string
    content: string
    created_at: string
}

export interface MessageSource {
    chunk_id: number
    page_number: number
}

export interface MessageExchangeResponse {
    user_message: MessageResponse
    assistant_message: MessageResponse
    sources: MessageSource[]
}

export function sendMessage(
conversationId: number,
content: string
): Promise<MessageExchangeResponse> {
    return apiRequest(`/conversations/${conversationId}/messages/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      content,
    }),
  })
}

export function getMessages(conversationId:number):Promise<MessageResponse[]>{
    return apiRequest(`/conversations/${conversationId}/messages/`)
}