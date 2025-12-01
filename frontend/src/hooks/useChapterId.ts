/**
 * useChapterId Hook
 *
 * Detects the current chapter ID based on the URL pathname.
 * Uses the chapter mapper plugin data to provide context-aware chapter IDs
 * for chatbot queries.
 *
 * @returns {string | null} Current chapter ID or null if not on a chapter page
 */

import { useLocation } from '@docusaurus/router';
import useGlobalData from '@docusaurus/useGlobalData';

interface ChapterMapperData {
  chapterMap: Record<string, string | null>;
}

export function useChapterId(): string | null {
  const location = useLocation();
  const globalData = useGlobalData();

  // Get chapter map from plugin data
  const pluginData = globalData['chapter-mapper-plugin'] as ChapterMapperData | undefined;
  const chapterMap = pluginData?.chapterMap;

  if (!chapterMap) {
    console.warn('[useChapterId] Chapter map not loaded from plugin');
    return null;
  }

  // Ensure location and pathname exist
  if (!location || !location.pathname) {
    console.warn('[useChapterId] Location or pathname not available');
    return null;
  }

  // Normalize pathname: remove trailing slashes and hash fragments
  let pathname = location.pathname;
  pathname = pathname.replace(/\/$/, ''); // Remove trailing slash
  pathname = pathname.split('#')[0];      // Remove hash fragment
  pathname = pathname.split('?')[0];      // Remove query string

  // Look up chapter ID in the map
  const chapterId = chapterMap[pathname];

  // Return chapter ID or null if not found
  return chapterId !== undefined ? chapterId : null;
}
