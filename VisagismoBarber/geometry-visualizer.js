'use strict';
window.geometryVisualizer={
 render(canvas,points,angle=0){
  const dpr=Math.min(devicePixelRatio||1,2),w=Math.max(260,canvas.clientWidth||360),h=300;
  canvas.width=w*dpr;canvas.height=h*dpr;canvas.style.height=`${h}px`;
  const ctx=canvas.getContext('2d');ctx.scale(dpr,dpr);ctx.fillStyle='#14201c';ctx.fillRect(0,0,w,h);
  const rad=Number(angle)*Math.PI/180,cos=Math.cos(rad),sin=Math.sin(rad);
  const projected=points.map(p=>{const x=p.x*cos-p.z*sin,z=p.x*sin+p.z*cos,scale=155/(1+z*.28);return{x:w/2+x*scale,y:38+p.y*scale,z}}).sort((a,b)=>a.z-b.z);
  for(const p of projected){ctx.beginPath();ctx.arc(p.x,p.y,3.2,0,Math.PI*2);ctx.fillStyle=`rgba(108,224,174,${Math.max(.3,Math.min(1,.72-p.z*.25))})`;ctx.fill()}
  ctx.fillStyle='#dce9e3';ctx.font='12px sans-serif';ctx.fillText('Superfície facial relativa — use o controle para girar',12,20);
 },
};
