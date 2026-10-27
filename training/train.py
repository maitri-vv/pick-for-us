"""Train sparse EASE on MovieLens. Research demo; see DATA_LICENSE.txt."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','2')
import argparse,csv,json,hashlib,time,pathlib
import numpy as np
from scipy.sparse import csr_matrix
parser=argparse.ArgumentParser();parser.add_argument('--data',required=True);args=parser.parse_args()
root=pathlib.Path(__file__).resolve().parents[1];data=pathlib.Path(args.data)
rows=list(csv.DictReader(open(data/'ratings.csv'))); movies={int(r['movieId']):r for r in csv.DictReader(open(data/'movies.csv'))};links={int(r['movieId']):r for r in csv.DictReader(open(data/'links.csv'))}
users={}
for r in rows: users.setdefault(int(r['userId']),[]).append((int(r['movieId']),float(r['rating']),int(r['timestamp'])))
train=[];tests={};seen={}
for u,rs in users.items():
 rs.sort(key=lambda r:(r[2],r[0]));n=max(1,int(len(rs)*.2));train.extend((u,*r) for r in rs[:-n]);tests[u]=rs[-n:];seen[u]={r[0] for r in rs[:-n]}
counts={};sums={}
for u,i,r,t in train: counts[i]=counts.get(i,0)+1;sums[i]=sums.get(i,0)+r
ids=sorted(i for i in counts if counts[i]>=10);ix={i:k for k,i in enumerate(ids)};n=len(ids)
pos=[(u-1,ix[i]) for u,i,r,t in train if i in ix and r>=4]
X=csr_matrix((np.ones(len(pos)),tuple(zip(*pos))),shape=(max(users),n));start=time.time()
gram=(X.T@X).toarray();gram.flat[::n+1]+=80.;P=np.linalg.inv(gram);B=-P/np.diag(P)[None,:];np.fill_diagonal(B,0)
# Sparse positive top-80 outgoing relationships, identical to production.
W=np.zeros_like(B)
for i in range(n):
 js=np.argsort(B[i])[-80:];js=js[B[i,js]>0];W[i,js]=np.round(B[i,js],6)
elapsed=time.time()-start
pop=np.asarray(X.sum(axis=0)).ravel();recalls=[];base=[];ndcgs=[];base_ndcgs=[];eval_users=0;targets=0
for u in sorted(users):
 truth={ix[i] for i,r,t in tests[u] if i in ix and r>=4}
 liked=[ix[i] for uu,i,r,t in train if uu==u and i in ix and r>=4]
 if not truth or len(liked)<3:continue
 scores=W[liked].sum(axis=0);baseline=pop.copy();excluded=[ix[i] for i in seen[u] if i in ix];scores[excluded]=-np.inf;baseline[excluded]=-np.inf
 pred=np.argsort(-scores,kind='stable')[:10];bp=np.argsort(-baseline,kind='stable')[:10]
 recalls.append(len(set(pred)&truth)/len(truth));base.append(len(set(bp)&truth)/len(truth));den=sum(1/np.log2(k+2) for k in range(min(10,len(truth))))
 ndcgs.append(sum(1/np.log2(k+2) for k,j in enumerate(pred) if j in truth)/den);base_ndcgs.append(sum(1/np.log2(k+2) for k,j in enumerate(bp) if j in truth)/den);eval_users+=1;targets+=len(truth)
globalmean=np.mean([r for u,i,r,t in train]);catalog=[]
for i in ids:
 m=movies[i];catalog.append({'id':i,'title':m['title'],'genres':m['genres'].split('|'),'count':counts[i],'rating':round(sums[i]/counts[i],2),'quality':round((sums[i]+20*globalmean)/(counts[i]+20),3),'imdb':links.get(i,{}).get('imdbId','')})
model={'name':'EASE-80 sparse positive','lambda':80,'neighbors':80,'movies':catalog,'weights':[[[int(j),float(W[i,j])] for j in np.flatnonzero(W[i])] for i in range(n)]}
metrics={'dataset':'MovieLens latest-small (September 2018 snapshot)','ratings':len(rows),'users':len(users),'source_movies':len(movies),'catalog_movies':n,'train_ratings':len(train),'heldout_ratings':len(rows)-len(train),'evaluated_users':eval_users,'relevant_test_items':targets,'model_recall_at_10':round(float(np.mean(recalls)),5),'popularity_recall_at_10':round(float(np.mean(base)),5),'model_ndcg_at_10':round(float(np.mean(ndcgs)),5),'popularity_ndcg_at_10':round(float(np.mean(base_ndcgs)),5),'fit_seconds':round(elapsed,2),'split':'Latest 20% per user by rating timestamp; ties broken by movie ID. Item eligibility and popularity computed only from training data. Positive = rating >=4. At least 3 training positives and 1 eligible test positive.','evaluation':'All eligible unseen items; no sampled negatives. Evaluate sparse positive top-80 model with the complete training-positive profile. This does not evaluate new users with 1–5 picks, group fairness, genre filters or shuffle.','source_sha256':{f:hashlib.sha256((data/f).read_bytes()).hexdigest() for f in ['ratings.csv','movies.csv','links.csv']},'limitations':['Historical catalog through 2018, skewed toward English-language films and MovieLens participants.','Per-user temporal split is not a single global time cutoff; cross-user information can come from later timestamps.','Offline ratings metrics do not establish real-world satisfaction or reduced decision time.','This is a development snapshot experiment, not a standardized benchmark or state-of-the-art claim.']}
(root/'lib/model.json').write_text(json.dumps(model,separators=(',',':')));(root/'lib/metrics.json').write_text(json.dumps(metrics,indent=2));print(json.dumps(metrics,indent=2))
