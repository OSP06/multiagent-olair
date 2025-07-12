import os

try:
    from openai import OpenAI
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    USE_OPENAI = True
except ImportError:
    USE_OPENAI = False

def summarize_lease(text: str) -> str:
    """
    Summarize the lease using an LLM or return dummy summary if offline.
    """
    if not text.strip():
        return "❌ No lease text provided."

    if USE_OPENAI:
        try:
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",  # or "gpt-4" if available
                messages=[
                    {"role": "system", "content": "You are a legal assistant summarizing commercial lease agreements."},
                    {"role": "user", "content": f"Summarize this lease in bullet points:\n{text}"}
                ],
                temperature=0.3,
                max_tokens=300
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"⚠️ LLM summarization failed: {str(e)}"

    # Dummy fallback
    return (
        "📄 **Dummy Lease Summary**:\n"
        "- Monthly rent due on the 1st with a grace period\n"
        "- Security deposit required before move-in\n"
        "- 30-day termination notice allowed by either party\n"
        "- Tenant pays for utilities\n"
        "- Pets not allowed without permission"
    )
