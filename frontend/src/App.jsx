import { useState, useRef, useEffect, useCallback } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Analytics } from '@vercel/analytics/react';

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

const LlamaIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
    <path d="M16.361 10.26a.894.894 0 0 0-.558.47l-.072.148.001.207c0 .193.004.217.059.353.076.193.152.312.291.448.24.238.51.3.872.205a.86.86 0 0 0 .517-.436.752.752 0 0 0 .08-.498c-.064-.453-.33-.782-.724-.897a1.06 1.06 0 0 0-.466 0zm-9.203.005c-.305.096-.533.32-.65.639a1.187 1.187 0 0 0-.06.52c.057.309.31.59.598.667.362.095.632.033.872-.205.14-.136.215-.255.291-.448.055-.136.059-.16.059-.353l.001-.207-.072-.148a.894.894 0 0 0-.565-.472 1.02 1.02 0 0 0-.474.007Zm4.184 2c-.131.071-.223.25-.195.383.031.143.157.288.353.407.105.063.112.072.117.136.004.038-.01.146-.029.243-.02.094-.036.194-.036.222.002.074.07.195.143.253.064.052.076.054.255.059.164.005.198.001.264-.03.169-.082.212-.234.15-.525-.052-.243-.042-.28.087-.355.137-.08.281-.219.324-.314a.365.365 0 0 0-.175-.48.394.394 0 0 0-.181-.033c-.126 0-.207.03-.355.124l-.085.053-.053-.032c-.219-.13-.259-.145-.391-.143a.396.396 0 0 0-.193.032zm.39-2.195c-.373.036-.475.05-.654.086-.291.06-.68.195-.951.328-.94.46-1.589 1.226-1.787 2.114-.04.176-.045.234-.045.53 0 .294.005.357.043.524.264 1.16 1.332 2.017 2.714 2.173.3.033 1.596.033 1.896 0 1.11-.125 2.064-.727 2.493-1.571.114-.226.169-.372.22-.602.039-.167.044-.23.044-.523 0-.297-.005-.355-.045-.531-.288-1.29-1.539-2.304-3.072-2.497a6.873 6.873 0 0 0-.855-.031zm.645.937a3.283 3.283 0 0 1 1.44.514c.223.148.537.458.671.662.166.251.26.508.303.82.02.143.01.251-.043.482-.08.345-.332.705-.672.957a3.115 3.115 0 0 1-.689.348c-.382.122-.632.144-1.525.138-.582-.006-.686-.01-.853-.042-.57-.107-1.022-.334-1.35-.68-.264-.28-.385-.535-.45-.946-.03-.192.025-.509.137-.776.136-.326.488-.73.836-.963.403-.269.934-.46 1.422-.512.187-.02.586-.02.773-.002zm-5.503-11a1.653 1.653 0 0 0-.683.298C5.617.74 5.173 1.666 4.985 2.819c-.07.436-.119 1.04-.119 1.503 0 .544.064 1.24.155 1.721.02.107.031.202.023.208a8.12 8.12 0 0 1-.187.152 5.324 5.324 0 0 0-.949 1.02 5.49 5.49 0 0 0-.94 2.339 6.625 6.625 0 0 0-.023 1.357c.091.78.325 1.438.727 2.04l.13.195-.037.064c-.269.452-.498 1.105-.605 1.732-.084.496-.095.629-.095 1.294 0 .67.009.803.088 1.266.095.555.288 1.143.503 1.534.071.128.243.393.264.407.007.003-.014.067-.046.141a7.405 7.405 0 0 0-.548 1.873c-.062.417-.071.552-.071.991 0 .56.031.832.148 1.279L3.42 24h1.478l-.05-.091c-.297-.552-.325-1.575-.068-2.597.117-.472.25-.819.498-1.296l.148-.29v-.177c0-.165-.003-.184-.057-.293a.915.915 0 0 0-.194-.25 1.74 1.74 0 0 1-.385-.543c-.424-.92-.506-2.286-.208-3.451.124-.486.329-.918.544-1.154a.787.787 0 0 0 .223-.531c0-.195-.07-.355-.224-.522a3.136 3.136 0 0 1-.817-1.729c-.14-.96.114-2.005.69-2.834.563-.814 1.353-1.336 2.237-1.475.199-.033.57-.028.776.01.226.04.367.028.512-.041.179-.085.268-.19.374-.431.093-.215.165-.333.36-.576.234-.29.46-.489.822-.729.413-.27.884-.467 1.352-.561.17-.035.25-.04.569-.04.319 0 .398.005.569.04a4.07 4.07 0 0 1 1.914.997c.117.109.398.457.488.602.034.057.095.177.132.267.105.241.195.346.374.43.14.068.286.082.503.045.343-.058.607-.053.943.016 1.144.23 2.14 1.173 2.581 2.437.385 1.108.276 2.267-.296 3.153-.097.15-.193.27-.333.419-.301.322-.301.722-.001 1.053.493.539.801 1.866.708 3.036-.062.772-.26 1.463-.533 1.854a2.096 2.096 0 0 1-.224.258.916.916 0 0 0-.194.25c-.054.109-.057.128-.057.293v.178l.148.29c.248.476.38.823.498 1.295.253 1.008.231 2.01-.059 2.581a.845.845 0 0 0-.044.098c0 .006.329.009.732.009h.73l.02-.074.036-.134c.019-.076.057-.3.088-.516.029-.217.029-1.016 0-1.258-.11-.875-.295-1.57-.597-2.226-.032-.074-.053-.138-.046-.141.008-.005.057-.074.108-.152.376-.569.607-1.284.724-2.228.031-.26.031-1.378 0-1.628-.083-.645-.182-1.082-.348-1.525a6.083 6.083 0 0 0-.329-.7l-.038-.064.131-.194c.402-.604.636-1.262.727-2.04a6.625 6.625 0 0 0-.024-1.358 5.512 5.512 0 0 0-.939-2.339 5.325 5.325 0 0 0-.95-1.02 8.097 8.097 0 0 1-.186-.152.692.692 0 0 1 .023-.208c.208-1.087.201-2.443-.017-3.503-.19-.924-.535-1.658-.98-2.082-.354-.338-.716-.482-1.15-.455-.996.059-1.8 1.205-2.116 3.01a6.805 6.805 0 0 0-.097.726c0 .036-.007.066-.015.066a.96.96 0 0 1-.149-.078A4.857 4.857 0 0 0 12 3.03c-.832 0-1.687.243-2.456.698a.958.958 0 0 1-.148.078c-.008 0-.015-.03-.015-.066a6.71 6.71 0 0 0-.097-.725C8.997 1.392 8.337.319 7.46.048a2.096 2.096 0 0 0-.585-.041Zm.293 1.402c.248.197.523.759.682 1.388.03.113.06.244.069.292.007.047.026.152.041.233.067.365.098.76.102 1.24l.002.475-.12.175-.118.178h-.278c-.324 0-.646.041-.954.124l-.238.06c-.033.007-.038-.003-.057-.144a8.438 8.438 0 0 1 .016-2.323c.124-.788.413-1.501.696-1.711.067-.05.079-.049.157.013zm9.825-.012c.17.126.358.46.498.888.28.854.36 2.028.212 3.145-.019.14-.024.151-.057.144l-.238-.06a3.693 3.693 0 0 0-.954-.124h-.278l-.119-.178-.119-.175.002-.474c.004-.669.066-1.19.214-1.772.157-.623.434-1.185.68-1.382.078-.062.09-.063.159-.012z" />
  </svg>
);


