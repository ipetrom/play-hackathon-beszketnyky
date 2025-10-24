import React from 'react'
import { Bot, Zap, Brain, Clock } from 'lucide-react'
import { useAgentStore } from '../stores/agentStore'

const Header: React.FC = () => {
  const { currentThread, preferredAgent, streamingEnabled, toggleStreaming } = useAgentStore()

  const agentInfo = {
    auto: { icon: <Bot className="w-5 h-5" />, name: 'Automatyczny', color: 'text-blue-500' },
    workforce: { icon: <Zap className="w-5 h-5" />, name: 'Workforce', color: 'text-yellow-500' },
    strategist: { icon: <Brain className="w-5 h-5" />, name: 'Strategist', color: 'text-purple-500' },
  }

  const currentAgent = agentInfo[preferredAgent]

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Thread info */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className={`${currentAgent.color}`}>
              {currentAgent.icon}
            </span>
            <span className="font-medium text-gray-900">
              {currentAgent.name}
            </span>
          </div>
          
          {currentThread && (
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <Clock className="w-4 h-4" />
              <span>
                {new Intl.DateTimeFormat('pl-PL', {
                  hour: '2-digit',
                  minute: '2-digit',
                  day: 'numeric',
                  month: 'short',
                }).format(currentThread.updated_at)}
              </span>
            </div>
          )}
        </div>

        {/* Controls */}
        <div className="flex items-center gap-4">
          {/* Streaming toggle */}
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={streamingEnabled}
              onChange={toggleStreaming}
              className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
            <span className="text-gray-700">Streaming</span>
          </label>

          {/* Current thread title */}
          {currentThread && (
            <div className="text-sm font-medium text-gray-900 max-w-xs truncate">
              {currentThread.title}
            </div>
          )}
        </div>
      </div>
    </header>
  )
}

export default Header