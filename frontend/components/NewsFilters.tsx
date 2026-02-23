'use client';

import { useRouter, useSearchParams } from 'next/navigation';

export default function NewsFilters() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const setParam = (key: string, value: string) => {
    const p = new URLSearchParams(searchParams.toString());
    p.set(key, value);
    router.push(`/news?${p.toString()}`);
  };

  return (
    <div className="row" style={{ marginBottom: 12 }}>
      <select defaultValue={searchParams.get('topic') || 'all'} onChange={(e) => setParam('topic', e.target.value)}>
        <option value="all">All</option>
        <option value="ai">AI</option>
        <option value="scitech">ScienceTech</option>
      </select>
      <select defaultValue={searchParams.get('range') || '7d'} onChange={(e) => setParam('range', e.target.value)}>
        <option value="24h">24h</option>
        <option value="7d">7d</option>
        <option value="30d">30d</option>
        <option value="all">ALL</option>
      </select>
      <input
        defaultValue={searchParams.get('query') || ''}
        placeholder="검색"
        onKeyDown={(e) => {
          if (e.key === 'Enter') setParam('query', (e.target as HTMLInputElement).value);
        }}
      />
    </div>
  );
}
