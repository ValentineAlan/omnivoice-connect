import io
import json
import pathlib
import socket
import sys
import threading
import time
import unittest
import urllib.error
import urllib.request
import uuid
import wave
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'connect'))
import protocol
import server


def frame(kind, data=None, payload=b'', separate=False):
    header = {'type': kind, 'payload_length': len(payload)}
    extra = b''
    if separate:
        extra = json.dumps(data or {}).encode()
        header['data_length'] = len(extra)
    else:
        header['data'] = data or {}
    return json.dumps(header).encode() + b'\n' + extra + payload


INFO = frame('info', {'tts': [{'name':'omnivoice','voices':[{'name':'example'}]}]}, separate=True)


class FakeSocket:
    def __init__(self, data): self.data = io.BytesIO(data); self.sent = b''
    def recv(self, n): return self.data.read(min(n, 7))
    def sendall(self, data): self.sent += data
    def settimeout(self, timeout): pass
    def connect(self, address): pass
    def close(self): pass
    def __enter__(self): return self
    def __exit__(self, *args): pass


class ProtocolTests(unittest.TestCase):
    def invoke(self, data, sample=False):
        sock = FakeSocket(data)
        with patch.object(protocol, 'resolve_target', return_value=[(socket.AF_INET,socket.SOCK_STREAM,0,('192.168.1.50',10200))]), patch.object(protocol.socket,'socket',return_value=sock):
            return protocol.check('192.168.1.50',10200,sample)

    def test_discovery_and_separate_json(self):
        result, audio = self.invoke(INFO)
        self.assertTrue(result['reachable']); self.assertFalse(result['speech'])
        self.assertEqual(result['assist'],'not_verified'); self.assertIsNone(audio)

    def test_sample_wave_and_partial_reads(self):
        pcm = b'\x01\x00' * 240
        result, audio = self.invoke(INFO+frame('audio-start',{'rate':24000,'width':2,'channels':1})+frame('audio-chunk',payload=pcm)+frame('audio-stop'),True)
        self.assertTrue(result['speech'])
        with wave.open(io.BytesIO(audio),'rb') as wav:
            self.assertEqual(wav.getframerate(),24000);self.assertEqual(wav.readframes(240),pcm)

    def test_non_tts_and_wrong_service(self):
        for data in [frame('info',{'tts':[]}),frame('pong')]:
            with self.assertRaises(protocol.CheckError): self.invoke(data)

    def test_truncated_audio(self):
        with self.assertRaises(protocol.CheckError):
            self.invoke(INFO+frame('audio-start',{'rate':24000,'width':2,'channels':1})+b'{"type":"audio-chunk","payload_length":8}\nxx',True)

    def test_audio_requires_start_and_non_silence(self):
        for tail in [frame('audio-chunk',payload=b'xx'),frame('audio-start',{'rate':24000,'width':2,'channels':1})+frame('audio-chunk',payload=b'\x00\x00')+frame('audio-stop')]:
            with self.assertRaises(protocol.CheckError): self.invoke(INFO+tail,True)

    def test_invalid_frame_lengths(self):
        for length in [-1, True, 1048577, '100']:
            with self.assertRaises(protocol.CheckError):
                protocol.Wire(FakeSocket(json.dumps({'type':'info','payload_length':length}).encode()+b'\n'),1).event()

    def test_invalid_json_shapes(self):
        for raw in [b'[]\n',b'{"type":"info","data":[]}\n',b'garbage\n']:
            with self.assertRaises(protocol.CheckError): protocol.Wire(FakeSocket(raw),1).event()

    def test_deadline(self):
        with self.assertRaises(protocol.CheckError): protocol.Wire(FakeSocket(INFO),-1).event()

    def test_target_input_validation(self):
        for host,port in [('http://host',10200),('host/path',10200),('host',True),('host',65536),('',10200)]:
            with self.assertRaises(protocol.CheckError):protocol.validate_target(host,port)

    def test_private_address_policy_and_rebinding(self):
        for ip in ['127.0.0.1','169.254.169.254','172.30.32.1','8.8.8.8','::1','::ffff:127.0.0.1']:
            with patch.object(protocol.socket,'getaddrinfo',return_value=[(socket.AF_INET,socket.SOCK_STREAM,0,'',(ip,10200))]):
                with self.assertRaises(protocol.CheckError):protocol.resolve_target('server',10200)
        for ip in ['192.168.1.50','10.0.0.2','fd00::123']:
            with patch.object(protocol.socket,'getaddrinfo',return_value=[(socket.AF_INET,socket.SOCK_STREAM,0,'',(ip,10200))]):
                self.assertEqual(protocol.resolve_target('server',10200)[0][3][0],ip)

    def test_total_audio_limit(self):
        with patch.object(protocol,'MAX_AUDIO',2),self.assertRaises(protocol.CheckError):
            self.invoke(INFO+frame('audio-start',{'rate':24000,'width':2,'channels':1})+frame('audio-chunk',payload=b'xxxx'),True)


