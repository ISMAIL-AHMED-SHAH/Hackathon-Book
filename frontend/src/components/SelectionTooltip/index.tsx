/**
 * SelectionTooltip Component
 *
 * Displays a floating tooltip when text is selected, allowing users to
 * ask questions about the selected content via the chatbot.
 *
 * Features:
 * - Detects text selection using useTextSelection hook
 * - Positions tooltip near selection using Floating UI
 * - Handles viewport edge cases with flip and shift middleware
 * - Triggers chatbot with selected text as context
 */

import React, { useEffect, useRef, useState } from 'react';
import {
  useFloating,
  offset,
  flip,
  shift,
  autoUpdate,
} from '@floating-ui/react';
import { useTextSelection } from '@site/src/hooks/useTextSelection';
import styles from './styles.module.css';

interface SelectionTooltipProps {
  onAskAboutText: (selectedText: string) => void;
}

export default function SelectionTooltip({ onAskAboutText }: SelectionTooltipProps): JSX.Element | null {
  const selection = useTextSelection();
  const [isVisible, setIsVisible] = useState(false);
  const [virtualElement, setVirtualElement] = useState<{
    getBoundingClientRect: () => DOMRect;
  } | null>(null);

  const { refs, floatingStyles, update } = useFloating({
    placement: 'top',
    middleware: [
      offset(10),
      flip(),
      shift({ padding: 8 }),
    ],
    whileElementsMounted: autoUpdate,
  });

  // Update virtual element when selection changes
  useEffect(() => {
    if (selection && selection.text && selection.text.trim().length > 0) {
      // Create virtual element from selection range
      const range = selection.range;
      setVirtualElement({
        getBoundingClientRect: () => range,
      });
      setIsVisible(true);
    } else {
      setIsVisible(false);
      setVirtualElement(null);
    }
  }, [selection]);

  // Update floating position when virtual element changes
  useEffect(() => {
    if (virtualElement) {
      refs.setReference(virtualElement);
      update?.();
    }
  }, [virtualElement, refs, update]);

  const handleAskAboutThis = () => {
    if (selection && selection.text) {
      onAskAboutText(selection.text);
      setIsVisible(false);
      // Clear selection
      window.getSelection()?.removeAllRanges();
    }
  };

  if (!isVisible || !selection) {
    return null;
  }

  return (
    <div
      ref={refs.setFloating}
      style={floatingStyles}
      className={styles.tooltip}
    >
      <button
        onClick={handleAskAboutThis}
        className={styles.askButton}
        aria-label="Ask about selected text"
      >
        💬 Ask about this
      </button>
    </div>
  );
}
