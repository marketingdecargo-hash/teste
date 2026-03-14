# App Python para visualizar status de planilha via SheetDB

Este projeto cria um painel em **Streamlit** que consome uma API do **SheetDB** para:

- Ler os registros da planilha publicada no SheetDB;
- Consolidar e visualizar os valores de uma coluna de status (tabela + gráfico).

## API usada

Endpoint solicitado:

```text
https://sheetdb.io/api/v1/jydw3jtmsrhd1
```

## 1) Pré-requisitos

- Python 3.10+

## 2) Instalação

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3) Execução

```bash
streamlit run app.py
```

Depois:

1. Confirme/ajuste a URL da API no sidebar;
2. Informe a coluna de status (padrão: `status`);
3. Clique em **Carregar dados**.

## 4) Teste rápido da API (CLI)

```bash
python - <<'PY'
import requests
url = "https://sheetdb.io/api/v1/jydw3jtmsrhd1"
res = requests.get(url, timeout=30)
res.raise_for_status()
data = res.json()
print(f"status_code={res.status_code}")
print(f"registros={len(data)}")
print(f"colunas={list(data[0].keys()) if data else []}")
PY
```
