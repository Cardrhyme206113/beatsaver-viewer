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

self.addEventListener('install',()=>self.skipWaiting());
self.addEventListener('activate',event=>event.waitUntil(self.clients.claim()));
self.addEventListener('fetch',event=>{
  const url=new URL(event.request.url);
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
