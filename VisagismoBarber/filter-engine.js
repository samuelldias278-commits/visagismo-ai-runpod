'use strict';

const filterEngine=(()=>{
 const filters=[
  {id:'buzz',name:'Buzz Cut',src:'assets/filters/buzz-square-v2.png',width:1.58,y:-.02},
  {id:'french-crop',name:'French Crop',src:'assets/filters/french-crop-square-v2.png',width:1.72,y:.015},
  {id:'textured-crop',name:'Textured Crop',src:'assets/filters/textured-crop-square-v2.png',width:1.78,y:-.015},
  {id:'side-part',name:'Side Part clássico',src:'assets/filters/side-part-square-v2.png',width:1.82,y:-.035},
  {id:'low-fade',name:'Low Fade',src:'assets/filters/low-fade-square-v2.png',width:1.68,y:-.005},
 ];
 const cache=new Map();
 function load(src){if(!cache.has(src))cache.set(src,new Promise((resolve,reject)=>{const img=new Image();img.onload=()=>resolve(img);img.onerror=()=>reject(new Error(`Não foi possível abrir ${src}`));img.src=src}));return cache.get(src)}
 function clamp(value,min,max){return Math.max(min,Math.min(max,Number(value)))}
 function sampleHairColor(photo,mask){
  const size=160,c=document.createElement('canvas');c.width=size;c.height=size;const cctx=c.getContext('2d',{willReadFrequently:true});
  cctx.drawImage(photo,0,0,size,size);const pixels=cctx.getImageData(0,0,size,size).data;
  cctx.clearRect(0,0,size,size);cctx.drawImage(mask,0,0,size,size);const alpha=cctx.getImageData(0,0,size,size).data;
  const values=[];for(let i=0;i<pixels.length;i+=16){if(alpha[i+3]>100){const r=pixels[i],g=pixels[i+1],b=pixels[i+2],light=(r+g+b)/3;if(light>12&&light<235)values.push([r,g,b])}}
  if(values.length<20)return{rgb:[58,43,36],css:'rgb(58 43 36)',confidence:'baixa'};
  values.sort((a,b)=>(a[0]+a[1]+a[2])-(b[0]+b[1]+b[2]));const middle=values.slice(Math.floor(values.length*.2),Math.ceil(values.length*.8));
  const rgb=[0,1,2].map(channel=>Math.round(middle.reduce((sum,p)=>sum+p[channel],0)/middle.length));return{rgb,css:`rgb(${rgb.join(' ')})`,confidence:values.length>150?'alta':'média'}
 }
 async function render(canvas,{photoDataUrl,filterId,anchors,scale=1,offsetY=0,opacity=.82,asymmetryCorrection=.6,showOriginal=false,receding='nenhuma',allowedHairMaskDataUrl=null,hairMaskDataUrl=null,hairMetrics=null,realism='conservador',preserveColor=true,feather=8,originalTexture=.22}){
  const photo=await load(photoDataUrl),filter=filters.find(x=>x.id===filterId)||filters[0];
  canvas.width=photo.naturalWidth;canvas.height=photo.naturalHeight;
  const ctx=canvas.getContext('2d');ctx.clearRect(0,0,canvas.width,canvas.height);ctx.drawImage(photo,0,0);
  if(showOriginal)return{filterId:filter.id,mode:'original-comparison'};
  const overlay=await load(filter.src);
  const left=anchors?.leftTemple,right=anchors?.rightTemple,forehead=anchors?.forehead;
  const templeWidth=left&&right?Math.hypot((right.x-left.x)*canvas.width,(right.y-left.y)*canvas.height):canvas.width*.38;
  const centerX=left&&right?(left.x+right.x)*canvas.width/2:canvas.width/2;
  const foreheadY=forehead?forehead.y*canvas.height:canvas.height*.28;
  const coverage=Number(hairMetrics?.visibleHairCoverage||0),severity=({leves:.045,moderadas:.1,acentuadas:.16})[receding]||0;
  const safeScaleMax=severity>=.16?1.03:severity>=.1?1.09:coverage&&coverage<.02?1.08:1.2;
  const requestedScale=Number(scale),effectiveScale=realism==='livre'?clamp(requestedScale,.7,1.3):clamp(requestedScale,.78,safeScaleMax);
  const width=templeWidth*filter.width*effectiveScale,height=width*(overlay.naturalHeight/overlay.naturalWidth);
  const x=centerX-width/2,y=foreheadY-height*.48+canvas.height*(filter.y+Number(offsetY));
  const rawAsymmetry=left&&right&&forehead?(forehead.x-(left.x+right.x)/2)/Math.max(.001,Math.abs(right.x-left.x)):0;
  const correction=Math.max(-.12,Math.min(.12,rawAsymmetry))*Number(asymmetryCorrection);
  const halfSource=overlay.naturalWidth/2,leftWidth=width/2*(1-correction),rightWidth=width/2*(1+correction);
  const layer=document.createElement('canvas');layer.width=canvas.width;layer.height=canvas.height;const lctx=layer.getContext('2d');lctx.globalAlpha=clamp(opacity,.35,1);
  lctx.drawImage(overlay,0,0,halfSource,overlay.naturalHeight,x,y,leftWidth,height);
  lctx.drawImage(overlay,halfSource,0,halfSource,overlay.naturalHeight,x+leftWidth,y,rightWidth,height);
  if(severity&&left&&right&&forehead){lctx.save();lctx.globalCompositeOperation='destination-out';for(const side of [left,right]){const cx=(side.x+(forehead.x-side.x)*.58)*canvas.width,cy=(forehead.y+.025)*canvas.height;lctx.beginPath();lctx.ellipse(cx,cy,templeWidth*severity,templeWidth*severity*.72,0,0,Math.PI*2);lctx.fill()}lctx.restore()}
  let biologicalMask=null,hairColor=null;
  if(allowedHairMaskDataUrl){
   biologicalMask=await load(allowedHairMaskDataUrl);const maskLayer=document.createElement('canvas');maskLayer.width=canvas.width;maskLayer.height=canvas.height;const mctx=maskLayer.getContext('2d');
   mctx.filter=`blur(${clamp(feather,0,16)}px)`;mctx.drawImage(biologicalMask,0,0,canvas.width,canvas.height);mctx.filter='none';lctx.save();lctx.globalCompositeOperation='destination-in';lctx.globalAlpha=1;lctx.drawImage(maskLayer,0,0);lctx.restore();
   hairColor=sampleHairColor(photo,await load(hairMaskDataUrl||allowedHairMaskDataUrl));
   if(preserveColor){lctx.save();lctx.globalCompositeOperation='color';lctx.globalAlpha=realism==='conservador'?.72:.55;lctx.fillStyle=hairColor.css;lctx.fillRect(0,0,canvas.width,canvas.height);lctx.restore()}
  }
  if(biologicalMask&&Number(originalTexture)>0){const detail=document.createElement('canvas');detail.width=canvas.width;detail.height=canvas.height;const dctx=detail.getContext('2d');dctx.drawImage(photo,0,0);dctx.globalCompositeOperation='destination-in';dctx.drawImage(biologicalMask,0,0,canvas.width,canvas.height);lctx.save();lctx.globalCompositeOperation='soft-light';lctx.globalAlpha=clamp(originalTexture,0,.45);lctx.drawImage(detail,0,0);lctx.restore()}
  ctx.drawImage(layer,0,0);
  return{filterId:filter.id,requestedScale,effectiveScale,scaleLimited:effectiveScale!==requestedScale,safeScaleMax,offsetY:Number(offsetY),opacity:Number(opacity),realism,preserveColor:Boolean(preserveColor),sampledHairColor:hairColor,feather:Number(feather),originalTexture:Number(originalTexture),asymmetryCorrection:Number(asymmetryCorrection),detectedAsymmetry:Math.round(rawAsymmetry*1000)/1000,recedingPreserved:receding,biologicalMaskApplied:Boolean(allowedHairMaskDataUrl),mode:anchors?'adaptive-mediapipe':'central-fallback'};
 }
 function download(canvas,name='simulacao-visagismo.png'){const a=document.createElement('a');a.download=name;a.href=canvas.toDataURL('image/png');a.click()}
 return{status:'ADAPTIVE_2D',version:'2.1.0',filters,render,download};
})();
