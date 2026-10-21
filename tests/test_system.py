from app.generator import MockGenerator
from app.evaluator import MockEvaluator,validate_checks,EvaluationError
from app.memory import Memory
from app.orchestrator import run
import pytest

def test_rejection_and_retry(tmp_path):
    result=run('Introduction to RAG',MockGenerator(),MockEvaluator(),Memory(tmp_path/'test.db'))
    assert result['status']=='passed'
    assert len(result['history'])==2
    assert not result['history'][0]['passed']
    assert result['history'][1]['passed']

def test_retry_limit(tmp_path):
    class AlwaysBad(MockGenerator):
        def generate(self,topic,feedback,insights,attempt): return super().generate(topic,feedback,insights,1)
    result=run('Introduction to RAG',AlwaysBad(),MockEvaluator(),Memory(tmp_path/'test.db'))
    assert result['status']=='failed' and result['lesson'] is None
    assert len(result['history'])==3

def test_memory_across_runs(tmp_path):
    mem=Memory(tmp_path/'test.db')
    run('Introduction to RAG',MockGenerator(),MockEvaluator(),mem)
    assert 'accuracy' in mem.insights('Introduction to RAG')

def test_invalid_judge_response():
    with pytest.raises(EvaluationError): validate_checks({'checks':[]})

def test_system_error_fails_closed(tmp_path):
    class Broken:
        def evaluate(self,lesson): raise RuntimeError('API unavailable')
    result=run('Introduction to RAG',MockGenerator(),Broken(),Memory(tmp_path/'test.db'),0)
    assert result['status']=='failed'

def test_judge_json_parser_accepts_fenced_json():
    from app.evaluator import _extract_json_object
    assert _extract_json_object('```json\n{"checks": []}\n```') == {"checks": []}


def test_live_evaluator_repairs_malformed_judge_once():
    from types import SimpleNamespace
    from app.evaluator import LiveEvaluator
    ids = ['accuracy','accessibility','example','jargon','coverage','flow','standalone','knowledge_check']
    valid = {'checks': [{'id': i, 'passed': True, 'reason': 'Specific evidence is present.'} for i in ids]}
    class Completions:
        def __init__(self): self.calls = 0
        def create(self, **kwargs):
            self.calls += 1
            content = 'not json' if self.calls == 1 else __import__('json').dumps(valid)
            return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content))])
    client = SimpleNamespace(chat=SimpleNamespace(completions=Completions()))
    evaluator = LiveEvaluator(client, 'test-model')
    checks = evaluator.evaluate('# Lesson\nQuestion: X?\nRetrieved: Y\nAnswer: Z\n\nCheck your understanding?\n1?\n2?')
    assert client.chat.completions.calls == 2
    assert len([c for c in checks if c.id in ids]) == 8


def test_structural_checks_require_explicit_worked_example_and_three_answered_questions():
    from app.evaluator import structural_checks
    lesson = """# Introduction to RAG
## Worked example
**Question:** When does the library close on Friday?
**Retrieved evidence:** The library closes at 5 PM on Friday.
**Answer:** It closes at 5 PM.
## Check your understanding
1. What does RAG stand for? Answer: Retrieval-Augmented Generation.
2. Does RAG guarantee truth? Answer: No.
3. What happens before an answer is written? Answer: Relevant evidence is retrieved.
"""
    results = {c.id: c.passed for c in structural_checks(lesson)}
    assert results['has_title'] is True
    assert results['has_worked_example'] is True
    assert results['has_questions'] is True


def test_structural_checks_reject_missing_retrieved_evidence_label():
    from app.evaluator import structural_checks
    lesson = """# Introduction to RAG
## Worked example
**Question:** When does the library close?
The timetable says 5 PM.
**Answer:** At 5 PM.
## Check your understanding
1. What is RAG? Answer: Retrieval-Augmented Generation.
2. Does it guarantee truth? Answer: No.
3. What happens first? Answer: Retrieval.
"""
    results = {c.id: c.passed for c in structural_checks(lesson)}
    assert results['has_worked_example'] is False
