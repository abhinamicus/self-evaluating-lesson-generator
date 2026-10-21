import sqlite3, json
from datetime import datetime,timezone

class Memory:
    def __init__(self,path):
        self.path=path
        with self._connect() as db:
            db.execute('CREATE TABLE IF NOT EXISTS runs (run_id TEXT PRIMARY KEY, topic TEXT, status TEXT, timestamp TEXT)')
            db.execute('CREATE TABLE IF NOT EXISTS attempts (run_id TEXT, attempt INTEGER, passed INTEGER, failures TEXT, PRIMARY KEY(run_id,attempt))')
    def _connect(self): return sqlite3.connect(self.path)
    def insights(self,topic):
        with self._connect() as db:
            rows=db.execute('SELECT failures FROM attempts JOIN runs USING(run_id) WHERE topic=? AND passed=0 ORDER BY timestamp DESC LIMIT 15',(topic,)).fetchall()
        reasons=[]
        for (raw,) in rows:
            for x in json.loads(raw):
                if x['id'] not in [r['id'] for r in reasons]: reasons.append(x)
        return '; '.join(f"{x['id']}: {x['reason']}" for x in reasons[:5]) or 'None'
    def start(self,run_id,topic):
        with self._connect() as db: db.execute('INSERT INTO runs VALUES(?,?,?,?)',(run_id,topic,'running',datetime.now(timezone.utc).isoformat()))
    def record(self,run_id,attempt,checks):
        failures=[c.as_dict() for c in checks if not c.passed]
        with self._connect() as db: db.execute('INSERT INTO attempts VALUES(?,?,?,?)',(run_id,attempt,int(not failures),json.dumps(failures)))
    def finish(self,run_id,status):
        with self._connect() as db: db.execute('UPDATE runs SET status=? WHERE run_id=?',(status,run_id))
