'use client';

import { useTranslations } from 'next-intl';
import { Citation } from '@/lib/types';
import { FileText, ChevronDown, ChevronRight } from 'lucide-react';
import { useState } from 'react';

export default function CitationList({ citations }: { citations: Citation[] }) {
    const t = useTranslations('ChatInterface');
    const [isOpen, setIsOpen] = useState(false);

    if (!citations || citations.length === 0) return null;

    return (
        <div className="mt-2 border-t pt-2 border-gray-100 dark:border-zinc-700">
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="flex items-center text-xs text-indigo-600 hover:text-indigo-800 dark:text-indigo-400 dark:hover:text-indigo-300 font-medium"
            >
                {isOpen ? <ChevronDown className="h-3 w-3 mr-1" /> : <ChevronRight className="h-3 w-3 mr-1" />}
                {citations.length} {t('sources')}
            </button>

            {isOpen && (
                <div className="mt-2 space-y-2">
                    {citations.map((cite, idx) => (
                        <div key={idx} className="bg-gray-50 dark:bg-zinc-700/50 p-2 rounded text-xs border border-gray-200 dark:border-zinc-600">
                            <div className="flex items-start">
                                <FileText className="h-3 w-3 text-gray-400 dark:text-gray-500 mt-0.5 mr-1 flex-shrink-0" />
                                <div>
                                    <span className="font-semibold text-gray-700 dark:text-gray-200 block">{cite.filename}</span>
                                    {cite.page_number && <span className="text-gray-500 dark:text-gray-400 block">{t('page')} {cite.page_number}</span>}
                                    {cite.line_range && <span className="text-gray-500 dark:text-gray-400 block">{t('lines')} {cite.line_range}</span>}
                                    <p className="mt-1 text-gray-600 dark:text-gray-300 italic bg-white dark:bg-zinc-700 p-1 rounded border border-gray-100 dark:border-zinc-600">
                                        "...{cite.text}..."
                                    </p>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
