'use client';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { ChevronDown, Hexagon, User } from 'lucide-react';
import { useState } from 'react';
import { Message } from '@/lib/types';

interface MessageBubbleProps {
    message: Message;
}

export function MessageBubble({ message }: MessageBubbleProps) {
    const [showLogs, setShowLogs] = useState(false);
    const isUser = message.role === 'user';

    if (isUser) {
        return (
            <div className="flex justify-end mb-4">
                <div className="flex items-start gap-3 max-w-[80%]">
                    <div className="bg-gray-100 rounded-2xl px-4 py-3 text-gray-800">
                        <p className="leading-relaxed">{message.content}</p>
                    </div>
                    <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0">
                        <User size={16} className="text-gray-600" />
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="flex justify-start mb-6">
            <div className="flex items-start gap-3 max-w-[85%]">
                <div className="w-8 h-8 rounded-lg bg-navy flex items-center justify-center flex-shrink-0">
                    <Hexagon size={16} className="text-white" />
                </div>
                <div className="flex-1">
                    {message.logs.length > 0 && (
                        <button
                            onClick={() => setShowLogs(!showLogs)}
                            className="flex items-center gap-1 text-xs text-gray-400 mb-2 hover:text-gray-600 transition-colors"
                        >
                            <ChevronDown
                                size={14}
                                className={`transition-transform ${showLogs ? 'rotate-180' : ''}`}
                            />
                            Ver processo ({message.logs.length})
                        </button>
                    )}

                    {showLogs && message.logs.length > 0 && (
                        <div className="bg-gray-50 rounded-lg p-3 mb-3 border border-gray-100">
                            {message.logs.map((log, i) => (
                                <p key={i} className="text-xs text-gray-500 italic">
                                    {log}
                                </p>
                            ))}
                        </div>
                    )}

                    <div className="prose prose-gray max-w-none">
                        {message.isStreaming && !message.content ? (
                            <div className="flex items-center gap-2 text-gray-400">
                                <div className="w-2 h-2 bg-navy rounded-full animate-pulse" />
                                <span className="text-sm">Analisando...</span>
                            </div>
                        ) : (
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                {message.content}
                            </ReactMarkdown>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
