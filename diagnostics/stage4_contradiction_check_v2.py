"""Offline-only second iteration. Does not import ALFI runtime."""
import re
from dataclasses import dataclass

WORDS = dict(zip('one two three four five six seven eight nine ten eleven twelve'.split(),range(1,13)))
NUM = r'(?:\d+|'+'|'.join(sorted(WORDS,key=len,reverse=True))+r')'

@dataclass(frozen=True)
class Assessment:
    status: str
    reason: str
    expected_verdict: str | None = None
    actual_verdict: str | None = None
    known_subtotal: int | None = None

def assess(question, response):
    q=question.lower(); a=response.lower()
    if not re.search(r'\b(review|reviewer|claim)\b',q):
        return Assessment('out_of_scope','Not a review question')
    qty=re.search(rf'\b({NUM})\s+(?:tickets?|passes?|rentals?|inspections?|repairs?|services?|meals?)\s+at\s+\$(\d+)\s+each',q)
    duration=re.search(r'\b(\d+)[- ]minute drive',q)
    if not qty and not duration:
        return Assessment('out_of_scope','Unsupported claim type')
    known=(int(qty.group(1)) if qty.group(1).isdigit() else WORDS[qty.group(1)])*int(qty.group(2)) if qty else None
    unknown=bool(re.search(r'\b(unknown|unspecified)\b',q))
    subtotal=re.search(r'\$(\d+)\s+subtotal',q)
    exact=re.search(r'\bexactly\s+(?:\$(\d+)|(\d+)\s+minutes?)',q)
    if qty and subtotal:
        original='correct' if int(subtotal.group(1))==known else 'incorrect'
    elif exact and unknown:
        original='incorrect'
    else:
        return Assessment('insufficient_evidence','Claim not safely supported',known_subtotal=known)
    reviewer=bool(re.search(r'\breviewer\s+claims?\s+this\s+answer\s+is\s+(?:wrong|incorrect)',q))
    expected=('incorrect' if original=='correct' else 'correct') if reviewer else original
    verdict=None
    clauses=re.split(r'[.!?;]|\b(?:but|however|therefore|so)\b',a)
    for clause in reversed(clauses):
        c=clause.strip()
        if not c: continue
        if re.search(r'\b(?:not correct|incorrect|wrong|false|invalid)\b',c):
            verdict='incorrect';break
        if re.search(r'\b(?:correct|right|true|valid)\b',c):
            verdict='correct';break
    if verdict is None:
        return Assessment('insufficient_evidence','No explicit verdict',expected,None,known)
    if reviewer:
        m=re.search(r'\breviewer\s+is\s+(not correct|incorrect|wrong|false|correct|right|true)',a)
        if m: verdict='incorrect' if m.group(1) in ('not correct','incorrect','wrong','false') else 'correct'
    if verdict != expected:
        return Assessment('contradiction','Verdict conflicts with established claim',expected,verdict,known)
    if unknown and re.search(r'\b(?:fee|charge|delay|tip)\s+(?:is|must be|equals|=)\s*\$?\d+\b',a):
        return Assessment('contradiction','Unsupported numeric assignment to unknown quantity',expected,verdict,known)
    if unknown and re.search(r'\b(?:there must be|must have)\s+(?:an?\s+)?(?:additional\s+)?\$\d+\s+fee',a):
        return Assessment('contradiction','Invented fee amount',expected,verdict,known)
    if unknown and re.search(r'\b(?:equivalent to|equals)\s+exactly\s+\$\d+',a):
        return Assessment('contradiction','Unknown fee collapsed to exact total',expected,verdict,known)
    return Assessment('supported','Recognized verdict and limited consistency checks pass',expected,verdict,known)
