'use client';

import { useEffect, useState } from 'react';
import { Link } from '@/i18n/routing';
import { useTranslations } from 'next-intl';
import { api } from '@/lib/api';
import { KnowledgeBase } from '@/lib/types';
import Header from '@/components/Header';
import CreateKBModal from '@/components/CreateKBModal';
import { Plus, Database, Trash2 } from 'lucide-react';

export default function DashboardPage() {
    const t = useTranslations('Dashboard');
    const [kbs, setKbs] = useState<KnowledgeBase[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [isModalOpen, setIsModalOpen] = useState(false);

    const fetchKbs = async () => {
        try {
            const data = await api.get<KnowledgeBase[]>('/kb');
            setKbs(Array.isArray(data) ? data : []); // Ensure array
        } catch (err: any) {
            setError(err.message || 'Failed to load Knowledge Bases');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchKbs();
    }, []);

    const handleDelete = async (e: React.MouseEvent, id: string) => {
        e.preventDefault(); // Prevent link navigation
        if (!confirm(t('deleteConfirm'))) return;

        try {
            await api.delete(`/kb/${id}`);
            setKbs(kbs.filter((kb) => kb.id !== id));
        } catch (err: any) {
            alert(err.message || 'Failed to delete');
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-zinc-900">
            <Header />

            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="flex justify-between items-center mb-6">
                    <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{t('title')}</h1>
                    <button
                        onClick={() => setIsModalOpen(true)}
                        className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700"
                    >
                        <Plus className="h-4 w-4 mr-2" />
                        {t('newKB')}
                    </button>
                </div>

                {loading ? (
                    <div className="text-center py-12 dark:text-gray-300">Loading...</div>
                ) : error ? (
                    <div className="text-center py-12 text-red-600">{error}</div>
                ) : kbs.length === 0 ? (
                    <div className="text-center py-12 bg-white dark:bg-zinc-800 rounded-lg shadow dashed border-2 border-gray-200 dark:border-zinc-700">
                        <Database className="mx-auto h-12 w-12 text-gray-400" />
                        <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">{t('noKB')}</h3>
                        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">{t('noKBDesc')}</p>
                    </div>
                ) : (
                    <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                        {kbs.map((kb) => (
                            <Link
                                key={kb.id}
                                href={`/kb/${kb.id}`}
                                className="block bg-white dark:bg-zinc-800 overflow-hidden shadow rounded-lg hover:shadow-md transition-shadow"
                            >
                                <div className="px-4 py-5 sm:p-6">
                                    <div className="flex justify-between items-start">
                                        <div className="flex items-center">
                                            <div className="flex-shrink-0 bg-indigo-100 dark:bg-indigo-900/50 rounded-md p-3">
                                                <Database className="h-6 w-6 text-indigo-600 dark:text-indigo-400" />
                                            </div>
                                            <div className="ml-4">
                                                <h3 className="text-lg font-medium text-gray-900 dark:text-white truncate">{kb.name}</h3>
                                                <p className="text-sm text-gray-500 dark:text-gray-400">{new Date(kb.created_at).toLocaleDateString()}</p>
                                            </div>
                                        </div>
                                        <button
                                            onClick={(e) => handleDelete(e, kb.id)}
                                            className="text-gray-400 hover:text-red-600 dark:hover:text-red-400"
                                            title={t('delete')}
                                        >
                                            <Trash2 className="h-4 w-4" />
                                        </button>
                                    </div>
                                    {kb.description && (
                                        <p className="mt-4 text-sm text-gray-500 dark:text-gray-400 line-clamp-2">{kb.description}</p>
                                    )}
                                </div>
                            </Link>
                        ))}
                    </div>
                )}
            </main>

            <CreateKBModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                onCreated={fetchKbs}
            />
        </div>
    );
}
