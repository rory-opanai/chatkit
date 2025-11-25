import { ChatKit, useChatKit } from "@openai/chatkit-react";

import {
  LISTING_CHATKIT_API_DOMAIN_KEY,
  LISTING_CHATKIT_API_URL,
  LISTING_COMPOSER_PLACEHOLDER,
  LISTING_GREETING,
  LISTING_STARTER_PROMPTS,
} from "../lib/config";

type ChatKitPanelProps = {
  onThreadChange: (threadId: string | null) => void;
  onResponseCompleted: () => void;
};

export function ChatKitPanel({
  onThreadChange,
  onResponseCompleted,
}: ChatKitPanelProps) {
  const chatkit = useChatKit({
    api: {
      url: LISTING_CHATKIT_API_URL,
      domainKey: LISTING_CHATKIT_API_DOMAIN_KEY,
    },
    theme: {
      colorScheme: "light",
      color: {
        grayscale: {
          hue: 220,
          tint: 6,
          shade: -2,
        },
        accent: {
          primary: "#0f172a",
          level: 1,
        },
      },
      radius: "round",
    },
    startScreen: {
      greeting: LISTING_GREETING,
      prompts: LISTING_STARTER_PROMPTS,
    },
    composer: {
      placeholder: LISTING_COMPOSER_PLACEHOLDER,
    },
    threadItemActions: {
      feedback: false,
    },
    onResponseEnd: onResponseCompleted,
    onThreadChange: ({ threadId }) => onThreadChange(threadId ?? null),
    onError: ({ error }) => {
      console.error("ChatKit error", error);
    },
  });

  return (
    <div className="relative h-full w-full overflow-hidden rounded-3xl border border-slate-200/60 bg-white shadow-card">
      <ChatKit control={chatkit.control} className="block h-full w-full" />
    </div>
  );
}
