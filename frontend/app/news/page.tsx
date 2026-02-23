import Link from 'next/link';
import IngestButton from '@/components/IngestButton';
import NewsFilters from '@/components/NewsFilters';
import { getFeed } from '@/lib/api';

export default async function NewsPage({ searchParams }: { searchParams: Record<string, string> }) {
  const topic = searchParams.topic || 'all';
  const range = searchParams.range || '7d';
  const query = searchParams.query || '';
  const { items, fallback } = await getFeed({ topic, range, query, sort: 'new' });

  return (
    <main>
      {fallback && <div className="banner">API 실패로 정적 데이터 표시 중</div>}
      <div className="row" style={{ justifyContent: 'space-between', alignItems: 'center' }}>
        <NewsFilters />
        <IngestButton />
      </div>
      {items.map((item) => (
        <Link href={`/news/${item.id}`} key={item.id}>
          <article className="card">
            <h3>{item.title_ko || item.title}</h3>
            <p>{item.summary_one_liner_ko || '요약 없음'}</p>
            <div className="row small">
              <span>{item.source}</span>
              <span>{item.published_at?.slice(0, 19).replace('T', ' ')}</span>
            </div>
            <div style={{ marginTop: 8 }}>
              {(item.tags || []).slice(0, 5).map((t) => (
                <span key={t} className="badge">#{t}</span>
              ))}
              {!item.url && <span className="badge warn">원문 링크 없음</span>}
            </div>
          </article>
        </Link>
      ))}
    </main>
  );
}
