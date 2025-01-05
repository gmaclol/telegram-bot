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
from fuzzywuzzy import process

# Lista modelli modem
modelli_modem = ["RFID", "POWER", "SFP", "WI-FI 6 VODAFONE", "SIM TRIO", "ONT SKY", "CPE EOLO"]

# File per salvare i dati
FILE_PATH = "giacenza_modem.csv"

# Funzione per autocorreggere
def autocorreggi(nome_modem):
    correzione = process.extractOne(nome_modem, modelli_modem)
    if correzione[1] > 70:  # Threshold
        return correzione[0]
    return nome_modem

# Funzione per salvare i dati
def salva_dati(username, messaggio):
    righe = messaggio.split("\n")
    dati = []
    for riga in righe:
        parti = riga.split(maxsplit=1)
        if len(parti) < 2:
            continue
        quantita = parti[0].strip()
        nome_modem = autocorreggi(parti[1].strip())
        dati.append({"Modem": nome_modem, "Quantità": quantita, "Utente": username})

    # Salva in un file CSV
    df = pd.DataFrame(dati)
    df.to_csv(FILE_PATH, mode="a", header=False, index=False)

# Gestore per i messaggi
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    messaggio = update.message.text
    chat_id = update.effective_chat.id
    try:
        salva_dati(username, messaggio)
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
        "```\n2 RFID\n3 POWER\n1 WI-FI 6 VODAFONE\n```\n"
        "Ogni volta che mi invii una lista, ti manderò anche il file aggiornato.\n",
        parse_mode="Markdown"
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
