import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, matplotlib.patches as mp
import pandas as pd, numpy as np, json, re
plt.rcParams.update({'font.size':9,'figure.dpi':150,'axes.grid':True,'grid.alpha':.3,
                     'axes.spines.top':False,'axes.spines.right':False})
F='/tmp/rep/fig'; CSV='/tmp/csv'
J=json.load(open('/tmp/rep/facts.json',encoding='utf-8'))
B='#1f4e79'; O='#c55a11'; G='#548235'; R='#c00000'

# H1 - ring buffer
fig,ax=plt.subplots(figsize=(7.2,3.4))
n=24
for i in range(n):
    a=90-i*360/n
    col = O if i<9 else B
    w=mp.Wedge((0,0),1,a-360/n,a,width=.32,facecolor=col,edgecolor='w',lw=1.2)
    ax.add_patch(w)
ax.annotate('con trỏ ghi\n(17/07/2026)',xy=(.72,.62),xytext=(1.5,1.15),fontsize=8,
    arrowprops=dict(arrowstyle='->',color='k',lw=1.2),ha='center')
ax.text(0,0,'ID = 0 … 521.102\nchỉ số ô nhớ',ha='center',va='center',fontsize=9)
ax.annotate('Ô CHƯA GHI ĐÈ\ndữ liệu 07–08/2025',xy=(-.85,.35),xytext=(-2.45,.75),color=B,fontsize=8,va='center',ha='left',arrowprops=dict(arrowstyle='->',color=B,lw=1))
ax.annotate('Ô VỪA GHI ĐÈ\ndữ liệu 06–07/2026',xy=(.72,-.55),xytext=(1.25,-1.05),color=O,fontsize=8,va='center',ha='left',arrowprops=dict(arrowstyle='->',color=O,lw=1))
ax.set_xlim(-2.9,2.9); ax.set_ylim(-1.5,1.5); ax.set_aspect(1); ax.axis('off'); ax.grid(False)

fig.tight_layout(); fig.savefig(f'{F}/h31_ring.png',bbox_inches='tight'); plt.close(fig)

# H2 - truoc/sau sort
d=pd.read_csv(f'{CSV}/His_131.csv',usecols=['UTCTimestamp_Ticks'])
ts=d.UTCTimestamp_Ticks.to_numpy()
def toy(t): return (t-638879350252370000)/1e7/86400
fig,ax=plt.subplots(1,2,figsize=(7.4,2.9))
k=slice(0,3000)
ax[0].plot(np.arange(3000),toy(ts[k]),lw=.5,color=R)
ax[0].set_title('Trước khi sắp xếp (3.000 dòng đầu)',fontsize=9)
ax[0].set_xlabel('Vị trí dòng trong file'); ax[0].set_ylabel('Ngày kể từ 12/07/2025')
s=np.sort(ts)
ax[1].plot(np.arange(0,len(s),200),toy(s[::200]),lw=1.2,color=G)
ax[1].set_title('Sau khi sắp xếp theo timestamp',fontsize=9)
ax[1].set_xlabel('Vị trí dòng trong file')

fig.tight_layout(); fig.savefig(f'{F}/h41_sort.png',bbox_inches='tight'); plt.close(fig)

# H3 - do phu
tp=pd.DataFrame(J['time']).sort_values('coverage')
fig,ax=plt.subplots(figsize=(7.2,3.6))
c=[R if v<60 else (O if v<97 else G) for v in tp.coverage]
ax.barh(tp.table,tp.coverage,color=c)
ax.axvline(100,color='k',lw=.8,ls='--')
for i,(v,t) in enumerate(zip(tp.coverage,tp.table)): ax.text(v+1,i,f'{v:.1f}%',va='center',fontsize=7.5)
ax.set_xlabel('Độ phủ dữ liệu (%)'); ax.set_xlim(0,124)

fig.tight_layout(); fig.savefig(f'{F}/h42_cov.png',bbox_inches='tight'); plt.close(fig)

# H4 - heatmap san co du lieu theo ngay
fig,axs=plt.subplots(3,1,figsize=(7.4,5.2),sharex=True)
for ax,t in zip(axs,['His_131','Weather','His_431A']):
    x=pd.read_csv(f'{CSV}/{t}.csv',usecols=['ts_utc'])
    ts2=pd.to_datetime(x.ts_utc)+pd.Timedelta(hours=7)
    g=pd.DataFrame({'d':ts2.dt.floor('D'),'h':ts2.dt.hour}).groupby(['d','h']).size()
    piv=g.unstack('h').reindex(columns=range(24))
    nom=60 if t!='His_report' else 300
    im=ax.imshow((piv.to_numpy()/ (3600/nom)*100).clip(0,100).T,aspect='auto',cmap='RdYlGn',
                 vmin=0,vmax=100,origin='lower',
                 extent=[0,len(piv),0,24],interpolation='nearest')
    ax.set_ylabel(f'{t}\ngiờ'); ax.set_yticks([0,6,12,18,24]); ax.grid(False)
axs[-1].set_xlabel('Ngày kể từ 12/07/2025')
fig.colorbar(im,ax=axs,label='% mẫu có sẵn trong giờ',pad=.02)

fig.savefig(f'{F}/h43_heat.png',bbox_inches='tight'); plt.close(fig)

# H5 - diurnal
dj=J['diurnal']; h=list(range(24))
fig,ax=plt.subplots(figsize=(7.2,3.4))
ax2=ax.twinx()
for c,col,lb in [('SOLAR_WS_Rad_1',O,'Bức xạ Rad_1 (W/m²)'),('SOLAR_WS_Rad_2',R,'Bức xạ Rad_2 (W/m²)')]:
    ax.plot(h,[dj[c].get(str(i),dj[c].get(i)) for i in h],color=col,marker='o',ms=3,label=lb)
