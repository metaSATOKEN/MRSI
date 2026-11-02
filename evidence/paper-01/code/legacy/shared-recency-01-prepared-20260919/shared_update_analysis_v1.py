"""SU01 descriptive scoring on the fixed four-group denominator."""
import shared_update_design_v1 as d

def conjunction(values):
    if any(v is False for v in values):return False
    return None if any(v is None for v in values) else True
def interval(values):
    return [sum(v is True for v in values)/len(values),sum(v is not False for v in values)/len(values)]
def content(v):
    if isinstance(v,dict):return {k:content(x) for k,x in v.items() if k not in ('origin_id','channel_read_refs','channel_origin_ids')}
    if isinstance(v,list):return [content(x) for x in v]
    return v
def equivalent(v,w):
    if type(v) is list:return len(v)==len(w) and len(set(v))==len(v) and set(v)==set(w)
    if type(v) is dict:return set(v)==set(w) and all(equivalent(v[k],w[k]) for k in v)
    return v==w
def score_fields(p,expected,stage):
    probe=stage in ('BASE','PROBE');full={};values={}
    for k,t in expected.items():
        v=p.get(k)
        full[k]=None if v is None else equivalent(v,t)
        if probe:
            if k in ('mascot','channel'):values[k]=full[k]
        else:values[k]=None if v is None else equivalent(content(v),content(t))
    return dict(full=conjunction(list(full.values())),content=conjunction(list(values.values())),full_components=full,content_components=values)

def analyze(groups,slots,outputs):
    if set(outputs)!={s['id'] for s in slots}:raise ValueError('exact planned ID set required')
    gm={g['group']:g for g in groups};parsed={};scores={};rows=[]
    for s in slots:
        p=d.parse(outputs[s['id']],s['stage']);parsed[s['id']]=p
        score=score_fields(p,d.ideal(gm[s['group']],s),s['stage']);scores[s['id']]=score
        rows.append({k:s[k] for k in ('id','group','stage','role','arm','repetition')}|score|dict(structural_complete=d.continuable(p)))
    for row,s in zip(rows,slots):
        if s['stage'] not in ('BASE','PROBE'):continue
        packet=d.payload(gm[s['group']],s,parsed);p=parsed[s['id']];support={}
        records={} if packet is None else {x['record_id']:x['body'] for x in packet['records']}
        for field,name in [('mascot','PRIVATE'),('channel','GROUP')]:
            value=p[field];origin=p[field+'_origin_ids'];direct=p[field+'_read_refs']
            if value is None or origin is None or direct is None or name not in records:ok=None
            elif value=='UNKNOWN':ok=origin==direct==[]
            elif field=='mascot':
                c=records[name]['customer'];ok=c['subject']==s['role'] and c['animal']==value and equivalent(origin,[c['origin_id']]) and direct==['PRIVATE']
            else:
                cov=records[name]['coverage'];ok=all(cov[r]['observer']==r for r in d.ROLES) and d.best(cov)==value and equivalent(origin,[cov[r]['origin_id'] for r in d.ROLES]) and direct==['GROUP']
            support[field]=ok
        row['input_support']=support
        row['full']=scores[s['id']]['full']=conjunction([row['full']]+list(support.values()))
    blocks={};branches={a:{'full':[],'content':[]} for a in d.ARMS};pairs={'full':[],'content':[]}
    for g in groups:
        gid=g['group'];blocks[gid]={}
        for axis in ('full','content'):
            def val(stage,r,arm=None,rep=None):return scores[d.sid(g,stage,r,arm,rep)][axis]
            B=conjunction([val('ENCODE',r) for r in d.ROLES]+[val('EDIT',g['editor'])]+[val('BASE',r) for r in d.ROLES])
            arms={}
            for arm in d.ARMS:
                U=val('UPDATE',g['notifier'],arm);R=val('RECEIVE',g['receiver'],arm)
                J=[conjunction([val('PROBE',r,arm,rep) for r in d.ROLES]) for rep in (1,2)]
                C=conjunction([B,U,R]+J);arms[arm]=dict(U=U,R=R,J=J,C=C);branches[arm][axis].append(C)
            pair=conjunction([arms[a]['C'] for a in d.ARMS]);pairs[axis].append(pair)
            blocks[gid][axis]=dict(B=B,arms=arms,paired=pair)
    summary={}
    for arm in d.ARMS:
        rows_arm=[s for s in slots if s['stage']=='PROBE' and s['arm']==arm]
        metrics={}
        for field in ('mascot','channel'):
            vals=[scores[s['id']]['full_components'][field] for s in rows_arm]
            unknown=[None if parsed[s['id']][field] is None else parsed[s['id']][field]=='UNKNOWN' for s in rows_arm]
            metrics['I' if field=='mascot' else 'G']=interval(vals)
            metrics[field+'_unknown']=interval(unknown)
        for role_kind in ('notifier','receiver'):
            rs=[s for s in rows_arm if s['role']==gm[s['group']][role_kind]]
            metrics[role_kind]={field:interval([scores[s['id']]['full_components'][field] for s in rs]) for field in ('mascot','channel')}
        agree=[];repeat=[];paths=[]
        for g in groups:
            for rep in (1,2):
                choices=[parsed[d.sid(g,'PROBE',r,arm,rep)]['channel'] for r in d.ROLES]
                agree.append(None if None in choices else choices[0]==choices[1])
            for r in d.ROLES:
                ids=[d.sid(g,'PROBE',r,arm,rep) for rep in (1,2)]
                ps=[parsed[i] for i in ids]
                repeat.append(None if any(not d.continuable(p) for p in ps) else all(equivalent(ps[0][k],ps[1][k]) for k in d.PROBE_FIELDS))
                base=parsed[d.sid(g,'BASE',r)]
                paths.append(dict(group=g['group'],role=r,baseline=base['channel'],final=[p['channel'] for p in ps],mascot_baseline=base['mascot'],mascot_final=[p['mascot'] for p in ps]))
        metrics.update(group_channel_agreement=interval(agree),same_input_response_agreement=interval(repeat),paths=paths)
        summary[arm]=metrics
    main=interval(pairs['full'])
    status='MET_IN_FIXED_SAMPLE' if main[0]==1 else 'NOT_MET_IN_FIXED_SAMPLE' if main[1]<1 else 'INCONCLUSIVE'
    by_stage={stage:{axis:interval([r[axis] for r in rows if r['stage']==stage]) for axis in ('full','content')} for stage in d.PROMPTS}
    return dict(planned_slots=len(slots),planned_groups=4,C_PAIR=main,C_PAIR_CONTENT=interval(pairs['content']),
        prediction_status=status,conditions={a:{'C':interval(branches[a]['full']),'C_CONTENT':interval(branches[a]['content']),**summary[a]} for a in d.ARMS},
        delta_C=[interval(branches['CHANGE']['full'])[0]-interval(branches['STABLE']['full'])[1],interval(branches['CHANGE']['full'])[1]-interval(branches['STABLE']['full'])[0]],
        stage_scores=by_stage,blocks=blocks,rows=rows,scope='Fixed four known scenarios; shared baseline, two branches, two independent final calls. Missingness bounds, not confidence intervals.',inferential_tests=None)
