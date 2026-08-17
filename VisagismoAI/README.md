# Visagismo AI — V2

Backend local para análise facial 2D, mapa capilar por segmentação, validação multivista das fotos e armazenamento opcional criptografado.

## Recursos atuais

- leitura facial 2D com pontos de referência do MediaPipe;
- segmentação local do cabelo por ONNX Runtime em CPU;
- estimativa visual de cobertura, assimetria e entradas aparentes;
- máscara biológica que impede o filtro de desenhar muito além do cabelo detectado;
- combinação conservadora entre informação do cliente e evidência da câmera;
- armazenamento opcional criptografado, sem salvar as máscaras temporárias em Base64.

O modelo esperado fica em:

`VisagismoAI/models/hair_segmentation.onnx`

As instruções de preparação estão em `SEGMENTATION_SETUP.md`.

## Executar

```powershell
cd "C:\Users\Samuel\Documents\projeto barbearia"
.\.venv\Scripts\Activate.ps1
python -m uvicorn VisagismoAI.main:app --host 127.0.0.1 --port 8001
```

Abra `http://127.0.0.1:8001/docs` para testar a API.

## Privacidade

- Sem `store_history`, a foto é analisada em memória e descartada.
- Com `store_history`, a imagem é normalizada, remove metadados e é armazenada com AES-256-GCM.
- A chave local fica em `.secrets/master.key` e não deve ser copiada para repositórios.
- Esta etapa ainda é uma análise estética de superfície, não uma análise clínica do crânio.
- A câmera estima pixels visíveis; ela não mede folículos, densidade microscópica ou estrutura óssea interna.
- Luz, oclusões, ângulo, cabelo muito claro e baixa resolução podem reduzir a confiança. Quando a qualidade é insuficiente, o sistema desativa automaticamente a máscara capilar.
- A pré-visualização preserva melhor os limites reais, mas continua sendo uma simulação 2D aproximada, não uma garantia do resultado do corte.
