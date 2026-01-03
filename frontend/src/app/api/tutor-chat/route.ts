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
    - Keep responses conversational and adaptive
    - Prefer short explanations first, then expand if needed
    - Ask questions only when they genuinely help
    - Teach through examples when useful, not by default
    - Avoid lecturing or overexplaining
    - Match the student's level and tone
    - Sound human, not academic

    If the student wants the answer directly, give it.
    If they seem confused, guide them step by step.
    If the question is simple, keep the response simple.

    Use markdown for clarity when helpful, but don't overformat.
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