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
      content: `You are a helpful, patient, and encouraging AI tutor. Your goal is to:
- Help students understand concepts deeply, not just give answers
- Ask guiding questions to promote critical thinking
- Provide clear explanations with examples
- Encourage students and build their confidence
- Break down complex topics into manageable pieces
- Use analogies and real-world examples when helpful
- Be concise but thorough in your explanations
- Format your responses with markdown for better readability

When a student asks a question:
1. First, make sure you understand what they're asking
2. Guide them toward the answer rather than giving it directly (unless they explicitly ask for the solution)
3. Explain the underlying concepts
4. Check their understanding with follow-up questions`
    };

    const response = await client.chat.completions.create({
      messages: [systemPrompt, ...messages],
      max_completion_tokens: 2000,
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