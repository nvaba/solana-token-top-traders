import requests
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

with open('top_traders.json', 'r') as file:
    data = json.load(file)

def getMakerData(maker):
    url = f"https://gmgn.ai/defi/quotation/v1/smartmoney/sol/walletNew/{maker}?period=7d" # change period to 30d if you want monthly data
    response = requests.get(url)
    print(f"[-] Dumping data..")
    if response.status_code == 200:
        makerData = response.json()
        if makerData['msg'] == "success":
            makerData = makerData['data']
            try:
                if makerData['pnl_7d'] is not None:
                    unrealizedProfit = makerData['unrealized_profit']
                    realizedProfit = makerData['realized_profit']
                    unrealizedPnL = makerData['unrealized_pnl']
                    weekPnL = makerData['pnl_7d'] * 100
                    monthPnL = makerData['pnl_30d'] * 100
                    winrate = makerData['winrate'] * 100

                    return {
                        "maker": maker,
                        "realized_profit": realizedProfit,
                        "unrealized_profit": unrealizedProfit,
                        "unrealized_pnl": unrealizedPnL,
                        "pnl_7d": weekPnL,
                        "pnl_30d": monthPnL,
                        "winrate": winrate
                    }
            except TypeError:
                pass
    return {"maker": maker, "error": "data fetch failed"}

makers = [trader_info['maker'] for topTraders in data.values() for trader_info in topTraders.values()]

results = []

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = {executor.submit(getMakerData, maker): maker for maker in makers}
    for future in as_completed(futures):
        result = future.result()
        if "error" not in result:
            results.append(result)

result_dict = {}
for result in results:
    maker = result.pop('maker')
    result_dict[maker] = result

with open('maker_data.json', 'w') as outfile:
    json.dump(result_dict, outfile, indent=4)
    print(f"[✅] Dumped profit data for {len(makers)} wallet(s)..")
