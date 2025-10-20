# postech-pressao

Biblioteca simples para classificar aferições de pressão arterial como **BAIXA**, **NORMAL** ou **ALTA** a partir de pares `(sistólica, diastólica)`.

> **Atenção:** uso educacional/didático. Não substitui orientação clínica.

## Instalação

```bash
pip install postech-pressao
```

## Uso (Python)

```python
from postech_pressao import train_default_model, predict_labels

model = train_default_model()
resultados = predict_labels(model, [(120,80), (140,90), (100,70)])
print(resultados)  # ['NORMAL', 'ALTA', 'BAIXA'] (exemplo)
```

## Uso (CLI)

```bash
postech-pressao --pares 120,80 140,90 100,70
# 120/80 => NORMAL
# 140/90 => ALTA
# 100/70 => BAIXA
```

## Como funciona
- O modelo é um **LinearSVC** (scikit-learn) treinado com um conjunto de exemplos simples incluído na lib.
- As predições retornam rótulos legíveis: **BAIXA**, **NORMAL**, **ALTA**.

## Desenvolvimento

```bash
python -m venv .venv && source .venv/bin/activate
pip install -U pip build twine pytest
pip install -e .
pytest -q
```

## Build & Publicação

```bash
python -m build
twine check dist/*
# TestPyPI
twine upload -r testpypi dist/*
# PyPI
twine upload dist/*
```

Para testar a instalação a partir do TestPyPI:

```bash
python -m pip install --index-url https://test.pypi.org/simple/ --no-deps postech-pressao
```

## Licença
MIT
