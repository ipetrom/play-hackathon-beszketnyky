import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface Message {
  id: string
  content: string
  role: 'user' | 'assistant'
  timestamp: Date
  agent_used?: 'workforce' | 'strategist' | 'supervisor'
  metadata?: Record<string, any>
}

export interface ConversationThread {
  id: string
  title: string
  messages: Message[]
  created_at: Date
  updated_at: Date
}

export interface AgentState {
  // Stan konwersacji
  currentThread: ConversationThread | null
  threads: ConversationThread[]
  isLoading: boolean
  error: string | null
  
  // Ustawienia agentów
  preferredAgent: 'auto' | 'workforce' | 'strategist'
  streamingEnabled: boolean
  
  // Actions
  createNewThread: () => void
  selectThread: (threadId: string) => void
  sendMessage: (content: string) => Promise<void>
  sendStreamingMessage: (content: string) => Promise<void>
  clearError: () => void
  setPreferredAgent: (agent: 'auto' | 'workforce' | 'strategist') => void
  toggleStreaming: () => void
  deleteThread: (threadId: string) => void
  updateThreadTitle: (threadId: string, title: string) => void
}

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const useAgentStore = create<AgentState>()(
  persist(
    (set, get) => ({
      // Initial state
      currentThread: null,
      threads: [],
      isLoading: false,
      error: null,
      preferredAgent: 'auto',
      streamingEnabled: false,
      
      // Actions
      createNewThread: () => {
        const newThread: ConversationThread = {
          id: `thread_${Date.now()}`,
          title: 'Nowa rozmowa',
          messages: [],
          created_at: new Date(),
          updated_at: new Date(),
        }
        
        set((state) => ({
          currentThread: newThread,
          threads: [newThread, ...state.threads],
        }))
      },
      
      selectThread: (threadId: string) => {
        const thread = get().threads.find(t => t.id === threadId)
        if (thread) {
          set({ currentThread: thread })
        }
      },
      
      sendMessage: async (content: string) => {
        const { currentThread, preferredAgent } = get()
        
        if (!currentThread) {
          get().createNewThread()
        }
        
        const thread = get().currentThread!
        
        // Dodaj wiadomość użytkownika
        const userMessage: Message = {
          id: `msg_${Date.now()}`,
          content,
          role: 'user',
          timestamp: new Date(),
        }
        
        set((state) => ({
          isLoading: true,
          error: null,
          currentThread: {
            ...thread,
            messages: [...thread.messages, userMessage],
            updated_at: new Date(),
          },
        }))
        
        try {
          // Wyślij request do API
          const response = await fetch(`${API_BASE_URL}/agent`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              message: content,
              thread_id: thread.id,
              agent_type: preferredAgent === 'auto' ? undefined : preferredAgent,
            }),
          })
          
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`)
          }
          
          const data = await response.json()
          
          // Dodaj odpowiedź asystenta
          const assistantMessage: Message = {
            id: `msg_${Date.now()}_assistant`,
            content: data.response,
            role: 'assistant',
            timestamp: new Date(),
            agent_used: data.agent_used,
            metadata: data.metadata,
          }
          
          set((state) => {
            const updatedThread = {
              ...state.currentThread!,
              messages: [...state.currentThread!.messages, assistantMessage],
              updated_at: new Date(),
              title: state.currentThread!.messages.length === 1 ? 
                content.slice(0, 50) + (content.length > 50 ? '...' : '') : 
                state.currentThread!.title,
            }
            
            return {
              isLoading: false,
              currentThread: updatedThread,
              threads: state.threads.map(t => 
                t.id === updatedThread.id ? updatedThread : t
              ),
            }
          })
          
        } catch (error) {
          console.error('Error sending message:', error)
          set({
            isLoading: false,
            error: error instanceof Error ? error.message : 'Wystąpił błąd podczas wysyłania wiadomości',
          })
        }
      },
      
      sendStreamingMessage: async (content: string) => {
        const { currentThread, preferredAgent } = get()
        
        if (!currentThread) {
          get().createNewThread()
        }
        
        const thread = get().currentThread!
        
        // Dodaj wiadomość użytkownika
        const userMessage: Message = {
          id: `msg_${Date.now()}`,
          content,
          role: 'user',
          timestamp: new Date(),
        }
        
        // Placeholder dla wiadomości asystenta
        const assistantMessage: Message = {
          id: `msg_${Date.now()}_assistant`,
          content: '',
          role: 'assistant',
          timestamp: new Date(),
        }
        
        set((state) => ({
          isLoading: true,
          error: null,
          currentThread: {
            ...thread,
            messages: [...thread.messages, userMessage, assistantMessage],
            updated_at: new Date(),
          },
        }))
        
        try {
          const response = await fetch(`${API_BASE_URL}/agent/stream`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              message: content,
              thread_id: thread.id,
              agent_type: preferredAgent === 'auto' ? undefined : preferredAgent,
            }),
          })
          
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`)
          }
          
          const reader = response.body?.getReader()
          const decoder = new TextDecoder()
          
          if (reader) {
            let accumulatedContent = ''
            
            while (true) {
              const { done, value } = await reader.read()
              
              if (done) break
              
              const chunk = decoder.decode(value)
              const lines = chunk.split('\n')
              
              for (const line of lines) {
                if (line.startsWith('data: ')) {
                  const data = line.slice(6)
                  if (data === '[DONE]') {
                    set({ isLoading: false })
                    return
                  }
                  
                  accumulatedContent += data
                  
                  // Aktualizuj wiadomość asystenta
                  set((state) => {
                    const updatedMessages = state.currentThread!.messages.map(msg =>
                      msg.id === assistantMessage.id
                        ? { ...msg, content: accumulatedContent }
                        : msg
                    )
                    
                    const updatedThread = {
                      ...state.currentThread!,
                      messages: updatedMessages,
                      updated_at: new Date(),
                    }
                    
                    return {
                      currentThread: updatedThread,
                      threads: state.threads.map(t => 
                        t.id === updatedThread.id ? updatedThread : t
                      ),
                    }
                  })
                }
              }
            }
          }
          
        } catch (error) {
          console.error('Error with streaming message:', error)
          set({
            isLoading: false,
            error: error instanceof Error ? error.message : 'Wystąpił błąd podczas streamingu',
          })
        }
      },
      
      clearError: () => set({ error: null }),
      
      setPreferredAgent: (agent: 'auto' | 'workforce' | 'strategist') => {
        set({ preferredAgent: agent })
      },
      
      toggleStreaming: () => {
        set((state) => ({ streamingEnabled: !state.streamingEnabled }))
      },
      
      deleteThread: (threadId: string) => {
        set((state) => ({
          threads: state.threads.filter(t => t.id !== threadId),
          currentThread: state.currentThread?.id === threadId ? null : state.currentThread,
        }))
      },
      
      updateThreadTitle: (threadId: string, title: string) => {
        set((state) => ({
          threads: state.threads.map(t => 
            t.id === threadId ? { ...t, title, updated_at: new Date() } : t
          ),
          currentThread: state.currentThread?.id === threadId 
            ? { ...state.currentThread, title, updated_at: new Date() }
            : state.currentThread,
        }))
      },
    }),
    {
      name: 'agent-store',
      // Zapisuj tylko wybrane pola
      partialize: (state) => ({
        threads: state.threads,
        preferredAgent: state.preferredAgent,
        streamingEnabled: state.streamingEnabled,
      }),
    }
  )
)