# Visagismo AI no Runpod — pacote preparado

Este diretório empacota apenas a análise facial/capilar existente como worker de fila Serverless. Ele não inclui geração fotográfica por difusão.

## Segurança e custo

- CPU, sem GPU para MediaPipe/ONNX.
- `workersMin: 0`: escala a zero quando ocioso.
- `workersMax: 1`: limita concorrência e custo.
- A fotografia é processada em memória e não é persistida pelo worker.
- A chave Runpod nunca entra na imagem Docker.
- Limite de 7 MB para a imagem original, deixando margem para o acréscimo do Base64 no limite de payload.

## Construção futura

O contexto da construção é a raiz do projeto:

```powershell
docker build -f runpod_deploy/Dockerfile -t SEU_REGISTRO/visagismo-analise:v2 .
```

Depois de publicar a imagem em um registro, crie um template Serverless e um endpoint CPU com mínimo zero. Não execute essa etapa sem confirmar preço, registro e política de retenção.

## Contrato da chamada

Envie para `/run` ou `/runsync`:

```json
{
  "input": {
    "photoBase64": "data:image/jpeg;base64,...",
    "consentId": "id-de-consentimento",
    "viewLabel": "Foto frontal"
  }
}
```

O retorno mantém `quality`, `faceGeometry` e `hairAnalysis` compatíveis com o backend local.

## Teste local do handler

O teste abaixo chama diretamente a função e não usa a Runpod:

```powershell
$env:PYTHONPATH = (Get-Location).Path
.\.venv\Scripts\python.exe runpod_deploy\smoke_test.py ".segmentation-test\client-photo-crop.jpg"
```
