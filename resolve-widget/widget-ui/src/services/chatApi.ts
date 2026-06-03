import { API_BASE_URL } from "../config/api";

export const chatApi = {
  async getHistory(conversationId: string) {
    const response = await fetch(
      `${API_BASE_URL}/chat/history/${conversationId}`,
    );

    if (!response.ok) {
      throw new Error("Failed to load history");
    }

    return response.json();
  },
};
