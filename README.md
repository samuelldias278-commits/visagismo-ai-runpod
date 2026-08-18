# Visagismo AI Runpod

Projeto privado do sistema de análise facial e capilar para visagismo. A interface continua funcionando localmente; o diretório `runpod_deploy` contém o worker Serverless CPU preparado para a Runpod.

## Privacidade

Fotos, históricos criptografados, chaves, ambientes virtuais, logs e credenciais não fazem parte deste repositório. A imagem Serverless processa fotografias em memória e não persiste o conteúdo recebido.

## Imagem do worker

O workflow `Publicar imagem Runpod` constrói a imagem nos servidores do GitHub e publica no GitHub Container Registry. Nenhuma chave Runpod é usada durante a construção.

Consulte [runpod_deploy/README.md](runpod_deploy/README.md) para o contrato da API e as restrições de custo.

## Simulação generativa opcional

A simulação realista usa o endpoint de edição de imagens no backend. Para ativá-la,
configure no ambiente do serviço, nunca no frontend ou no Git:

- `OPENAI_API_KEY`: chave de um projeto da OpenAI com faturamento e acesso a imagens.
- `GENERATIVE_ACCESS_CODE`: código privado exigido antes de cada geração para proteger os créditos.

Sem as duas variáveis, o restante do aplicativo continua funcionando e o endpoint generativo
responde como não configurado. A foto frontal é processada temporariamente e o resultado não é
gravado pelo aplicativo.
