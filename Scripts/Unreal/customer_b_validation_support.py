"""B dialogue/score expectations: test fixtures, never production score authority."""
KNOWN=('BEST','GOOD','POOR')
def expected_b_rows(visit,v1=None,v2=None):
 if visit==1:return ['B1_Current_%02d'%i for i in range(1,7)]
 if visit==2:return (['B2_Memory_'+v1]if v1 in KNOWN else [])+['B2_Current_%02d'%i for i in range(1,6)]
 assert visit==3
 common=['B3_Current_%02d'%i for i in range(1,4)]
 if v1 not in KNOWN or v2 not in KNOWN:return ['B3_Memory_NEUTRAL']+common+['B3_Payoff_Clarify']
 return ['B3_Memory_'+v2,'B3_Earlier_'+v1]+common+['B3_Payoff_Aligned'if v1 in ('BEST','GOOD')and v2 in ('BEST','GOOD')else 'B3_Payoff_Clarify']
def expected_score(identity,visit,choice):
 vector=(0,0,3)if identity=='B'and visit==1 else (1,1,2)if identity=='B'else (3,2,0)
 return vector[choice-1]
def expected_result(score):return {0:'POOR',1:'POOR',2:'GOOD',3:'BEST'}[score]
