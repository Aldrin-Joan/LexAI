/**
 * WebSocket Manager — singleton with auto-reconnect
 * and EventEmitter-style listener pattern.
 */

const WS_BASE = `ws://localhost:8001`;

class WebSocketManager {
  constructor() {
    this.socket = null;
    this.listeners = {};
    this.reconnectDelay = 3000;
    this.maxDelay = 30000;
    this.shouldReconnect = false;
    this.url = null;
  }

  connect(path, token) {
    const url = token
      ? `${WS_BASE}${path}?token=${token}`
      : `${WS_BASE}${path}`;
    this.url = url;
    this.shouldReconnect = true;
    this._open(url);
  }

  _open(url) {
    if (this.socket) {
      this.socket.onclose = null;
      this.socket.close();
    }
    this.socket = new WebSocket(url);

    this.socket.onopen = () => {
      this.reconnectDelay = 3000;
      this._emit('open');
    };

    this.socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this._emit('message', data);
      } catch {
        this._emit('message', { raw: event.data });
      }
    };

    this.socket.onerror = (err) => {
      this._emit('error', err);
    };

    this.socket.onclose = () => {
      this._emit('close');
      if (this.shouldReconnect) {
        setTimeout(() => {
          this.reconnectDelay = Math.min(
            this.reconnectDelay * 1.5,
            this.maxDelay
          );
          this._open(this.url);
        }, this.reconnectDelay);
      }
    };
  }

  send(data) {
    if (this.socket?.readyState === WebSocket.OPEN) {
      const payload = typeof data === 'string' ? data : JSON.stringify(data);
      this.socket.send(payload);
    }
  }

  disconnect() {
    this.shouldReconnect = false;
    if (this.socket) {
      this.socket.onclose = null;
      this.socket.close();
      this.socket = null;
    }
  }

  on(event, callback) {
    if (!this.listeners[event]) this.listeners[event] = [];
    this.listeners[event].push(callback);
    return () => this.off(event, callback);
  }

  off(event, callback) {
    if (this.listeners[event]) {
      this.listeners[event] = this.listeners[event].filter(
        (cb) => cb !== callback
      );
    }
  }

  _emit(event, data) {
    (this.listeners[event] || []).forEach((cb) => cb(data));
  }

  get isOpen() {
    return this.socket?.readyState === WebSocket.OPEN;
  }
}

export const wsManager = new WebSocketManager();
