import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { YoutubeTranscript } from 'youtube-transcript/dist/youtube-transcript.esm.js';
import { z } from 'zod';

// ── 1. Create the server ──────────────────────────────────────────────────────

const server = new McpServer({
  name: 'youtube',
  version: '1.0.0',
});

// ── 2. Define the tool ────────────────────────────────────────────────────────

server.tool(
  'summarize_youtube',
  'Fetch the transcript of a YouTube video and return it for summarization.',
  {
    url:   z.string().describe('YouTube video URL'),
    focus: z.string().optional().describe('Optional topic to focus on, e.g. "the part about RAG"'),
  },
  async ({ url, focus }) => {
    const videoId = extractVideoId(url);
    if (!videoId) {
      return { content: [{ type: 'text', text: `Could not extract video ID from URL: ${url}` }] };
    }

    let segments;
    try {
      segments = await YoutubeTranscript.fetchTranscript(videoId);
    } catch (err) {
      return { content: [{ type: 'text', text: `Failed to fetch transcript: ${err.message}` }] };
    }

    const transcript = segments.map(s => s.text).join(' ');

    const focusLine = focus ? `Focus on: ${focus}\n\n` : '';
    const output = `${focusLine}Transcript (${segments.length} segments):\n\n${transcript}`;

    return { content: [{ type: 'text', text: output }] };
  },
);

// ── 3. Start listening on stdio ───────────────────────────────────────────────

const transport = new StdioServerTransport();
await server.connect(transport);

// ── Helpers ───────────────────────────────────────────────────────────────────

function extractVideoId(url) {
  const match = url.match(/(?:v=|youtu\.be\/)([a-zA-Z0-9_-]{11})/);
  return match ? match[1] : null;
}
