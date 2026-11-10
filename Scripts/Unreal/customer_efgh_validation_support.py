"""Single-visit expectations, never runtime routing or scoring authority."""
PROFILES={'E':('Quiet','Jazz','Sociable'),'F':('Restless','Electronic','Adventurous'),'G':('Quiet','Folk','Sociable'),'H':('Quiet','Classical','Reflective')}
DAYS={'E':1,'F':3,'G':5,'H':6}
ORDERS={'E':2,'F':2,'G':2,'H':3}
SCORES={'E':(2,3,0),'F':(0,0,3),'G':(1,2,0),'H':(1,1,0)}

def expected_efgh_rows(identity):
 assert identity in PROFILES
 return [identity+'1_Current_%02d'%i for i in range(1,5)]
