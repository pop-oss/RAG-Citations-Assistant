"use client";

import { usePathname, useRouter } from "next/navigation";
import { useLocale } from "next-intl";
import { useTransition } from "react";

export default function LanguageSwitcher() {
    const router = useRouter();
    const pathname = usePathname();
    const localActive = useLocale();
    const [isPending, startTransition] = useTransition();

    const onSelectChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        const nextLocale = e.target.value;
        startTransition(() => {
            // Replace the locale in the pathname
            // /en/dashboard -> /zh/dashboard
            const segments = pathname.split('/');
            segments[1] = nextLocale;
            const newPath = segments.join('/');

            router.replace(newPath);
        });
    };

    return (
        <select
            defaultValue={localActive}
            className="bg-transparent border border-gray-300 text-gray-700 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
            onChange={onSelectChange}
            disabled={isPending}
        >
            <option value="en">English</option>
            <option value="zh">中文</option>
        </select>
    );
}
