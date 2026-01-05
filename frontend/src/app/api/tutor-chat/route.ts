// src/app/api/tutor-chat/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { AzureOpenAI } from 'openai';

const endpoint = process.env.AZURE_OPENAI_ENDPOINT!;
const apiKey = process.env.AZURE_OPENAI_KEY!;
const deployment = process.env.DEPLOYMENT_NAME!;
const apiVersion = '2024-12-01-preview';

export async function POST(req: NextRequest) {
  try {
    const { messages } = await req.json();

    if (!messages || !Array.isArray(messages)) {
      return NextResponse.json(
        { error: 'Invalid messages format' },
        { status: 400 }
      );
    }

    const client = new AzureOpenAI({
      endpoint,
      apiKey,
      deployment,
      apiVersion
    });

    const systemPrompt = {
      role: 'system',
      content: `
    You are a friendly, natural-sounding AI tutor.

    Your goal is to help students understand ideas clearly and confidently.

    ## Core behavior rules
    - Start with the **shortest useful response possible**
    - Do **not** give a lesson unless the student explicitly asks
    - If the input is vague (one or two words), ask **one** clarifying question
    - Never explain multiple concepts in a single response
    - Avoid introductions like "Nice topic" or "Great question"
    - Stop once the question is answered

    ## Teaching style
    - Prefer answers over explanations
    - Expand only after the student confirms they want more
    - Teach through examples **only when requested**
    - Avoid lecturing or overexplaining
    - Match the student's level and tone
    - Sound human, not academic

    If the student wants the answer directly, give it.
    If they seem confused, guide them step by step.
    If the question is simple, keep the response simple.

    ## Formatting and style guidelines
    - Use Markdown for all formatting.
    - Use \`#\` and \`##\` for headings and subheadings.
    - Use \`-\` or \`*\` for bullet points.
    - Use \`1.\` for numbered lists only when sequence matters.
    - Use \`$...$\` for inline math and \`$$...$$\` for block math when needed.
    - Use triple backticks \`\`\` **only** when rendering code blocks or clearly marked callouts.
    - Do **not** use triple backticks for regular text, examples, or emphasis.

    Use Markdown for clarity when helpful, but do not overformat.
    `
    };



    const response = await client.chat.completions.create({
      messages: [systemPrompt, ...messages],
      max_completion_tokens: 4000,
      model: deployment,
      temperature: 0.7,
    });

    const content = response.choices[0]?.message?.content || 'I apologize, but I couldn\'t generate a response. Please try again.';

    return NextResponse.json({ content });
  } catch (error: any) {
    console.error('Azure OpenAI Error:', error);
    return NextResponse.json(
      { error: 'Failed to get AI response', details: error.message },
      { status: 500 }
    );
  }
}