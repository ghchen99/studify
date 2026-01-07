import { NextRequest, NextResponse } from 'next/server';
import { AzureOpenAI } from 'openai';

const endpoint = process.env.AZURE_OPENAI_ENDPOINT!;
const apiKey = process.env.AZURE_OPENAI_KEY!;
const deployment = process.env.DEPLOYMENT_NAME!;
const apiVersion = '2024-12-01-preview';

export async function POST(req: NextRequest) {
  try {
    const { messages } = await req.json();

    if (!Array.isArray(messages)) {
      return NextResponse.json({ error: 'Invalid messages' }, { status: 400 });
    }

    const client = new AzureOpenAI({
      endpoint,
      apiKey,
      apiVersion
    });

    const systemPrompt = {
      role: 'system',
      content:
        'You are a friendly AI tutor. Keep responses short, clear, and helpful. ' +
        '- Be an engaging and supportive tutor at the same time, dont be overly verbose.\n\n' +
        'Formatting and style guidelines:\n' +
        '- Use Markdown for all formatting.\n' +
        '- Use `#` and `##` for headings and subheadings.\n' +
        '- Use `-` or `*` for bullet points.\n' +
        '- Use `1.` for numbered lists only when sequence matters.\n' +
        '- Use `$...$` for inline math and `$$...$$` for block math when needed.\n\n' +
        '- Use triple backticks ``` **only** when rendering code blocks or clearly marked callouts.\n' +
        '- Do **not** use triple backticks for regular text, examples, or emphasis.\n\n' +
        'Ensure the lesson is engaging, clearly written, and ready to render in a Markdown/KaTeX environment.'
    };

    const formattedMessages = messages.map((msg: any) => {
      if (msg.image) {
        return {
          role: msg.role,
          content: [
            { type: 'text', text: msg.content },
            {
              type: 'image_url',
              image_url: { url: msg.image }
            }
          ]
        };
      }

      return {
        role: msg.role,
        content: msg.content
      };
    });

    const response = await client.chat.completions.create({
      model: deployment,
      messages: [systemPrompt, ...formattedMessages],
      temperature: 0.7,
      max_completion_tokens: 4000
    });

    const content =
      response.choices[0]?.message?.content ??
      'I could not generate a response.';

    return NextResponse.json({ content });
  } catch (error: any) {
    console.error('Tutor Chat Error:', error);
    return NextResponse.json(
      { error: 'Failed to generate response' },
      { status: 500 }
    );
  }
}
