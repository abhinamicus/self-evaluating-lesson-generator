from .prompts import GENERATOR, REFERENCE

GOOD = """# Introduction to RAG

## What is RAG?
RAG means Retrieval-Augmented Generation. It helps an AI assistant look up useful information before answering. Think of an open-book exam: you first find the right page, then write an answer using it.

## Why does it matter?
An AI assistant may not know your school's latest timetable. RAG lets it read an updated timetable instead of guessing. It can still make mistakes, so check important answers.

## How does it work?
1. **Collect:** Save trusted documents, such as a school timetable.
2. **Prepare:** Split long documents into small pieces called chunks.
3. **Index:** Organize chunks for searching. Some systems use embeddings (number patterns representing meaning) in a vector database (a searchable store of those patterns).
4. **Retrieve:** When someone asks a question, find the most relevant pieces.
5. **Generate:** Give those pieces and the question to a language model (AI that writes text). Ask it to answer using the evidence.
6. **Verify:** Check the answer against the source, and show where it came from.

## Worked example
**Question:** What time does the library close on Friday?
**Retrieved evidence:** 'Friday library hours: 9 AM to 5 PM.'
**Answer:** The library closes at 5 PM on Friday, according to the timetable.

## Important limits
RAG does not train the language model on the documents. It supplies information at answer time. If the documents are wrong, old, or unrelated, the answer can still be wrong. It does not guarantee correct answers.

## Quick recap
RAG means: find useful information first, then write an answer using it. It is helpful when answers depend on documents or new information.

## Check your understanding
1. **What does RAG stand for?** Answer: Retrieval-Augmented Generation.
2. **Does RAG guarantee truth?** Answer: No. The documents and answer can be wrong.
3. **What happens before the AI writes an answer?** Answer: The system retrieves relevant information.
"""
BAD = GOOD.replace('It can still make mistakes, so check important answers.', 'RAG guarantees correct answers every time.').replace('It does not guarantee correct answers.', 'It always guarantees correct answers.')

class MockGenerator:
    def generate(self, topic, feedback, insights, attempt):
        return BAD if attempt == 1 else GOOD

class LiveGenerator:
    def __init__(self, client, model): self.client, self.model = client, model
    def generate(self, topic, feedback, insights, attempt):
        r=self.client.chat.completions.create(model=self.model,temperature=0.3,messages=[{'role':'user','content':GENERATOR.format(topic=topic,reference=REFERENCE,insights=insights,feedback=feedback)}])
        return r.choices[0].message.content or ''
