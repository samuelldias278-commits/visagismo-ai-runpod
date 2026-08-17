const BEARD_SOURCE='https://us.braun.com/en-us/male-grooming-tips/facial-hair-styles/the-most-popular-beard-styles-for-men';
const B_FACES=['oval','redondo','quadrado','retangular','triangular','diamante'],B_AGES=['18–25','26–35','36–45','46–60','60+'];
const B=(id,nome,densidade,min,aceitaFalhas,rostos,estilos,idades,descricao,requisitos)=>({id,nome,densidade,min,aceitaFalhas,rostos,estilos,idades,descricao,requisitos,imagem:`assets/images/barba-${id}.svg`,referencia:BEARD_SOURCE});
window.BARBAS=[
B('clean','Rosto barbeado','baixa',0,true,B_FACES,['clássico','discreto','profissional'],B_AGES,'Sem barba, contornos limpos.','Não exige crescimento.'),
B('stubble','Stubble / 3 dias','baixa',0,true,B_FACES,['clássico','moderno','casual'],B_AGES,'Sombra curta de 1–3 mm.','Poucos dias de crescimento.'),
B('curta','Barba curta','baixa',1,true,['oval','quadrado','retangular','diamante'],['clássico','profissional','casual'],B_AGES,'Contorno curto e limpo.','Cobertura básica.'),
B('boxed','Short Boxed Beard','media',1,false,['oval','redondo','triangular'],['clássico','profissional'],['26–35','36–45','46–60','60+'],'Curta e estruturada.','Densidade lateral média.'),
B('media','Barba média','media',2,false,['oval','redondo','quadrado','triangular'],['clássico','casual'],['26–35','36–45','46–60'],'Comprimento intermediário.','Boa cobertura geral.'),
B('cheia','Barba cheia clássica','alta',3,false,['oval','retangular','triangular'],['clássico','marcante'],['26–35','36–45','46–60','60+'],'Volume completo.','Alta densidade e crescimento.'),
B('degrade','Barba degradê','media',1,true,['oval','redondo','quadrado'],['moderno','profissional'],['18–25','26–35','36–45'],'Transição das costeletas ao queixo.','Comprimento curto ou médio.'),
B('cavanhaque','Cavanhaque clássico','baixa',1,true,['redondo','quadrado','diamante'],['clássico','discreto'],['26–35','36–45','46–60','60+'],'Foco no bigode e queixo.','Crescimento central.'),
B('circle','Circle Beard','media',1,true,['redondo','quadrado','oval'],['clássico','profissional'],['26–35','36–45','46–60','60+'],'Bigode conectado ao cavanhaque.','Conexão ao redor da boca.'),
B('van-dyke','Van Dyke','media',2,true,['redondo','quadrado','oval'],['clássico','marcante'],['26–35','36–45','46–60'],'Bigode separado e queixo pontudo.','Comprimento médio central.'),
B('balbo','Balbo','media',2,true,['redondo','quadrado','oval'],['clássico','marcante'],['26–35','36–45','46–60'],'Bigode e queixo sem costeletas.','Boa cobertura central.'),
B('bigode-curta','Bigode + barba curta','media',1,true,['oval','quadrado','retangular','triangular'],['clássico','profissional'],['26–35','36–45','46–60','60+'],'Bigode sobre base curta.','Crescimento no bigode e queixo.'),
B('chinstrap','Chin Strap','media',1,false,['oval','redondo','retangular'],['moderno','marcante'],['18–25','26–35','36–45'],'Faixa na mandíbula.','Cobertura mandibular contínua.'),
B('anchor','Anchor Beard','media',1,true,['redondo','quadrado','diamante'],['moderno','marcante'],['26–35','36–45','46–60'],'Formato de âncora.','Boa cobertura central.'),
B('ducktail','Ducktail','alta',3,false,['redondo','quadrado','retangular'],['clássico','marcante'],['26–35','36–45','46–60'],'Cheia e afunilada no queixo.','Alta densidade.'),
B('garibaldi','Garibaldi','alta',3,false,['oval','retangular','diamante','triangular'],['clássico','marcante'],['36–45','46–60','60+'],'Cheia, larga e arredondada.','Muito volume.'),
B('verdi','Verdi','alta',3,false,['oval','diamante','triangular'],['clássico','marcante'],['36–45','46–60','60+'],'Cheia com bigode modelado.','Alta densidade e produto.'),
B('hollywoodian','Hollywoodian','media',2,true,['quadrado','redondo','oval'],['moderno','marcante'],['26–35','36–45','46–60'],'Queixo e mandíbula sem costeletas.','Cobertura central e mandibular.'),
B('mutton-chops','Mutton Chops','alta',2,false,['retangular','oval','triangular'],['clássico','marcante'],['36–45','46–60','60+'],'Costeletas largas, queixo limpo.','Alta densidade lateral.'),
B('soul-patch','Soul Patch','baixa',1,true,['quadrado','oval','redondo'],['moderno','discreto'],['18–25','26–35','36–45'],'Pequena área abaixo do lábio.','Crescimento mínimo central.')
];
window.BARBAS.forEach(x=>{x.imagem={src:`assets/images/barba-${x.id}.jpg`,origem:'gerada para o projeto'};x.referenciasTecnicas=['Milady Standard Barbering — desenho de barba e bigode','OpenTextBC — consulta e adaptação ao formato facial','Braun/Philips — comprimentos, contornos e manutenção prática'];x.modeloTecnico={
 simetria:'marcar centro do lábio, queixo, ângulos mandibulares e alturas das bochechas; corrigir visualmente sem perseguir simetria anatômica perfeita',
 linhaBochecha:['cheia','garibaldi','ducktail','verdi'].includes(x.id)?'natural e limpa, preservando densidade':'definida conforme cobertura e formato facial',
 linhaPescoco:x.id==='clean'?'barbear integralmente com avaliação da pele':'curva contínua acima do pomo de adão, sem subir excessivamente',
 distribuicao:x.aceitaFalhas?'permite direcionar o desenho para regiões de maior cobertura':'depende de cobertura relativamente uniforme',
 tecnica:x.min>=3?'crescimento prévio, desbaste por zonas, tesoura e acabamento de contorno':'máquina com pentes graduais, aparador de precisão e acabamento',
 adaptacaoFacial:'usar largura lateral para ampliar e comprimento no queixo para alongar; evitar reforçar desproporções já predominantes'
};});
