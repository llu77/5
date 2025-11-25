/**
 * Frontend Integration Example
 * How to use the Cloudflare Pages Functions API from React
 */

import { useState, useEffect } from 'react';

// ============================================
// 1. API Client Setup
// ============================================

const API_BASE_URL = import.meta.env.PROD
  ? 'https://your-project.pages.dev'
  : 'http://localhost:8788';

class APIClient {
  private token: string | null = null;

  constructor() {
    // Load token from localStorage
    this.token = localStorage.getItem('authToken');
  }

  setToken(token: string) {
    this.token = token;
    localStorage.setItem('authToken', token);
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('authToken');
  }

  private async fetch(endpoint: string, options: RequestInit = {}) {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'Request failed' }));
      throw new Error(error.error || `HTTP ${response.status}`);
    }

    return response.json();
  }

  // Auth endpoints
  async login(email: string, password: string) {
    const data = await this.fetch('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });

    this.setToken(data.token);
    return data;
  }

  async register(email: string, password: string, name: string) {
    const data = await this.fetch('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, name }),
    });

    this.setToken(data.token);
    return data;
  }

  async logout() {
    await this.fetch('/api/auth/logout', { method: 'POST' });
    this.clearToken();
  }

  async getCurrentUser() {
    return this.fetch('/api/auth/me');
  }

  // Chat endpoints
  async sendMessage(message: string, conversationId?: string) {
    return this.fetch('/api/chat', {
      method: 'POST',
      body: JSON.stringify({
        message,
        conversationId,
        model: 'claude-sonnet-4-5-20250929',
        maxTokens: 2048,
      }),
    });
  }

  async getConversation(conversationId: string) {
    return this.fetch(`/api/chat?conversationId=${conversationId}`);
  }

  async deleteConversation(conversationId: string) {
    return this.fetch(`/api/chat?conversationId=${conversationId}`, {
      method: 'DELETE',
    });
  }

  // Health check
  async healthCheck() {
    return this.fetch('/api/health');
  }
}

export const api = new APIClient();

// ============================================
// 2. React Hooks
// ============================================

export function useAuth() {
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadUser();
  }, []);

  async function loadUser() {
    try {
      const data = await api.getCurrentUser();
      setUser(data.user);
    } catch (err) {
      console.error('Failed to load user:', err);
    } finally {
      setLoading(false);
    }
  }

  async function login(email: string, password: string) {
    setLoading(true);
    setError(null);

    try {
      const data = await api.login(email, password);
      setUser(data.user);
      return data;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Login failed';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }

  async function register(email: string, password: string, name: string) {
    setLoading(true);
    setError(null);

    try {
      const data = await api.register(email, password, name);
      setUser(data.user);
      return data;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Registration failed';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }

  async function logout() {
    setLoading(true);

    try {
      await api.logout();
      setUser(null);
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      setLoading(false);
    }
  }

  return {
    user,
    loading,
    error,
    login,
    register,
    logout,
    isAuthenticated: !!user,
  };
}

export function useChat() {
  const [messages, setMessages] = useState<any[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function sendMessage(content: string) {
    setLoading(true);
    setError(null);

    const userMessage = {
      role: 'user',
      content,
      timestamp: Date.now(),
    };

    setMessages(prev => [...prev, userMessage]);

    try {
      const response = await api.sendMessage(content, conversationId || undefined);

      const assistantMessage = {
        role: 'assistant',
        content: response.response,
        timestamp: Date.now(),
        cached: response.cached,
      };

      setMessages(prev => [...prev, assistantMessage]);
      setConversationId(response.conversationId);

      return response;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to send message';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }

  async function loadConversation(id: string) {
    setLoading(true);
    setError(null);

    try {
      const response = await api.getConversation(id);
      setMessages(response.messages);
      setConversationId(id);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load conversation';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }

  async function clearConversation() {
    if (conversationId) {
      try {
        await api.deleteConversation(conversationId);
      } catch (err) {
        console.error('Failed to delete conversation:', err);
      }
    }

    setMessages([]);
    setConversationId(null);
  }

  return {
    messages,
    conversationId,
    loading,
    error,
    sendMessage,
    loadConversation,
    clearConversation,
  };
}

// ============================================
// 3. Example Components
// ============================================

// Login Component
export function LoginForm() {
  const { login, loading, error } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();

    try {
      await login(email, password);
      // Redirect to dashboard
    } catch (err) {
      // Error is handled by hook
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <h2>Login</h2>

      {error && <div className="error">{error}</div>}

      <input
        type="email"
        value={email}
        onChange={e => setEmail(e.target.value)}
        placeholder="Email"
        required
      />

      <input
        type="password"
        value={password}
        onChange={e => setPassword(e.target.value)}
        placeholder="Password"
        required
      />

      <button type="submit" disabled={loading}>
        {loading ? 'Logging in...' : 'Login'}
      </button>
    </form>
  );
}

// Chat Component
export function ChatInterface() {
  const { messages, loading, sendMessage, clearConversation } = useChat();
  const [input, setInput] = useState('');

  async function handleSend(e: React.FormEvent) {
    e.preventDefault();

    if (!input.trim() || loading) return;

    const message = input.trim();
    setInput('');

    try {
      await sendMessage(message);
    } catch (err) {
      console.error('Failed to send message:', err);
    }
  }

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <h2>AI Chat</h2>
        <button onClick={clearConversation}>Clear</button>
      </div>

      <div className="chat-messages">
        {messages.map((msg, i) => (
          <div key={i} className={`message message-${msg.role}`}>
            <div className="message-role">{msg.role}</div>
            <div className="message-content">{msg.content}</div>
            {msg.cached && <span className="cached-badge">Cached</span>}
          </div>
        ))}

        {loading && (
          <div className="message message-assistant">
            <div className="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}
      </div>

      <form className="chat-input" onSubmit={handleSend}>
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="Type your message..."
          disabled={loading}
        />
        <button type="submit" disabled={loading || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}

// Dashboard with Health Check
export function Dashboard() {
  const { user, logout } = useAuth();
  const [health, setHealth] = useState<any>(null);

  useEffect(() => {
    loadHealth();
  }, []);

  async function loadHealth() {
    try {
      const data = await api.healthCheck();
      setHealth(data);
    } catch (err) {
      console.error('Health check failed:', err);
    }
  }

  return (
    <div className="dashboard">
      <header>
        <h1>Dashboard</h1>
        <div>
          Welcome, {user?.name}
          <button onClick={logout}>Logout</button>
        </div>
      </header>

      {health && (
        <div className={`health-status health-${health.status}`}>
          <h3>System Status: {health.status}</h3>
          <ul>
            <li>KV: {health.checks.kv.status} ({health.checks.kv.latency}ms)</li>
            <li>API Keys: {health.checks.apiKeys.status}</li>
            <li>Memory: {health.checks.memory.status}</li>
          </ul>
        </div>
      )}

      <ChatInterface />
    </div>
  );
}

// ============================================
// 4. Main App with Protected Routes
// ============================================

export function App() {
  const { user, loading } = useAuth();

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!user) {
    return <LoginForm />;
  }

  return <Dashboard />;
}
