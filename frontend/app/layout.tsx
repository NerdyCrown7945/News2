import './globals.css';
import Link from 'next/link';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body>
        <div className="container">
          <h1><Link href="/news">AI / SciTech News Digest</Link></h1>
          {children}
        </div>
      </body>
    </html>
  );
}
