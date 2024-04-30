import requests

def fetch_order_book(exchange_url):
    response = requests.get(exchange_url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch order book from", exchange_url)
        return None

def normalize_order_book(order_book_data):
    
    transformed_data = {'bids': [], 'asks': []}
    
    for side in ['bids', 'asks']:
        for item in order_book_data[side]:
            if isinstance(item, list):
                
                price, amount, timestamp = item
                
                transformed_data[side].append({'price': float(price), 'quantity': float(amount), 'timestamp': timestamp})
            
            elif 'price' in item and 'amount' in item:
                # Handle second data format
                transformed_data[side].append({'price': float(item['price']), 'quantity': float(item['amount']), 'timestamp': item['timestamp']})
    
    
    return transformed_data


def fetch_order_book_kraken(url, pair):
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        order_book = data.get('result', {}).get('XXBTZUSD', {})
        if order_book:
            asks = [{'price': float(ask[0]), 'quantity': float(ask[1]), 'timestamp': ask[2]} for ask in order_book.get('asks', [])]
            bids = [{'price': float(bid[0]), 'quantity': float(bid[1]), 'timestamp': bid[2]} for bid in order_book.get('bids', [])]
            return {'asks': asks, 'bids': bids}
        else:
            print(f"No order book data found for pair {pair}.")
            return None
        
    else:
        print("Failed to fetch order book data.")
        return None



def get_price_to_buy(order_book, quantity):
    total_quantity = 0
    cost = 0
    for ask in order_book['asks']:
        if total_quantity + ask['quantity'] >= quantity:
            cost += (quantity - total_quantity) * ask['price']
            break
        else:
            cost += ask['quantity'] * ask['price']
            total_quantity += ask['quantity']
    return cost / quantity

def get_price_to_sell(order_book, quantity):
    total_quantity = 0
    revenue = 0
    for bid in order_book['bids']:
        if total_quantity + bid['quantity'] >= quantity:
            revenue += (quantity - total_quantity) * bid['price']
            break
        else:
            revenue += bid['quantity'] * bid['price']
            total_quantity += bid['quantity']
    return revenue / quantity

def main():
    coinbase_url = 'https://api.pro.coinbase.com/products/BTC-USD/book?level=2'
    gemini_url = 'https://api.gemini.com/v1/book/BTCUSD'

    coinbase_order_book_data = fetch_order_book(coinbase_url)
    gemini_order_book_data = fetch_order_book(gemini_url)
    
    kraken_url = 'https://api.kraken.com/0/public/Depth?pair=XBTUSD'
    order_book_data_kraken = fetch_order_book_kraken(kraken_url, 'XBTUSD')

    if coinbase_order_book_data and gemini_order_book_data and order_book_data_kraken:
        coinbase_order_book = normalize_order_book(coinbase_order_book_data)
        gemini_order_book = normalize_order_book(gemini_order_book_data)

        quantity = 10  # Bitcoin quantity

        coinbase_buy_price = get_price_to_buy(coinbase_order_book, quantity)
        coinbase_sell_price = get_price_to_sell(coinbase_order_book, quantity)
        gemini_buy_price = get_price_to_buy(gemini_order_book, quantity)
        gemini_sell_price = get_price_to_sell(gemini_order_book, quantity)
        
        kraken_buy_price = get_price_to_buy(order_book_data_kraken, quantity)
        kraken_sell_price = get_price_to_sell(order_book_data_kraken, quantity)

        print("Coinbase Pro:")
        print("Price to buy", quantity, "bitcoin:", coinbase_buy_price)
        print("Price to sell", quantity, "bitcoin:", coinbase_sell_price)

        print("\nGemini Exchange:")
        print("Price to buy", quantity, "bitcoin:", gemini_buy_price)
        print("Price to sell", quantity, "bitcoin:", gemini_sell_price)
        
        print("\nKraken Exchange:")
        print("Price to buy", quantity, "bitcoin:", kraken_buy_price)
        print("Price to sell", quantity, "bitcoin:", kraken_sell_price)
    else:
        print("Failed to fetch order books.")
        
        
    

if __name__ == "__main__":
    main()