class AppTests(unittest.TestCase):
    def setUp(self):
        self.folder = pathlib.Path('data').resolve() / ('test-'+uuid.uuid4().hex)
        self.folder.mkdir(parents=True,mode=0o755)
        self.http = server.make_server(('127.0.0.1',0),self.folder,dev=True)
        self.thread = threading.Thread(target=self.http.serve_forever,daemon=True);self.thread.start()
        self.base = 'http://127.0.0.1:'+str(self.http.server_port)

    def tearDown(self):
        self.http.shutdown();self.http.server_close();self.thread.join()
        for p in self.folder.iterdir():p.unlink()
        self.folder.rmdir()

    def request(self,path,body=None,token=True):
        headers={'Content-Type':'application/json'}
        if token:headers['X-Connect-Token']=self.http.state.token
        req=urllib.request.Request(self.base+path,data=json.dumps(body).encode() if body is not None else None,headers=headers)
        return urllib.request.urlopen(req,timeout=3)

    def test_ingress_denies_nonproxy(self):
        self.http.allowed_peer='172.30.32.2'
        with self.assertRaises(urllib.error.HTTPError) as error:self.request('/')
        self.assertEqual(error.exception.code,403)

    def test_csrf_denies_missing_token(self):
        with self.assertRaises(urllib.error.HTTPError) as error:self.request('/api/check',{'host':'host','port':10200},False)
        self.assertEqual(error.exception.code,403)

    def test_page_and_relative_assets(self):
        with self.request('/') as response:
            page=response.read().decode();self.assertIn('src="app.js"',page)
            self.assertIn("object-src 'none'",response.headers['Content-Security-Policy'])
        with self.request('/app.js') as response:self.assertIn(b"new URL('.', window.location.href)",response.read())

    def test_compose_no_interpolation_or_path_injection(self):
        for path in ['/mnt/pool/data\nother','/mnt/$SECRET','/mnt/data:ro','relative']:
            with self.assertRaises(ValueError):server.compose(10200,'truenas',path)
        text=server.compose(10201,'truenas','/mnt/pool/voice data')
        self.assertIn('"10201:10200"',text);self.assertIn('"/mnt/pool/voice data:/data"',text)
        self.assertIn('omnivoice_data:',server.compose(10200,'docker',''))

    def test_state_persists_and_job_results(self):
        with patch.object(server,'check',return_value=({'reachable':True,'speech':False,'voices':['private_voice']},None)):
            with self.request('/api/check',{'host':'192.168.1.50','port':10200}) as response:job=json.load(response)['id']
            for _ in range(100):
                with self.request('/api/job/'+job) as response:state=json.load(response)
                if state['status']!='running':break
                time.sleep(.01)
            self.assertEqual(state['status'],'done')
        restored=server.State(self.folder)
        self.assertEqual(restored.settings,{'host':'192.168.1.50','port':10200})
        self.assertIsNone(restored.job)

    def test_busy_and_expiry(self):
        self.http.state.job={'id':'test','created':time.monotonic(),'status':'running'}
        with self.assertRaises(protocol.CheckError):self.http.state.start('host',10200,False)
        self.http.state.job['created']-=601
        with self.assertRaises(KeyError):self.http.state.snapshot('test')

    def test_diagnostics_excludes_private_fields(self):
        js=(server.STATIC/'app.js').read_text()
        export=js.split("$('diagnostics').onclick=")[1].split("for(const id")[0]
        for private in ['settings','host','voices','token','audio.wav']:self.assertNotIn(private,export)


if __name__=='__main__':unittest.main()
