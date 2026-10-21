from dataclasses import dataclass, asdict
CHECK_IDS = ('accuracy','accessibility','example','jargon','coverage','flow','standalone','knowledge_check')
@dataclass
class Check:
    id: str
    passed: bool
    reason: str
    def as_dict(self): return asdict(self)
