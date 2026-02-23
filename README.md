# SEGNALI DI INVESTIMENTO - Analisi Multi-Indice & Trading

Web app professionale in Streamlit per lo screening di titoli azionari su mercati Italiani e Americani.

## Funzionalità Principali
- **Supporto Multi-Indice**: FTSE MIB, FTSE Italia All Share, Dow Jones, S&P 500, Nasdaq 100.
- **Analisi Fondamentale**: Valutazione automatica di P/E, P/B, ROE, crescita e fair value di Graham.
- **Analisi Tecnica**: Monitoraggio di **RSI (14)** e medie mobili (**SMA 50/200**) per identificare trend e segnali di ipercompra/ipervendita.
- **Sentiment & News**: Analisi tramite AI del tono delle notizie recenti (Google News RSS).
- **Investor Profiles**: Strategie selezionabili (Value, Growth, News, Bilanciata) per personalizzare lo score.
- **Manuale Integrato**: Guida completa agli indicatori consultabile direttamente nell'app.

## Installazione Locale

1. Clonare il repository o scaricare la cartella.
2. Assicurarsi di avere Python installato.
3. Eseguire il file `run_app.bat` (Windows) oppure:

```bash
python -m venv .venv
# Attivazione ambiente (.venv\Scripts\activate su Windows)
pip install -r requirements.txt
streamlit run app.py
```

## Condivisione
Per condividere l'app online gratuitamente, il metodo consigliato è **Streamlit Community Cloud**:
1. Caricare il codice su un repository **GitHub**.
2. Accedere a [share.streamlit.io](https://share.streamlit.io).
3. Selezionare il repository e l'app sarà online con un link pubblico!

---
*Disclaimer: Questa applicazione ha scopo puramente informativo e non costituisce consulenza finanziaria.*
