import numpy as np, sys
G=dict(cycle=1.2,amp=70.,duty=0.6,heel_phase=0.08,heel_off=0.42,toe_up=8.,heel_up=14.,
       swing_pitch=30., pitch_peak=0.22, flat_at=0.65, clear=12., clear_peak=0.45,
       near_center=10.,far_center=-10.,slack=0.012,min_flex=6.)
B=dict(near_hip=(579,610),near_ankle=(492,1360),near_heel=(470,1414),near_ball=(578,1414),near_toe=(614,1406),
       far_hip=(618,611),far_ankle=(585,1358),far_heel=(560,1403),far_ball=(672,1404),far_toe=(708,1393))
V=lambda t:np.array(t,float)
def rot(v,a): c,s=np.cos(a),np.sin(a); return np.array([v[0]*c-v[1]*s, v[0]*s+v[1]*c])
def ss(a,b,x): t=np.clip((x-a)/(b-a),0,1); return t*t*(3-2*t)
def ik(h,a,l1,l2):
    d=np.clip(np.linalg.norm(a-h),abs(l1-l2)+1e-3,l1+l2-1e-3); u=(a-h)/np.linalg.norm(a-h)
    x=(l1*l1-l2*l2+d*d)/(2*d); y=np.sqrt(max(l1*l1-x*x,0)); return h+u*x+np.array([u[1],-u[0]])*y
legs={}
for s_ in ('near','far'):
    lg={k:V(B[f'{s_}_{k}']) for k in ('hip','ankle','heel','ball','toe')}
    lg['l']=np.linalg.norm(lg['hip']-lg['ankle'])/2*(1+G['slack']); lg['knee']=ik(lg['hip'],lg['ankle'],lg['l'],lg['l'])
    lg['center']=lg['ball'][0]+G[s_+'_center']; lg['phase']=0. if s_=='near' else .5; legs[s_]=lg
def stance(lg,p):
    A,d=G['amp'],G['duty']; ball=V((lg['center']+A-2*A*p/d, lg['ball'][1]))
    if p<G['heel_phase']:
        th=-np.radians(G['toe_up'])*(1-ss(0,G['heel_phase'],p)); heel=ball-(lg['ball']-lg['heel'])
        return heel+rot(lg['ankle']-lg['heel'],th), th
    th=np.radians(G['heel_up'])*ss(G['heel_off'],d,p) if p>G['heel_off'] else 0.
    return ball+rot(lg['ankle']-lg['ball'],th), th
def pitch(s):
    a0,a1,a2,a3=np.radians([G['heel_up'],G['swing_pitch'],0,-G['toe_up']])
    if s<G['pitch_peak']: return a0+(a1-a0)*ss(0,G['pitch_peak'],s)
    if s<G['flat_at']: return a1+(a2-a1)*ss(G['pitch_peak'],G['flat_at'],s)
    return a2+(a3-a2)*ss(G['flat_at'],1,s)
def clearance(s):  # высота нижней точки подошвы над землёй
    return G['clear']*np.sin(np.pi*min(s/ (2*G['clear_peak']),1)) if s< G['clear_peak']*2 else G['clear']*np.sin(np.pi*(1-(s-2*G['clear_peak'])/(2-2*2*G['clear_peak'])) /2)*0+ G['clear']*np.sin(np.pi*s)**1
def foot(lg,p):
    d=G['duty']
    if p<d: return stance(lg,p)
    s=(p-d)/(1-d); a0,_=stance(lg,d); a1,_=stance(lg,0.)
    m=-2*G['amp']*(1-d)/d; s2,s3=s*s,s*s*s
    x=(2*s3-3*s2+1)*a0[0]+(s3-2*s2+s)*m+(-2*s3+3*s2)*a1[0]+(s3-s2)*m
    th=pitch(s); c=G['clear']*np.sin(np.pi*s)
    g=lg['ball'][1]
    y=min(g-c-rot(q-lg['ankle'],th)[1] for q in (lg['heel'],lg['ball'],lg['toe']))
    return V((x,y)),th
def run(verbose=True):
    out=[]
    for i in range(36):
        p=i/36; root=V((0,-G.get('bob',3)*np.cos(2*np.pi*2*(p-G.get('bob_hi',.3))))); F={}
        for s_,lg in legs.items(): F[s_]=foot(lg,(p+lg['phase'])%1)
        low=0
        for s_,lg in legs.items():
            h=lg['hip']+root; a=F[s_][0]; lmax=2*lg['l']*np.cos(np.radians(G['min_flex']/2)); dx=a[0]-h[0]
            low=max(low,(a[1]-h[1])-np.sqrt(max(lmax*lmax-dx*dx,0)))
        root[1]+=low; row=[p,root[1]]
        for s_,lg in legs.items():
            h=lg['hip']+root; a=F[s_][0]; k=ik(h,a,lg['l'],lg['l'])
            t1=k-h; t2=a-k; flex=np.degrees(np.arctan2(t1[0]*t2[1]-t1[1]*t2[0], t1@t2))
            # flex >0 : колено вперёд (нормальный сгиб); <0 переразгибание
            thigh=np.degrees(np.arctan2(t1[0],t1[1]))
            lowest=max(a[1]+rot(q-lg['ankle'],F[s_][1])[1] for q in (lg['heel'],lg['ball'],lg['toe']))
            row+= [flex, thigh, np.degrees(F[s_][1]), lg['ball'][1]-lowest, k[0]-lg['knee'][0]]
        out.append(row)
    if verbose:
        print(' p    root | near: flex thigh pitch clear kneeDx | far: flex thigh pitch clear kneeDx')
        for r in out: print(' '.join(f'{v:6.1f}' if j else f'{v:4.2f}' for j,v in enumerate(r)))
    return np.array(out)
if __name__=='__main__': run()
