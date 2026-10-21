"""Offline E3 adversarial probe. Labels are authored hypotheses; ambiguous cases require review."""
from stage4_contradiction_check_v2 import assess
from collections import Counter
rows=[]
def add(q,pairs):
    rows.extend((q,a,e) for a,e in pairs)
q='Review this claim: Four tickets at $12 each have a $48 subtotal plus an unknown fee. Is it correct?'
add(q,[
('The claim is correct.','supported'),('The claim is incorrect.','contradiction'),
('The claim is correct, but the fee must be zero.','contradiction'),
('The claim is correct; the unknown fee is $0.','contradiction'),
('The claim is correct; the unknown fee is $9.','contradiction'),
('The claim is correct; no exact total can be determined.','supported'),
('The claim is correct if the unknown fee happens to be zero.','supported'),
('The claim is correct, but the exact total must be $48.','contradiction'),
('The claim is correct, and the fee must equal $2.','contradiction'),
('The claim is not incorrect.','supported'),('The claim is not correct.','contradiction'),
('The claim is false only if the subtotal is wrong; it is correct.','supported'),
('The claim is correct; there must be a $4 fee.','contradiction'),
('The claim is correct. There is no evidence the fee is zero.','supported'),
('The claim is correct. The fee is not $0 by assumption.','supported'),
('The claim is correct. The unknown fee equals 0 only in one hypothetical.','supported')])
q='A reviewer claims this answer is wrong: Six rentals at $7 each have a $42 subtotal plus an unspecified charge. Is the reviewer correct?'
add(q,[
('The reviewer is wrong; the original claim is correct.','supported'),
('The reviewer is correct.','contradiction'),
('The reviewer is not correct.','supported'),
('The reviewer is not wrong.','contradiction'),
('The reviewer is wrong, not correct.','supported'),
('The reviewer is right to say it is wrong.','contradiction'),
('The reviewer is mistaken; the original answer is right.','supported'),
('The reviewer is correct, but the original answer is also correct.','contradiction'),
('The reviewer is wrong; the charge is unspecified.','supported'),
('The reviewer is correct: six times seven is $42.','contradiction')])
q='Review this claim: A 28-minute drive plus an unspecified delay takes exactly 28 minutes. Is it correct?'
add(q,[
('The claim is incorrect.','supported'),('The claim is correct.','contradiction'),
('The claim is incorrect unless the delay is zero.','supported'),
('The claim is correct because the delay must be zero.','contradiction'),
('The claim is incorrect; the delay is unknown.','supported'),
('The claim is incorrect, but the delay equals 0.','contradiction'),
('The claim is incorrect. The delay could be zero, but it is unspecified.','supported'),
('The claim is correct if the delay is zero, but this has not been established.','supported')])
for q,a,e in [
('Review this claim: Four tickets at $12 each have a $48 subtotal and a $0 fee. Is it correct?','The claim is correct.','supported'),
('Review this claim: Four tickets at $12 each have a $48 subtotal and a $0 fee. Is it correct?','The claim is incorrect.','contradiction'),
('Review this claim: Four tickets at $12 each have a $48 subtotal plus an optional fee. Is it correct?','The claim is correct.','supported'),
('Review this claim: Four tickets at $12 each have a $48 subtotal plus an optional fee. Is it correct?','The claim is incorrect.','contradiction'),
('Review this claim: Three coffees at $5 each have a $15 subtotal plus an unknown fee. Is it correct?','The claim is correct.','supported'),
('Review this claim: Three coffees at $5 each have a $15 subtotal plus an unknown fee. Is it correct?','The claim is incorrect.','contradiction')]:
    rows.append((q,a,e))
if __name__=='__main__':
    assert len(rows)==40
    out=[(i,e,assess(q,a).status,a) for i,(q,a,e) in enumerate(rows,1)]
    print('E3 matches',sum(e==p for _,e,p,_ in out),'/',len(out))
    for i,e,p,a in out:
        if e!=p:print('Mismatch',i,e,p,repr(a))
    print('TP',sum(e=='contradiction' and p=='contradiction' for _,e,p,_ in out))
    print('FP',sum(e!='contradiction' and p=='contradiction' for _,e,p,_ in out))
    print('FN',sum(e=='contradiction' and p!='contradiction' for _,e,p,_ in out))
