/**
 * Root Component Swizzle
 *
 * This component wraps the entire Docusaurus application.
 * It never unmounts during navigation, making it perfect for
 * injecting persistent UI elements like the chatbot widget.
 *
 * @see https://docusaurus.io/docs/swizzling
 */

import React from 'react';
import BrowserOnly from '@docusaurus/BrowserOnly';
import ChatbotWidget from '@site/src/components/ChatbotWidget';

interface RootProps {
  children: React.ReactNode;
}

export default function Root({ children }: RootProps): JSX.Element {
  return (
    <>
      {children}
      <BrowserOnly fallback={<div></div>}>
        {() => <ChatbotWidget />}
      </BrowserOnly>
    </>
  );
}
