export interface ChatMessage {
  role: "user" | "assistant";
  message: string;
  timestamp?: Date | string;
}


export interface WidgetChatConfig {
  userId?: string;
  userEmail?: string;
}

export interface ChatResponse {
  conversation_id?: string;
  ai_response?: string;
  type?: string;
  delta?: string;
  error?: string;
}
