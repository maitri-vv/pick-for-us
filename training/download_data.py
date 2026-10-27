"""Download the exact research snapshot; preserve original GroupLens terms."""
import argparse,hashlib,io,json,pathlib,urllib.request,zipfile
p=argparse.ArgumentParser();p.add_argument('--destination',default='data/ml-latest-small');p.add_argument('--mirror',action='store_true',help='Use documented GitHub mirror if the original host is unavailable');a=p.parse_args()
root=pathlib.Path(__file__).resolve().parents[1];expected=json.loads((root/'lib/metrics.json').read_text())['source_sha256'];out=pathlib.Path(a.destination);out.mkdir(parents=True,exist_ok=True)
files=['ratings.csv','movies.csv','links.csv','README.txt']
if a.mirror:
 blobs={name:urllib.request.urlopen('https://raw.githubusercontent.com/smanihwr/ml-latest-small/master/'+name,timeout=60).read() for name in files}
else:
 raw=urllib.request.urlopen('https://files.grouplens.org/datasets/movielens/ml-latest-small.zip',timeout=60).read()
 with zipfile.ZipFile(io.BytesIO(raw)) as z:blobs={name:z.read('ml-latest-small/'+name) for name in files}
for name,digest in expected.items():
 if hashlib.sha256(blobs[name]).hexdigest()!=digest:raise SystemExit('Snapshot hash mismatch: '+name+'. Do not silently evaluate a different dataset.')
for name,blob in blobs.items():(out/name).write_bytes(blob)
print('Verified snapshot saved to',out,'Read README.txt for the GroupLens research-use terms.')
