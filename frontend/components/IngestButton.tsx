'use client';

import { useState } from 'react';
import { triggerIngest } from '@/lib/api';

export default function IngestButton() {
  const [loading, setLoading] = useState(false);
  const staticOnly = process.env.NEXT_PUBLIC_STATIC_ONLY === 'true';

  return (
    <button
      disabled={loading || staticOnly}
      onClick={async () => {
        setLoading(true);
        try {
          await triggerIngest();
          alert('수집 완료');
        } catch {
          alert('수집 실패');
        } finally {
          setLoading(false);
        }
      }}
    >
      {loading ? '수집 중...' : '수집 실행'}
    </button>
  );
}
