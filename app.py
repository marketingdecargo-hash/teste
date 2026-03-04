import json
import os
from typing import Any, Dict, Optional

import gspread
import pandas as pd
import plotly.express as px
import streamlit as st
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.metadata.readonly",
]


def get_credentials() -> Credentials:
    """Carrega credenciais de service account por arquivo ou variável de ambiente."""
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    credentials_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")

    if credentials_path and os.path.exists(credentials_path):
        return Credentials.from_service_account_file(credentials_path, scopes=SCOPES)

    if credentials_json:
        info = json.loads(credentials_json)
        return Credentials.from_service_account_info(info, scopes=SCOPES)

    raise RuntimeError(
        "Credenciais não encontradas. Defina GOOGLE_APPLICATION_CREDENTIALS "
        "ou GOOGLE_SERVICE_ACCOUNT_JSON."
    )


@st.cache_resource(show_spinner=False)
def get_clients() -> tuple[gspread.Client, Any]:
    credentials = get_credentials()
    gspread_client = gspread.authorize(credentials)
    drive_service = build("drive", "v3", credentials=credentials)
    return gspread_client, drive_service


def fetch_sheet(spreadsheet_id: str, worksheet_name: Optional[str]) -> pd.DataFrame:
    client, _ = get_clients()
    spreadsheet = client.open_by_key(spreadsheet_id)

    if worksheet_name:
        worksheet = spreadsheet.worksheet(worksheet_name)
    else:
        worksheet = spreadsheet.get_worksheet(0)

    records = worksheet.get_all_records()
    return pd.DataFrame(records)


def fetch_drive_metadata(file_id: str) -> Dict[str, Any]:
    _, drive_service = get_clients()
    metadata = (
        drive_service.files()
        .get(
            fileId=file_id,
            fields="id,name,mimeType,owners(displayName,emailAddress),modifiedTime,lastModifyingUser(displayName,emailAddress),webViewLink,trashed",
        )
        .execute()
    )
    return metadata


def normalize_status(df: pd.DataFrame, status_column: str) -> pd.DataFrame:
    clean_df = df.copy()
    clean_df[status_column] = (
        clean_df[status_column].astype(str).str.strip().replace({"": "Sem status"})
    )
    return clean_df


def render_metadata(metadata: Dict[str, Any]) -> None:
    owner = metadata.get("owners", [{}])[0]
    last_user = metadata.get("lastModifyingUser", {})

    st.subheader("📄 Informações do arquivo no Google Drive")
    col1, col2, col3 = st.columns(3)
    col1.metric("Nome", metadata.get("name", "-"))
    col2.metric("Modificado em", metadata.get("modifiedTime", "-"))
    col3.metric("Na lixeira", "Sim" if metadata.get("trashed") else "Não")

    st.markdown(
        f"**Proprietário:** {owner.get('displayName', '-') } ({owner.get('emailAddress', '-')})"
    )
    st.markdown(
        f"**Última edição por:** {last_user.get('displayName', '-') } ({last_user.get('emailAddress', '-')})"
    )
    st.markdown(f"[Abrir planilha no Drive]({metadata.get('webViewLink', '#')})")


def render_status_dashboard(df: pd.DataFrame, status_column: str) -> None:
    if status_column not in df.columns:
        st.error(f"A coluna '{status_column}' não existe na planilha.")
        st.write("Colunas disponíveis:", ", ".join(df.columns))
        return

    normalized_df = normalize_status(df, status_column)
    counts = (
        normalized_df[status_column]
        .value_counts(dropna=False)
        .rename_axis("status")
        .reset_index(name="quantidade")
    )

    st.subheader("📊 Resumo de status")
    st.dataframe(counts, use_container_width=True)

    fig = px.pie(
        counts,
        values="quantidade",
        names="status",
        title="Distribuição por status",
        hole=0.3,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🔎 Dados completos")
    st.dataframe(normalized_df, use_container_width=True)


def main() -> None:
    st.set_page_config(page_title="Monitor de Status do Sheets", layout="wide")
    st.title("Monitor de Status de Planilha Google Sheets")
    st.caption("Visualize status por coluna e metadados do arquivo no Google Drive")

    with st.sidebar:
        st.header("Configuração")
        spreadsheet_id = st.text_input("Spreadsheet ID", help="ID da URL da planilha")
        worksheet_name = st.text_input("Aba (opcional)")
        status_column = st.text_input("Coluna de status", value="status")
        carregar = st.button("Carregar dados", type="primary")

    if not carregar:
        st.info("Preencha os dados na barra lateral e clique em 'Carregar dados'.")
        return

    if not spreadsheet_id:
        st.warning("Informe o Spreadsheet ID.")
        return

    try:
        metadata = fetch_drive_metadata(spreadsheet_id)
        df = fetch_sheet(spreadsheet_id, worksheet_name or None)

        render_metadata(metadata)

        if df.empty:
            st.warning("A aba está vazia ou sem cabeçalho.")
            return

        render_status_dashboard(df, status_column)
    except Exception as error:  # noqa: BLE001
        st.exception(error)


if __name__ == "__main__":
    main()
