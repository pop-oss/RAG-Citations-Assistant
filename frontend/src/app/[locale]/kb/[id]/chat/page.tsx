'use client';

import { use } from 'react';
import Header from '@/components/Header';
import ChatInterface from '@/components/ChatInterface';

export default function ChatPage({ params }: { params: Promise<{ id: string }> }) {
    const { id } = use(params);

    return (
        <div className="h-screen flex flex-col bg-gray-50">
            <Header />
            <div className="flex-1 overflow-hidden">
                <ChatInterface kbId={id} />
            </div>
        </div>
    );
}
