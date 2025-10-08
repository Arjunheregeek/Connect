import React, { useState } from 'react';
import './App.css';

const AGENT_API_URL = 'https://connect-agent.onrender.com';

function App() {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [isFirstQuery, setIsFirstQuery] = useState(true);

    const sendMessage = async () => {
        if (!input.trim()) return;

        const userMessage = input.trim();
        setInput('');
        setMessages(prev => [...prev, { type: 'user', content: userMessage }]);
        setLoading(true);

        try {
            // Wake up the server on first query (handles cold start)
            if (isFirstQuery) {
                setIsFirstQuery(false);
                try {
                    await fetch(`${AGENT_API_URL}/`, { method: 'GET' });
                } catch (err) {
                    console.log('Waking up server...');
                }
                // Give server a moment to warm up
                await new Promise(resolve => setTimeout(resolve, 2000));
            }

            // Call the LangGraph Connect Agent API
            const response = await fetch(`${AGENT_API_URL}/ask`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    question: userMessage,
                    conversation_id: `conv-${Date.now()}`
                })
            });

            const data = await response.json();

            let botResponse;
            if (data.success && data.response) {
                botResponse = data.response;
            } else {
                botResponse = 'Sorry, I could not process your request.';
            }

            setMessages(prev => [...prev, { type: 'bot', content: botResponse }]);
        } catch (error) {
            console.error('Error:', error);
            setMessages(prev => [...prev, {
                type: 'bot',
                content: 'Sorry, there was an error connecting to the server.'
            }]);
        } finally {
            setLoading(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    };

    return (
        <div className="App">
            <header className="App-header">
                <h1>Connect Knowledge Graph</h1>
                <p>Ask me about people in our professional network!</p>
            </header>

            <div className="chat-container">
                <div className="messages">
                    {messages.length === 0 && (
                        <div className="welcome-message">
                            <p>👋 Hi! I can help you find people in our knowledge graph.</p>
                            <p>Try asking:</p>
                            <ul>
                                <li>"Find Python developers"</li>
                                <li>"Who works at Google?"</li>
                                <li>"Find people with machine learning skills"</li>
                            </ul>
                        </div>
                    )}

                    {messages.map((message, index) => (
                        <div key={index} className={`message ${message.type}`}>
                            <div className="message-content">
                                {message.content}
                            </div>
                        </div>
                    ))}

                    {loading && (
                        <div className="message bot">
                            <div className="message-content">
                                <div className="typing">Thinking...</div>
                            </div>
                        </div>
                    )}
                </div>

                <div className="input-container">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder="Ask about people in the knowledge graph..."
                        disabled={loading}
                    />
                    <button onClick={sendMessage} disabled={loading || !input.trim()}>
                        Send
                    </button>
                </div>
            </div>
        </div>
    );
}

export default App;