from telegram.ext import Updater, MessageHandler, Filters
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
        quantità = parti[0].strip()
        nome_modem = autocorreggi(parti[1].strip())
        dati.append({"Modem": nome_modem, "Quantità": quantità, "Utente": username})

    # Salva in un file CSV
    df = pd.DataFrame(dati)
    df.to_csv(FILE_PATH, mode="a", header=False, index=False)

# Funzione per gestire i messaggi
def handle_message(update, context):
    username = update.message.from_user.username
    messaggio = update.message.text
    try:
        salva_dati(username, messaggio)
        update.message.reply_text("Dati registrati con successo!")
    except Exception as e:
        update.message.reply_text(f"Errore: {str(e)}")

# Configurazione del bot
def main():
    updater = Updater("IL_TUO_TOKEN_BOT", use_context=True)
    dp = updater.dispatcher

    # Gestione dei messaggi
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Avvio del bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
