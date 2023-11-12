import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import Send from './images/send.png';
import './App.css';

const App = () => {
  const [message, setMessage] = useState('');
  const [conversations, setConversations] = useState([]);
  const [botIsTyping, setBotIsTyping] = useState(false);
  const [isError, setIsError] = useState(false);
  const messagesEndRef = useRef(null);

  const fetchResponse = async () => {
    setIsError(false);
    setConversations((oldConversations) => [
      ...oldConversations,
      { message, from: 'User' },
    ]);
    setMessage('');
    setBotIsTyping(true);

    try {
      const res = await axios.post('http://localhost:5001/api/pdfchatbot', {
        message,
      });
      setTimeout(() => {
        setConversations((oldConversations) => [
          ...oldConversations,
          { message: res.data.response, from: 'Bot' },
        ]);
        setBotIsTyping(false);
      }, 2000);
    } catch (error) {
      console.error(error);
      setIsError(true);
      setBotIsTyping(false);
    }
  };

  const fetchGreeting = async () => {
    if (conversations.length === 0) {
      // Only fetch greeting if conversations array is empty
      console.log('fetchGreeting called'); // Add this line
      try {
        const res = await axios.get(
          'http://localhost:5001/api/chatbot/greeting'
        );
        setConversations((oldConversations) => [
          ...oldConversations,
          { message: res.data.greeting, from: 'Bot' },
        ]);
      } catch (error) {
        console.error(error);
        setIsError(true);
      }
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === 'Enter') {
      fetchResponse();
    }
  };

  const clearHistory = () => {
    setConversations([]);
  };

  const restartChat = () => {
    setIsError(false);
    setConversations([]);
  };

  useEffect(() => {
    fetchGreeting();
  }, []); // Empty array means this effect will only run once after the component mounts

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [conversations, botIsTyping]);

  if (isError) {
    return (
      <div className='chatContainer'>
        <div className='chatHeader'>
          ChatBot
          <button className='clearButton' onClick={restartChat}>
            Restart Chat
          </button>
        </div>
        <div className='chatHistory'>
          {conversations.map((conversation, index) => (
            <div key={index} className={conversation.from}>
              <div>{conversation.message}</div>
            </div>
          ))}
          <div className='Bot'>
            <div>An error occurred, please restart the chat</div>
          </div>
          <div ref={messagesEndRef} />
        </div>
      </div>
    );
  }

  return (
    <div className='chatContainer'>
      <div className='chatHeader'>
        ChatBot
        {conversations.length > 0 && (
          <button className='clearButton' onClick={clearHistory}>
            Clear Chat
          </button>
        )}
      </div>
      <div className='chatHistory'>
        {conversations.map((conversation, index) => (
          <div key={index} className={conversation.from}>
            <div
              dangerouslySetInnerHTML={{ __html: conversation.message }}
            ></div>
          </div>
        ))}
        {botIsTyping && (
          <div className='Bot'>
            <div>Bot is typing...</div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <div className='inputArea'>
        <input
          className='inputField'
          type='text'
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <button className='sendButton' onClick={fetchResponse}>
          <img src={Send} alt='Send' />
        </button>
      </div>
    </div>
  );
};

export default App;
