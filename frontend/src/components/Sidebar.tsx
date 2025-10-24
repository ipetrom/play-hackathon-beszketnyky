import React from 'react'
import { 
  MessageSquare, 
  Settings, 
  Zap, 
  Brain, 
  Trash2,
  Plus,
  Bot
} from 'lucide-react'
import { useAgentStore } from '../stores/agentStore'

const Sidebar: React.FC = () => {
  const {
    threads,
    currentThread,
    preferredAgent,
    createNewThread,
    selectThread,
    deleteThread,
    setPreferredAgent,
  } = useAgentStore()

  const agentIcons = {
    auto: <Bot className="w-4 h-4" />,
    workforce: <Zap className="w-4 h-4" />,
    strategist: <Brain className="w-4 h-4" />,
  }

  const agentLabels = {
    auto: 'Automatyczny',
    workforce: 'Workforce (Mistral)',
    strategist: 'Strategist (GPT-4o)',
  }

  return (
    <div className="w-64 bg-gray-900 text-white flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-700">
        <h1 className="text-lg font-semibold">AI Agents Platform</h1>
        <p className="text-xs text-gray-400 mt-1">Hackathon Beszketnyky</p>
      </div>

      {/* New Chat Button */}
      <div className="p-4">
        <button
          onClick={createNewThread}
          className="w-full flex items-center justify-center gap-2 bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg transition-colors duration-200"
        >
          <Plus className="w-4 h-4" />
          Nowa rozmowa
        </button>
      </div>

      {/* Agent Selection */}
      <div className="px-4 pb-4">
        <label className="block text-xs font-medium text-gray-400 mb-2">
          Wybór agenta
        </label>
        <select
          value={preferredAgent}
          onChange={(e) => setPreferredAgent(e.target.value as any)}
          className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          <option value="auto">🤖 Automatyczny</option>
          <option value="workforce">⚡ Workforce (Mistral)</option>
          <option value="strategist">🧠 Strategist (GPT-4o)</option>
        </select>
      </div>

      {/* Conversation History */}
      <div className="flex-1 overflow-y-auto">
        <div className="px-4 pb-2">
          <h3 className="text-xs font-medium text-gray-400 mb-2">Historia rozmów</h3>
        </div>
        
        <div className="space-y-1 px-2">
          {threads.map((thread) => (
            <div
              key={thread.id}
              className={`group relative flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer transition-colors duration-200 ${
                currentThread?.id === thread.id
                  ? 'bg-primary-600 text-white'
                  : 'hover:bg-gray-800 text-gray-300'
              }`}
              onClick={() => selectThread(thread.id)}
            >
              <MessageSquare className="w-4 h-4 flex-shrink-0" />
              <span className="flex-1 text-sm truncate">{thread.title}</span>
              
              {/* Delete button - only show on hover */}
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  deleteThread(thread.id)
                }}
                className="opacity-0 group-hover:opacity-100 flex-shrink-0 p-1 hover:bg-red-600 rounded transition-all duration-200"
              >
                <Trash2 className="w-3 h-3" />
              </button>
            </div>
          ))}
          
          {threads.length === 0 && (
            <div className="px-3 py-8 text-center text-gray-500">
              <MessageSquare className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p className="text-sm">Brak rozmów</p>
              <p className="text-xs">Rozpocznij nową rozmowę</p>
            </div>
          )}
        </div>
      </div>

      {/* Agent Info Panel */}
      <div className="p-4 border-t border-gray-700">
        <div className="flex items-center gap-2 mb-2">
          {agentIcons[preferredAgent]}
          <span className="text-sm font-medium">
            {agentLabels[preferredAgent]}
          </span>
        </div>
        
        <div className="text-xs text-gray-400">
          {preferredAgent === 'auto' && (
            <p>System automatycznie wybierze najlepszego agenta dla Twojego zapytania.</p>
          )}
          {preferredAgent === 'workforce' && (
            <p>Scaleway Mistral - tagowanie, streszczanie, podstawowe Q&A.</p>
          )}
          {preferredAgent === 'strategist' && (
            <p>OpenAI GPT-4o - analiza ryzyka, wsparcie decyzyjne, złożone rozumowanie.</p>
          )}
        </div>
      </div>

      {/* Settings */}
      <div className="p-4 border-t border-gray-700">
        <button className="w-full flex items-center gap-2 text-gray-400 hover:text-white transition-colors duration-200">
          <Settings className="w-4 h-4" />
          <span className="text-sm">Ustawienia</span>
        </button>
      </div>
    </div>
  )
}

export default Sidebar