const ChevronIcon = ({ isOpen }) => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ transform: isOpen ? 'rotate(90deg)' : 'rotate(0deg)', transition: 'transform 150ms ease' }}>
    <path d="m9 18 6-6-6-6" />
  </svg>
);

const LoaderIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="think-loader">
    <path d="M21 12a9 9 0 1 1-6.219-8.56" />
  </svg>
);

function ThoughtProcessBlock({ msg }) {
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef(null);

  useEffect(() => {
    // Intentionally removed auto-open logic so the block stays closed by default.
  }, []);

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) {
          setIsOpen(false);
        }
      });
    }, { threshold: 0.1 });

    observer.observe(el);
    return () => observer.unobserve(el);
  }, []);

  const toggleOpen = () => setIsOpen(prev => !prev);

  const title = msg.isStreaming && msg.statusLogs?.length > 0 
    ? msg.statusLogs[msg.statusLogs.length - 1] 
    : "Thought Process";

  return (
    <div className="think-block" ref={containerRef}>
      <button className="think-summary" onClick={toggleOpen}>
        <ChevronIcon isOpen={isOpen} />
        {msg.isStreaming && <LoaderIcon />}
        <span>{title}</span>
      </button>
      <div className={`think-content-wrapper ${isOpen ? 'is-open' : ''}`}>
        <div className="think-content-inner">
          <div className="think-content">
            {msg.statusLogs?.length > 0 && (
              <ul className="status-logs">
                {msg.statusLogs.map((log, i) => (
                  <li key={i}>{log}</li>
                ))}
              </ul>
            )}
            {msg.contextDocs && (
              <div className="context-docs">
                {msg.contextDocs.official?.length > 0 && (
                  <div className="context-section">
                    <div className="context-title">Guide data:</div>
                    <ul>
                      {msg.contextDocs.official.map((doc, i) => (
                        <li key={i}>{doc.substring(0, 150)}...</li>
                      ))}
                    </ul>
                  </div>
                )}
                {msg.contextDocs.community?.length > 0 && (
                  <div className="context-section">
                    <div className="context-title">Community data:</div>
                    <ul>
                      {msg.contextDocs.community.map((doc, i) => (
                        <li key={i}>{doc.substring(0, 150)}...</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── Suggested Prompts ────────────────────────────────────────────────────────

const SUGGESTED_PROMPTS = [
  "How do I maximize my XP multipliers?",
  "What are the possible outcomes for Sunbear's D20?",
  "What's the method to get diamonds from farming?",
  "Show me the stats and abilities for the Kraken pet.",
];

// ─── Message Actions (Copy / Regenerate) ─────────────────────────────────────

function MessageActions({ content, onRegenerate, onReply, isLast, tokens, model }) {
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
      {(model || tokens) && (
        <div className="model-tokens-info" title="Model & Tokens">
          <LlamaIcon />
          <span>
            {model ? (model.includes('70b') ? 'llama-70b' : 'llama-8b') : ''}
            {model && tokens ? ' - ' : ''}
            {tokens ? <>{tokens.toLocaleString()} tokens</> : ''}
          </span>
        </div>
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

let giantRegex = null;
const itemMap = {};

fetch('/images.json')
  .then(r => r.json())
  .then(data => {
    for (const [name, url] of Object.entries(data)) {
      const norm = name.toLowerCase().replace(/[^a-z0-9]/g, '').replace(/s$/, '');
      itemMap[norm] = { name, url };
    }
    
    // Build a giant alternating regex of all item names, sorted by length descending
    const sortedItems = Object.keys(data).sort((a, b) => b.length - a.length);
    const escapedNames = sortedItems.map(n => {
      let escaped = n.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      // Replace literal spaces or escaped hyphens with a flexible matcher: space, hyphen, or nothing
      return escaped.replace(/( |\\-)/g, '[- ]?');
    });
    giantRegex = new RegExp(`\\b(${escapedNames.join('|')})s?\\b`, 'gi');
  })
  .catch(() => {});

const parseEmojis = (text) => {
  // Clean up LLM hallucinations where it wraps standard HTML-like emojis in backticks
  let cleaned = text.replace(/`(<a?:[a-zA-Z0-9_]+:\d+>[^`]*)`/g, "$1");
  
  cleaned = cleaned.replace(/<(a?):([a-zA-Z0-9_]+):(\d+)>/g, (_, isAnimated, name, id) => {
    const ext = isAnimated === 'a' ? 'gif' : 'png';
    return `![${name}](https://cdn.discordapp.com/emojis/${id}.${ext}?v=1)`;
  });

  if (giantRegex) {
    // Inject missing images using substring search for known items inside wrapped terms
    cleaned = cleaned.replace(/(!\[.*?\]\(.*?\)\s*)?(\*\*|\*)([^*`\n]+)\2/g, (match, existingImg, wrapper, term) => {
      if (existingImg || term.includes('![')) return match; 
      
      const newTerm = term.replace(giantRegex, (innerMatch, capturedName) => {
        const normName = capturedName.toLowerCase().replace(/[^a-z0-9]/g, '').replace(/s$/, '');
        const item = itemMap[normName];
        if (item) {
          return `![${item.name}](${item.url}) ${innerMatch}`;
        }
        return innerMatch;
      });
      
      return `${wrapper}${newTerm}${wrapper}`;
    });
  }
  
  return cleaned;
};

const mdComponents = {
  img: ({ node, src, ...props }) => {
    let optimizedSrc = src;
    if (src && src.includes('cdn.discordapp.com/emojis/')) {
      const baseUrl = src.split('?')[0];
      if (baseUrl.endsWith('.gif')) {
        optimizedSrc = baseUrl.replace('.gif', '.webp') + '?animated=true';
      } else if (baseUrl.endsWith('.png')) {
        optimizedSrc = baseUrl.replace('.png', '.webp') + '?animated=false&size=44';
      }
    }
    return (
      <img src={optimizedSrc} {...props} style={{ display: 'inline', width: 22, height: 22, verticalAlign: 'middle', margin: '0 4px' }} />
    );
  },
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
  const [isWakingUp, setIsWakingUp] = useState(false);
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

    // Always append to visual UI chat history with an empty assistant message for streaming
    setMessages(prev => [
      ...prev,
      {
        role: 'user',
        content: question,
        replyTo: contextToUse ? contextToUse[1].content : null
      },
      {
        role: 'assistant',
        content: '',
        statusLogs: [],
        contextDocs: null,
        isStreaming: true
      }
    ]);
    setInput('');
    setIsLoading(true);
    setIsWakingUp(false);
    setFollowUpContext(null);

    const wakeupTimer = setTimeout(() => {
      setIsWakingUp(true);
    }, 8000);

    try {
      const apiUrl = import.meta.env.VITE_API_URL || '';
      const response = await fetch(`${apiUrl}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: payloadMessages }),
      });

      clearTimeout(wakeupTimer);
      setIsWakingUp(false);

      if (!response.ok) {
        let errorMessage = `Server error (${response.status})`;
        if (response.status === 502 || response.status === 503 || response.status === 504) {
          errorMessage = "The backend is waking up from sleep. Please wait a moment and try again.";
        } else {
          try {
            const errData = await response.json();
            if (errData.detail) errorMessage = errData.detail;
          } catch (_) { }
        }
        throw new Error(errorMessage);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let done = false;
      let buffer = '';

      while (!done) {
        const { value, done: doneReading } = await reader.read();
        done = doneReading;
        if (value) {
          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop(); // Keep the last incomplete line in buffer

          for (const line of lines) {
            if (line.trim() === '') continue;
            try {
              const data = JSON.parse(line);
              setMessages(prev => {
                const newMessages = [...prev];
                const lastIdx = newMessages.length - 1;
                const lastMsg = { ...newMessages[lastIdx] };

                if (data.type === 'status') {
                  lastMsg.statusLogs = [...(lastMsg.statusLogs || []), data.message];
                } else if (data.type === 'context') {
                  lastMsg.contextDocs = { official: data.official, community: data.community };
                } else if (data.type === 'chunk') {
                  lastMsg.content += data.content;
                } else if (data.type === 'metadata') {
                  lastMsg.model = data.model;
                  lastMsg.tokens = data.tokens;
                } else if (data.type === 'error') {
                  lastMsg.content += `\n\n**Error:** ${data.message}`;
                  lastMsg.isError = true;
                }
                newMessages[lastIdx] = lastMsg;
                return newMessages;
              });
            } catch (e) {
              console.error('Error parsing stream line:', line, e);
            }
          }
        }
      }

      // When done, mark streaming as false
      setMessages(prev => {
        const newMessages = [...prev];
        const lastIdx = newMessages.length - 1;
        newMessages[lastIdx] = { ...newMessages[lastIdx], isStreaming: false };
        return newMessages;
      });

    } catch (error) {
      clearTimeout(wakeupTimer);
      setIsWakingUp(false);

      let displayError = error.message;
      if (displayError.includes('Failed to fetch') || displayError.includes('NetworkError')) {
        displayError = "The server is currently waking up or unavailable. Please wait a moment and try again.";
      }

      setMessages(prev => {
        const newMessages = [...prev];
        const lastIdx = newMessages.length - 1;
        newMessages[lastIdx] = {
          ...newMessages[lastIdx],
          content: newMessages[lastIdx].content + `\n\n**Error:** ${displayError}`,
          isError: true,
          isStreaming: false
        };
        return newMessages;
      });
    } finally {
      setIsLoading(false);
      clearTimeout(wakeupTimer);
      setIsWakingUp(false);
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
                    {(msg.statusLogs?.length > 0 || msg.contextDocs) && (
                      <ThoughtProcessBlock msg={msg} />
                    )}

                    {msg.content === '' && msg.statusLogs?.length > 0 ? null : (
                      <div className="prose message-anim-in">
                        <ReactMarkdown remarkPlugins={[remarkGfm]} components={mdComponents}>
                          {parseEmojis(msg.content)}
                        </ReactMarkdown>
                      </div>
                    )}
                    {!msg.isError && msg.content && !msg.isStreaming && (
                      <MessageActions
                        content={msg.content}
                        onRegenerate={handleRegenerate}
                        onReply={() => handleReplyClick(idx)}
                        isLast={isLastAssistant}
                        tokens={msg.tokens}
                        model={msg.model}
                      />
                    )}
                  </div>
                )}
              </div>
            );
          })}

          {/* Loading */}
          {isLoading && (!messages[messages.length - 1] || messages[messages.length - 1].role !== 'assistant') && (
            <div className="message message--assistant">
              <div className="assistant-content">
                <TypingIndicator />
                {isWakingUp && (
                  <div style={{ fontSize: '12px', color: 'var(--text-3)', marginTop: '8px' }}>
                    The backend is waking up from sleep. This usually takes about 50 seconds...
                  </div>
                )}
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
      <Analytics />
    </div>
  );
}
