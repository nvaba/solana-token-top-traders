import requests
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

with open('top_traders.json', 'r') as file:
    data = json.load(file)

def getMakerData(maker):
    url = f"https://gmgn.ai/defi/quotation/v1/smartmoney/sol/walletNew/{maker}?period=7d"
    response = requests.get(url)
    if response.status_code == 200:
        makerData = response.json()
        if makerData['msg'] == "success":
            makerData = makerData['data']
            try:
                return f"{maker} // RP: {makerData['realized_profit']:.2f} // URP: {makerData['unrealized_profit']:.2f} // 7d PnL: {makerData['pnl_7d'] * 100:.2f}%"
            except TypeError:
                return f"{maker} PnL is None"
    return f"{maker} data fetch failed"

makers = [trader_info['maker'] for topTraders in data.values() for trader_info in topTraders.values()]

results = []

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = {executor.submit(getMakerData, maker): maker for maker in makers}
    for future in as_completed(futures):
        result = future.result()
        results.append(result)
        print(result)
