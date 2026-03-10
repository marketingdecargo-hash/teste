from typing import Any

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

DEFAULT_API_URL = "https://sheetdb.io/api/v1/jydw3jtmsrhd1"


def fetch_sheetdb_data(api_url: str) -> pd.DataFrame:
    response = requests.get(api_url, timeout=30)
    response.raise_for_status()

    payload: Any = response.json()
    if not isinstance(payload, list):
        raise ValueError("A resposta da API não é uma lista de registros.")

    return pd.DataFrame(payload)


def normalize_status(df: pd.DataFrame, status_column: str) -> pd.DataFrame:
    normalized = df.copy()
    normalized[status_column] = (
        normalized[status_column]
        .astype(str)
        .str.strip()
        .replace({"": "Sem status", "nan": "Sem status", "None": "Sem status"})
    )
    return normalized


def render_status_dashboard(df: pd.DataFrame, status_column: str) -> None:
    if status_column not in df.columns:
        st.error(f"A coluna '{status_column}' não existe na resposta da API.")
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
    st.set_page_config(page_title="Monitor de Status (SheetDB)", layout="wide")
    st.title("Monitor de Status via SheetDB API")
    st.caption("Consome a API e mostra o resumo por coluna de status")

    with st.sidebar:
        st.header("Configuração")
        api_url = st.text_input("URL da API", value=DEFAULT_API_URL)
        status_column = st.text_input("Coluna de status", value="status")
        carregar = st.button("Carregar dados", type="primary")

    if not carregar:
        st.info("Preencha os dados na barra lateral e clique em 'Carregar dados'.")
        return

    if not api_url.strip():
        st.warning("Informe a URL da API.")
        return

    try:
        with st.spinner("Consultando API..."):
            df = fetch_sheetdb_data(api_url.strip())

        if df.empty:
            st.warning("A API retornou 0 registros.")
            return

        st.success(f"Registros carregados: {len(df)}")
        render_status_dashboard(df, status_column)
    except Exception as error:  # noqa: BLE001
        st.exception(error)


if __name__ == "__main__":
    main()
