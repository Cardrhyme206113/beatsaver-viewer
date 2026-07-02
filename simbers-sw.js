const CACHE_NAME='simplified-sabers-light-viewer-v1';
const INFO_NAME=[73,110,102,111,46,100,97,116];

function normalizeGeneratedZip(buffer){
  const bytes=new Uint8Array(buffer);
  for(let i=0;i<=bytes.length-INFO_NAME.length;i++){
    let matches=true;
    for(let j=0;j<INFO_NAME.length;j++){
      if(bytes[i+j]!==INFO_NAME[j]){matches=false;break;}
    }
    if(matches)bytes[i]=105;
  }
  return bytes;
}

function patchViewerHtml(html){
  html=html.replace('<title>BeatSaver Viewer</title>','<title>Simplified Sabers Viewer</title>');
  if(!html.includes('data-mode="90Degree"')){
    html=html.replace(
      '<li data-mode="OneSaber">OneSaber</li>',
      '<li data-mode="OneSaber">OneSaber</li><li data-mode="90Degree">90Degree</li><li data-mode="360Degree">360Degree</li>'
    );
  }
  html=html.replace(
    'bind__animation__scale="enabled: challenge.isLoading || !hasReceivedUserGesture && !challenge.hasLoadError"',
    'bind__animation__scale="enabled: challenge.isLoading || isSongBufferProcessing"'
  );
  html=html.replace(
    'bind__visible="challenge.isLoading || !hasReceivedUserGesture || challenge.hasLoadError"',
    'bind__visible="challenge.isLoading || isSongBufferProcessing || challenge.hasLoadError"'
  );
  const css='<style>#logo,.github-corner,#loadingGestureButton,#search,#subscribeForm{display:none!important}#controls{max-width:calc(100vw - 12px)!important;width:760px!important;margin-bottom:6px!important;border-radius:5px!important;background:rgba(4,4,7,.88)!important;border:1px solid rgba(255,255,255,.12)!important;box-sizing:border-box!important}@media(max-width:720px){#controls{width:calc(100vw - 10px)!important;flex-wrap:wrap!important;gap:5px!important;justify-content:center!important;padding:7px!important}#timeline{flex:1 1 110px!important;min-width:80px!important}#songInfoContainer{flex:1 1 100%!important}#songInfoSelect{position:static!important;margin-left:auto!important}}</style>';
  return html.replace('</head>',css+'</head>');
}

self.addEventListener('install',()=>self.skipWaiting());
self.addEventListener('activate',event=>event.waitUntil(self.clients.claim()));
self.addEventListener('fetch',event=>{
  const url=new URL(event.request.url);

  if(url.pathname.endsWith('/index.html')&&url.searchParams.get('simbers')==='1'){
    event.respondWith((async()=>{
      const response=await fetch(event.request);
      const html=patchViewerHtml(await response.text());
      return new Response(html,{status:response.status,statusText:response.statusText,headers:{'Content-Type':'text/html; charset=utf-8','Cache-Control':'no-store'}});
    })());
    return;
  }

  if(!url.pathname.endsWith('/generated-map.zip'))return;
  event.respondWith((async()=>{
    const cache=await caches.open(CACHE_NAME);
    const cached=await cache.match(event.request,{ignoreMethod:true});
    if(cached){
      const bytes=normalizeGeneratedZip(await cached.arrayBuffer());
      return new Response(bytes,{status:200,headers:{'Content-Type':'application/zip','Cache-Control':'no-store'}});
    }
    return new Response('Generated map is unavailable.',{status:404,headers:{'Content-Type':'text/plain; charset=utf-8','Cache-Control':'no-store'}});
  })());
});
