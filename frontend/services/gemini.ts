
import { GoogleGenAI } from "@google/genai";
import { SYSTEM_INSTRUCTION } from "../constants";

export const querySiliconPulse = async (query: string, liveContext: string) => {
  const apiKey = import.meta.env.VITE_GEMINI_API_KEY || "";
  
  if (!apiKey) {
    throw new Error("VITE_GEMINI_API_KEY not configured. Please set it in .env.local");
  }

  const ai = new GoogleGenAI({ apiKey });
  
  const prompt = `${SYSTEM_INSTRUCTION}

### LIVE UPDATES CONTEXT (streaming feed)
${liveContext}

### USER QUERY
${query}
  `;

  try {
    const response = await ai.models.generateContent({
      model: 'gemini-2.0-flash',
      contents: [{ 
        role: 'user', 
        parts: [{ text: prompt }] 
      }],
      generationConfig: {
        temperature: 0.2,
        maxOutputTokens: 4096,
      }
    } as any);

    return (response.text as string) || "No response generated";
  } catch (error: any) {
    console.error("Gemini API Error:", error);
    throw new Error(error?.message || "Failed to generate intelligence report. Check API key configuration.");
  }
};
