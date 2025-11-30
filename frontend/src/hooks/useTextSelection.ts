/**
 * useTextSelection Hook
 *
 * Detects and tracks user text selection using the browser Selection API.
 * Listens to mouseup and selectionchange events to capture highlighted text
 * and its bounding box for tooltip positioning.
 *
 * @returns {object} Selected text and range information
 */

import { useEffect, useState } from 'react';
import type { TextSelection } from '@site/src/types';

interface UseTextSelectionReturn {
  selection: TextSelection | null;
  clearSelection: () => void;
}

export function useTextSelection(): UseTextSelectionReturn {
  const [selection, setSelection] = useState<TextSelection | null>(null);

  useEffect(() => {
    /**
     * Handle text selection events
     * Captures selected text and bounding rectangle for tooltip positioning
     */
    const handleSelection = () => {
      const sel = window.getSelection();

      // No selection or empty selection
      if (!sel || sel.rangeCount === 0) {
        setSelection(null);
        return;
      }

      const text = sel.toString().trim();

      // Empty selection (just a cursor)
      if (text.length === 0) {
        setSelection(null);
        return;
      }

      // Ignore selections inside input/textarea elements
      const activeElement = document.activeElement;
      if (
        activeElement &&
        (activeElement.tagName === 'INPUT' ||
          activeElement.tagName === 'TEXTAREA' ||
          activeElement.getAttribute('contenteditable') === 'true')
      ) {
        setSelection(null);
        return;
      }

      // Get the range and bounding rectangle
      const range = sel.getRangeAt(0);
      const rect = range.getBoundingClientRect();

      // Create DOMRect object for positioning
      const domRect: DOMRect = {
        x: rect.x,
        y: rect.y,
        width: rect.width,
        height: rect.height,
        top: rect.top,
        right: rect.right,
        bottom: rect.bottom,
        left: rect.left,
        toJSON: () => ({}),
      };

      setSelection({
        text,
        range: domRect,
        startOffset: range.startOffset,
        endOffset: range.endOffset,
      });
    };

    // Attach event listeners
    document.addEventListener('mouseup', handleSelection);
    document.addEventListener('selectionchange', handleSelection);

    // Cleanup on unmount
    return () => {
      document.removeEventListener('mouseup', handleSelection);
      document.removeEventListener('selectionchange', handleSelection);
    };
  }, []);

  /**
   * Manually clear the current selection
   */
  const clearSelection = () => {
    setSelection(null);
    window.getSelection()?.removeAllRanges();
  };

  return {
    selection,
    clearSelection,
  };
}
