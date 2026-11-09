"""Assertions for live history production tests; never writes history/day authority."""
import unreal
FIELDS=('CustomerID','VisitNumber','Day','RecordID','RecommendationScore','RecommendationResult','Sequence')
def payload(entry):
 if entry is None:return None
 values=[entry.get_editor_property(k) for k in FIELDS]
 return {k:(str(v) if k in ('CustomerID','RecordID','RecommendationResult') else int(v)) for k,v in zip(FIELDS,values)}

class MemoryChecks:
 def __init__(self):self.entries=[];self.observed=[]
 def query(self,flow,identity):return [payload(x) for x in flow.call_method('GetRecommendationHistory',args=(identity,))]
 def before(self,flow,expected,index):
  identity,number,day,order=expected
  prior=[x for x in self.entries if x['CustomerID']==identity] if index else []
  assert self.query(flow,identity)==prior
  assert bool(flow.call_method('HasPreviousVisit',args=(identity,)))==bool(prior)
  latest=flow.call_method('GetLatestRecommendation',args=(identity,));assert payload(latest)==(prior[-1] if prior else None)
  context=flow.call_method('GetActiveVisitMemory')
  if index:
   assert (str(context[0]),int(context[1]),int(context[2]),bool(context[3]))==(identity,number,day,bool(prior)),context
   assert payload(context[4])==(prior[-1] if prior else None)
  else:assert str(context[0])=='None' and not context[3] and context[4] is None
  for entry in prior:assert payload(flow.call_method('GetRecommendationForVisit',args=(identity,entry['VisitNumber'])))==entry
  assert flow.call_method('GetRecommendationForVisit',args=(identity,999)) is None
  assert not flow.call_method('GetRecommendationHistory',args=('UNKNOWN',))
  assert not flow.call_method('HasPreviousVisit',args=('UNKNOWN',))
  if prior:
   latest.set_editor_property('RecordID','MUTATED_COPY')
   assert payload(flow.call_method('GetLatestRecommendation',args=(identity,)))==prior[-1]
  self.observed.append({'customer':identity,'visit':number,'day':day,'previous':prior})
 def selected(self,flow):
  flow.call_method('CommitRecommendationHistory')
  assert len(flow.get_editor_property('RecommendationHistory'))==len(self.entries),'Selection recorded history'
 def result(self,flow,expected,index,choice):
  identity,number,day,_=expected
  if index:
   self.entries.append(dict(CustomerID=identity,VisitNumber=number,Day=day,RecordID='RS00'+str(choice),RecommendationScore={1:3,2:2,3:0}[choice],RecommendationResult={1:'BEST',2:'GOOD',3:'POOR'}[choice],Sequence=len(self.entries)+1))
  assert len(flow.get_editor_property('RecommendationHistory'))==len(self.entries)
  expected_entries=[x for x in self.entries if x['CustomerID']==identity]
  for entry in expected_entries:
   ok,record=flow.get_editor_property('RecordCatalogue').call_method('ResolveRecord',args=(entry['RecordID'],));assert ok
  assert self.query(flow,identity)==expected_entries
  for _ in range(3):flow.call_method('HandleTurntableCompleted');flow.call_method('CommitRecommendationHistory')
  flow.call_method('ResetRecommendationHistory')
  assert len(flow.get_editor_property('RecommendationHistory'))==len(self.entries)
  assert self.query(flow,identity)==expected_entries,'Duplicate callback or active reset corrupted history'
  if index:
   context=flow.call_method('GetActiveVisitMemory');prior=[x for x in expected_entries if x['VisitNumber']<number]
   assert bool(context[3])==bool(prior) and payload(context[4])==(prior[-1] if prior else None),'Context included current result'
 def finish(self,flow):
  assert len(self.entries)==16
  for identity in ['A','B','C','D','E','F','G','H','TEMP_D7_01','TEMP_D7_02']:
   assert self.query(flow,identity)==[x for x in self.entries if x['CustomerID']==identity]
  assert self.entries[0]['RecordID']=='RS002' and self.entries[0]['RecommendationResult']=='GOOD'
  return {'entries':self.entries,'revisit_observations':self.observed,'duplicate_and_copy_isolation':True,'selection_not_recorded':True,'active_reset_rejected':True}
