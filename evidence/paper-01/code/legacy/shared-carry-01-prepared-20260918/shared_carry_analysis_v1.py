"""SC01 fixed-denominator, component-wise descriptive scoring; no model calls."""
import shared_carry_design_v1 as d


def bit(v):
    return [0,1] if v is None else [int(bool(v)),int(bool(v))]


def both(*values):
    if any(v is False or v == 0 for v in values): return False
    if any(v is None for v in values): return None
    return True


def mean_interval(values):
    if not values: raise ValueError('empty fixed denominator')
    b = [bit(v) for v in values]
    return [sum(x[0] for x in b)/len(b), sum(x[1] for x in b)/len(b)]


def difference(a,b):
    return [a[0]-b[1], a[1]-b[0]]


def equal_note(note, truth):
    return None if note is None else note == truth


def expected_shared(g):
    covs = {r:g['originals'][r]['coverage'] for r in d.ROLES}
    return dict(coverage=covs, channel=g['best_channel'], channel_sources=sorted(covs[r]['source_id'] for r in d.ROLES))


def shared_score(note, g):
    if note is None: return None
    t = expected_shared(g)
    return (note['coverage'] == t['coverage'] and note['channel'] == t['channel'] and
            len(note['channel_sources']) == 2 and set(note['channel_sources']) == set(t['channel_sources']))


def direct_support(g, slot, parsed, output, field):
    cited = output[field+'_sources']
    if cited is None: return None
    available = {'PRIVATE','GROUP'} if slot['arm']=='BOTH' else {'PRIVATE'} if slot['arm']=='PRIVATE' else {'GROUP'}
    if len(set(cited)) != len(cited) or not set(cited).issubset(available): return False
    if output[field] is None: return None
    if output[field] == 'UNKNOWN': return cited == []
    gid, r = g['group'], slot['role']
    pn = parsed.get(f'{gid}-ENCODE-{r}', {}).get('note')
    sn = parsed.get(f"{gid}-EDIT-{g['editor']}", {}).get('note')
    if field == 'mascot':
        if cited != ['PRIVATE']: return False
        return None if pn is None else (pn['customer'] == g['originals'][r]['customer'] and
                                       output[field] == pn['customer']['animal'])
    if 'GROUP' not in cited: return False
    if sn is None: return None
    cov_ok = (sn['coverage'] == expected_shared(g)['coverage'] and
              output[field] == g['best_channel'])
    if 'PRIVATE' in cited:
        if pn is None: return both(cov_ok,None)
        cov_ok = cov_ok and pn['coverage'] == g['originals'][r]['coverage']
    return cov_ok


def analyze(groups, slots, outputs):
    if set(outputs) != {s['id'] for s in slots}: raise ValueError('exact planned ID set required')
    parsed = {s['id']:d.parse(outputs[s['id']],s['stage']) for s in slots}
    by_group = {g['group']:g for g in groups}
    formation, f_components, rows = {}, {}, []
    for g in groups:
        gid = g['group']
        comp = {r:equal_note(parsed[f'{gid}-ENCODE-{r}']['note'],g['originals'][r]) for r in d.ROLES}
        comp['FINAL'] = shared_score(parsed[f"{gid}-EDIT-{g['editor']}"]['note'],g)
        f_components[gid] = comp
        formation[gid] = both(*comp.values())
    cells = {}
    for s in slots:
        if s['stage'] != 'PROBE': continue
        g = by_group[s['group']]; p = parsed[s['id']]
        iv = None if p['mascot'] is None else p['mascot'] == g['originals'][s['role']]['customer']['animal']
        gv = None if p['channel'] is None else p['channel'] == g['best_channel']
        si = direct_support(g,s,parsed,p,'mascot');sg = direct_support(g,s,parsed,p,'channel')
        cell = dict(I=iv,G=gv,I_source=si,G_source=sg,
                    self_unknown=None if p['mascot'] is None else p['mascot']=='UNKNOWN',
                    group_unknown=None if p['channel'] is None else p['channel']=='UNKNOWN')
        cells[(s['group'],s['role'],s['arm'],s['repetition'])] = cell
        rows.append(dict(id=s['id'],group=s['group'],role=s['role'],arm=s['arm'],repetition=s['repetition'],**cell))
    jv, js, ev, es, all_repeat = {}, {}, {}, {}, {}
    for arm in d.ARMS:
        jv[arm]=[];js[arm]=[];ev[arm]=[];es[arm]=[];all_repeat[arm]=[]
        for g in groups:
            group_js=[]
            for rep in (1,2):
                c=[cells[(g['group'],r,arm,rep)] for r in d.ROLES]
                v=both(*(x[k] for x in c for k in ('I','G')))
                s=both(*(x[k] for x in c for k in ('I','G','I_source','G_source')))
                jv[arm].append(v);js[arm].append(s);group_js.append(s)
                ev[arm].append(both(formation[g['group']],v));es[arm].append(both(formation[g['group']],s))
            all_repeat[arm].append(both(*group_js))
    table = {}
    for arm in d.ARMS:
        rs = [r for r in rows if r['arm']==arm]
        table[arm] = {k:mean_interval([r[k] for r in rs]) for k in ('I','G','I_source','G_source','self_unknown','group_unknown')}
        table[arm].update(J_value=mean_interval(jv[arm]),J_source=mean_interval(js[arm]),
                          both_repetitions=mean_interval(all_repeat[arm]))
    e = mean_interval(es['BOTH'])
    status = 'MET_IN_FIXED_SAMPLE' if e[0]==1 else 'NOT_MET_IN_FIXED_SAMPLE' if e[1]<1 else 'INCONCLUSIVE'
    f=mean_interval(list(formation.values()))
    fstatus='NO_JOINT_FORMATION' if f[1]==0 else 'OBSERVED_JOINT_FORMATION' if f[0]>0 else 'INCONCLUSIVE_FORMATION'
    return dict(planned_slots=len(slots),planned_groups=len(groups),formation=formation,
                formation_components=f_components,F=f,formation_status=fstatus,
                E_BOTH=e,E_VALUE=mean_interval(ev['BOTH']),prediction_status=status,conditions=table,
                L=difference(table['BOTH']['I'],table['PRIVATE']['I']),
                A=difference(table['BOTH']['G'],table['PRIVATE']['G']),rows=rows,
                scope='Fixed 4 groups, 2 materials, 2 probe repetitions; bounds are missingness bounds, not confidence intervals.',
                inferential_tests=None)
