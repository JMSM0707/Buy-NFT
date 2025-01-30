import time
import requests
import base58
from solana.rpc.api import Client
from solders.keypair import Keypair
from solders.transaction import Transaction
from solana.rpc.types import TxOpts
from solders.system_program import transfer

# Настройки
API_URL = "https://api.mainnet-beta.solana.com"  # URL для Solana
MAGIC_EDEN_API = "https://api.magiceden.dev"  # URL для Magic Eden API (проверьте правильный API)
WALLET_PRIVATE_KEY = "YOUR_PRIVATE_KEY_HERE"  # Ваш закрытый ключ в формате Base58
MIN_PRICE = 0.01  # Минимальная цена для покупки NFT
NFT_MINT_ADDRESS = "YOUR_NFT_COLLECTION_ADDRESS_HERE"  # Адрес коллекции NFT для отслеживания

# Инициализация клиента Solana
client = Client(API_URL)

# Генерация ключевой пары из закрытого ключа
private_key_bytes = base58.b58decode(WALLET_PRIVATE_KEY)  # Декодируем Base58
kp = Keypair.from_bytes(private_key_bytes)  # Создаем Keypair

def buy_nft(nft_data):
    # Убедитесь, что есть цена для покупки
    price = float(nft_data["price"])
    print(f"Цена NFT: {price}, Минимальная цена: {MIN_PRICE}")

    if price <= MIN_PRICE:
        print("Покупка NFT...")
        seller_address = nft_data["seller"]  # Предполагается, что в данных есть поле 'seller'
        
        # Создание транзакции для покупки
        transaction = Transaction()
        
        # Конвертация цены в лампорты (1 SOL = 1e9 лампортов)
        lamports = int(price * 1e9)

        # Добавление операции перевода SOL
        transaction.add(
            transfer({
                'from_pubkey': kp.public_key,
                'to_pubkey': seller_address,  # адрес продавца
                'lamports': lamports
            })
        )

        # Подписываем транзакцию
        transaction.sign(kp)

        try:
            # Отправка транзакции
            signature = client.send_transaction(transaction, kp, opts=TxOpts(skip_preflight=True))
            print(f"Транзакция успешна с подписью: {signature}")
        except Exception as e:
            print(f"Ошибка при попытке покупки NFT: {e}")

def monitor_nft():
    last_checked_nfts = set()  # Сохраняем идентификаторы уже проверенных NFT
    while True:
        # Получаем информацию о NFT коллекции
        response = requests.get(f"{MAGIC_EDEN_API}/v2/collections/{NFT_MINT_ADDRESS}/listings")
        
        if response.status_code != 200:
            print("Ошибка получения данных NFT.")
            time.sleep(2)  # Ожидание перед новой попыткой
            continue

        nft_listings = response.json().get('data', [])

        for nft in nft_listings:
            nft_id = nft["id"]
            if nft_id not in last_checked_nfts:  # Проверяем только новые NFT
                last_checked_nfts.add(nft_id)  # Добавляем NFT в проверенные

                # Проверяем цену NFT
                buy_nft(nft)

        time.sleep(2)  # Ожидание перед следующей проверкой

if __name__ == "__main__":
    monitor_nft()
