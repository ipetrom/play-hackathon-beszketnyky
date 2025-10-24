import React, { useEffect, useRef } from 'react'
import { Send, Bot, User, Zap, Brain, Copy, ThumbsUp, ThumbsDown } from 'lucide-react'
import { useAgentStore, Message } from '../stores/agentStore'
import toast from 'react-hot-toast'

const ChatView: React.FC = () => {
  const {
    currentThread,
    isLoading,
    error,
    sendMessage,
    sendStreamingMessage,
    streamingEnabled,
    clearError,
    createNewThread,
  } = useAgentStore()

  const [inputValue, setInputValue] = React.useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [currentThread?.messages])

  // Focus input on load
  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!inputValue.trim() || isLoading) return

    const message = inputValue.trim()
    setInputValue('')

    try {
      if (streamingEnabled) {
        await sendStreamingMessage(message)
      } else {
        await sendMessage(message)
      }
    } catch (error) {
      toast.error('Błąd podczas wysyłania wiadomości')
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e as any)
    }
  }

  const copyMessage = (content: string) => {
    navigator.clipboard.writeText(content)
    toast.success('Skopiowano do schowka')
  }

  const getAgentIcon = (agentUsed?: string) => {
    switch (agentUsed) {
      case 'workforce':
        return <Zap className="w-4 h-4 text-yellow-500" />
      case 'strategist':
        return <Brain className="w-4 h-4 text-purple-500" />
      default:
        return <Bot className="w-4 h-4 text-blue-500" />
    }
  }

  const getAgentName = (agentUsed?: string) => {
    switch (agentUsed) {
      case 'workforce':
        return 'Workforce Agent (Mistral)'
      case 'strategist':
        return 'Strategist Agent (GPT-4o)'
      default:
        return 'AI Assistant'
    }
  }

  // Create new thread if none exists
  if (!currentThread) {
    return (
      <div className="flex items-center justify-center h-full bg-gray-50">
        <div className="text-center">
          <Bot className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-700 mb-2">
            Witaj w AI Agents Platform
          </h2>
          <p className="text-gray-500 mb-6 max-w-md">
            Rozpocznij rozmowę z naszymi specjalistycznymi agentami AI. 
            System automatycznie wybierze najlepszego agenta dla Twojego zapytania.
          </p>
          <button
            onClick={createNewThread}
            className="btn-primary"
          >
            Rozpocznij rozmowę
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full">
      {/* Error banner */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 flex items-center justify-between">
          <span>{error}</span>
          <button
            onClick={clearError}
            className="text-red-500 hover:text-red-700 font-medium"
          >
            ✕
          </button>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {currentThread.messages.map((message) => (
          <MessageBubble
            key={message.id}
            message={message}
            onCopy={copyMessage}
            getAgentIcon={getAgentIcon}
            getAgentName={getAgentName}
          />
        ))}
        
        {isLoading && (
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0 w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
              <Bot className="w-4 h-4 text-gray-600" />
            </div>
            <div className="flex-1 bg-gray-100 rounded-lg p-4">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-gray-200 p-6">
        <form onSubmit={handleSubmit} className="flex gap-4">
          <div className="flex-1">
            <textarea
              ref={inputRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Napisz swoją wiadomość... (Enter - wyślij, Shift+Enter - nowa linia)"
              className="w-full p-3 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              rows={3}
              disabled={isLoading}
            />
          </div>
          <button
            type="submit"
            disabled={!inputValue.trim() || isLoading}
            className="flex-shrink-0 bg-primary-600 hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white p-3 rounded-lg transition-colors duration-200 flex items-center justify-center"
          >
            <Send className="w-5 h-5" />
          </button>
        </form>
      </div>
    </div>
  )
}

// Message component
interface MessageBubbleProps {
  message: Message
  onCopy: (content: string) => void
  getAgentIcon: (agentUsed?: string) => React.ReactNode
  getAgentName: (agentUsed?: string) => string
}

const MessageBubble: React.FC<MessageBubbleProps> = ({
  message,
  onCopy,
  getAgentIcon,
  getAgentName,
}) => {
  const isUser = message.role === 'user'

  return (
    <div className={`flex items-start gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
      {/* Avatar */}
      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
        isUser 
          ? 'bg-primary-600 text-white' 
          : 'bg-gray-200 text-gray-600'
      }`}>
        {isUser ? <User className="w-4 h-4" /> : getAgentIcon(message.agent_used)}
      </div>

      {/* Message content */}
      <div className={`flex-1 max-w-3xl ${isUser ? 'text-right' : ''}`}>
        {/* Header */}
        <div className={`flex items-center gap-2 mb-1 text-sm text-gray-500 ${
          isUser ? 'justify-end' : ''
        }`}>
          <span className="font-medium">
            {isUser ? 'Ty' : getAgentName(message.agent_used)}
          </span>
          <span>
            {new Intl.DateTimeFormat('pl-PL', {
              hour: '2-digit',
              minute: '2-digit',
            }).format(message.timestamp)}
          </span>
        </div>

        {/* Content */}
        <div className={`rounded-lg p-4 ${
          isUser 
            ? 'bg-primary-600 text-white' 
            : 'bg-gray-100 text-gray-900'
        }`}>
          <div className="prose prose-sm max-w-none">
            {message.content.split('\n').map((line, index) => (
              <div key={index}>{line}</div>
            ))}
          </div>
        </div>

        {/* Actions */}
        {!isUser && (
          <div className="flex items-center gap-2 mt-2">
            <button
              onClick={() => onCopy(message.content)}
              className="text-gray-400 hover:text-gray-600 p-1 rounded transition-colors duration-200"
              title="Kopiuj"
            >
              <Copy className="w-4 h-4" />
            </button>
            <button
              className="text-gray-400 hover:text-green-600 p-1 rounded transition-colors duration-200"
              title="Dobra odpowiedź"
            >
              <ThumbsUp className="w-4 h-4" />
            </button>
            <button
              className="text-gray-400 hover:text-red-600 p-1 rounded transition-colors duration-200"
              title="Słaba odpowiedź"
            >
              <ThumbsDown className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default ChatView