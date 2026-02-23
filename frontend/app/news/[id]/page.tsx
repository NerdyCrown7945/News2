import { getArticle } from '@/lib/api';

export default async function NewsDetail({ params }: { params: { id: string } }) {
  const { item, fallback } = await getArticle(params.id);

  if (!item) {
    return <div>기사를 찾을 수 없습니다.</div>;
  }

  return (
    <main className="card">
      {fallback && <span className="badge">정적 데이터 표시 중</span>}
      <h2>{item.title_ko || item.title}</h2>
      <p className="small">{item.source} · {item.published_at?.slice(0, 19).replace('T', ' ')}</p>

      <h4>요약</h4>
      <ul>
        {(item.summary_lines_ko || [item.summary_one_liner_ko]).map((line, idx) => <li key={idx}>{line}</li>)}
      </ul>

      <h4>핵심 포인트</h4>
      <ul>
        {(item.key_points_ko || []).map((p, idx) => <li key={idx}>{p}</li>)}
      </ul>

      {item.url ? (
        <p><a href={item.url} target="_blank">원문 기사 페이지 열기</a></p>
      ) : (
        <div className="banner">이 항목은 유효한 개별 기사 URL이 없어 원문 링크를 제공하지 않습니다.</div>
      )}
    </main>
  );
}
