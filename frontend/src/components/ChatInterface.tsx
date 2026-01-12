'use client';

import { useState, useRef, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { Send, Settings, User, Bot, AlertTriangle } from 'lucide-react';
import { Message, Citation } from '@/lib/types';
import { parseSSEStream } from '@/lib/streamParser';
import CitationList from './CitationList';

interface ChatInterfaceProps {
    kbId: string;
}

export default function ChatInterface({ kbId }: ChatInterfaceProps) {
    const t = useTranslations('ChatInterface');
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [model, setModel] = useState('deepseek'); // Default from prompt
    const [error, setError] = useState('');
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || loading) return;

        const userMsg: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: input,
            created_at: new Date().toISOString(),
        };

        setMessages((prev) => [...prev, userMsg]);
        setInput('');
        setLoading(true);
        setError('');

        // Create placeholder for assistant message
        const assistantMsgId = (Date.now() + 1).toString();
        const assistantMsg: Message = {
            id: assistantMsgId,
            role: 'assistant',
            content: '',
            created_at: new Date().toISOString(),
            citations: [],
        };
        setMessages((prev) => [...prev, assistantMsg]);

        try {
            // Get token from auth
            const token = localStorage.getItem('token');
            // POST /api/kb/{kb_id}/chat/stream
            // Use fetch directly for streaming support
            const response = await fetch(`/api/kb/${kbId}/chat/stream`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
                },
                body: JSON.stringify({ message: userMsg.content, chat_provider: model }), // 'chat_provider' per contract
            });

            if (!response.ok) {
                throw new Error(`Error: ${response.statusText}`);
            }

            if (!response.body) throw new Error('No response body');

            const reader = response.body.getReader();

            await parseSSEStream(reader, (event) => {
                setMessages((prev) => {
                    const newMessages = [...prev];
                    const lastMsgIndex = newMessages.findIndex((m) => m.id === assistantMsgId);
                    if (lastMsgIndex === -1) return prev;

                    const lastMsg = { ...newMessages[lastMsgIndex] };

                    if (event.type === 'token') {
                        lastMsg.content += event.data.token;
                    } else if (event.type === 'citations') {
                        lastMsg.citations = event.data.citations;
                    } else if (event.type === 'error') {
                        // Handle error in stream
                        console.error('Stream error:', event.data);
                        // Optionally show error in message or toaster
                    }

                    newMessages[lastMsgIndex] = lastMsg;
                    return newMessages;
                });
            });

        } catch (err: any) {
            console.error(err);
            setError(err.message || 'Failed to send message');
            // Remove the incomplete assistant message or mark as error?
            // For now keep it to show partial content if any.
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-full bg-white dark:bg-zinc-800">
            {/* Model Selector Bar */}
            <div className="px-4 py-2 border-b dark:border-zinc-700 bg-gray-50 dark:bg-zinc-900 flex items-center justify-between">
                <div className="flex items-center text-sm text-gray-700 dark:text-gray-300">
                    <Settings className="h-4 w-4 mr-2" />
                    <span className="mr-2">Model:</span>
                    <select
                        value={model}
                        onChange={(e) => setModel(e.target.value)}
                        className="bg-white dark:bg-zinc-800 border dark:border-zinc-600 text-gray-700 dark:text-gray-300 text-sm rounded-md focus:ring-indigo-500 focus:border-indigo-500 block p-1"
                    >
                        <option value="deepseek">DeepSeek</option>
                        <option value="zhipu">Zhipu (ChatGLM)</option>
                        <option value="qwen">Qwen (Tongyi)</option>
                    </select>
                </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-6 bg-gray-50 dark:bg-zinc-900">
                {messages.length === 0 && (
                    <div className="flex items-center justify-center h-full text-gray-400 dark:text-gray-500">
                        <p>{t('placeholder')}</p>
                    </div>
                )}
                {messages.map((msg) => (
                    <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`flex max-w-3xl ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                            <div className={`flex-shrink-0 h-8 w-8 rounded-full flex items-center justify-center mx-2 ${msg.role === 'user' ? 'bg-indigo-600' : 'bg-green-600'}`}>
                                {msg.role === 'user' ? <User className="h-5 w-5 text-white" /> : <Bot className="h-5 w-5 text-white" />}
                            </div>
                            <div className={`p-4 rounded-lg shadow-sm text-sm ${msg.role === 'user'
                                ? 'bg-indigo-600 text-white rounded-br-none'
                                : 'bg-white dark:bg-zinc-800 border border-gray-200 dark:border-zinc-700 text-gray-800 dark:text-gray-200 rounded-bl-none'
                                }`}>
                                <div className="whitespace-pre-wrap">{msg.content}</div>
                                {msg.citations && msg.citations.length > 0 && (
                                    <div className="mt-2 text-left">
                                        {/* Ensure citations are rendered nicely mainly for assistant */}
                                        <CitationList citations={msg.citations} />
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                ))}
                {error && (
                    <div className="flex justify-center">
                        <div className="bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 px-4 py-2 rounded-md text-sm flex items-center">
                            <AlertTriangle className="h-4 w-4 mr-2" /> {error}
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="border-t dark:border-zinc-700 p-4 bg-white dark:bg-zinc-800">
                <form onSubmit={handleSend} className="max-w-4xl mx-auto relative">
                    <input
                        type="text"
                        className="w-full border-gray-300 dark:border-zinc-600 dark:bg-zinc-700 dark:text-white rounded-full pl-5 pr-12 py-3 shadow-sm focus:ring-indigo-500 focus:border-indigo-500 placeholder-gray-400 dark:placeholder-gray-500"
                        placeholder={t('placeholder')}
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        disabled={loading}
                    />
                    <button
                        type="submit"
                        disabled={loading || !input.trim()}
                        className="absolute right-2 top-2 p-2 bg-indigo-600 text-white rounded-full hover:bg-indigo-700 disabled:opacity-50"
                    >
                        <Send className="h-4 w-4" />
                    </button>
                </form>
            </div>
        </div>
    );
}
