import { useEffect, useRef } from 'react';
import { UniverInstanceType, LocaleType } from '@univerjs/core';
import { createUniver } from '@univerjs/presets';
import { UniverSheetsCorePreset } from '@univerjs/preset-sheets-core';

const locales = {
  [LocaleType.EN_US]: {
    sheet: {
      defaultSheetName: 'Sheet',
      operation: {
        rename: 'Rename'
      }
    },
    common: {
      confirm: 'Confirm',
      cancel: 'Cancel'
    }
  }
};

import '@univerjs/design/lib/index.css';
import '@univerjs/ui/lib/index.css';
import '@univerjs/sheets-ui/lib/index.css';
import '@univerjs/docs-ui/lib/index.css';

export default function Home() {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    try {
      const { univer } = createUniver({
        locale: LocaleType.EN_US,
        locales,
        presets: [UniverSheetsCorePreset({
          sheets: {
            scrollConfig: {
              minWidth: 1200
            }
          }
        })]
      });
      
      const workbook = univer.createUnit(UniverInstanceType.UNIVER_SHEET, {
        container: containerRef.current,
        sheetConfig: {
          columnCount: 26,
          rowCount: 100,
          defaultColumnWidth: 120,
          defaultRowHeight: 30,
          viewportWidth: 1200,
          viewportHeight: 800
        }
      });
    } catch (error) {
      console.error('Error initializing Univer:', error);
    }
  }, []);

  return <div style={{ width: '100%', height: '100vh', minWidth: '1200px', display: 'flex', flexDirection: 'column' }} ref={containerRef}></div>;
}
