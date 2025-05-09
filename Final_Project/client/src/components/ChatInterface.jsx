import React, { useState, useRef, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from "axios";
import ReactMarkdown from 'react-markdown';

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [attachedImage, setAttachedImage] = useState(null);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {'image/*': ['.jpeg', '.png', '.jpg']},
    onDrop: files => handleFileAttach(files[0]),
    noClick: true
  });

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(scrollToBottom, [messages]);

  const handleTextSubmit = async (e) => {
    e.preventDefault();
    if (!inputText.trim() && !attachedImage) return;

    // Create user message
    const userMessage = {
      id: Date.now().toString(),
      content: inputText,
      isUser: true,
      timestamp: new Date(),
      ...(attachedImage && { metadata: { preview: URL.createObjectURL(attachedImage) } }),
    };

    setMessages((prev) => [...prev, userMessage]);

    try {
      const formData = new FormData();
      let endpoint = '/query';

      if (attachedImage) {
        formData.append('file', attachedImage);
        endpoint = '/query-image';
      }
      if (inputText.trim()) {
        formData.append('message', inputText);
      }

      const response = await axios.post(
        `http://localhost:8000${endpoint}`,
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );

      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          isUser: false,
          timestamp: new Date(),
          metadata: {
            response: {
              text: response.data.text,
              images: response.data.images
            }
          },
        },
      ]);
    } catch (error) {
      console.error('API Error:', error.response?.data || error.message);
    }

    // Reset input and attached image
    setInputText('');
    setAttachedImage(null);
  };

  const handleFileAttach = (file) => {
    setAttachedImage(file);
  };

  const handleUploadClick = () => {
    fileInputRef.current.click();
  };

  return (
    <div className="chat-container">
      <div className="messages-container">
        {messages.length === 0 && (
          <div className="empty-state">
            <div className="empty-state-content">
              <h3>Welcome to Image Gallery Assistant</h3>
              <p>Get started by:</p>
              <ul>
                <li>Asking questions about your images</li>
                <li>Dragging and dropping an image to search</li>
                <li>Combining text and image queries</li>
              </ul>
              <div className="example-prompts">
                <p>Try something like:</p>
                <button type="button" onClick={() => setInputText("Show me images from last summer")}>
                  "Show me images from Summer Vacation 2021"
                </button>
                <button type="button" onClick={() => setInputText("Find pictures of beaches")}>
                  "Find pictures of beaches"
                </button>
              </div>
            </div>
          </div>
        )}
        {messages.map(message => (
          <div key={message.id} className={`message ${message.isUser ? 'user' : 'bot'}`}>
            {message.isUser && (
              <>
                {message.content && (
                  <div className="text-message">
                    <ReactMarkdown>{message.content}</ReactMarkdown>
                  </div>
                )}
                {message.metadata?.preview && (
                  <div className="image-message">
                    <img
                      src={message.metadata.preview}
                      alt="Uploaded content"
                      className="image-preview"
                    />
                  </div>
                )}
              </>
            )}

            {message.metadata?.response && (
              <div className="bot-response">
                <div className="response-text">
                  <ReactMarkdown>{message.metadata.response.text}</ReactMarkdown>
                </div>
                <div className="gallery-grid">
                  {message.metadata.response.images?.map((imageUri, index) => (
                    <div key={index} className="gallery-item">
                      <img
                        src={imageUri}
                        alt={`Search result ${index + 1}`}
                        className="gallery-image"
                      />
                      <div className="image-meta">
                        <span className="image-name">{imageUri.split('\\').pop()}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
            <div className="message-timestamp">
              {message.timestamp.toLocaleTimeString()}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <div {...getRootProps()} className={`input-container ${isDragActive ? 'active' : ''}`}>
        <input {...getInputProps()} />
        {attachedImage && (
          <div className="attached-image-preview">
            <img
              src={URL.createObjectURL(attachedImage)}
              alt="Attached content"
              className="attached-preview"
            />
            <button
              type="button"
              className="remove-attachment"
              onClick={(e) => {
                e.stopPropagation();
                setAttachedImage(null);
              }}
            >
              ×
            </button>
          </div>
        )}
        <form onSubmit={handleTextSubmit}>
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Type a message or drop an image..."
          />
          <button type="button" className="upload-button" onClick={handleUploadClick}>
            <span role="img" aria-label="Upload">📷</span>
          </button>
          <button type="submit" className="send-button">Send</button>
        </form>
        <input
          type="file"
          ref={fileInputRef}
          style={{ display: 'none' }}
          accept="image/*"
          onChange={(e) => handleFileAttach(e.target.files[0])}
        />
        {isDragActive && (
          <div className="dropzone-overlay">
            Drop image here to upload
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatInterface;