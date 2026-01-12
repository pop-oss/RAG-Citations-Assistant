'use client';

import { Link, useRouter } from '@/i18n/routing';
import { useTranslations } from 'next-intl';
import { LogOut, User } from 'lucide-react';
import LanguageSwitcher from './LanguageSwitcher';

export default function Header() {
    const router = useRouter();
    const t = useTranslations('Common');

    const handleLogout = () => {
        if (typeof window !== 'undefined') {
            localStorage.removeItem('token');
        }
        router.push('/login');
    };

    return (
        <header className="bg-white dark:bg-zinc-800 shadow">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
                <div className="flex items-center">
                    <Link href="/dashboard" className="text-xl font-bold text-indigo-600 dark:text-indigo-400">
                        RAG Knowledge Base
                    </Link>
                </div>
                <div className="flex items-center space-x-4">
                    <LanguageSwitcher />
                    <div className="flex items-center text-gray-500 dark:text-gray-300">
                        <User className="h-5 w-5 mr-1" />
                        <span className="text-sm">{t('admin')}</span>
                    </div>
                    <button
                        onClick={handleLogout}
                        className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 rounded-full hover:bg-gray-100 dark:hover:bg-zinc-700"
                        title={t('logout')}
                    >
                        <LogOut className="h-5 w-5" />
                    </button>
                </div>
            </div>
        </header>
    );
}
