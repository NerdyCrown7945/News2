import { ArticleDetail, FeedItem } from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://127.0.0.1:8000';
const STATIC_ONLY = process.env.NEXT_PUBLIC_STATIC_ONLY === 'true';

export async function getFeed(params: Record<string, string>) {
  const qs = new URLSearchParams(params).toString();
  if (!STATIC_ONLY) {
    try {
      const r = await fetch(`${API_BASE}/feed?${qs}`, { cache: 'no-store' });
      if (!r.ok) throw new Error('api failed');
      const data = await r.json();
      return { items: data.items as FeedItem[], fallback: false };
    } catch {
      // fallback
    }
  }
  const r = await fetch('/data/feed.json', { cache: 'no-store' });
  const data = await r.json();
  return { items: data.items as FeedItem[], fallback: true };
}

export async function getArticle(id: string) {
  if (!STATIC_ONLY) {
    try {
      const r = await fetch(`${API_BASE}/article/${id}`, { cache: 'no-store' });
      if (!r.ok) throw new Error('api failed');
      const data = await r.json();
      return { item: data as ArticleDetail, fallback: false };
    } catch {}
  }

  const r = await fetch(`/data/articles/${id}.json`, { cache: 'no-store' });
  const data = await r.json();
  return { item: data as ArticleDetail, fallback: true };
}

export async function triggerIngest() {
  const r = await fetch(`${API_BASE}/ingest/run`, { method: 'POST' });
  if (!r.ok) throw new Error('failed');
  return r.json();
}
