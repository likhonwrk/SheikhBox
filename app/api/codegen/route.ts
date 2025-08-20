import { streamObject } from 'ai';
import { z } from 'zod';

export const codeBlockSchema = z.object({
  language: z.string(),
  filename: z.string(),
  code: z.string(),
});
// Allow streaming responses up to 30 seconds
export const maxDuration = 30;

export async function POST(req: Request) {
  const context = await req.json();

  const result = streamObject({
    model: 'openai/gpt-4o',
    schema: codeBlockSchema,
    prompt:
      `You are a helpful coding assitant. Only generate code, no markdown formatting or backticks, or text.` +
      context,
  });

  return result.toTextStreamResponse();
}
