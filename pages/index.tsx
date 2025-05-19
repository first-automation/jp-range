import { useEffect, useRef } from 'react';
import { Univer } from '@univerjs/core';
import { UniverUI } from '@univerjs/ui';
import { SheetPlugin } from '@univerjs/sheets';

export default function Home() {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (containerRef.current) {
      const univer = new Univer();
      univer.registerPlugin(UniverUI);
      univer.registerPlugin(SheetPlugin);
      univer.createSpreadsheet({
        container: containerRef.current,
      });
    }
  }, []);

  return <div style={{ width: '100%', height: '100vh' }} ref={containerRef}></div>;
}
