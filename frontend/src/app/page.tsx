'use client';
import { useState, useRef, useEffect } from 'react';
import { Trash2, Settings, Sliders, CheckSquare, X } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  logs?: string[];
  resources?: { url: string; title: string }[];
}

const DOMAINS = [
  { id: 'mckinsey.com', label: 'McKinsey' },
  { id: 'bcg.com', label: 'BCG' },
  { id: 'bain.com', label: 'Bain' },
  { id: 'gartner.com', label: 'Gartner' },
  { id: 'ey.com', label: 'EY' },
  { id: 'hbr.org', label: 'HBR' },
  { id: 'mit.edu', label: 'MIT' },
];

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [threadId, setThreadId] = useState(() => crypto.randomUUID()); // State so we can reset it

  // Config State
  const [model, setModel] = useState('groq');
  const [temperature, setTemperature] = useState(0.2);
  const [maxTokens, setMaxTokens] = useState(4096);
  const [selectedDomains, setSelectedDomains] = useState<string[]>(DOMAINS.map(d => d.id));
  const [showSettings, setShowSettings] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const clearChat = () => {
    if (confirm('Tem certeza que deseja limpar o chat?')) {
      setMessages([]);
      setThreadId(crypto.randomUUID()); // Reset thread for backend memory
    }
  };

  const toggleDomain = (domain: string) => {
    if (selectedDomains.includes(domain)) {
      setSelectedDomains(prev => prev.filter(d => d !== domain));
    } else {
      setSelectedDomains(prev => [...prev, domain]);
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: input,
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    const assistantMessage: Message = {
      id: crypto.randomUUID(),
      role: 'assistant',
      content: '',
      logs: [],
      resources: [],
    };

    setMessages(prev => [...prev, assistantMessage]);

    try {
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: input,
          thread_id: threadId,
          model,
          temperature,
          max_tokens: maxTokens,
          search_domains: selectedDomains
        }),
      });

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      while (reader) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n').filter(Boolean);

        for (const line of lines) {
          const data = JSON.parse(line);

          setMessages(prev => {
            const newMessages = [...prev];
            const lastMsg = newMessages[newMessages.length - 1];

            if (data.type === 'log') {
              lastMsg.logs = [...(lastMsg.logs || []), data.message];
            } else if (data.type === 'answer') {
              lastMsg.content = (lastMsg.content || "") + data.content; // Concatenar se não for completo, mas backend geralmente manda full token stream. Backend server.py envia full content updates? 
              // Wait, server logic: yield json.dumps({"type": "answer", "content": msg.content})
              // LangGraph astream updates often send the *new* chunk or accumulated message.
              // Logic check: msg.content in LangGraph usually is the accumulated content if stream_mode="values", or delta if "messages" key in "updates".
              // In this server implementation: node_data["messages"] contains the FULL message object from the node.
              // So it replaces content. Let's fix loop to just replace content.
              lastMsg.content = data.content;
            } else if (data.type === 'resources') {
              lastMsg.resources = data.data;
            }

            return newMessages;
          });
        }
      }
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex relative overflow-hidden">

      {/* Settings Overlay (Mobile/Desktop Toggle) */}
      <div className={`fixed inset-y-0 right-0 w-80 bg-white border-l shadow-2xl transform transition-transform duration-300 z-50 overflow-y-auto ${showSettings ? 'translate-x-0' : 'translate-x-full'}`}>
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="font-serif text-lg font-bold text-navy flex items-center gap-2">
              <Settings className="w-5 h-5" /> Configurações
            </h2>
            <button onClick={() => setShowSettings(false)} className="text-gray-400 hover:text-red-500">
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Model Params */}
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Modelo</label>
              <select
                value={model}
                onChange={(e) => setModel(e.target.value)}
                className="w-full p-2 border rounded-md text-sm"
              >
                <option value="groq">Llama 3.3 70B (Groq)</option>
                <option value="kimi">Kimi K2 Instruct</option>
              </select>
            </div>

            <div>
              <div className="flex justify-between mb-1">
                <label className="block text-sm font-medium text-gray-700">Temperatura: {temperature}</label>
                <span className="text-xs text-gray-400">Criatividade vs Precisão</span>
              </div>
              <input
                type="range" min="0" max="1" step="0.1"
                value={temperature}
                onChange={(e) => setTemperature(parseFloat(e.target.value))}
                className="w-full"
              />
              <p className="text-xs text-gray-500 mt-1">
                Baixa (0.0-0.3): Fatos precisos, código.<br />
                Alta (0.7+): Ideias criativas, brainstorming.
              </p>
            </div>

            <div>
              <div className="flex justify-between mb-1">
                <label className="block text-sm font-medium text-gray-700">Max Tokens: {maxTokens}</label>
                <span className="text-xs text-gray-400">Tamanho da resposta</span>
              </div>
              <select
                value={maxTokens}
                onChange={(e) => setMaxTokens(parseInt(e.target.value))}
                className="w-full p-2 border rounded-md text-sm"
              >
                <option value="1024">1024 (Rápido)</option>
                <option value="2048">2048 (Padrão)</option>
                <option value="4096">4096 (Longo)</option>
                <option value="8192">8192 (Muito Longo)</option>
              </select>
              <p className="text-xs text-gray-500 mt-1">Limita o comprimento máximo da resposta gerada.</p>
            </div>

            {/* Domains - Moved to Sidebar */}
          </div>
        </div>
      </div>

      {/* Sidebar (Left) */}
      <aside className="hidden lg:flex w-72 border-r border-gray-200 bg-white flex-col justify-between p-6">
        <div className="flex-1 overflow-y-auto">
          <h1 className="font-serif text-lg text-navy font-bold mb-1 leading-tight">Consultoria Estratégica + Big Four</h1>
          <p className="text-xs text-gray-500 mb-6">Powered by GenAI</p>

          <div className="space-y-2 mb-8">
            <button
              onClick={() => setShowSettings(!showSettings)}
              className="w-full flex items-center gap-2 p-2 text-sm text-gray-600 hover:bg-gray-50 rounded-lg border border-gray-200"
            >
              <Settings className="w-4 h-4" /> Configurações
            </button>

            <button
              onClick={clearChat}
              className="w-full flex items-center gap-2 p-2 text-sm text-red-600 hover:bg-red-50 rounded-lg border border-red-100"
            >
              <Trash2 className="w-4 h-4" /> Limpar Chat
            </button>
          </div>

          <div className="mb-6">
            <label className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3 block">Fontes Selecionadas</label>
            <div className="space-y-2">
              {DOMAINS.map((domain) => (
                <label key={domain.id} className="flex items-center gap-2 cursor-pointer hover:bg-gray-50 p-1 rounded group transition-colors">
                  <div className={`w-4 h-4 rounded border flex items-center justify-center transition-colors ${selectedDomains.includes(domain.id) ? 'bg-navy border-navy' : 'border-gray-300'}`}>
                    {selectedDomains.includes(domain.id) && <CheckSquare className="w-3 h-3 text-white" />}
                    <input
                      type="checkbox"
                      className="hidden"
                      checked={selectedDomains.includes(domain.id)}
                      onChange={() => toggleDomain(domain.id)}
                    />
                  </div>
                  <span className={`text-sm ${selectedDomains.includes(domain.id) ? 'text-navy font-medium' : 'text-gray-500'}`}>{domain.label}</span>
                </label>
              ))}
            </div>
          </div>
        </div>

        <div className="text-xs text-gray-400 pt-4 border-t">
          <p>v2.5.0</p>
        </div>
      </aside>

      {/* Main Chat Area */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden relative">
        <header className="lg:hidden p-4 border-b flex justify-between items-center bg-white">
          <h1 className="font-serif text-base text-navy font-bold">Consultoria Estratégica</h1>
          <button onClick={() => setShowSettings(true)} className="p-2">
            <Settings className="w-5 h-5" />
          </button>
        </header>

        <div className="flex-1 overflow-y-auto p-4 md:p-8 scroll-smooth w-full max-w-4xl mx-auto">
          {messages.length === 0 ? (
            <div className="text-center py-20 animate-in fade-in duration-500">
              <div className="w-16 h-16 bg-navy/10 rounded-full flex items-center justify-center mx-auto mb-6">
                <span className="text-2xl">A</span>
              </div>
              <h2 className="font-serif text-3xl text-gray-800 mb-4 font-medium">How can I help today?</h2>
              <p className="text-gray-500 max-w-md mx-auto mb-8">
                I am a consultant specialized in governance and strategy. My answers are based on sources like Gartner, McKinsey, and MIT.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-lg mx-auto">
                {['Estratégia de Adoção de IA', 'Framework Data Mesh', 'Cultura Data-Driven', 'Governance Risk Compliance'].map((q) => (
                  <button
                    key={q}
                    onClick={() => setInput(q)}
                    className="p-4 border border-gray-200 hover:border-navy hover:bg-navy/5 rounded-xl text-left transition-colors text-sm font-medium text-gray-700"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="space-y-8 pb-4">
              {messages.map((msg) => (
                <div key={msg.id} className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  {msg.role === 'assistant' && (
                    <div className="w-8 h-8 rounded-full bg-navy flex-shrink-0 flex items-center justify-center text-white text-xs">
                      AI
                    </div>
                  )}

                  <div className={`max-w-[85%] lg:max-w-[75%] ${msg.role === 'user' ? 'bg-navy text-white shadow-md' : 'bg-white shadow-sm border border-gray-100'} rounded-2xl px-6 py-5`}>

                    {/* Logs Collapsible */}
                    {msg.logs && msg.logs.length > 0 && (
                      <details className="mb-4 group">
                        <summary className="text-xs text-gray-400 cursor-pointer list-none flex items-center gap-1 hover:text-gray-600">
                          <span className="w-1.5 h-1.5 rounded-full bg-gray-400"></span>
                          Thought Process ({msg.logs.length} steps)
                        </summary>
                        <div className="mt-2 pl-2 border-l-2 border-gray-100 space-y-1">
                          {msg.logs.map((log, i) => (
                            <div key={i} className="text-xs text-gray-500 font-mono">{log}</div>
                          ))}
                        </div>
                      </details>
                    )}

                    {/* Content */}
                    <div className={`prose ${msg.role === 'user' ? 'prose-invert' : 'prose-gray'} max-w-none text-sm md:text-base leading-relaxed`}>
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {msg.content}
                      </ReactMarkdown>
                    </div>

                    {/* Resources */}
                    {msg.resources && msg.resources.length > 0 && (
                      <div className="mt-6 pt-4 border-t border-gray-100">
                        <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Fontes Verificadas</h4>
                        <div className="grid gap-2">
                          {msg.resources.map((r, i) => (
                            <a key={i} href={r.url} target="_blank" rel="noopener noreferrer" className="block p-2 rounded hover:bg-gray-50 border border-transparent hover:border-gray-200 transition-all group">
                              <div className="text-sm font-medium text-navy group-hover:underline truncate">{r.title}</div>
                              <div className="text-xs text-gray-400 truncate">{r.url}</div>
                            </a>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="p-4 bg-white border-t border-gray-100 shadow-lg-up">
          <div className="max-w-4xl mx-auto flex gap-3 relative">
            <button
              onClick={clearChat}
              className="lg:hidden absolute -top-12 right-0 p-2 bg-white rounded-full shadow border text-red-500"
              title="Limpar Chat"
            >
              <Trash2 className="w-4 h-4" />
            </button>

            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  sendMessage();
                }
              }}
              placeholder="Digite sua pergunta estratégica..."
              className="flex-1 p-4 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-navy focus:border-transparent resize-none h-[60px] max-h-[120px] shadow-sm text-sm"
              disabled={isLoading}
            />
            <button
              onClick={sendMessage}
              disabled={isLoading || !input.trim()}
              className="px-6 rounded-xl bg-navy text-white font-medium hover:bg-navy-dark disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-md flex items-center gap-2"
            >
              {isLoading ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                'Enviar'
              )}
            </button>
          </div>
          <div className="text-center mt-2">
            <span className="text-[10px] text-gray-400">
              Modelo: {model === 'groq' ? 'Llama 3.3 70B' : 'Kimi K2'} • Temp: {temperature} • Tokens: {maxTokens}
            </span>
          </div>
        </div>
      </main>
    </div>
  );
}
