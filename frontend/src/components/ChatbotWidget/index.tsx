/**
 * ChatbotWidget Component
 *
 * A persistent floating chatbot widget that appears on every page.
 * Integrates with the backend RAG API to answer questions about textbook content.
 *
 * Features:
 * - Open/close toggle
 * - Query submission with chapter context
 * - Response rendering with source citations
 * - Error handling for API failures
 * - Loading states
 * - Selected text context support
 */

import React, { useState, useEffect, useImperativeHandle, forwardRef } from 'react';
import { useChapterId } from '@site/src/hooks/useChapterId';
import { useApiClient } from '@site/src/hooks/useApiClient';
import type {
  ChatbotQuery,
  ChatbotResponse,
  ConversationTurn,
  SourceCitation,
} from '@site/src/types';
import { GUEST_USER_ID } from '@site/src/types';
import styles from './styles.module.css';

export interface ChatbotWidgetRef {
  openWithSelectedText: (text: string) => void;
}

const ChatbotWidget = forwardRef<ChatbotWidgetRef>((props, ref) => {
  // State management
  const [isOpen, setIsOpen] = useState(false);
  const [currentQuery, setCurrentQuery] = useState('');
  const [selectedText, setSelectedText] = useState<string | null>(null);
  const [conversationHistory, setConversationHistory] = useState<ConversationTurn[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Hooks
  const chapterId = useChapterId();
  const { postQuery } = useApiClient();

  // Expose methods to parent via ref
  useImperativeHandle(ref, () => ({
    openWithSelectedText: (text: string) => {
      setSelectedText(text);
      setIsOpen(true);
      setCurrentQuery(''); // Clear any existing query
    },
  }));

  /**
   * Handle query submission
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validate query
    if (!currentQuery.trim()) {
      return;
    }

    // Build query object
    const query: ChatbotQuery = {
      query_text: currentQuery.trim(),
      chapter_id: chapterId,
      user_id: GUEST_USER_ID,
      ...(selectedText && { selected_text: selectedText }),
    };

    setIsLoading(true);
    setError(null);

    try {
      // Call backend API
      const response: ChatbotResponse = await postQuery(query);

      // Add to conversation history
      const turn: ConversationTurn = {
        query,
        response,
        timestamp: new Date().toISOString(),
      };

      setConversationHistory([...conversationHistory, turn]);
      setCurrentQuery(''); // Clear input
      setSelectedText(null); // Clear selected text context
    } catch (err) {
      // Handle errors
      const errorMessage = err instanceof Error ? err.message : 'Failed to get response';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Render a single source citation
   */
  const renderSource = (source: SourceCitation, index: number): JSX.Element => {
    return (
      <div key={source.chunk_id || index} className={styles.source}>
        <div className={styles.sourceHeader}>
          <strong>{source.section_title}</strong>
          <span className={styles.similarity}>
            {(source.similarity_score * 100).toFixed(0)}% match
          </span>
        </div>
        <p className={styles.sourceExcerpt}>{source.content_excerpt}</p>
      </div>
    );
  };

  /**
   * Render a conversation turn (question + answer)
   */
  const renderTurn = (turn: ConversationTurn, index: number): JSX.Element => {
    return (
      <div key={index} className={styles.turn}>
        {/* User question */}
        <div className={styles.question}>
          <strong>You:</strong> {turn.query.query_text}
        </div>

        {/* AI answer */}
        <div className={styles.answer}>
          <strong>AI:</strong>
          <p>{turn.response.answer}</p>

          {/* Source citations */}
          {turn.response.sources.length > 0 && (
            <div className={styles.sources}>
              <div className={styles.sourcesHeader}>Sources:</div>
              {turn.response.sources.map((source, idx) => renderSource(source, idx))}
            </div>
          )}

          {/* Metadata */}
          <div className={styles.metadata}>
            <span>Confidence: {(turn.response.confidence_score * 100).toFixed(0)}%</span>
            <span>Status: {turn.response.grounding_status}</span>
            <span>Time: {turn.response.processing_time_ms}ms</span>
          </div>
        </div>
      </div>
    );
  };

  return (
    <>
      {/* Toggle button (always visible) */}
      <button
        className={`${styles.toggleButton} ${isOpen ? styles.open : ''}`}
        onClick={() => setIsOpen(!isOpen)}
        aria-label={isOpen ? 'Close chatbot' : 'Open chatbot'}
      >
        {isOpen ? '✕' : '💬'}
      </button>

      {/* Chat panel (shown when open) */}
      {isOpen && (
        <div className={styles.chatPanel}>
          {/* Header */}
          <div className={styles.header}>
            <h3>AI Assistant</h3>
            {chapterId && (
              <span className={styles.context}>Context: {chapterId}</span>
            )}
          </div>

          {/* Conversation history */}
          <div className={styles.conversationHistory}>
            {conversationHistory.length === 0 ? (
              <div className={styles.emptyState}>
                <p>Ask me anything about the textbook!</p>
                <p className={styles.example}>
                  Try: "What are ROS 2 nodes?" or "Explain pub/sub pattern"
                </p>
              </div>
            ) : (
              conversationHistory.map((turn, index) => renderTurn(turn, index))
            )}

            {/* Loading indicator */}
            {isLoading && (
              <div className={styles.loading}>
                <div className={styles.spinner}></div>
                <p>Thinking...</p>
              </div>
            )}

            {/* Error message */}
            {error && (
              <div className={styles.error}>
                <strong>Error:</strong> {error}
              </div>
            )}
          </div>

          {/* Selected text context (if available) */}
          {selectedText && (
            <div className={styles.selectedTextContext}>
              <div className={styles.selectedTextLabel}>
                <strong>Selected:</strong>
                <button
                  onClick={() => setSelectedText(null)}
                  className={styles.clearButton}
                  aria-label="Clear selected text"
                >
                  ✕
                </button>
              </div>
              <div className={styles.selectedTextContent}>
                {selectedText.length > 100
                  ? `${selectedText.substring(0, 100)}...`
                  : selectedText}
              </div>
            </div>
          )}

          {/* Input form */}
          <form onSubmit={handleSubmit} className={styles.inputForm}>
            <input
              type="text"
              value={currentQuery}
              onChange={(e) => setCurrentQuery(e.target.value)}
              placeholder={selectedText ? "Ask about the selected text..." : "Ask a question..."}
              className={styles.input}
              disabled={isLoading}
              aria-label="Question input"
            />
            <button
              type="submit"
              className={styles.submitButton}
              disabled={isLoading || !currentQuery.trim()}
              aria-label="Submit question"
            >
              {isLoading ? '⏳' : '→'}
            </button>
          </form>
        </div>
      )}
    </>
  );
});

export default ChatbotWidget;
