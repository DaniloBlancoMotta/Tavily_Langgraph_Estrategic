'use client';
import { useState, useCallback } from 'react';
import { Message } from '@/lib/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export function useChat() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [threadId] = useState(() => crypto.randomUUID());

    const sendMessage = useCallback(async (content: string) => {
        if (!content.trim() || isLoading) return;

        const userMessage: Message = {
            id: crypto.randomUUID(),
            role: 'user',
            content: content.trim(),
            logs: [],
        };

        const assistantMessage: Message = {
            id: crypto.randomUUID(),
            role: 'assistant',
            content: '',
            logs: [],
            isStreaming: true,
        };

        setMessages(prev => [...prev, userMessage, assistantMessage]);
        setIsLoading(true);
        setError(null);

        try {
            const response = await fetch(`${API_URL}/api/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: content, thread_id: threadId }),
            });

            if (!response.ok) throw new Error('Erro na requisição');

            const reader = response.body?.getReader();
            const decoder = new TextDecoder();

            if (!reader) throw new Error('Stream não disponível');

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value);
                const lines = chunk.split('\n').filter(Boolean);

                for (const line of lines) {
                    try {
                        const data = JSON.parse(line);

                        setMessages(prev => {
                            const updated = [...prev];
                            const lastMsg = updated[updated.length - 1];

                            if (data.type === 'log') {
                                lastMsg.logs = [...lastMsg.logs, data.content];
                            } else if (data.type === 'answer') {
                                lastMsg.content = data.content;
                            } else if (data.type === 'error') {
                                setError(data.content);
                            }

                            return updated;
                        });
                    } catch {
                        // Ignore parse errors
                    }
                }
            }

            setMessages(prev => {
                const updated = [...prev];
                updated[updated.length - 1].isStreaming = false;
                return updated;
            });
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Erro desconhecido');
        } finally {
            setIsLoading(false);
        }
    }, [isLoading, threadId]);

    const clearMessages = useCallback(() => {
        setMessages([]);
        setError(null);
    }, []);

    return { messages, isLoading, error, sendMessage, clearMessages };
}
