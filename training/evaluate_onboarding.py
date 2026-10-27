"""Evaluate deployed single-person scoring with five recent training likes."""
import csv,json,pathlib,sys,numpy as np
root=pathlib.Path(__file__).resolve().parents[1];model=json.loads((root/'lib/model.json').read_text());metrics=json.loads((root/'lib/metrics.json').read_text());movies=model['movies'];idx={m['id']:i for i,m in enumerate(movies)};users={}
for r in csv.DictReader(open(pathlib.Path(sys.argv[1])/'ratings.csv')):users.setdefault(int(r['userId']),[]).append((int(r['movieId']),float(r['rating']),int(r['timestamp'])))
quality=np.array([(m['quality']-2)/3 for m in movies]);rec=[];base=[];count=0
for u,rs in sorted(users.items()):
 rs.sort(key=lambda r:(r[2],r[0]));n=max(1,int(len(rs)*.2));train,test=rs[:-n],rs[-n:];likes=[idx[i] for i,r,t in train if r>=4 and i in idx];truth={idx[i] for i,r,t in test if r>=4 and i in idx}
 if len(likes)<5 or not truth:continue
 score=np.zeros(len(movies))
 for i in likes[-5:]:
  for j,w in model['weights'][i]:score[j]+=w
 if score.max()>0:score/=score.max()
 score=.9*score+.1*quality;baseline=quality.copy();excluded=[idx[i] for i,r,t in train if i in idx];score[excluded]=-np.inf;baseline[excluded]=-np.inf
 rank=sorted(range(len(movies)),key=lambda i:(-score[i],-movies[i]['count']))[:10];brank=sorted(range(len(movies)),key=lambda i:(-baseline[i],-movies[i]['count']))[:10]
 rec.append(len(set(rank)&truth)/len(truth));base.append(len(set(brank)&truth)/len(truth));count+=1
metrics['five_like_evaluation']={'users':count,'model_recall_at_10':round(float(np.mean(rec)),5),'quality_baseline_recall_at_10':round(float(np.mean(base)),5),'protocol':'Use last five eligible training likes per user, production 0.9 normalized affinity + 0.1 quality ranking; exclude all training-seen movies. Same held-out latest-20% split. Does not represent real new-user satisfaction.'}
(root/'lib/metrics.json').write_text(json.dumps(metrics,indent=2));print(json.dumps(metrics['five_like_evaluation'],indent=2))
