import json
from app.config import settings
from app.schemas import MCQ

def generate_mcqs(topic, count, difficulty, passages):
    if settings.demo_mode:
        excerpt = " ".join(p["text"] for p in passages)[:350]
        items = []
        for _ in range(count):
            items.append(MCQ(
                question=f"Which statement is best supported by the retrieved curriculum about {topic}?",
                options=[
                    "The retrieved passage discusses this topic.",
                    "The passage says the topic has no connection to the subject.",
                    "The passage says all examples are incorrect.",
                    "The passage says evidence cannot be collected."
                ],
                answer="The retrieved passage discusses this topic.",
                explanation="Demo-mode template only; live mode uses the language model.",
                source_excerpt=excerpt or "No source excerpt available."
            ))
        return items, "demo"
    if not settings.openai_api_key:
        raise RuntimeError("Set OPENAI_API_KEY or enable DEMO_MODE")
    from openai import OpenAI
    context = "\\n\\n".join(f"[{p['source']}] {p['text']}" for p in passages)
    prompt = f"""Create {count} {difficulty} MCQs about {topic}, using ONLY this context.
Return JSON: {{"questions":[{{"question":"...","options":["...","...","...","..."],"answer":"exact option text","explanation":"...","source_excerpt":"verbatim supporting text"}}]}}.
Four distinct options per question, exactly one correct answer. Do not invent facts.
CONTEXT:
{context}"""
    client = OpenAI(api_key=settings.openai_api_key)
    response = client.chat.completions.create(model=settings.openai_model, temperature=0.2,
        response_format={"type": "json_object"},
        messages=[{"role": "system", "content": "Return only valid JSON grounded in the given context."},
                  {"role": "user", "content": prompt}])
    payload = json.loads(response.choices[0].message.content or "{}")
    questions = [MCQ.model_validate(q) for q in payload.get("questions", [])]
    if len(questions) != count:
        raise ValueError(f"Expected {count} questions, received {len(questions)}")
    return questions, "openai"
