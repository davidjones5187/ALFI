from stage4_contradiction_check_v2 import assess
import json
from collections import Counter

# Independent, manually labeled challenge set; no modifications to classifier.
CASES = [
("H01","Review this claim: Seven tickets at $8 each have a $56 subtotal plus an unspecified fee. Is it correct?","The claim is correct: $56 is the subtotal and the fee is unknown.","supported"),
("H02","Review this claim: Seven tickets at $8 each have a $56 subtotal plus an unspecified fee. Is it correct?","The claim is incorrect. Seven times eight is $56.","contradiction"),
("H03","Review this claim: Two rentals at $23 each have a $45 subtotal plus an unknown charge. Is it correct?","Incorrect. The subtotal is $46.","supported"),
("H04","Review this claim: Two rentals at $23 each have a $45 subtotal plus an unknown charge. Is it correct?","Correct, the subtotal is $45.","contradiction"),
("H05","A reviewer claims this answer is wrong: Five passes at $13 each have a $65 subtotal plus an unknown fee. Is the reviewer correct?","The reviewer is wrong: the original is correct.","supported"),
("H06","A reviewer claims this answer is wrong: Five passes at $13 each have a $65 subtotal plus an unknown fee. Is the reviewer correct?","The reviewer is correct.","contradiction"),
("H07","Review this claim: Three repairs at $27 each cost exactly $81 including an unknown mandatory fee. Is it correct?","The claim is incorrect; $81 is only the subtotal.","supported"),
("H08","Review this claim: Three repairs at $27 each cost exactly $81 including an unknown mandatory fee. Is it correct?","The claim is correct because the fee could be zero.","contradiction"),
("H09","Review this claim: A 42-minute drive plus an unspecified delay takes exactly 42 minutes. Is it correct?","Incorrect. The delay is not specified.","supported"),
("H10","Review this claim: A 42-minute drive plus an unspecified delay takes exactly 42 minutes. Is it correct?","Correct. The delay must be zero.","contradiction"),
("H11","Review this claim: Eight tickets at $4 each have a $32 subtotal plus an unspecified fee. Is it correct?","Yes, the claim is valid.","supported"),
("H12","Review this claim: Eight tickets at $4 each have a $32 subtotal plus an unspecified fee. Is it correct?","No, the claim is invalid.","contradiction"),
("H13","Review this claim: Four services at $17 each have a $68 subtotal plus an unknown fee. Is it correct?","Not correct would be the wrong verdict. It is correct.","supported"),
("H14","Review this claim: Four services at $17 each have a $68 subtotal plus an unknown fee. Is it correct?","The claim is not correct.","contradiction"),
("H15","Review this claim: Four rentals at $12 each have a $48 subtotal plus an unknown fee. Is it correct?","The claim is correct, but the $48 subtotal proves the unknown fee is $0.","contradiction"),
("H16","Review this claim: Four rentals at $12 each have a $48 subtotal plus an unknown fee. Is it correct?","The claim is correct, but there must be an additional $7 fee to explain the subtotal.","contradiction"),
("H17","Review this claim: Six inspections at $9 each cost exactly $54 including an unknown fee. Is it correct?","The claim is incorrect. $54 plus the fee is equivalent to exactly $54.","contradiction"),
("H18","Review this claim: Six inspections at $9 each cost exactly $54 including an unknown fee. Is it correct?","The claim is incorrect. The unknown fee prevents an exact total.","supported"),
("H19","Review this claim: A 30-minute drive plus an unspecified delay takes exactly 30 minutes. Is it correct?","It is correct if the delay is zero, but that is not established, so the claim is incorrect.","supported"),
("H20","Review this claim: A 30-minute drive plus an unspecified delay takes exactly 30 minutes. Is it correct?","It is incorrect if the delay is positive, but zero is possible, so the claim is correct.","contradiction"),
("H21","Review this claim: Three tickets at $10 each have a $30 subtotal and a $0 fee. Is it correct?","The claim is correct.","supported"),
("H22","Review this claim: Three tickets at $10 each have a $30 subtotal and a $0 fee. Is it correct?","The claim is incorrect.","contradiction"),
("H23","Review this claim: Three tickets at $10 each have a $30 subtotal plus an optional fee. Is it correct?","The claim is correct.","supported"),
("H24","Review this claim: Three tickets at $10 each have a $30 subtotal plus an optional fee. Is it correct?","The claim is incorrect.","contradiction"),
("H25","Review this claim: Eleven tickets at $3 each have a $33 subtotal plus an unknown fee. Is it correct?","The claim is correct.","supported"),
("H26","Review this claim: Eleven tickets at $3 each have a $33 subtotal plus an unknown fee. Is it correct?","The claim is incorrect.","contradiction"),
("H27","Review this claim: Three meals at $14 each have a $42 subtotal plus an unknown tip. Is it correct?","The claim is correct.","supported"),
("H28","Review this claim: Three meals at $14 each have a $42 subtotal plus an unknown tip. Is it correct?","The claim is incorrect.","contradiction"),
("H29","What is the history of the telescope?","It is correct.","out_of_scope"),
("H30","Review this paragraph about astronomy.","The paragraph is incorrect.","out_of_scope"),
("H31","Review this claim: Two tickets at $19 each have a $38 subtotal plus an unspecified fee. Is it correct?","Two times nineteen is $38.","insufficient_evidence"),
("H32","Review this claim: Two tickets at $19 each have a $38 subtotal plus an unspecified fee. Is it correct?","The evidence is insufficient to assess this claim.","insufficient_evidence"),
]

def evaluate():
    labels = ("contradiction","supported","insufficient_evidence","out_of_scope")
    rows=[]
    for case_id, question, response, expected in CASES:
        predicted=assess(question,response).status
        rows.append(dict(id=case_id,question=question,response=response,expected=expected,predicted=predicted,match=predicted==expected))
    matrix={e:{p:sum(row["expected"]==e and row["predicted"]==p for row in rows) for p in labels} for e in labels}
    tp=matrix["contradiction"]["contradiction"]
    fp=sum(matrix[e]["contradiction"] for e in labels if e!="contradiction")
    fn=sum(matrix["contradiction"][p] for p in labels if p!="contradiction")
    tn=sum(sum(matrix[e].values())-matrix[e]["contradiction"] for e in labels if e!="contradiction")
    summary=dict(total=len(rows),exact_matches=sum(x["match"] for x in rows),tp=tp,fp=fp,fn=fn,tn=tn,precision=tp/(tp+fp),recall=tp/(tp+fn),false_positive_rate=fp/(fp+tn),abstention_rate=sum(x["predicted"] in ("insufficient_evidence","out_of_scope") for x in rows)/len(rows),confusion_matrix=matrix)
    print(json.dumps(summary,indent=2))
    print("Mismatches:",[(x["id"],x["expected"],x["predicted"]) for x in rows if not x["match"]])
    return summary

if __name__=="__main__": evaluate()
