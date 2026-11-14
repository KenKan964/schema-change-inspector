import json,os,tempfile,subprocess,sys,unittest
from pathlib import Path
import sci
def preserve(name,data):
 if not os.environ.get('SCI_EVIDENCE'):return
 dest=Path(os.path.abspath(os.environ['SCI_EVIDENCE']))
 if any(x.is_symlink() for x in [dest,*dest.parents]):raise ValueError('symlink evidence path')
 dest.mkdir(parents=True,exist_ok=True)
 with (dest/(name+'.json')).open('x',encoding='utf-8') as f:json.dump(data,f,indent=2)

# Independent subset evaluator for generated counterexamples, not sci.valid.
def accepts(s,x):
 if type(s) is bool:return s
 kind='null' if x is None else 'boolean' if type(x) is bool else 'integer' if type(x) is int or type(x) is float and x.is_integer() else 'number' if type(x) is float else 'string' if type(x) is str else 'object' if type(x) is dict else 'array'
 ts=s.get('type',list(sci.TYPES));ts=[ts] if isinstance(ts,str) else ts
 if kind not in ts and not(kind=='integer' and 'number' in ts):return False
 if 'enum' in s and not any(type(x)==type(v) and x==v or type(x) in (int,float) and type(v) in (int,float) and x==v for v in s['enum']):return False
 if isinstance(x,dict):
  if any(k not in x for k in s.get('required',[])):return False
  return all(accepts(s.get('properties',{}).get(k,s.get('additionalProperties',True)),v) for k,v in x.items())
 return True
B='BREAKING';N='NON_BREAKING';U='UNKNOWN';I='INVALID_SCHEMA'
CASES=[('required',{'type':'object'},{'type':'object','required':['x']},B),('remove_required',{'type':'object','required':['x']},{'type':'object'},N),('enum_shrink',{'enum':['a','b']},{'enum':['a']},B),('enum_expand',{'enum':['a']},{'enum':['a','b']},N),('type_widen',{'type':'integer'},{'type':'number'},N),('type_narrow',{'type':'number'},{'type':'integer'},B),('union',{'type':'string'},{'type':['string','null']},N),('union_narrow',{'type':['string','null']},{'type':'string'},B),('additional',{'type':'object'},{'type':'object','additionalProperties':False},B),('allow_extra',{'type':'object','additionalProperties':False},{'type':'object'},N),('identical',{'type':'string'},{'type':'string'},N),('order',{'type':['null','string']},{'type':['string','null']},N),('nested',{'type':'object','properties':{'x':{'type':'number'}}},{'type':'object','properties':{'x':{'type':'integer'}}},B),('array',{'type':'array'},{'type':'array'},N),('items',{'type':'array','items':{'type':'string'}},{'type':'array'},U),('oneof',{'oneOf':[]},{},U),('allof',{'allOf':[]},{},U),('anyof',{'anyOf':[]},{},U),('ref',{'$ref':'https://invalid.example/schema'},{},U),('dynamic',{}, {'$dynamicRef':'x'},U),('pattern',{'pattern':'x'},{},U),('invalidtype',{'type':'wat'},{},I),('invalidrequired',{'required':'x'},{},I),('invalidenum',{'enum':[]},{},I),('enumduplicates',{'enum':[1,1.0]},{},I),('falseold',False,False,N),('falsenew',{},False,B),('true',{},True,N),('null',{'type':'null'},{'type':'string'},B),('annotations',{'title':'a'},{'title':'b'},N),('newprop',{'type':'object'},{'type':'object','properties':{'x':{'type':'string'}}},B),('enumfalse',{'enum':[True]},{'enum':[1]},B),('badprops',{'properties':[]},{},I),('badadditional',{'additionalProperties':5},{},I),('dialect',{'$schema':'https://invalid.example/dialect'},{},U),('no_fake_witness',False,{'type':'string'},N)]
class Acceptance(unittest.TestCase):pass
def make(name,a,b,label):
 def test(self):
  r=sci.compare(a,b);self.assertEqual(r['classification'],label,r);self.assertEqual(r,sci.compare(a,b))
  if r['counterexample_available']:self.assertTrue(accepts(a,r['counterexample']));self.assertFalse(accepts(b,r['counterexample']))
  if label==B:self.assertTrue(r['counterexample_available'])
  preserve(name,{'expected':label,'report':r})
 return test
for n,a,b,l in CASES:setattr(Acceptance,'test_'+n,make(n,a,b,l))
class Safety(unittest.TestCase):
 def test_cli_inputs_unchanged_and_output_exclusive(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td);(p/'a').write_text('{"$ref":"https://invalid.example/x"}');(p/'b').write_text('{}');cmd=[sys.executable,sci.__file__,'--old',str(p/'a'),'--new',str(p/'b'),'--out',str(p/'out')]
   before=(p/'a').read_bytes();r=subprocess.run(cmd,capture_output=True,text=True);self.assertEqual(r.returncode,2);self.assertEqual(json.loads(r.stdout)['classification'],U)
   saved=(p/'out/report.json').read_bytes();r=subprocess.run(cmd,capture_output=True,text=True);self.assertEqual(r.returncode,2);self.assertEqual((p/'out/report.json').read_bytes(),saved);self.assertEqual((p/'a').read_bytes(),before)
 def test_unknown_allow_explicit(self):self.assertEqual(sci.exit_code({'classification':U},'allow'),0);self.assertEqual(sci.exit_code({'classification':U}),2)
 def test_limits(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'x'
   for raw in [' '*65537,'['*33+'0'+']'*33,'{"x":1,"x":2}','{"x":NaN}']:
    p.write_text(raw)
    with self.assertRaises(ValueError):sci.parse(p)
