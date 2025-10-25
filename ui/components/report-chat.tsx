"use client"

import type React from "react"

import { useState, useEffect, useRef } from "react"
import { X, Send } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet"
import { useToast } from "@/hooks/use-toast"
import type { ChatMessage } from "@/lib/types"

interface ReportChatProps {
  reportId: string
  isOpen: boolean
  onClose: () => void
}

export function ReportChat({ reportId, isOpen, onClose }: ReportChatProps) {
  const { toast } = useToast()
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (isOpen) {
      loadMessages()
    }
  }, [isOpen, reportId])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  const loadMessages = async () => {
    try {
      // TODO: Replace with actual API call
      // const response = await fetch(`/api/reports/${reportId}/chat`)
      // const data = await response.json()

      // Load from localStorage
      const stored = localStorage.getItem(`chat_${reportId}`)
      if (stored) {
        setMessages(JSON.parse(stored))
      } else {
        setMessages([])
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load chat history.",
        variant: "destructive",
      })
    }
  }

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userMessage: ChatMessage = {
      id: `msg_${Date.now()}`,
      reportId,
      role: "user",
      content: input.trim(),
      createdAt: new Date().toISOString(),
    }

    const newMessages = [...messages, userMessage]
    setMessages(newMessages)
    setInput("")
    setIsLoading(true)

    try {
      // TODO: Replace with actual API call
      // const response = await fetch(`/api/reports/${reportId}/chat`, {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ content: input.trim() })
      // })
      // const data = await response.json()

      // Mock AI response
      await new Promise((resolve) => setTimeout(resolve, 1000))

      const assistantMessage: ChatMessage = {
        id: `msg_${Date.now() + 1}`,
        reportId,
        role: "assistant",
        content: `This is a mock response about report ${reportId}. In production, this would be an AI-generated answer based on the report content and your question: "${input.trim()}"`,
        createdAt: new Date().toISOString(),
      }

      const updatedMessages = [...newMessages, assistantMessage]
      setMessages(updatedMessages)

      // Save to localStorage
      localStorage.setItem(`chat_${reportId}`, JSON.stringify(updatedMessages))
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to send message. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <Sheet open={isOpen} onOpenChange={onClose}>
      <SheetContent side="right" className="w-full sm:max-w-lg flex flex-col p-0">
        <SheetHeader className="p-6 pb-4 border-b">
          <div className="flex items-center justify-between">
            <SheetTitle>Ask about this report</SheetTitle>
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X className="h-4 w-4" />
              <span className="sr-only">Close</span>
            </Button>
          </div>
          <div className="pt-2">
            <Badge variant="secondary" className="text-xs">
              Report #{reportId}
            </Badge>
          </div>
        </SheetHeader>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 ? (
            <div className="text-center text-muted-foreground py-12">
              <p>No messages yet</p>
              <p className="text-sm mt-2">Ask a question about this report</p>
            </div>
          ) : (
            messages.map((message) => (
              <div key={message.id} className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}>
                <div
                  className={`max-w-[80%] rounded-lg p-3 ${
                    message.role === "user" ? "bg-primary text-primary-foreground" : "bg-muted"
                  }`}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <Badge variant={message.role === "user" ? "secondary" : "outline"} className="text-xs">
                      {message.role === "user" ? "You" : "Assistant"}
                    </Badge>
                    <span className="text-xs opacity-70">{new Date(message.createdAt).toLocaleTimeString()}</span>
                  </div>
                  <p className="text-sm leading-relaxed">{message.content}</p>
                </div>
              </div>
            ))
          )}
          {isLoading && (
            <div className="flex justify-start">
              <div className="max-w-[80%] rounded-lg p-3 bg-muted">
                <div className="flex items-center gap-2">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-foreground/40 rounded-full animate-bounce" />
                    <div className="w-2 h-2 bg-foreground/40 rounded-full animate-bounce [animation-delay:0.2s]" />
                    <div className="w-2 h-2 bg-foreground/40 rounded-full animate-bounce [animation-delay:0.4s]" />
                  </div>
                  <span className="text-xs text-muted-foreground">Thinking...</span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="p-6 pt-4 border-t">
          <div className="flex gap-2">
            <Input
              placeholder="Ask a question..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={isLoading}
            />
            <Button onClick={handleSend} disabled={!input.trim() || isLoading} size="icon">
              <Send className="h-4 w-4" />
              <span className="sr-only">Send message</span>
            </Button>
          </div>
        </div>
      </SheetContent>
    </Sheet>
  )
}
