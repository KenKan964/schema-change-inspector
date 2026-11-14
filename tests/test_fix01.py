import hashlib,json,os,subprocess,sys,tempfile,unittest
from pathlib import Path
import sci
from test_acceptance import preserve
ROOT=Path(sci.__file__).parent
class Fix01(unittest.TestCase):
 def conflict(self,kind):
  with tempfile.TemporaryDirectory() as td:
   base=Path(td);d=base/'evidence';d.mkdir();marker=base/'marker';marker.write_bytes(b'SCI FIX01 synthetic marker');target=d/'required.json'
   if kind=='existing':target.write_bytes(marker.read_bytes());protected=target
   elif kind=='file_symlink':
    try:target.symlink_to(marker)
    except OSError:self.skipTest('symlink unavailable')
    protected=marker
   else:
    d.rmdir();(base/'real').mkdir()
    try:d.symlink_to(base/'real',target_is_directory=True)
    except OSError:self.skipTest('symlink unavailable')
    protected=marker
   before=hashlib.sha256(protected.read_bytes()).hexdigest();r=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-p','test_acceptance.py','-v'],cwd=ROOT,env=dict(os.environ,SCI_EVIDENCE=str(d)),capture_output=True,text=True)
   self.assertNotEqual(r.returncode,0);self.assertEqual(hashlib.sha256(protected.read_bytes()).hexdigest(),before)
   if kind=='directory_symlink':self.assertEqual(list((base/'real').iterdir()),[])
   preserve('FIX01_'+kind,{'exit_code':r.returncode,'before_sha256':before,'after_sha256':hashlib.sha256(protected.read_bytes()).hexdigest(),'stdout':r.stdout,'stderr':r.stderr})
 def test_existing(self):self.conflict('existing')
 def test_file_symlink(self):self.conflict('file_symlink')
 def test_directory_symlink(self):self.conflict('directory_symlink')

def numeric_test(name,old,new,classification='UNKNOWN',allow=False):
 def test(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td);(p/'old').write_text(old);(p/'new').write_text(new);cmd=[sys.executable,str(ROOT/'sci.py'),'--old',str(p/'old'),'--new',str(p/'new'),'--out',str(p/'out')]
   if allow:cmd+=['--unknown','allow']
   r=subprocess.run(cmd,capture_output=True,text=True);data=json.loads(r.stdout);self.assertEqual(data['classification'],classification,data);self.assertEqual(r.returncode,0 if allow or classification=='NON_BREAKING' else 2 if classification=='UNKNOWN' else 1)
   if classification=='UNKNOWN':self.assertFalse(data['counterexample_available']);self.assertEqual(data['findings'][0]['rule_id'],'UNSUPPORTED_NUMERIC_PRECISION')
   self.assertEqual((p/'old').read_text(),old);preserve('FIX01_'+name,data)
 return test
for name,a,b,label,allow in [
 ('NP01','{"enum":[1.0000000000000001]}','{"enum":[1]}','UNKNOWN',False),
 ('NP02','{"enum":[1.0000000000000001]}','{"type":"integer"}','UNKNOWN',False),
 ('NP03','{"enum":[9007199254740993e0]}','{"enum":[9007199254740992]}','UNKNOWN',False),
 ('NP04','{"enum":[1e-400]}','{"enum":[0]}','UNKNOWN',False),
 ('allow','{"enum":[0.1]}','{}','UNKNOWN',True),
 ('one','{"enum":[1]}','{"enum":[1.0]}','NON_BREAKING',False),
 ('bool','{"enum":[true]}','{"enum":[1.0]}','BREAKING',False),
 ('exact_fraction','{"enum":[1.5]}','{"type":"integer"}','BREAKING',False),
 ('huge_exponent','{"enum":[1e99999]}','{}','UNKNOWN',False),
 ('huge_integer','{"enum":['+'1'*129+']}','{}','UNKNOWN',False),
 ('nested','{"properties":{"x":{"enum":[0.1]}}}','{}','UNKNOWN',False)]:setattr(Fix01,'test_'+name,numeric_test(name,a,b,label,allow))
