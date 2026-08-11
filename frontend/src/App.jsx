import { useState, useRef, useEffect, useCallback } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

// ─── SVG Icon Components ──────────────────────────────────────────────────────

const SendIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="m22 2-7 20-4-9-9-4Z" />
    <path d="M22 2 11 13" />
  </svg>
);

const ReplyIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M9 14 4 9l5-5" />
    <path d="M4 9h10.5a5.5 5.5 0 0 1 5.5 5.5v0a5.5 5.5 0 0 1-5.5 5.5H11" />
  </svg>
);

const CopyIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect width="14" height="14" x="8" y="8" rx="2" ry="2" />
    <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2" />
  </svg>
);

const CheckIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M20 6 9 17l-5-5" />
  </svg>
);

const RefreshIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8" />
    <path d="M21 3v5h-5" />
    <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16" />
    <path d="M8 16H3v5" />
  </svg>
);



// ─── Suggested Prompts ────────────────────────────────────────────────────────

const SUGGESTED_PROMPTS = [
  "Give information of XP multipliers.",
  "What are Sunbear's D20 outcomes?",
  "How to get diamonds from farming?",
  "Show me the stats and commands for a Kraken pet.",
];

// ─── Message Actions (Copy / Regenerate) ─────────────────────────────────────

function MessageActions({ content, onRegenerate, onReply, isLast }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = useCallback(() => {
    navigator.clipboard.writeText(content).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  }, [content]);

  return (
    <div className="msg-actions">
      <button onClick={handleCopy} className="msg-action-btn" title="Copy">
        {copied ? <CheckIcon /> : <CopyIcon />}
        <span>{copied ? 'Copied' : 'Copy'}</span>
      </button>
      <button onClick={onReply} className="msg-action-btn" title="Follow-up">
        <ReplyIcon />
        <span>Reply</span>
      </button>
      {isLast && (
        <button onClick={onRegenerate} className="msg-action-btn" title="Regenerate">
          <RefreshIcon />
          <span>Regenerate</span>
        </button>
      )}
    </div>
  );
}

// ─── Typing Dots ──────────────────────────────────────────────────────────────

function TypingIndicator() {
  return (
    <div className="typing-indicator">
      <span /><span /><span />
    </div>
  );
}

// ─── Markdown Renderer ────────────────────────────────────────────────────────

const parseEmojis = (text) =>
  text.replace(/<:([a-zA-Z0-9_]+):(\d+)>/g, (_, name, id) =>
    `![${name}](https://cdn.discordapp.com/emojis/${id}.png?v=1)`
  );

const mdComponents = {
  img: ({ node, ...props }) => (
    <img {...props} style={{ display: 'inline', width: 20, height: 20, verticalAlign: 'middle', margin: '0 2px' }} />
  ),
  code: ({ node, className, children, ...props }) => {
    const match = /language-(\w+)/.exec(className || '');
    // If it has a language class or contains newlines, treat it as a block
    const isBlock = match || String(children).includes('\n');

    if (!isBlock) {
      return <code className="inline-code" {...props}>{children}</code>;
    }
    return (
      <div className="code-block">
        <pre><code className={className} {...props}>{children}</code></pre>
      </div>
    );
  },
};

