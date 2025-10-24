import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import ChatView from './views/ChatView'
import { useAgentStore } from './stores/agentStore'

function App() {
  const { isLoading } = useAgentStore()

  return (
    <Layout>
      <Routes>
        <Route path="/" element={<ChatView />} />
        <Route path="/chat" element={<ChatView />} />
        {/* Dodaj więcej rout tutaj w przyszłości */}
      </Routes>
      
      {/* Global loading overlay */}
      {isLoading && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
            <p className="mt-4 text-sm text-gray-600">Przetwarzanie żądania...</p>
          </div>
        </div>
      )}
    </Layout>
  )
}

export default App