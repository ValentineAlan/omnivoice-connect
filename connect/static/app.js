'use strict';
const $ = id => document.getElementById(id);
let token, version, result = null, lastCode = null, configuration = '', working = false;
const base = new URL('.', window.location.href);
async function api(path, body) {
  const response = await fetch(new URL(path, base), body === undefined ? {} : {
    method: 'POST', headers: {'Content-Type':'application/json','X-Connect-Token':token}, body:JSON.stringify(body)
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || 'The companion could not complete this request.');
  return data;
}
function download(name, text, type) {
  const url=URL.createObjectURL(new Blob([text],{type}));
  const a=document.createElement('a');a.href=url;a.download=name;a.click();
  setTimeout(()=>URL.revokeObjectURL(url),1000);
}
function reset() {
  result=null;lastCode=null;$('audio-panel').hidden=true;$('player').pause();$('player').removeAttribute('src');$('player').load();
  $('reachable').textContent='○ Server connection: not checked';$('speech').textContent='○ Speech generation: not checked';
  $('confirmed').checked=false;$('assist').textContent='○ Assist: awaiting your test';
}
for(const id of ['host','port']) $(id).addEventListener('input',reset);
$('confirmed').addEventListener('change',()=>{$('assist').textContent=$('confirmed').checked?'✓ Assist: you confirmed a spoken response':'○ Assist: awaiting your test';});
async function run(sample) {
  if(working)return;
  working=true;reset();
  for(const id of ['check','sample','host','port'])$(id).disabled=true;
  $('status').textContent=sample?'Generating your sample. A cold server may take up to 90 seconds…':'Checking the Wyoming service…';
  try {
    const job=await api(sample?'api/sample':'api/check',{host:$('host').value.trim(),port:Number($('port').value)});
    let state;
    const deadline=Date.now()+120000;
    do {
      if(Date.now()>deadline)throw new Error('The check is taking too long. Wait a moment, then try again.');
      await new Promise(resolve=>setTimeout(resolve,700));
      state=await api('api/job/'+encodeURIComponent(job.id));
    } while(state.status==='running');
    if(state.status==='error'){lastCode=state.code;throw new Error(state.message);}
    result=state.result;
    $('reachable').textContent='✓ Wyoming TTS reachable · '+result.voice_count+' voice(s): '+result.voices.join(', ');
    $('speech').textContent=result.speech?'✓ Audio generated · press play to hear it':'○ Speech generation: not checked yet';
    $('status').textContent=result.speech?'Your sample is ready. Listen below, then connect Assist.':'Your server advertises a TTS voice. Generate a sample to test speech.';
    if(result.speech){$('player').src=new URL('api/audio/'+encodeURIComponent(job.id),base);$('audio-panel').hidden=false;$('timing').textContent='First audio: '+result.first_audio_seconds+' s · sample length: '+result.audio_seconds+' s. This measures the server test, not Assist latency.';}
  } catch(error){$('status').textContent=error.message;}
  finally{working=false;for(const id of ['check','sample','host','port'])$(id).disabled=false;}
}
$('check').onclick=()=>run(false);$('sample').onclick=()=>run(true);
$('platform').onchange=()=>{const nas=$('platform').value==='truenas';$('dataset-label').hidden=!nas;$('configuration').hidden=true;$('storage-help').textContent=nas?'Create a dedicated dataset and grant UID/GID 568 write access before starting.':'Docker uses a persistent named volume for model files and voices.';};
for(const id of ['dataset','install-port'])$(id).addEventListener('input',()=>{$('configuration').hidden=true;});
$('generate').onclick=async()=>{
  $('generate-status').textContent='';$('configuration').hidden=true;
  try{const data=await api('api/compose',{port:Number($('install-port').value),platform:$('platform').value,path:$('dataset').value});configuration=data.compose;$('compose').textContent=configuration;$('configuration').hidden=false;$('port').value=$('install-port').value;reset();}
  catch(error){$('generate-status').textContent=error.message;}
};
$('download-compose').onclick=()=>download('compose.yaml',configuration,'text/yaml');
$('diagnostics').onclick=()=>download('omnivoice-connect-diagnostics.json',JSON.stringify({companion_version:version,server_reachable:result?.reachable??false,speech_generated:result?.speech??false,assist_user_confirmed:$('confirmed').checked,error_code:lastCode,first_audio_seconds:result?.first_audio_seconds??null},null,2),'application/json');
for(const id of ['check','sample','generate'])$(id).disabled=true;
api('api/state').then(state=>{token=state.token;version=state.version;$('host').value=state.settings.host;$('port').value=state.settings.port;for(const id of ['check','sample','generate'])$(id).disabled=false;}).catch(()=>{$('status').textContent='Could not load the companion. Reopen it through Home Assistant.';});