// ─── App ──────────────────────────────────────────────────────────────────────

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [followUpContext, setFollowUpContext] = useState(null);

  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);
  const lastUserQuestion = useRef('');

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  // Auto-grow textarea
  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = 'auto';
    el.style.height = Math.min(el.scrollHeight, 200) + 'px';
  }, [input]);

  const sendMessage = useCallback(async (question, overrideContext = null) => {
    if (!question.trim() || isLoading) return;

    lastUserQuestion.current = question;

    // Determine payload based on followUpContext or override
    const contextToUse = overrideContext !== null ? overrideContext : followUpContext;
    let payloadMessages = [{ role: 'user', content: question }];
    if (contextToUse) {
      payloadMessages = [...contextToUse, { role: 'user', content: question }];
    }

    // Always append to visual UI chat history
    setMessages(prev => [...prev, {
      role: 'user',
      content: question,
      replyTo: contextToUse ? contextToUse[1].content : null
    }]);
    setInput('');
    setIsLoading(true);
    setFollowUpContext(null); // Clear context after sending

    try {
      const apiUrl = import.meta.env.VITE_API_URL || '';
      const response = await fetch(`${apiUrl}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: payloadMessages }),
      });

      let errorMessage = `Server error (${response.status})`;
      if (!response.ok) {
        try {
          const errData = await response.json();
          if (errData.detail) errorMessage = errData.detail;
        } catch (_) { }
        throw new Error(errorMessage);
      }

      const data = await response.json();
      setMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
    } catch (error) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `**Error:** ${error.message}`,
        isError: true,
      }]);
    } finally {
      setIsLoading(false);
    }
  }, [isLoading, followUpContext]);

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage(input);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  };

  const handleRegenerate = () => {
    // Regenerate uses the full UI history minus the last assistant message
    setMessages(prev => prev.slice(0, -1));
    // For regenerate, we just use the last question, ignoring any previous threaded context
    sendMessage(lastUserQuestion.current, null);
  };

  const isEmpty = messages.length === 0;

  const handleReplyClick = (idx) => {
    // Find the closest user message before this assistant message
    let userMsg = null;
    for (let i = idx - 1; i >= 0; i--) {
      if (messages[i].role === 'user') {
        userMsg = messages[i];
        break;
      }
    }

    if (userMsg && messages[idx]) {
      setFollowUpContext([userMsg, messages[idx]]);
      textareaRef.current?.focus();
    }
  };

  return (
    <div className="app">
      {/* ── Header ── */}
      <header className="header">
        <div className="header-inner">
          <div className="header-brand-group">
            <img src="/DankGPT.png" alt="DankGPT Logo" className="header-logo" />
            <span className="brand-name">DankGPT</span>
          </div>
        </div>
      </header>

      {/* ── Chat Area ── */}
      <main className="chat-area">
        <div className="chat-inner">

          {/* Empty state */}
          {isEmpty && (
            <div className="empty-state">
              <h1 className="empty-heading">How can I help you?</h1>
              <p className="empty-sub">Ask anything about the Dank Memer Discord bot.</p>
              <div className="suggestions">
                {SUGGESTED_PROMPTS.map((p, i) => (
                  <button
                    key={i}
                    className="suggestion-btn"
                    onClick={() => sendMessage(p)}
                    disabled={isLoading}
                  >
                    {p}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Messages */}
          {messages.map((msg, idx) => {
            const isLastAssistant = msg.role === 'assistant' && idx === messages.length - 1;
            return (
              <div key={idx} className={`message message--${msg.role}${msg.isError ? ' message--error' : ''}`}>
                {msg.role === 'user' ? (
                  <div className="user-message-container">
                    {msg.replyTo && (
                      <div className="user-reply-badge">
                        <ReplyIcon /> Replying to: "{msg.replyTo.substring(0, 50)}..."
                      </div>
                    )}
                    <div className="user-bubble">{msg.content}</div>
                  </div>
                ) : (
                  <div className="assistant-content">
                    <div className="prose">
                      <ReactMarkdown remarkPlugins={[remarkGfm]} components={mdComponents}>
                        {parseEmojis(msg.content)}
                      </ReactMarkdown>
                    </div>
                    {!msg.isError && (
                      <MessageActions
                        content={msg.content}
                        onRegenerate={handleRegenerate}
                        onReply={() => handleReplyClick(idx)}
                        isLast={isLastAssistant && !isLoading}
                      />
                    )}
                  </div>
                )}
              </div>
            );
          })}

          {/* Loading */}
          {isLoading && (
            <div className="message message--assistant">
              <div className="assistant-content">
                <TypingIndicator />
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </main>

      {/* ── Composer ── */}
      <div className="composer-wrap">
        <div className="composer-inner">
          {followUpContext && (
            <div className="reply-indicator">
              <span className="reply-label"><ReplyIcon /> Replying to context</span>
              <span className="reply-snippet">"{followUpContext[1].content.substring(0, 40)}..."</span>
              <button className="reply-cancel" onClick={() => setFollowUpContext(null)}>✕</button>
            </div>
          )}
          <form className={`composer ${followUpContext ? 'composer--replying' : ''}`} onSubmit={handleSubmit}>
            <textarea
              ref={textareaRef}
              className="composer-input"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isLoading}
              placeholder="Ask about Dank Memer…"
              rows={1}
              maxLength={500}
            />
            <button
              type="submit"
              className="composer-send"
              disabled={isLoading || !input.trim()}
              aria-label="Send message"
            >
              <SendIcon />
            </button>
          </form>
          <p className="disclaimer">AI can make mistakes. Check important information.</p>
        </div>
      </div>
    </div>
  );
}
