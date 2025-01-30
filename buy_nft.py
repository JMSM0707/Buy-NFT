import time
import base64
import requests
from solana.rpc.api import Client
from solana.keypair import Keypair
from solana.transaction import Transaction
from solana.rpc.types import TxOpts
from solana.system_program import transfer

# Настройки
API_URL = "https://api.mainnet-beta.solana.com"  # URL для Solana
MAGIC_EDEN_API = "https://api.magiceden.io"  # URL для Magic Eden API
WALLET_PRIVATE_KEY = "YOUR_PRIVATE_KEY"  # Ваш закрытый ключ (безопасно не хранить в открытом виде)
MIN_PRICE = 1.0  # Минимальная цена для покупки NFT
NFT_MINT_ADDRESS = "NFT_MINT_ADDRESS_HERE"  # Адрес NFT для отслеживания

# Инициализация клиента Solana
client = Client(API_URL)

# Генерация ключевой пары из закрытого ключа
keypair = Keypair.from_secret_key(base64.b64decode(WALLET_PRIVATE_KEY))

def buy_nft(nft_mint_address):
    # Получите данные NFT
    nft_info = requests.get(f"{MAGIC_EDEN_API}/v1/nft/{nft_mint_address}").json()
    
    if not nft_info["success"] or "price" not in nft_info["data"]:
        print("Ошибка получения данных NFT.")
        return

    # Убедитесь, что есть цена для покупки
    price = float(nft_info["data"]["price"])
    print(f"Цена NFT: {price}, Минимальная цена: {MIN_PRICE}")

    if price <= MIN_PRICE:
        print("Покупка NFT...")
        seller_address = nft_info["data"]["seller"]  # Предполагается, что в API есть поле 'seller'

        # Создание транзакции для покупки
        transaction = Transaction()
        
        # Конвертация цены в лампорты (1 SOL = 1e9 лампортов)
        lamports = int(price * 1e9)

        # Добавление операции перевода SOL
        transaction.add(
            transfer({
                'from_pubkey': keypair.public_key,
                'to_pubkey': seller_address,  # адрес продавца
                'lamports': lamports
            })
        )

        # Подписываем транзакцию
        transaction.sign(keypair)

        try:
            # Отправка транзакции
            signature = client.send_transaction(transaction, keypair, opts=TxOpts(skip_preflight=True))
            print(f"Транзакция успешна с подписью: {signature}")
        except Exception as e:
            print(f"Ошибка при попытке покупки NFT: {e}")

def monitor_nft():
    while True:
        buy_nft(NFT_MINT_ADDRESS)
        time.sleep(60)  # Проверьте каждую минуту

if __name__ == "__main__":
    monitor_nft()
