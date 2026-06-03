export class WidgetWebSocket {
  private socket: WebSocket | null = null;

  connect(
    url: string,
    onMessage: (data: any) => void,
    onOpen?: () => void,
    onClose?: () => void,
    onError?: () => void,
  ) {
    this.socket = new WebSocket(url);

    this.socket.onopen = () => {
      onOpen?.();
    };

    this.socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
      } catch (error) {
        console.error(error);
      }
    };

    this.socket.onclose = () => {
      onClose?.();
    };

    this.socket.onerror = () => {
      onError?.();
    };
  }

  send(payload: any) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(payload));
    }
  }

  disconnect() {
    this.socket?.close();
  }

  isConnected() {
    return this.socket?.readyState === WebSocket.OPEN;
  }
}
