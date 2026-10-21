from uuid import uuid4
from .evaluator import EvaluationError

def run(topic,generator,evaluator,memory,max_retries=2):
    if max_retries not in (0,1,2): raise ValueError('max_retries must be 0, 1, or 2')
    run_id=str(uuid4()); memory.start(run_id,topic)
    feedback='None'; insights=memory.insights(topic); history=[]; lesson=''
    for attempt in range(1,max_retries+2):
        try:
            lesson=generator.generate(topic,feedback,insights,attempt)
            checks=evaluator.evaluate(lesson)
            if not checks: raise EvaluationError('Evaluator returned no checks')
        except Exception as exc:
            # Fail closed: API/JSON errors never approve content.
            from .schemas import Check
            checks=[Check('system_error',False,f'{type(exc).__name__}: {exc}')]
        failures=[c.as_dict() for c in checks if not c.passed]
        memory.record(run_id,attempt,checks)
        history.append({'attempt':attempt,'passed':not failures,'checks':[c.as_dict() for c in checks],'failures':failures})
        if not failures:
            memory.finish(run_id,'passed')
            return {'run_id':run_id,'topic':topic,'status':'passed','lesson':lesson,'history':history,'prior_insights':insights}
        feedback='; '.join(f"{x['id']}: {x['reason']}" for x in failures)
    memory.finish(run_id,'failed')
    return {'run_id':run_id,'topic':topic,'status':'failed','lesson':None,'history':history,'prior_insights':insights}
