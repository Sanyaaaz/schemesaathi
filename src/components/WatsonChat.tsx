import { useEffect } from "react";

type WatsonAssistantInstance = {
  render: () => Promise<void>;
};

declare global {
  interface Window {
    watsonAssistantChatOptions?: {
      integrationID: string;
      region: string;
      serviceInstanceID: string;
      onLoad: (instance: WatsonAssistantInstance) => Promise<void>;
      clientVersion?: string;
    };
  }
}

const WatsonChat = () => {
  useEffect(() => {
    if (window.watsonAssistantChatOptions) return;

    window.watsonAssistantChatOptions = {
      integrationID: "f2ef4728-7b6d-4bee-8a20-10eb01153608",
      region: "us-south",
      serviceInstanceID: "6dd129f6-9666-4912-9219-af195937f9eb",
      onLoad: async (instance) => {
        await instance.render();
      },
    };

    setTimeout(() => {
      const script = document.createElement("script");
      script.src =
        "https://web-chat.global.assistant.watson.appdomain.cloud/versions/" +
        (window.watsonAssistantChatOptions?.clientVersion || "latest") +
        "/WatsonAssistantChatEntry.js";
      document.head.appendChild(script);
    }, 0);
  }, []);

  return null; // No visible UI needed unless you want to display a label or help
};

export default WatsonChat;
