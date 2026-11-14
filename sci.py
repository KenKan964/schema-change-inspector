"""Sound sufficient inclusion proof + validated witnesses for a small JSON Schema subset."""
import argparse,hashlib,itertools,json,sys
from pathlib import Path
TYPES={'null','boolean','integer','number','string','array','object'}
SUPPORTED={'$schema','title','description','type','properties','required','enum','additionalProperties'}
DIALECT='https://json-schema.org/draft/2020-12/schema'
def equal(a,b):
 if isinstance(a,bool) or isinstance(b,bool):return type(a)==type(b) and a==b
 if isinstance(a,(int,float)) and isinstance(b,(int,float)):return a==b
 if type(a)!=type(b):return False
 if isinstance(a,list):return len(a)==len(b) and all(equal(x,y) for x,y in zip(a,b))
 if isinstance(a,dict):return a.keys()==b.keys() and all(equal(a[k],b[k]) for k in a)
 return a==b
def ptr(path,key):return path+'/'+str(key).replace('~','~0').replace('/','~1')
def validate_schema(s,path='',depth=0):
 if depth>12:raise ValueError('schema_depth')
 if type(s) is bool:return []
 if not isinstance(s,dict):raise ValueError('schema_must_be_object_or_boolean')
 unknown=[]
 for k in s:
  if k not in SUPPORTED:unknown.append(ptr(path,k))
 if '$schema' in s and s['$schema']!=DIALECT:unknown.append(ptr(path,'$schema'))
 if 'type' in s:
  t=s['type'];ts=t if isinstance(t,list) else [t]
  if not ts or not all(isinstance(x,str) and x in TYPES for x in ts) or len(ts)!=len(set(ts)):raise ValueError('invalid_type')
 for k in ('title','description'):
  if k in s and not isinstance(s[k],str):raise ValueError('annotation_type')
 if 'required' in s and (not isinstance(s['required'],list) or not all(isinstance(x,str) for x in s['required']) or len(s['required'])!=len(set(s['required']))):raise ValueError('required')
 if 'enum' in s:
  e=s['enum']
  if not isinstance(e,list) or not e or any(equal(x,y) for i,x in enumerate(e) for y in e[:i]):raise ValueError('enum')
 if 'additionalProperties' in s and type(s['additionalProperties']) is not bool:
  if not isinstance(s['additionalProperties'],dict):raise ValueError('additionalProperties')
  unknown.append(ptr(path,'additionalProperties'))
 if 'properties' in s:
  if not isinstance(s['properties'],dict):raise ValueError('properties')
  if len(s['properties'])>16:raise ValueError('property_limit')
  for k,v in s['properties'].items():unknown+=validate_schema(v,ptr(ptr(path,'properties'),k),depth+1)
 return unknown

def kind(v):
 if v is None:return 'null'
 if isinstance(v,bool):return 'boolean'
 if isinstance(v,(int,float)):return 'integer' if v==int(v) else 'number'
 return {str:'string',list:'array',dict:'object'}[type(v)]
def types(s):
 t=s.get('type',list(TYPES));t=set(t if isinstance(t,list) else [t]);return t|({'integer'} if 'number' in t else set())
def valid(s,v):
 if type(s) is bool:return s
 if kind(v) not in types(s):return False
 if 'enum' in s and not any(equal(v,x) for x in s['enum']):return False
 if isinstance(v,dict):
  if not set(s.get('required',[]))<=v.keys():return False
  for k,x in v.items():
   if not valid(s.get('properties',{}).get(k,s.get('additionalProperties',True)),x):return False
 return True

def subset(a,b):
 if a is False or b is True:return True
 if b is False:return False
 if a is True:a={}
 if 'enum' in a:return all(not valid(a,x) or valid(b,x) for x in a['enum'])
 if 'enum' in b:return False
 if not types(a)<=types(b):return False
 if 'object' in types(a):
  if not set(b.get('required',[]))<=set(a.get('required',[])):return False
  ap=a.get('properties',{});bp=b.get('properties',{});aa=a.get('additionalProperties',True);ba=b.get('additionalProperties',True)
  if not subset(aa,ba):return False
  for k in ap.keys()|bp.keys():
   if not subset(ap.get(k,aa),bp.get(k,ba)):return False
 return True

def candidates(a,b,depth=0,fuel=None):
 if fuel is None:fuel=[2000]
 fuel[0]-=1
 vals=[None,False,True,0,1,-1,1.5,'','x',[],[None],{}]
 for s in (a,b):
  if isinstance(s,dict):vals+=s.get('enum',[])
 if fuel[0]>0 and depth<5 and any(isinstance(s,dict) for s in (a,b)):
  sa=a if isinstance(a,dict) else {};sb=b if isinstance(b,dict) else {};ap=sa.get('properties',{});bp=sb.get('properties',{})
  names=sorted(set(ap)|set(bp)|set(sa.get('required',[]))|set(sb.get('required',[])))
  base={}
  for k in names:
   choices=candidates(ap.get(k,True),bp.get(k,True),depth+1,fuel)[:40]
   base[k]=next((x for x in choices if valid(ap.get(k,sa.get('additionalProperties',True)),x)),None)
  vals+=[base,{k:base[k] for k in sa.get('required',[])}]
  fresh='__extra__'
  while fresh in names:fresh+='x'
  vals.append(dict(base,**{fresh:0}))
  for k in names:
   vals.append({n:x for n,x in base.items() if n!=k})
   for x in candidates(ap.get(k,True),bp.get(k,True),depth+1,fuel)[:30]:vals.append(dict(base,**{k:x}))
 return vals[:1000]

