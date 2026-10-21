import argparse, json, os
from pathlib import Path
from app.generator import MockGenerator,LiveGenerator
from app.evaluator import MockEvaluator,LiveEvaluator
from app.memory import Memory
from app.orchestrator import run

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--mode',choices=['mock','live'],default='mock')
    parser.add_argument('--topic',default='Introduction to RAG')
    parser.add_argument('--db',default='lesson_memory.db')
    parser.add_argument('--max-retries',type=int,choices=[0,1,2],default=2)
    args=parser.parse_args()
    if args.mode=='live':
        from dotenv import load_dotenv
        from openai import OpenAI
        load_dotenv()
        provider=os.getenv('LLM_PROVIDER','gemini').strip().lower()
        if provider=='gemini':
            api_key=os.getenv('GEMINI_API_KEY')
            if not api_key: parser.error('Set GEMINI_API_KEY in .env, or set LLM_PROVIDER=openai and configure OPENAI_API_KEY')
            # Gemini's documented OpenAI-compatible endpoint lets us reuse the same
            # generator/evaluator adapters without adding another SDK dependency.
            client=OpenAI(api_key=api_key,base_url='https://generativelanguage.googleapis.com/v1beta/openai/')
            model=os.getenv('GEMINI_MODEL','gemini-3.8-flash')
        elif provider=='openai':
            api_key=os.getenv('OPENAI_API_KEY')
            if not api_key: parser.error('Set OPENAI_API_KEY in .env when LLM_PROVIDER=openai')
            client=OpenAI(api_key=api_key)
            model=os.getenv('OPENAI_MODEL','gpt-4o-mini')
        else:
            parser.error('LLM_PROVIDER must be gemini or openai')
        generator,evaluator=LiveGenerator(client,model),LiveEvaluator(client,model)
    else: generator,evaluator=MockGenerator(),MockEvaluator()
    result=run(args.topic,generator,evaluator,Memory(args.db),args.max_retries)
    out=Path('outputs');out.mkdir(exist_ok=True)
    (out/'last_run.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
    if result['lesson'] is not None: (out/'final_lesson.md').write_text(result['lesson'],encoding='utf-8')
    else: (out/'final_lesson.md').unlink(missing_ok=True)
    print(f"Status: {result['status']} | attempts: {len(result['history'])}")
    for item in result['history']:
        print(f"Attempt {item['attempt']}: {'PASS' if item['passed'] else 'FAIL'}")
        for f in item['failures']: print(f"  - {f['id']}: {f['reason']}")
    print('Artifacts: outputs/last_run.json; outputs/final_lesson.md (only on pass)')
    if result['status']!='passed': raise SystemExit(1)

if __name__=='__main__': main()
