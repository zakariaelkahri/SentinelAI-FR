import React, { useState } from 'react';
import { api } from '../services/api';

const assistantPrompts = [
  'What should I do if a restricted area alarm triggers after midnight?',
  'How do I handle a suspicious package report in the lobby?',
  'Give me a quick escalation checklist for a weapon sighting.',
];

function SecurityAssistant() {
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (event) => {
    event.preventDefault();
    const trimmedQuestion = question.trim();
    if (!trimmedQuestion || isSubmitting) {
      return;
    }

    const userMessage = {
      id: `${Date.now()}-user`,
      role: 'user',
      text: trimmedQuestion,
    };

    setMessages((previous) => [...previous, userMessage]);
    setQuestion('');
    setError('');
    setIsSubmitting(true);

    try {
      const response = await api.askSecurityAssistant(trimmedQuestion);
      const assistantMessage = {
        id: `${Date.now()}-assistant`,
        role: 'assistant',
        text: response?.answer || 'No answer returned by assistant.',
      };
      setMessages((previous) => [...previous, assistantMessage]);
    } catch (requestError) {
      const errorMessage =
        requestError?.response?.data?.detail ||
        requestError?.message ||
        'Assistant request failed.';
      setError(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="page-shell">
      <header className="page-header">
        <p className="page-eyebrow">Operations Workspace</p>
        <h1 className="page-title">Security Assistant</h1>
        <p className="page-subtitle">
          Ask protocol questions and get answers grounded in the security manual.
        </p>
      </header>

      <section className="card assistant-card">
        <div className="assistant-toolbar">
          <h2>Conversation</h2>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => {
              setMessages([]);
              setError('');
            }}
            disabled={isSubmitting || messages.length === 0}
          >
            Clear
          </button>
        </div>

        <div className="chip-link-row">
          {assistantPrompts.map((prompt) => (
            <button
              key={prompt}
              type="button"
              className="chip-link"
              onClick={() => setQuestion(prompt)}
              disabled={isSubmitting}
            >
              {prompt}
            </button>
          ))}
        </div>

        <div className="assistant-chat">
          {messages.length === 0 && (
            <p className="empty-state">
              Example: What should I do if I find a suspicious package during patrol?
            </p>
          )}

          {messages.map((message) => (
            <article
              key={message.id}
              className={`assistant-message assistant-message-${message.role}`}
            >
              <p className="assistant-message-role">
                {message.role === 'user' ? 'You' : 'Assistant'}
              </p>
              <p className="assistant-message-text">{message.text}</p>
            </article>
          ))}
        </div>

        {error && <div className="auth-error">{error}</div>}

        <form className="assistant-form" onSubmit={handleSubmit}>
          <label className="form-group" htmlFor="assistant-question">
            <span>Your question</span>
            <textarea
              id="assistant-question"
              className="form-input assistant-input"
              placeholder="Type your protocol question..."
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              rows={4}
              disabled={isSubmitting}
              maxLength={4000}
              required
            />
          </label>
          <button type="submit" className="btn" disabled={isSubmitting || !question.trim()}>
            {isSubmitting ? 'Asking...' : 'Ask Assistant'}
          </button>
        </form>
      </section>
    </div>
  );
}

export default SecurityAssistant;
