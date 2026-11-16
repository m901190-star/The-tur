/**
 * The sliver of the claude.ai artifact runtime this app uses.
 *
 * When the web build is published as an artifact, the page is framed by a
 * viewer that exposes `window.claude.use(name)`. It is absent everywhere else
 * — the native app, a plain browser, a saved copy — so every call site has to
 * treat it as optional rather than feature-detect once.
 */

export interface McpError {
  code: string;
  message: string;
  server?: string;
  retryable?: boolean;
}

export interface McpNamespace {
  callTool(
    server: string,
    tool: string,
    input?: unknown,
    options?: { signal?: AbortSignal },
  ): Promise<{ payload?: unknown }>;
}

interface ClaudeRuntime {
  use(name: 'mcp'): Promise<McpNamespace | null>;
}

declare global {
  interface Window {
    claude?: ClaudeRuntime;
  }
}

/**
 * Resolves the runtime's MCP namespace, or null when this page is not inside
 * a viewer that serves it. Never throws: absence is the normal case.
 */
export async function useMcp(): Promise<McpNamespace | null> {
  try {
    const runtime = typeof window !== 'undefined' ? window.claude : undefined;
    if (!runtime?.use) return null;
    return await runtime.use('mcp');
  } catch {
    return null;
  }
}

export function errorCodeOf(error: unknown): string {
  if (error && typeof error === 'object' && 'code' in error) {
    const { code } = error as McpError;
    if (typeof code === 'string') return code;
  }
  return 'upstream_error';
}
