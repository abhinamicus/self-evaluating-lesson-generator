# Introduction to RAG

Hello! Welcome to your very first lesson on **RAG**. If you have finished Class 12 and want to learn about Artificial Intelligence (AI) from scratch, you are in the right place. You do not need any prior knowledge. We will keep things simple, step by step, and easy to understand.

---

## What is RAG?

**RAG** stands for **Retrieval-Augmented Generation**. 

Let us break down these big words into simple plain English:
* **Retrieval:** Finding and fetching useful information from a collection of documents.
* **Generation:** Creating or writing an answer using AI.
* **Augmented:** Improved or added to.

Put it all together: **RAG** is a technique where an AI system looks up information from external documents first, and then uses that exact information to write a smart, correct answer.

---

## Why does it matter?

Normal AI models (like ChatGPT) only know what they learned during their training. 
* They can forget new facts.
* They do not know your personal notes, your company reports, or local Indian college textbooks unless they were in their training data.
* Sometimes, normal AI models **hallucinate**. This means they make up false facts and sound very confident while doing it.

RAG gives an AI relevant information to use when answering a question. This can reduce guessing and improve factual accuracy, especially when the retrieved documents are reliable and up to date. However, RAG cannot guarantee a correct answer.

---

## An everyday analogy

Imagine you are sitting inside an exam hall. 
* **A normal AI** is like a student who is not allowed to carry any books. They must write the answers purely from memory. If they forget something, they guess.
* **RAG** is like a student who is allowed to bring an open textbook into the exam. When a question is asked, the student first opens the book, finds the exact page, reads it, and then writes the correct answer. 

---

## How does it work?

Let us look at the step-by-step workflow of RAG. 

1. **Documents are split into chunks:** 
   * *Technical word:* **Document chunking** means taking a very long book or PDF and cutting it into small, manageable paragraphs or sentences (chunks).
2. **Chunks are indexed:** 
   * *Technical word:* **Indexing** means organizing these small pieces so the computer can search through them quickly, like an index at the back of a textbook.
   * *Technical word:* **Embeddings** are created during this process. An embedding is a way to turn words into numbers so a computer understands the meaning behind them.
   * *Technical word:* **Vector database** is a special digital storage folder designed to hold these numbers and quickly find similar meanings.
3. **Retrieving relevant chunks:** 
   * When you ask a question, the system searches the vector database and finds the specific chunks that match your question.
4. **Inserting text into the model prompt:** 
   * *Technical word:* **Prompt** is the message or instruction you give to the AI. The system takes your question *plus* the retrieved text chunks and feeds them together into the AI model.
5. **Generating a grounded answer:** 
   * *Technical word:* **Grounded answer** means an answer that is strictly based on the retrieved facts rather than wild guessing.

---

## Worked example

**Question:** What is the capital of France according to the travel guide?  
**Retrieved evidence:** "Chapter 3: Paris is the capital and most populous city of France."  
**Answer:** According to the travel guide, Paris is the capital of France.

---

## Limitations of RAG

Even though RAG is very powerful, it is important to know its limits:
* **Does not guarantee correctness:** RAG does not guarantee 100% true answers. If the retrieved documents contain irrelevant, outdated, or malicious information, the system can make mistakes. The AI model can also still hallucinate (make things up).
* **Not training:** RAG is completely different from training or fine-tuning an AI model. RAG just hands documents to the model as temporary reading material; it does not permanently change or teach the core AI model.

---

## Short recap

* **RAG** stands for Retrieval-Augmented Generation.
* It fetches facts from external documents and gives them to the AI as context before answering.
* It helps reduce guessing, but it does **not** guarantee 100% correct answers.
* It is not the same as training a model.

---

## Check your understanding

1. What does the acronym RAG stand for?  
   **Answer:** RAG stands for Retrieval-Augmented Generation.

2. Does RAG guarantee that the AI will always give a 100% correct answer?  
   **Answer:** No, RAG does not guarantee correctness. Errors can still happen if the retrieved documents are wrong or if the model hallucinates.

3. Is RAG the same thing as training or fine-tuning an AI model?  
   **Answer:** No, RAG is not the same as training or fine-tuning a model.