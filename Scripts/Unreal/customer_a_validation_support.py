"""Independent expected row contract used by A matrix and live week tests."""
A2_BODY=['A2_Current_%02d'%i for i in range(1,6)]
A3_BODY=['A3_Current_%02d'%i for i in range(1,4)]
KNOWN=('BEST','GOOD','POOR')
def expected_a_rows(visit,v1=None,v2=None):
 if visit==2:return (['A2_Memory_'+v1]if v1 in KNOWN else [])+A2_BODY
 assert visit==3
 if v1 not in KNOWN or v2 not in KNOWN:return ['A3_Memory_NEUTRAL']+A3_BODY+['A3_Payoff_Clarify']
 return ['A3_Memory_'+v2,'A3_Earlier_'+v1]+A3_BODY+['A3_Payoff_Aligned'if v1 in ('BEST','GOOD')and v2 in ('BEST','GOOD')else 'A3_Payoff_Clarify']