pc='Substation_Level_110kV_Bay131_MEAS_P'
ax2.plot(h,[dj[pc].get(str(i),dj[pc].get(i)) for i in h],color=B,marker='s',ms=3,lw=2,label='Công suất Bay131 (MW)')
ax.axvline(12,color='k',ls=':',lw=1); ax.text(12.2,ax.get_ylim()[1]*.9,'12h trưa',fontsize=8)
ax.set_xlabel('Giờ Việt Nam (GMT+7)'); ax.set_ylabel('Bức xạ (W/m²)'); ax2.set_ylabel('Công suất (MW)')
ax.set_xticks(range(0,24,2)); ax2.grid(False)
l1,b1=ax.get_legend_handles_labels(); l2,b2=ax2.get_legend_handles_labels()
ax.legend(l1+l2,b1+b2,fontsize=7.5,loc='upper left')

fig.tight_layout(); fig.savefig(f'{F}/h61_diurnal.png',bbox_inches='tight'); plt.close(fig)

# H6 - scatter curtailment
rep=pd.read_csv(f'{CSV}/His_report.csv',low_memory=False)
rep['ts']=pd.to_datetime(rep.ts_utc)+pd.Timedelta(hours=7)
m=rep[(rep.ts.dt.hour>=8)&(rep.ts.dt.hour<=15)].dropna(subset=['SOLAR_WS_Rad_1',pc])
fig,ax=plt.subplots(figsize=(7.2,3.6))
ax.scatter(m.SOLAR_WS_Rad_1,m[pc],s=1.2,alpha=.06,color=B,rasterized=True)
cur=pd.DataFrame(J['curtail']); cen=[125,300,500,700,900,1200]
ax.plot(cen[:len(cur)],cur['mean'],color=O,marker='o',lw=2,label='Trung bình theo dải bức xạ')
ax.axhline(39.27,color=R,ls='--',lw=1,label='Max quan sát 39,27 MW')
ax.set_xlabel('Bức xạ SOLAR_WS_Rad_1 (W/m²)'); ax.set_ylabel('Công suất Bay131 (MW)')
ax.legend(fontsize=8,loc='upper left')

fig.tight_layout(); fig.savefig(f'{F}/h81_scatter.png',bbox_inches='tight',dpi=140); plt.close(fig)

# H7 - so do do luong
fig,ax=plt.subplots(figsize=(7.4,3.9))
def box(x,y,w,h,txt,col,fs=7.5):
    ax.add_patch(mp.FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.02',
        facecolor=col,edgecolor='#333',lw=.9,alpha=.9))
    ax.text(x+w/2,y+h/2,txt,ha='center',va='center',fontsize=fs,color='w' if col!='#eee' else '#000')
box(3.6,3.15,2.8,.6,'LƯỚI 110 kV','#444',8)
box(3.6,2.3,2.8,.6,'Bay 131  •  His_131\n22,38 MW  —  BIẾN MỤC TIÊU',B,7.5)
box(3.9,1.5,2.2,.5,'MBA T1  •  His_T1','#7f7f7f')
box(3.6,.75,2.8,.5,'Bay 431 (22 kV tổng)  •  His_431\n22,41 MW   r = 0,9998',G)
ax.plot([5,5],[3.15,2.9],color='k',lw=1.1); ax.plot([5,5],[2.3,2.0],color='k',lw=1.1)
ax.plot([5,5],[1.5,1.25],color='k',lw=1.1); ax.plot([5,5],[.75,.45],color='k',lw=1.1)
ax.plot([1.2,8.8],[.45,.45],color='k',lw=1.6)
for i,(lbl,xx) in enumerate(zip(['471','473','475','477'],[1.5,3.0,4.5,6.0])):
    ax.plot([xx+.45,xx+.45],[.45,.2],color='k',lw=1)
    box(xx,-.35,.9,.55,f'Bay{lbl}',O,7)
box(7.3,-.35,1.5,.55,'431A…437\n(7 lộ)','#bfbfbf',7)
ax.plot([8.05,8.05],[.45,.2],color='k',lw=1)
ax.text(1.2,-.75,'Σ 471+473+475+477 = 23,15 MW   (r = 0,9984 với Bay131)',fontsize=7.5,color=O)
ax.text(1.2,-1.0,'Σ 431A…437 = 23,42 MW   (độ phủ chỉ 46–48%, có giá trị rác)',fontsize=7.5,color='#777')
ax.set_xlim(.8,9.2); ax.set_ylim(-1.3,4.0); ax.axis('off'); ax.grid(False)

fig.tight_layout(); fig.savefig(f'{F}/h51_topo.png',bbox_inches='tight'); plt.close(fig)

# H8 - phan bo buoc mau
fig,ax=plt.subplots(figsize=(7.2,3.2))
d2=pd.read_csv(f'{CSV}/His_131.csv',usecols=['UTCTimestamp_Ticks'])
dd=np.diff(np.sort(d2.UTCTimestamp_Ticks.to_numpy()))/1e7
ax.hist(dd[(dd>0)&(dd<200)],bins=np.arange(0,200,2),color=B)
ax.set_yscale('log'); ax.set_xlabel('Khoảng cách giữa hai mẫu liên tiếp (giây)')
ax.set_ylabel('Số lần (thang log)')
ax.axvline(60,color=O,ls='--',lw=1.2); ax.text(63,ax.get_ylim()[1]*.3,'60 s danh định\n99,5% số mẫu',fontsize=8,color=O)

fig.tight_layout(); fig.savefig(f'{F}/h44_hist.png',bbox_inches='tight'); plt.close(fig)
print("done")
