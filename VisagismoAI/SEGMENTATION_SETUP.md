# Ambiente de segmentação seguro por CPU

Este ambiente fica separado do MediaPipe para preservar a API funcional.

## Instalado

- Ambiente: `.venv-segmentation`
- ONNX Runtime CPU 1.28.0
- OpenCV headless 5.0.0
- Open3D 0.19.0 (núcleo; sem integração Jupyter)
- BiSeNet Face Parsing (MIT): `third_party/face-parsing`
- Modelo ResNet-18 ONNX: `third_party/face-parsing/weights/resnet18.onnx`

Consumo medido da pilha: aproximadamente 654 MB. Orçamento desta fase: 1 GB.

## Teste validado

```powershell
& .\.venv-segmentation\Scripts\python.exe third_party\face-parsing\onnx_inference.py `
  --model third_party\face-parsing\weights\resnet18.onnx `
  --input VisagismoBarber\assets\images\corte-side-part.jpg `
  --output .segmentation-test
```

O modelo executou com `CPUExecutionProvider` e gerou máscara em menos de um segundo.

## Não instalado por segurança

- SAM 2: recomenda WSL e GPU NVIDIA; não detectados nesta máquina.
- PyTorch3D: sem wheel simples para esta combinação Windows/Python e normalmente requer toolchain/CUDA.
- Diffusers/ControlNet/IP-Adapter: pesos grandes e lentos por CPU; aguardar GPU ou serviço separado.
- COLMAP: removido; ocuparia espaço sem ganho suficiente na captura atual.
- DECA/FLAME/StyleGAN Salon: restrições de licença para uso comercial e/ou pesquisa.

O Open3D funciona para nuvens de pontos. `pip check` informa apenas componentes Jupyter opcionais que foram omitidos para evitar o problema de caminhos longos do Windows.
