"""Offline-only narrow claim/verdict contradiction diagnostic. No ALFI imports or writes."""
import re
from dataclasses import dataclass, asdict

WORDS = {'one':1,'two':2,'three':3,'four':4,'five':5,'six':6,'seven':7,'eight':8,'nine':9,'ten':10}
NUM = r'(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten)'

@dataclass(frozen=True)
class Assessment:
    status: str
    reason: str
    expected_verdict: str | None = None
    actual_verdict: str | None = None
    known_subtotal: int | None = None

def _number(s):
    return int(s) if s.isdigit() else WORDS[s.lower()]

def _verdict(response):
    matches = list(re.finditer(r'\b(?:incorrect|not correct|wrong|false|correct|right|true)\b', response, re.I))
    if not matches:
        return None
    last = matches[-1].group().lower()
    return 'incorrect' if last in ('incorrect','not correct','wrong','false') else 'correct'

def assess(question: str, response: str) -> Assessment:
    """Conservative narrow diagnostic, not a general reasoning/verdict oracle."""
    q = question.lower()
    if not any(k in q for k in ('review', 'claim', 'reviewer')):
        return Assessment('out_of_scope', 'Not a review prompt')
    reviewer = bool(re.search(r'\breviewer\b.{0,35}\b(?:wrong|incorrect)\b', q))
    qty = re.search(rf'\b({NUM})\s+(?:tickets?|passes?|rentals?|inspections?|repairs?|services?)\s+at\s+\$(\d+)\s+each', q)
    duration = re.search(r'\b(\d+)[- ]minute drive\b', q)
    if not qty and not duration:
        return Assessment('out_of_scope', 'Unrecognized quantitative review pattern')
    known = _number(qty.group(1))*int(qty.group(2)) if qty else None
    unknown = bool(re.search(r'\b(?:unknown|unspecified)\b', q))
    if not unknown:
        return Assessment('insufficient_evidence', 'No recognized unknown-value qualifier', known_subtotal=known)
    if qty:
        subtotal_claim = re.search(r'\$(\d+)\s+subtotal', q)
        exact_claim = bool(re.search(r'\bexactly\s+\$\d+\b', q))
        if subtotal_claim:
            expected_original = 'correct' if int(subtotal_claim.group(1)) == known else 'incorrect'
        elif exact_claim:
            expected_original = 'incorrect'
        else:
            return Assessment('insufficient_evidence', 'No supported claim target', known_subtotal=known)
    else:
        if not re.search(r'\bexactly\s+\d+\s+minutes?\b', q):
            return Assessment('insufficient_evidence', 'No exact-duration assertion')
        expected_original = 'incorrect'
    expected = ('incorrect' if expected_original == 'correct' else 'correct') if reviewer else expected_original
    actual = _verdict(response)
    if actual is None:
        return Assessment('insufficient_evidence', 'No explicit verdict detected', expected, None, known)
    if actual != expected:
        return Assessment('contradiction', 'Final verdict conflicts with recognized claim evidence', expected, actual, known)
    if qty and re.search(r'\b(?:equivalent to|equal to|equals)\s+\$'+str(known)+r'\b', response, re.I) and re.search(r'unknown|unspecified', response, re.I) and re.search(r'\b(?:fee|charge)\b', response, re.I):
        return Assessment('contradiction', 'Unknown fee described as equal to zero contribution', expected, actual, known)
    return Assessment('supported', 'Explicit verdict agrees with recognized claim evidence; other reasoning not verified', expected, actual, known)

if __name__ == '__main__':
    import argparse, json
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--question',required=True)
    parser.add_argument('--response',required=True)
    args=parser.parse_args()
    print(json.dumps(asdict(assess(args.question,args.response)),indent=2))
