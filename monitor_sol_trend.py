from telethon import TelegramClient, events
import re
import logging
import asyncio
import configparser
import winsound  # Importar a biblioteca para o som

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregar configurações do arquivo de configuração
config = configparser.ConfigParser()
config.read('config.ini')

# Insira suas credenciais da API do Telegram
api_id = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']
phone_number = config['Telegram']['phone_number']
bot_token = config['Bot']['token']
delay_between_sends = int(config['Settings']['delay_between_sends'])  # Ler o tempo de espera

session_name = 'monitor_sol_trend'

client = TelegramClient(session_name, api_id, api_hash)

# Expressão regular para identificar contratos
# Atualizada para capturar o padrão de contrato do @totalcaller
contrato_pattern = r'\b[A-Za-z0-9]{32,44}\b|CA:\s*([A-Za-z0-9]+)'  # Captura contratos e o formato CA:
sent_contracts = set()

async def send_trade_link(contract, destination):
    try:
        if client.is_connected():
            await client.send_message(destination, contract)
            logger.info(f"Contrato enviado ao {destination}: {contract}")
            winsound.Beep(900, 100)  # Frequência de 1000 Hz por 500 ms
        else:
            logger.error("Cliente não está conectado.")
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem: {e}")

@client.on(events.NewMessage(chats=list(config['Origins'].values())))
async def handle_new_message(event):
    message = event.message.message
    logger.info(f"Nova mensagem recebida no canal:\n{message}")

    match = re.findall(contrato_pattern, message)
    if match:
        # Se houver correspondência, você pode querer processar todos os contratos encontrados
        for contrato in match:
            logger.info(f"Contrato identificado: {contrato}")
            
            if contrato not in sent_contracts:
                sent_contracts.add(contrato)
                for destination in config['Destinations'].values():
                    await send_trade_link(contrato, destination)
                    await asyncio.sleep(delay_between_sends)  # Usar o tempo de espera configurado
            else:
                logger.info("Contrato já enviado anteriormente.")
    else:
        logger.info("Nenhum contrato encontrado na mensagem.")

async def main():
    try:
        await client.start(phone=phone_number)
        logger.info("Monitorando mensagens do canal...")
        await client.run_until_disconnected()
    except Exception as e:
        logger.error(f"Erro ao iniciar o cliente: {e}")

if __name__ == "__main__":
    asyncio.run(main())