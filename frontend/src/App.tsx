
import { useState } from 'react'
import './App.css'

function App() {
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [messages, setMessages] = useState<
    { role: 'user' | 'assistant'; text: string }[]
  >([])


  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()

    if (!message.trim()) return

    const userMessage = message.trim()

    setMessages((previousMessages) => [
      ...previousMessages,
      { role: 'user', text: userMessage },
    ])

    setLoading(true)
    setError('')

    try {
      const response = await fetch(
        'https://my-ai-rag-app.onrender.com/api/v1/chat',
        // 'http://127.0.0.1:8000/api/v1/chat',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ message: userMessage }),
        }
      )

      if (!response.ok) {
        throw new Error(`Backend returned HTTP ${response.status}`)
      }

      const data = await response.json()

      setMessages((previousMessages) => [
        ...previousMessages,
        { role: 'assistant', text: data.response },
      ])

      setMessage('')
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Something went wrong'
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="header">
        <h1>Corporate HR Assistant</h1>
        <p>How can I help you today?</p>
      </header>


      <main className="chat">
        <div className="assistant-message">
          Hello! I'm your HR assistant. Ask me about company policies,
          working hours, remote work, or office information.
        </div>

        {messages.map((msg, index) => (
          <div
            key={index}
            className={
              msg.role === 'user'
                ? 'user-message'
                : 'assistant-message'
            }
          >
            {msg.text}
          </div>
        ))}

        {loading && (
          <p>Searching company information...</p>
        )}

        {error && (
          <p className="error-message">{error}</p>
        )}


        <form className="message-form" onSubmit={handleSubmit}>
          <input
            type="text"
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            placeholder="Ask an HR question..."
          />

          <button type="submit" disabled={loading}>
            {loading ? 'Thinking...' : 'Send'}
          </button>
        </form>
      </main>
    </div>
  )
}

export default App