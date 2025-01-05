import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
import pandas as pd

# Lista completa dei modelli modem
modelli_modem = ["RFID", "POWER", "SFP", "WI-FI 6 VODAFONE", "SIM TRIO", "ONT SKY", "CPE EOLO"]

# File per salvare i dati
FILE_PATH = "giacenza_modem.csv"

# Funzione per salvare i dati della lista
def salva_lista(username, messaggio):
    righe = messaggio.split("\n")
    dati = {modem: 0 for modem in modelli_modem}  # Inizializza tutti i modem a 0

    for riga in righe:
        try:
            parti = riga.split(",")
            modem = parti[0].strip()
            quantita = int(parti[1].strip())
            if modem in dati:
                dati[modem] = quantita
        except (IndexError, ValueError):
            continue  # Salta righe malformate

    # Crea una lista di righe per il file CSV
    righe_csv = [[modem, quantita, username if idx == 0 else ""] for idx, (modem, quantita) in enumerate(dati.items())]

    # Crea un DataFrame con i dati
    df = pd.DataFrame(righe_csv, columns=["Modem", "Quantità", "Utente"])

    # Salva i dati nel file CSV
    df.to_csv(FILE_PATH, mode="w", header=True, index=False)

# Gestore per i messaggi
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    messaggio = update.message.text
    chat_id = update.effective_chat.id
    try:
        salva_lista(username, messaggio)
        await update.message.reply_text("Dati registrati con successo! Ti invio il file aggiornato.")

        # Invia il file aggiornato
        with open(FILE_PATH, "rb") as file:
            await context.bot.send_document(chat_id=chat_id, document=file)

    except Exception as e:
        await update.message.reply_text(f"Errore durante l'elaborazione: {str(e)}")

# Gestore del comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Ciao! Sono il tuo bot per la gestione delle giacenze modem.\n"
        "Puoi inviarmi una lista nel formato:\n"
        "Modem, Numero\nModem, Numero\n"
        "Se non menzioni un modem, sarà registrato con quantità 0.\n"
        "Ogni volta che invii una lista, ti manderò il file aggiornato."
    )

# Configura l'applicazione Telegram
def main():
    BOT_TOKEN = os.getenv("IL_TUO_TOKEN_BOT")
    if not BOT_TOKEN:
        raise ValueError("Il token del bot non è stato trovato. Controlla le variabili d'ambiente.")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Aggiungi i gestori
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()