def diff(a,b,path=''):
 if equal(a,b):return []
 if isinstance(a,dict) and isinstance(b,dict):
  out=[]
  for k in sorted(a.keys()|b.keys()):
   if k in a and k in b:out+=diff(a[k],b[k],ptr(path,k))
   else:out.append({'pointer':ptr(path,k),'old_present':k in a,'new_present':k in b,'old':a.get(k),'new':b.get(k)})
  return out
 return [{'pointer':path,'old_present':True,'new_present':True,'old':a,'new':b}]
def compare(old,new):
 r={'schema_version':'sci-report-v1','rule_version':'sci-rules-v1','compatibility':'L(old) subset L(new): input acceptance only','classification':'INVALID_SCHEMA','findings':[],'counterexample':None,'counterexample_available':False}
 try:unknown=validate_schema(old)+validate_schema(new)
 except (ValueError,TypeError,RecursionError):r['findings']=[{'pointer':'','rule_id':'INVALID_SCHEMA','old':old,'new':new,'counterexample':None,'reason':'schema shape/limit invalid'}];return r
 def at(obj,p):
  try:
   for k in p.split('/')[1:]:obj=obj[k.replace('~1','/').replace('~0','~')]
   return obj
  except (KeyError,TypeError):return None
 changes=diff(old,new)
 if unknown:
  r['classification']='UNKNOWN';r['findings']=[{'pointer':p,'rule_id':'UNSUPPORTED_KEYWORD','old':at(old,p),'new':at(new,p),'counterexample':None,'reason':'unsupported semantics; no inclusion claim'} for p in sorted(set(unknown))];return r
 if subset(old,new):label='NON_BREAKING';rule='SUBSET_SUFFICIENT_PROOF'
 else:
  witness=next((v for v in candidates(old,new) if valid(old,v) and not valid(new,v)),None)
  # None itself is a legitimate counterexample; use explicit independent membership test.
  found=any(valid(old,v) and not valid(new,v) for v in candidates(old,new))
  if found:r['counterexample']=witness;r['counterexample_available']=True;label='BREAKING';rule='VALIDATED_COUNTEREXAMPLE'
  else:label='UNKNOWN';rule='INCLUSION_UNPROVEN'
 r['classification']=label
 r['findings']=[dict(x,rule_id=rule,counterexample=r['counterexample'],counterexample_available=r['counterexample_available'],reason='global schema decision; pointer identifies changed input fragment') for x in changes] or [{'pointer':'','old':old,'new':new,'rule_id':rule,'counterexample':None,'counterexample_available':False}]
 return r

class UnsupportedNumber(ValueError):pass

def exact_number(token):
 from decimal import Decimal
 import math
 if len(token)>256:raise UnsupportedNumber('numeric token exceeds 256 characters')
 parts=token.lower().split('e')
 if len(parts)==2:
  exponent=parts[1].lstrip('+-')
  if len(exponent)>4 or abs(int(parts[1]))>400:raise UnsupportedNumber('decimal exponent magnitude exceeds 400')
 value=Decimal(token)
 rounded=float(token)
 if not math.isfinite(rounded) or Decimal.from_float(rounded)!=value:
  raise UnsupportedNumber('decimal not exactly representable in binary64; precision would be lost')
 return rounded

def exact_integer(token):
 if len(token.lstrip('-'))>128:raise UnsupportedNumber('integer exceeds 128 decimal digits')
 return int(token)

def parse(path):
 raw=Path(path).read_bytes()
 if len(raw)>65536:raise ValueError('size_limit')
 text=raw.decode('utf-8');depth=0;quoted=False;esc=False
 for c in text:
  if quoted:
   if esc:esc=False
   elif c=='\\':esc=True
   elif c=='"':quoted=False
  elif c=='"':quoted=True
  elif c in '{[':
   depth+=1
   if depth>32:raise ValueError('nest_limit')
  elif c in '}]':depth-=1
 def pairs(items):
  d={}
  for k,v in items:
   if k in d:raise ValueError('duplicate_key')
   d[k]=v
  return d
 return json.loads(text,object_pairs_hook=pairs,parse_float=exact_number,parse_int=exact_integer,parse_constant=lambda x:(_ for _ in ()).throw(ValueError('nonfinite')))
def exit_code(r,unknown='fail'):
 return {'NON_BREAKING':0,'BREAKING':1,'INVALID_SCHEMA':2,'UNKNOWN':2 if unknown=='fail' else 0}[r['classification']]
class Parser(argparse.ArgumentParser):
 def error(self,message):raise ValueError('arguments')
def main():
 try:
  p=Parser();p.add_argument('--old',required=True);p.add_argument('--new',required=True);p.add_argument('--out',required=True);p.add_argument('--unknown',choices=['fail','allow'],default='fail');a=p.parse_args()
  try:r=compare(parse(a.old),parse(a.new))
  except UnsupportedNumber as e:
   r={'schema_version':'sci-report-v1','rule_version':'sci-rules-v1','classification':'UNKNOWN','findings':[{'pointer':'','rule_id':'UNSUPPORTED_NUMERIC_PRECISION','reason':str(e),'old':None,'new':None,'counterexample':None,'counterexample_available':False}],'counterexample':None,'counterexample_available':False}
  r['unknown_policy']=a.unknown;r['exit_code']=exit_code(r,a.unknown)
  out=Path(a.out);out.mkdir(mode=0o700);(out/'report.json').write_text(json.dumps(r,ensure_ascii=True,indent=2)+'\n',encoding='utf-8')
 except (OSError,ValueError,TypeError,RecursionError):r={'classification':'INVALID_SCHEMA','exit_code':2,'findings':[{'pointer':'','rule_id':'INPUT_OR_OUTPUT_ERROR','counterexample':None}]}
 print(json.dumps(r,ensure_ascii=True));return r['exit_code']
if __name__=='__main__':sys.exit(main())
