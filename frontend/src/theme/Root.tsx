/**
 * Root Component Swizzle
 *
 * This component wraps the entire Docusaurus application.
 * It never unmounts during navigation, making it perfect for
 * injecting persistent UI elements like the chatbot widget and selection tooltip.
 *
 * @see https://docusaurus.io/docs/swizzling
 */

import React, { useRef } from 'react';
import BrowserOnly from '@docusaurus/BrowserOnly';
import ChatbotWidget, { ChatbotWidgetRef } from '@site/src/components/ChatbotWidget';
import SelectionTooltip from '@site/src/components/SelectionTooltip';

interface RootProps {
  children: React.ReactNode;
}

export default function Root({ children }: RootProps): JSX.Element {
  const chatbotRef = useRef<ChatbotWidgetRef>(null);

  const handleAskAboutText = (selectedText: string) => {
    if (chatbotRef.current) {
      chatbotRef.current.openWithSelectedText(selectedText);
    }
  };

  return (
    <>
      {children}
      {/* Temporarily disabled chatbot and selection tooltip to debug crash */}
      {/* <BrowserOnly fallback={<div></div>}>
        {() => (
          <>
            <ChatbotWidget ref={chatbotRef} />
            <SelectionTooltip onAskAboutText={handleAskAboutText} />
          </>
        )}
      </BrowserOnly> */}
    </>
  );
}
