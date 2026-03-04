# App Python para visualizar status de uma planilha Google Sheets

Este projeto cria um painel simples em **Streamlit** para:

- Ler uma planilha do Google Sheets;
- Exibir metadados do arquivo no Google Drive (proprietário, última modificação, lixeira, link);
- Consolidar e visualizar os valores de uma coluna de status (tabela + gráfico).

## 1) Pré-requisitos

- Python 3.10+
- Um projeto no Google Cloud com APIs habilitadas:
  - Google Sheets API
  - Google Drive API
- Uma Service Account com acesso de leitura à planilha (compartilhe a planilha com o e-mail da service account).

## 2) Instalação

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3) Credenciais

Você pode usar **uma** das opções abaixo:

1. Arquivo JSON da service account:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/caminho/credenciais.json"
```

2. JSON completo em variável de ambiente:

```bash
export GOOGLE_SERVICE_ACCOUNT_JSON='{"type":"service_account", ...}'
```

## 4) Execução

```bash
streamlit run app.py
```

Depois:

1. Cole o `Spreadsheet ID` (parte da URL entre `/d/` e `/edit`);
2. (Opcional) Informe o nome da aba;
3. Informe a coluna de status (por padrão `status`);
4. Clique em **Carregar dados**.

## 5) Exemplo de URL e ID

URL:

```text
https://docs.google.com/spreadsheets/d/1ABCDEFgHiJKLmNopQRSTuvWXyz1234567890/edit#gid=0
```

Spreadsheet ID:

```text
1ABCDEFgHiJKLmNopQRSTuvWXyz1234567890
```
