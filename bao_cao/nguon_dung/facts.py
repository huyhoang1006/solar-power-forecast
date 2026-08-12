import pandas as pd, numpy as np, json, re, glob, os
from collections import Counter
from datetime import datetime, timedelta
E=datetime(1,1,1)
def dt(t): return E+timedelta(microseconds=int(t)//10)
OUT={}

CSV='/tmp/csv'
tabs=[os.path.basename(f)[:-4] for f in sorted(glob.glob(CSV+'/*.csv'))
      if not os.path.basename(f).startswith('_')]
schema=json.load(open(CSV+'/_schema.json',encoding='utf-8'))
man=pd.read_csv(CSV+'/_manifest.csv')
OUT['meta']={'db':schema['database'],'server':schema['server_version'],
             'created':schema['dump_created'],'archive':schema['archive_version'],
             'dump_bytes':os.path.getsize('/sessions/ecstatic-fervent-einstein/mnt/PythonProject8/db_fujiwara.sql'),
             'n_toc_tables':len(schema['tables']),
             'total_rows':int(man.rows.sum()),'total_csv_bytes':int(man.bytes.sum())}

# ---- ch3: danh muc bang
OUT['tables']=[]
for t,info in schema['tables'].items():
    r=man[man.table==t]
    OUT['tables'].append({'name':t,'ncol':len(info['columns']),
        'rows':int(r.rows.iloc[0]) if len(r) else 0,
        'bytes':int(r.bytes.iloc[0]) if len(r) else 0})

# ---- ch4: truc thoi gian + thu tu luu tru
tp=[]
for t in tabs:
    try:
        d=pd.read_csv(f'{CSV}/{t}.csv',usecols=['ID','UTCTimestamp_Ticks'])
    except ValueError:
        continue
    if len(d)==0: continue
    ts=d.UTCTimestamp_Ticks.to_numpy(); ids=d.ID.to_numpy()
    dif=np.diff(ts); back=np.where(dif<0)[0]
    srt=np.sort(ts); uq=np.unique(srt)
    dd=np.round(np.diff(uq)/1e7).astype('int64')
    top=Counter(dd.tolist()).most_common(4)
    nom=top[0][0]
    span=(int(srt[-1])-int(srt[0]))/1e7
    gaps=np.diff(uq)/1e7; big=gaps[gaps>3*nom]
    blocks=Counter(np.diff(back).tolist()).most_common(1)
    tp.append({'table':t,'rows':len(d),'ncol':len(schema['tables'][t]['columns']),
      't0':str(dt(srt[0]))[:19],'t1':str(dt(srt[-1]))[:19],'span_days':round(span/86400,1),
      'nominal_s':int(nom),'pct_nominal':round(100*float((dd==nom).mean()),1),
      'coverage':round(100*len(uq)/(span/nom+1),1),'dup_ts':int(len(srt)-len(uq)),
      'n_back':int(len(back)),'block':int(blocks[0][0]) if blocks else 0,
      'block_n':int(blocks[0][1]) if blocks else 0,
      'n_gap':int(big.size),'gap_h':round(float(big.sum())/3600,1) if big.size else 0.0,
      'maxgap_h':round(float(big.max())/3600,1) if big.size else 0.0,
      'id_contiguous':bool(len(np.unique(ids))==len(ids) and ids.min()==0 and ids.max()==len(ids)-1),
      'id_max':int(ids.max()),
      'top_int':'; '.join(f'{k}s: {100*v/dd.size:.1f}%' for k,v in top[:3])})
OUT['time']=tp

# ---- ch4.7: sau khi sort
d=pd.read_csv(f'{CSV}/His_131.csv',usecols=['UTCTimestamp_Ticks'])
s=np.sort(d.UTCTimestamp_Ticks.to_numpy()); df=np.diff(s)/1e7
OUT['after_sort']={'back':int((df<0).sum()),'p50':float(np.median(df)),
  'p95':float(np.percentile(df,95)),'p99':float(np.percentile(df,99)),
  'gap10m':int((df>600).sum()),'t0':str(dt(s[0]))[:23],'t1':str(dt(s[-1]))[:23]}

# ---- ch5: topology
def ser(t,pat):
    dd=pd.read_csv(f'{CSV}/{t}.csv',low_memory=False)
    c=[x for x in dd.columns if re.search(pat,x)]
    if not c: return None
    dd['k']=(dd.UTCTimestamp_Ticks//600_000_000).astype('int64')
    return dd.groupby('k')[c[0]].mean().rename(t)
grp=['His_131','His_431','His_431A','His_432','His_433','His_434','His_435',
     'His_436','His_437','His_471','His_473','His_475','His_477']
M=pd.concat([ser(t,r'_(MEAS|Meas)_P$') for t in grp],axis=1)
M=M.join(ser('Weather',r'SOLAR_WS_Rad_1$'))
M['h']=((M.index*60)//3600)%24
day=M[(M.h>=2)&(M.h<=7)].copy()
gA=['His_431A','His_432','His_433','His_434','His_435','His_436','His_437']
gB=['His_471','His_473','His_475','His_477']
day['sumA']=day[gA].clip(upper=100).sum(axis=1,min_count=7)
day['sumB']=day[gB].sum(axis=1,min_count=4)
topo=[]
for lbl,c in [('Bay131 — 110kV, điểm đấu nối','His_131'),('Bay431 — 22kV tổng','His_431'),
              ('Tổng 471+473+475+477','sumB'),('Tổng 431A…437','sumA')]:
    v=day[c].dropna(); m=(~day.His_131.isna())&(~day[c].isna())
    r=float(np.corrcoef(day.His_131[m],day[c][m])[0,1]) if c!='His_131' else 1.0
    bias=float((day[c][m]-day.His_131[m]).mean()) if c!='His_131' else 0.0
    topo.append({'label':lbl,'n':int(len(v)),'mean':round(float(v.mean()),2),
                 'max':round(float(v.max()),2),'r':round(r,4),'bias':round(bias,3)})
OUT['topology']=topo
OUT['feeders']=[{'bay':c.replace('His_',''),'mean':round(float(day[c].clip(upper=100).mean()),2),
                 'max':round(float(day[c].clip(upper=100).max()),2)} for c in gA+gB]
OUT['n_day_samples']=int(len(day))

# ---- ch8: curtailment
w=day.dropna(subset=['His_131','Weather']); w=w[w.Weather>50]
bins=[50,200,400,600,800,1000,1400]
g=w.groupby(pd.cut(w.Weather,bins),observed=True).His_131.agg(['count','mean','std','max'])
OUT['curtail']=[{'bin':f'{int(i.left)}–{int(i.right)}','n':int(r['count']),
  'mean':round(r['mean'],2),'std':round(r['std'],2),'max':round(r['max'],2)}
  for i,r in g.iterrows()]

# ---- ch6/7: profile cot
cp=pd.read_csv('/tmp/report/column_profile.csv')
OUT['dead']=[{'table':r.table,'column':r.column,'null':r.pct_null,
              'note':'hằng số' if r.is_constant else ''}
  for r in cp.itertuples() if r.role not in('meta','time') and
     (r.is_constant==True or (pd.notna(r.pct_null) and r.pct_null>90))]
OUT['spike']=[{'table':r.table,'column':r.column,'p99':r.p99,'max':r.max,
               'ratio':round(r.max/r.p99) if r.p99 and r.p99>0 else None}
  for r in cp.itertuples() if r.role not in('meta','time') and pd.notna(r.p99)
     and r.p99>0 and r.max>100*r.p99]
OUT['irr']=[{'table':r.table,'column':r.column,'null':r.pct_null,'zero':r.pct_zero,
             'p50':r.p50,'p99':r.p99,'max':r.max,'mean':r.mean}
  for r in cp.itertuples() if r.role=='irradiance']
OUT['zero_issue']=[{'table':r.table,'column':r.column,'zero':r.pct_zero,'neg':r.pct_negative}
  for r in cp.itertuples() if r.role=='active_power' and pd.notna(r.pct_zero)]

# ---- ch6: diurnal + correlation
rep=pd.read_csv(f'{CSV}/His_report.csv',low_memory=False)
rep['ts']=pd.to_datetime(rep.ts_utc)+pd.Timedelta(hours=7)
rep['h']=rep.ts.dt.hour
prof={}
for c in ['SOLAR_WS_Rad_1','SOLAR_WS_Rad_2','SOLAR_WSRT1_Rad_1',
          'Substation_Level_110kV_Bay131_MEAS_P','SOLAR_WS_Panel_T','SOLAR_WS_Air_T']:
    if c in rep.columns:
        prof[c]=rep.groupby('h')[c].mean().round(3).to_dict()
OUT['diurnal']=prof
cc=rep[['SOLAR_WS_Rad_1','SOLAR_WS_Rad_2','SOLAR_WSRT1_Rad_1','SOLAR_WS_Panel_T',
        'SOLAR_WS_Air_T','SOLAR_WS_Humidity','SOLAR_WS_Wind_Speed',
        'Substation_Level_110kV_Bay131_MEAS_P']].corr()
OUT['corr']=cc['Substation_Level_110kV_Bay131_MEAS_P'].round(4).to_dict()

json.dump(OUT,open('/tmp/rep/facts.json','w',encoding='utf-8'),
          ensure_ascii=False,indent=1,default=str)
print("OK ->", len(json.dumps(OUT,default=str)), "bytes")
for k,v in OUT.items():
    print(f"  {k}: {len(v) if hasattr(v,'__len__') else v}")
