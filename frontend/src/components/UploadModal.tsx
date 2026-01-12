'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { api } from '@/lib/api';
import { X, Upload, FileText } from 'lucide-react';

interface UploadModalProps {
    isOpen: boolean;
    onClose: () => void;
    onUploaded: () => void;
    kbId: string;
}

export default function UploadModal({ isOpen, onClose, onUploaded, kbId }: UploadModalProps) {
    const t = useTranslations('UploadModal');
    const [files, setFiles] = useState<FileList | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    if (!isOpen) return null;

    const handleUpload = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!files || files.length === 0) return;

        setLoading(true);
        setError('');

        try {
            const formData = new FormData();
            for (let i = 0; i < files.length; i++) {
                formData.append('files', files[i]);
            }

            await api.post(`/kb/${kbId}/documents`, formData);

            setFiles(null);
            onUploaded();
            onClose();
        } catch (err: any) {
            setError(err.message || 'Upload failed');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
            <div className="bg-white dark:bg-zinc-800 rounded-lg shadow-xl w-full max-w-md mx-4">
                <div className="flex justify-between items-center p-4 border-b dark:border-zinc-700">
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white">{t('title')}</h3>
                    <button onClick={onClose} className="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300">
                        <X className="h-5 w-5" />
                    </button>
                </div>

                <form onSubmit={handleUpload} className="p-4 space-y-4">
                    <div className="border-2 border-dashed border-gray-300 dark:border-zinc-600 rounded-md p-6 flex flex-col items-center justify-center text-center dark:bg-zinc-800/50">
                        <Upload className="h-8 w-8 text-gray-400 mb-2" />
                        <label htmlFor="file-upload" className="cursor-pointer">
                            <span className="mt-2 block text-sm font-medium text-gray-900 dark:text-gray-300">
                                {files && files.length > 0 ? `${files.length} files selected` : t('dragDrop')}
                            </span>
                            <input
                                id="file-upload"
                                name="file-upload"
                                type="file"
                                className="sr-only"
                                multiple
                                accept=".pdf,.md,.txt"
                                onChange={(e) => setFiles(e.target.files)}
                            />
                        </label>
                        <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">{t('support')}</p>
                    </div>

                    {files && files.length > 0 && (
                        <div className="text-sm text-gray-600 dark:text-gray-300 bg-gray-50 dark:bg-zinc-700 p-2 rounded">
                            {Array.from(files).map((f, i) => (
                                <div key={i} className="flex items-center">
                                    <FileText className="h-4 w-4 mr-2" /> {f.name}
                                </div>
                            ))}
                        </div>
                    )}

                    {error && <div className="text-sm text-red-600">{error}</div>}

                    <div className="flex justify-end space-x-3 pt-2">
                        <button
                            type="button"
                            onClick={onClose}
                            className="px-4 py-2 border border-gray-300 dark:border-zinc-600 rounded-md text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-zinc-700"
                        >
                            {t('cancel')}
                        </button>
                        <button
                            type="submit"
                            disabled={loading || !files}
                            className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
                        >
                            {loading ? t('uploading') : t('upload')}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
