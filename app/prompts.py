REFERENCE = """RAG stands for Retrieval-Augmented Generation. It retrieves relevant information from an external collection of documents and gives it to a language model as context before the model writes an answer. Typical stages: documents are split into chunks; chunks are indexed, often with embeddings in a vector database; a user's question is used to retrieve relevant chunks; retrieved text is inserted into the model prompt; the model generates a grounded answer. Retrieval does not guarantee truth: irrelevant, outdated, or malicious documents can cause errors, and the model may still hallucinate. RAG is not the same as training or fine-tuning a model. Cite sources when available."""
GENERATOR = """You are an expert teacher for an Indian class-12 graduate with limited English and zero AI background. Write a standalone Markdown lesson on {topic}. Explain what it is, why it matters, and how it works in plain English. Define every technical word when first used. Use short sentences and a supportive teaching flow.

MANDATORY CONTENT — include every item below, using the exact headings and labels where shown:
1. A Markdown title beginning with #.
2. Sections titled 'What is RAG?', 'Why does it matter?', and 'How does it work?'.
3. An everyday analogy.
4. A step-by-step workflow, with each technical term explained in plain English.
5. A section titled '## Worked example' containing these three separate lines with concrete content: '**Question:** ...?', '**Retrieved evidence:** ...', and '**Answer:** ...'. The answer must follow from the retrieved evidence.
6. A section explaining limitations, including that RAG does not guarantee correctness and does not train the model by itself.
7. A short recap.
8. A section titled '## Check your understanding' with at least 3 numbered questions. Every question must end with a question mark and have its answer immediately after it, clearly marked 'Answer:'.

Before returning, check that all 8 items are present. Do not claim that RAG guarantees correct answers. Ground factual claims in this reference:
{reference}
Prior recurring lessons learned: {insights}
Feedback to fix from last attempt: {feedback}
Return only the Markdown lesson."""
JUDGE = """You are an independent quality reviewer. Evaluate the candidate lesson for an Indian class-12 graduate with limited English and zero AI background. Use the reference as the factual baseline. Return ONLY one valid JSON object, no Markdown fences or surrounding text. It must contain a 'checks' array of exactly 8 objects. Every object must have exactly these fields: 'id' (string), 'passed' (JSON boolean true/false), and 'reason' (non-empty string citing specific evidence from the lesson). Use each ID exactly once: accuracy, accessibility, example, jargon, coverage, flow, standalone, knowledge_check. Do not add or omit IDs. Be strict: mark false if unclear or unsupported. Accuracy fails for any material false claim including 'RAG guarantees correct answers' or 'RAG trains the model on documents'. Coverage requires what, why, and how; example requires concrete query, retrieved context, answer; knowledge_check requires questions and answers. No partial credit. Do not mark everything true by default.
REFERENCE:
{reference}
LESSON:
{lesson}"""
