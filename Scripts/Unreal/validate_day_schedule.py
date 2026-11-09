"""RED-first production schedule/data contract, run in Unreal Editor."""
import json,os,traceback
from pathlib import Path
import unreal
R={'complete':False,'pass':False}
try:
    root='/Game/RecordShop/Data/Schedule/'
    week=unreal.load_asset(root+'DA_TemporaryWeek')
    assert week, 'Missing production seven-day schedule'
    expected=[ [('A',1),('E',1)], [('B',1),('C',1)], [('A',2),('F',1),('D',1)], [('B',2),('C',2)], [('A',3),('G',1)], [('B',3),('D',2),('H',1)], [('TEMP_D7_01',1),('TEMP_D7_02',1)] ]
    days=week.get_editor_property('Days');assert len(days)==7
    observed=[];counts={}
    for day,entries in enumerate(expected,1):
        definition=days[day-1];assert definition.get_editor_property('Day')==day
        visits=definition.get_editor_property('Visits');assert len(visits)==len(entries)
        for order,(visit,(identity,number)) in enumerate(zip(visits,entries),1):
            assert str(visit.get_editor_property('CustomerID'))==identity
            assert visit.get_editor_property('VisitNumber')==number
            assert visit.get_editor_property('Day')==day and visit.get_editor_property('OrderInDay')==order
            assert visit.get_editor_property('CustomerClass'), 'Missing replaceable customer/content reference'
            observed.append({'day':day,'order':order,'customer_id':identity,'visit':number})
            counts.setdefault(identity,[]).append(number)
    assert counts['A']==counts['B']==[1,2,3]
    assert counts['C']==counts['D']==[1,2]
    assert str(week.get_editor_property('FinalStoryEventID'))=='FinalStoryEvent'
    R.update(visits=observed,repeated_visits=counts)
    R['pass']=True
except Exception:R['fatal']=traceback.format_exc()
R['complete']=True
Path(os.environ['MVP_RESULT']).write_text(json.dumps(R,indent=2,ensure_ascii=False),encoding='utf8')
