import json, re
from .schemas import CHECK_IDS, Check
from .prompts import JUDGE, REFERENCE

class EvaluationError(Exception): pass

def structural_checks(lesson):
    """Deterministic hard gates for required lesson structure and explicit examples."""
    has_question_label = bool(re.search(r'\*\*Question:\*\*|^Question:', lesson, re.I | re.M))
    has_retrieved_label = bool(re.search(r'\*\*Retrieved (?:evidence|timetable text|information):\*\*|^Retrieved (?:evidence|information|timetable text):', lesson, re.I | re.M))
    has_answer_label = bool(re.search(r'\*\*Answer:\*\*|^Answer:', lesson, re.I | re.M))
    question_marks = len(re.findall(r'\?', lesson))
    # Count numbered Q&A entries; require explicit answers to reduce false positives.
    numbered_questions = re.findall(r'^\s*\d+[.)]\s+.*\?', lesson, re.M)
    explicit_answers = len(re.findall(r'\bAnswer:\s*\S', lesson, re.I))
    has_qa_section = bool(re.search(r'check your understanding|knowledge check', lesson, re.I))
    return [
        Check('has_title', bool(re.search(r'^# .+', lesson, re.M)), 'Markdown title required'),
        Check('has_worked_example', has_question_label and has_retrieved_label and has_answer_label,
              'Worked example must label Question, Retrieved evidence, and Answer explicitly'),
        Check('has_questions', has_qa_section and len(numbered_questions) >= 3 and question_marks >= 3 and explicit_answers >= 3,
              'Knowledge check must contain at least 3 numbered questions ending in ? and 3 explicit answers'),
    ]

def validate_checks(data):
    if not isinstance(data,dict) or not isinstance(data.get('checks'),list): raise EvaluationError('Malformed judge JSON')
    checks=data['checks']
    if len(checks)!=len(CHECK_IDS) or {c.get('id') for c in checks if isinstance(c,dict)}!=set(CHECK_IDS): raise EvaluationError('Incorrect rubric IDs')
    if any(type(c.get('passed')) is not bool or not isinstance(c.get('reason'),str) or not c['reason'].strip() for c in checks): raise EvaluationError('Invalid rubric fields')
    return [Check(c['id'],c['passed'],c['reason']) for c in checks]

class MockEvaluator:
    def evaluate(self,lesson):
        errors=[]
        if re.search(r'RAG guarantees correct answers|always guarantees correct answers',lesson,re.I): errors.append('False claim: RAG guarantees correct answers')
        if re.search(r'RAG (trains|fine.tunes) the (AI |language )?model',lesson,re.I): errors.append('False claim: RAG trains the model')
        return [Check(i,not errors if i=='accuracy' else True,'; '.join(errors) if i=='accuracy' and errors else 'Fixture-based mock check; not semantic validation') for i in CHECK_IDS]+structural_checks(lesson)

def _extract_json_object(raw):
    """Parse a judge response, tolerating Markdown fences or brief surrounding text."""
    if not isinstance(raw, str) or not raw.strip():
        raise EvaluationError('Judge returned an empty response')
    candidate = raw.strip()
    candidate = re.sub(r'^```(?:json)?\s*', '', candidate, flags=re.I)
    candidate = re.sub(r'\s*```$', '', candidate)
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        # Some compatible endpoints ignore JSON mode. Recover the first JSON object
        # without accepting arbitrary prose as a valid evaluation.
        start, end = candidate.find('{'), candidate.rfind('}')
        if start >= 0 and end > start:
            try:
                return json.loads(candidate[start:end + 1])
            except json.JSONDecodeError as exc:
                raise EvaluationError(f'Judge response was not valid JSON: {exc.msg}') from exc
        raise EvaluationError('Judge response did not contain a JSON object')

class LiveEvaluator:
    def __init__(self,client,model): self.client,self.model=client,model

    def _judge_call(self, content):
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            response_format={'type':'json_object'},
            messages=[{'role':'user','content':content}],
        )
        return response.choices[0].message.content or ''

    def evaluate(self,lesson):
        prompt = JUDGE.format(reference=REFERENCE, lesson=lesson)
        last_error = None
        for attempt in range(2):
            raw = self._judge_call(prompt)
            try:
                checks = validate_checks(_extract_json_object(raw))
                return checks + structural_checks(lesson)
            except (EvaluationError, ValueError, TypeError, KeyError) as exc:
                last_error = exc
                if attempt == 0:
                    prompt = (
                        'Your previous response did not match the required JSON schema. '
                        'Return ONLY one JSON object with exactly this shape: '
                        '{"checks":[{"id":"accuracy","passed":true,"reason":"specific evidence"}, '
                        '{"id":"accessibility","passed":true,"reason":"specific evidence"}, '
                        '{"id":"example","passed":true,"reason":"specific evidence"}, '
                        '{"id":"jargon","passed":true,"reason":"specific evidence"}, '
                        '{"id":"coverage","passed":true,"reason":"specific evidence"}, '
                        '{"id":"flow","passed":true,"reason":"specific evidence"}, '
                        '{"id":"standalone","passed":true,"reason":"specific evidence"}, '
                        '{"id":"knowledge_check","passed":true,"reason":"specific evidence"}]}. '
                        'Every passed value must be a JSON boolean, not a string. Evaluate honestly; '
                        'do not default checks to true.\n\n' + JUDGE.format(reference=REFERENCE, lesson=lesson)
                    )
        raise EvaluationError(f'Judge JSON remained invalid after one repair attempt: {last_error}') from last_error
