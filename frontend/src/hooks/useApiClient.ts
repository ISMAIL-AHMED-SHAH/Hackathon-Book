/**
 * useApiClient Hook
 *
 * Provides a configured HTTP client for making requests to the backend RAG API.
 * Includes timeout handling, error responses, and environment-based configuration.
 *
 * @returns {object} API client with fetchData method and configuration
 */

import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import type { ChatbotQuery, ChatbotResponse, StandardErrorResponse } from '@site/src/types';

interface ApiClientConfig {
  apiUrl: string;
  apiTimeout: number;
}

interface ApiClientReturn {
  apiUrl: string;
  fetchData: <T = ChatbotResponse>(
    endpoint: string,
    options?: RequestInit
  ) => Promise<T>;
  postQuery: (query: ChatbotQuery) => Promise<ChatbotResponse>;
}

export function useApiClient(): ApiClientReturn {
  const { siteConfig } = useDocusaurusContext();

  // Get API configuration from customFields
  const apiUrl = (siteConfig.customFields?.apiUrl as string) || 'http://localhost:8000';
  const apiTimeoutStr = (siteConfig.customFields?.apiTimeout as string) || '10000';
  const apiTimeout = parseInt(apiTimeoutStr, 10);

  /**
   * Generic fetch wrapper with timeout and error handling
   */
  const fetchData = async <T = ChatbotResponse>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> => {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), apiTimeout);

    try {
      const url = `${apiUrl}${endpoint}`;
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });

      clearTimeout(timeoutId);

      // Handle non-OK responses
      if (!response.ok) {
        let errorData: StandardErrorResponse;
        try {
          errorData = await response.json();
        } catch {
          // If JSON parsing fails, create generic error
          errorData = {
            error_code: 'HTTP_ERROR',
            message: `HTTP ${response.status}: ${response.statusText}`,
          };
        }

        throw new Error(errorData.message || `HTTP ${response.status}`);
      }

      // Parse and return successful response
      return await response.json();
    } catch (error) {
      clearTimeout(timeoutId);

      // Handle timeout errors
      if (error instanceof Error && error.name === 'AbortError') {
        throw new Error('Request timeout - please try again');
      }

      // Re-throw other errors
      throw error;
    }
  };

  /**
   * Specialized method for posting chatbot queries
   */
  const postQuery = async (query: ChatbotQuery): Promise<ChatbotResponse> => {
    return fetchData<ChatbotResponse>('/v1/query', {
      method: 'POST',
      body: JSON.stringify(query),
    });
  };

  return {
    apiUrl,
    fetchData,
    postQuery,
  };
}
