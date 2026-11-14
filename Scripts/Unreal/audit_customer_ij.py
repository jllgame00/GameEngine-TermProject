"""Read-only current graph/data evidence before Day7 authoring."""
import unreal,json,os,sys,traceback
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir());sys.path.insert(0,str(ROOT/'Scripts/Unreal'))
from mvp_graph_helpers import L,G
def graph(bp,name):
 return [{'id':n.get_name(),'title':str(n.get_node_title()),'pins':[{'name':str(p.get_pin_name()),'value':p.get_pin_value(),'links':[q.get_owning_node().get_name()+':'+str(q.get_pin_name())for q in p.list_connected_pins()]}for p in n.list_all_pins()]}for n in G.get_graph_editor_by_name(bp,name).list_all_nodes()]
R={'complete':False,'pass':False,'read_only':True}
try:
 unreal.InternationalizationLibrary.set_current_language('en',False)
 bp=unreal.load_asset('/Game/RecordShop/UI/Result/WBP_Result_IntegrationFallback')
 R['result_graphs']={str(g.get_name()):graph(bp,str(g.get_name()))for g in L.list_graphs(bp)}
 bp=unreal.load_asset('/Game/RecordShop/Core/Flow/BP_GameFlowManager')
 R['flow_graphs']={n:graph(bp,n)for n in ('EndCurrentDay','FinishDayTransition','GetActiveNarrativeDefinition','AfterCustomerCycle')}
 week=unreal.load_asset('/Game/RecordShop/Data/Schedule/DA_TemporaryWeek')
 R['visits']=[v.export_text()if hasattr(v,'export_text')else {k:str(v.get_editor_property(k))for k in ('CustomerID','VisitNumber','Day','OrderInDay','CustomerClass','IsPlaceholderContent','StoryEventID','Narrative','CustomerData')}for d in week.get_editor_property('Days')for v in d.get_editor_property('Visits')]
 R['schema']=list(map(str,L.list_member_variable_names(unreal.load_asset('/Game/RecordShop/Data/Narrative/BP_VisitNarrativeDefinition'),False)))
 R['pass']=True
except Exception:R['fatal']=traceback.format_exc()
R['complete']=True;Path(os.environ['MVP_RESULT']).write_text(json.dumps(R,indent=2,ensure_ascii=False),encoding='utf8')
