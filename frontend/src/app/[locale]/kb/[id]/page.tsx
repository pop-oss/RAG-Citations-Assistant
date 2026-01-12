'use client';

import { useEffect, useState, use } from 'react';
import { Link } from '@/i18n/routing';
import { useTranslations } from 'next-intl';
import { api } from '@/lib/api';
import { KnowledgeBase, Document } from '@/lib/types';
import Header from '@/components/Header';
import UploadModal from '@/components/UploadModal';
import { Upload, MessageSquare, ArrowLeft, RefreshCw, CheckCircle, AlertCircle, Clock, FileText } from 'lucide-react';

export default function KBDetailPage({ params }: { params: Promise<{ id: string }> }) {
    const { id } = use(params);
    const t = useTranslations('KBDetail');

    const [kb, setKb] = useState<KnowledgeBase | null>(null);
    const [documents, setDocuments] = useState<Document[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [isUploadOpen, setIsUploadOpen] = useState(false);

    const fetchData = async () => {
        try {
            setLoading(true);
            const kbData = await api.get<KnowledgeBase>(`/kb/${id}`);
            setKb(kbData);

            const docData = await api.get<Document[]>(`/kb/${id}/documents`);
            setDocuments(Array.isArray(docData) ? docData : []);
        } catch (err: any) {
            setError(err.message || 'Failed to load data');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, [id]);

    const refreshDocuments = async () => {
        try {
            const docData = await api.get<Document[]>(`/kb/${id}/documents`);
            setDocuments(Array.isArray(docData) ? docData : []);
        } catch (e) {
            console.error(e);
        }
    };

    const StatusIcon = ({ status }: { status: Document['status'] }) => {
        if (status === 'ready') return <CheckCircle className="h-5 w-5 text-green-500" />;
        if (status === 'failed') return <AlertCircle className="h-5 w-5 text-red-500" />;
        return <Clock className="h-5 w-5 text-yellow-500 animate-pulse" />;
    };

    const getStatusLabel = (status: string) => {
        // @ts-ignore
        return t(`status.${status}`) || status;
    };

    if (loading) return <div className="min-h-screen bg-gray-50 dark:bg-zinc-900 flex items-center justify-center dark:text-gray-300">Loading...</div>;
    if (!kb) return <div className="min-h-screen bg-gray-50 dark:bg-zinc-900 flex items-center justify-center text-red-600">Knowledge Base not found</div>;

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-zinc-900">
            <Header />

            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {/* Breadcrumb / Back */}
                <div className="mb-6">
                    <Link href="/dashboard" className="text-indigo-600 hover:text-indigo-800 dark:text-indigo-400 dark:hover:text-indigo-300 flex items-center">
                        <ArrowLeft className="h-4 w-4 mr-1" /> {t('backToDashboard')}
                    </Link>
                </div>

                {/* KB Header */}
                <div className="bg-white dark:bg-zinc-800 shadow rounded-lg p-6 mb-8">
                    <div className="flex justify-between items-start">
                        <div>
                            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">{kb.name}</h1>
                            <p className="mt-2 text-gray-600 dark:text-gray-400">{kb.description}</p>
                        </div>
                        <div className="flex space-x-3">
                            <button
                                onClick={() => setIsUploadOpen(true)}
                                className="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-zinc-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-zinc-700 hover:bg-gray-50 dark:hover:bg-zinc-600"
                            >
                                <Upload className="h-4 w-4 mr-2" />
                                {t('uploadDocs')}
                            </button>
                            <Link
                                href={`/kb/${kb.id}/chat`}
                                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700"
                            >
                                <MessageSquare className="h-4 w-4 mr-2" />
                                {t('startChat')}
                            </Link>
                        </div>
                    </div>
                </div>

                {/* Document List */}
                <div className="bg-white dark:bg-zinc-800 shadow rounded-lg overflow-hidden">
                    <div className="px-6 py-4 border-b border-gray-200 dark:border-zinc-700 flex justify-between items-center">
                        <h3 className="text-lg font-medium text-gray-900 dark:text-white">{t('documents')} ({documents.length})</h3>
                        <button onClick={refreshDocuments} className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200" title={t('refresh')}>
                            <RefreshCw className="h-4 w-4" />
                        </button>
                    </div>

                    {documents.length === 0 ? (
                        <div className="p-8 text-center text-gray-500 dark:text-gray-400">
                            <FileText className="mx-auto h-12 w-12 text-gray-300 dark:text-gray-600 mb-3" />
                            {t('noDocs')}
                        </div>
                    ) : (
                        <ul className="divide-y divide-gray-200 dark:divide-zinc-700">
                            {documents.map((doc) => (
                                <li key={doc.id} className="px-6 py-4 hover:bg-gray-50 dark:hover:bg-zinc-700/50 flex justify-between items-center">
                                    <div className="flex items-center">
                                        <FileText className="h-5 w-5 text-gray-400 dark:text-gray-500 mr-3" />
                                        <div>
                                            <p className="text-sm font-medium text-gray-900 dark:text-white">{doc.filename}</p>
                                            <p className="text-xs text-gray-500 dark:text-gray-400">{new Date(doc.created_at).toLocaleString()}</p>
                                        </div>
                                    </div>
                                    <div className="flex items-center space-x-4">
                                        <span className="flex items-center text-sm capitalize dark:text-gray-300">
                                            <div className="mr-2"><StatusIcon status={doc.status} /></div>
                                            {getStatusLabel(doc.status)}
                                        </span>
                                    </div>
                                </li>
                            ))}
                        </ul>
                    )}
                </div>
            </main>

            <UploadModal
                isOpen={isUploadOpen}
                onClose={() => setIsUploadOpen(false)}
                onUploaded={() => { refreshDocuments(); }}
                kbId={kb.id}
            />
        </div>
    );
}
