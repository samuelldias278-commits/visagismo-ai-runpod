# Visagismo AI Runpod

Projeto privado do sistema de análise facial e capilar para visagismo. A interface continua funcionando localmente; o diretório `runpod_deploy` contém o worker Serverless CPU preparado para a Runpod.

## Privacidade

Fotos, históricos criptografados, chaves, ambientes virtuais, logs e credenciais não fazem parte deste repositório. A imagem Serverless processa fotografias em memória e não persiste o conteúdo recebido.

## Imagem do worker

O workflow `Publicar imagem Runpod` constrói a imagem nos servidores do GitHub e publica no GitHub Container Registry. Nenhuma chave Runpod é usada durante a construção.

Consulte [runpod_deploy/README.md](runpod_deploy/README.md) para o contrato da API e as restrições de custo.
