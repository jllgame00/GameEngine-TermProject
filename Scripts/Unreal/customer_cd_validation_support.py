"""C/D sequence expectations; test fixtures, never runtime narrative authority."""
PROFILES={'C':('Quiet','Folk','Sociable'),'D':('Quiet','Classical','Reflective')}
DAYS={'C':(2,4),'D':(3,6)}
SCORES={'C':(1,2,0),'D':(1,1,0)}
def expected_cd_rows(identity,visit,result=None):
 assert identity in PROFILES and visit in (1,2)
 intro=[identity+'2_Memory_'+result]if visit==2 and result in ('BEST','GOOD','POOR')else []
 return intro+[identity+str(visit)+'_Current_%02d'%i for i in range(1,6 if visit==1 else 5)]
