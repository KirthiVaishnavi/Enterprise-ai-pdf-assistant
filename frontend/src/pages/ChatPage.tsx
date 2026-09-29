import { useState, useEffect, useRef } from "react"
import { type ConversationResponse, createConversation, getConversations } from "../api/conversations"
import { sendMessage, getMessages, type MessageSource, type MessageResponse } from "../api/messages"
import { useLocation } from "react-router-dom"

function ChatPage() {
    const [conversation, setConversation] =useState<ConversationResponse|null>(null)
    const [conversations, setConversations]=useState<ConversationResponse[]>([])
    const [message, setMessage]=useState('')
    const [chatMessages, setChatMessages]=useState<MessageResponse[]>([])
    const [sendingConversationId, setSendingConversationId]=useState<number|null>(null)
    const [messageError, setMessageError]=useState('')
    const [messageSources, setMessageSources]=useState<MessageSource[]>([])
    const conversationRef = useRef<number | null>(null)
    const location=useLocation()
    
    const selectedDocument = location.state?.document ?? null
    const selectedDocumentConversations = conversations.filter(
        (item) => item.document_id === selectedDocument?.id
    )

    useEffect(() => {
        async function loadConversations() {
            const response = await getConversations()
            setConversations(response)
        }
        loadConversations()
    }, [])

    useEffect(() => {
    conversationRef.current = conversation?.id ?? null
    }, [conversation])

    async function handleSendMessage() {
        if (!conversation || !message.trim()) {
            return
        }
        const conversationId=conversation.id
        
        setSendingConversationId(conversationId)
        setMessageError('')

        try {
            const response = await sendMessage(conversationId, message.trim())
            setMessage('')

            if(conversationRef.current!==conversationId){
                return
            }
            setMessageSources(response.sources)
            setChatMessages((previous) => [
                ...previous, 
                response.user_message,
                response.assistant_message
            ])
        } 
        catch {
            setMessageError('Failed to send message. Please try again.')
        } 
        finally {
            setSendingConversationId(null)
        }
    }

    return (
        <div className="chat-page">

            <div className="chat-header">
                <h1>Chat</h1>
                <p>
                    {selectedDocument
                        ? `Selected: ${selectedDocument.filename}`
                        : 'No document selected'}
                </p>
            </div>

            <div className="chat-layout">
                <aside className="conversation-panel">
                    {
                        selectedDocumentConversations.length === 0 ? (
                            <p className="empty-conversation">
                                No conversations yet.
                            </p>
                        ) :
                        (selectedDocumentConversations.map((item) => (
                            <p
                                key={item.id}
                                onClick={async()=>{
                                    if (sendingConversationId!==item.id){setMessage('')}
                                    setConversation(item)
                                    setMessageError('')
                                    setMessageSources([])
                                    try{
                                        const response = await getMessages(item.id)
                                        setChatMessages(response)
                                    }
                                    catch{
                                        setMessageError('Failed to load conversation.')
                                    }
                                }}
                            >
                                Conversation {item.id}
                            </p>
                        )))
                    }

                    {selectedDocument && (
                        <button 
                            className="new-chat-button"
                            onClick={async ()=>{
                                const newConversation=await createConversation(selectedDocument.id)
                                setConversations((prev)=>[...prev,newConversation])
                                setConversation(newConversation)
                                setChatMessages([])
                                setMessage('')
                                setMessageSources([])
                                setMessageError('')
                            }}>
                            Start New Chat
                        </button>
                    )}
                </aside>

                <main className="chat-panel">
                    {conversation && (
                            <p className="active-conversation">Active conversation: {conversation.id}</p>
                        )}
                    
                    <div className="chat-messages">
                        {!conversation && selectedDocumentConversations.length > 0 && (
                            <p className="empty-chat">
                                Select a conversation to start chatting.
                            </p>
                        )}
                        {conversation && chatMessages.length === 0 && (
                            <p className="empty-chat">
                                Ask a question about your PDF to get started.
                            </p>
                        )}
                        {chatMessages.map((message) => (
                            <div key={message.id}
                            className={`message ${
                                    message.role === 'user'
                                        ? 'message-user'
                                        : 'message-assistant'
                                }`} 
                            >
                                <p>{message.role==='user'? 'You': 'Assistant'} : {message.content}</p>
                                {message.role === 'assistant' && message.id === chatMessages[chatMessages.length - 1]?.id && (
                                
                                <div className="message-sources">
                                    <p>Sources:</p>

                                    {messageSources.map((source) => (
                                    <p key={source.chunk_id}>
                                        Page {source.page_number} · Chunk {source.chunk_id}
                                    </p>
                                    ))}
                                </div>
                                )}
                            </div>
                        ))}
                    </div>

                    {messageError && <p className="chat-error">{messageError}</p>}
                    
                    {sendingConversationId===conversation?.id && <p className="chat-status">Assistant is thinking...</p>}

                    {conversation && (
                        <form className="chat-input" onSubmit={(event) => {
                            event.preventDefault()
                            handleSendMessage()
                        }}>
                            <input
                                type="text"
                                value={message}
                                onChange={(event) => setMessage(event.target.value)}
                                placeholder="Ask a question about your PDF"
                            />
                            <button type="submit" disabled={!message.trim()||sendingConversationId===conversation?.id}>
                                {sendingConversationId===conversation?.id ? "Sending...":'Send'}
                            </button>
                        </form>
                    )}
                </main>
            </div>
        </div>   
    )
}

export default ChatPage