export type FeedItem = {
  id: number;
  title: string;
  title_ko: string;
  url: string;
  source: string;
  topic: 'ai' | 'scitech' | 'all' | string;
  published_at: string;
  summary_one_liner_ko: string;
  tags: string[];
};

export type ArticleDetail = FeedItem & {
  snippet?: string;
  summary_lines_ko?: string[];
  key_points_ko?: string[];
};
