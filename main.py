from bs4 import BeautifulSoup
import tls_client
import json
import re

session = tls_client.Session(client_identifier="chrome_105")

headers: dict = {
    'accept': '*/*',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'priority': 'u=1, i',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
}

cookies: dict = {
     '_photon_ta': 'ADD YOUR PHOTON COOKIE HE'
}

allData: dict = {}
totalTraders: int = 0

def getPairByCA(contractAddress: str) -> str:
    getPairCA = session.get(f"https://photon-sol.tinyastro.io/en/lp/{contractAddress}", headers=headers).text
    soup = BeautifulSoup(getPairCA, "html.parser")
    pair = soup.find('a')['href'].replace("//", "/")

    return pair

def getPoolID(pair: str):
    getPoolID = session.get(f"https://photon-sol.tinyastro.io/en/{pair}", headers=headers).text
    soup = BeautifulSoup(getPoolID, "html.parser").find('script', string=re.compile(r'window\.taConfig.show')).string
    poolMatch = re.search(r"'pool-id': (\d+)", soup)
    pool_id = poolMatch.group(1)

    return pool_id

with open('tokens.txt', 'r') as fp:
    contractAddresses = fp.read().splitlines()
    print(f"[-] Dumping data..")



for contractAddress in contractAddresses:
        pair = getPairByCA(contractAddress)
        pool_id = getPoolID(pair)
        grabTopTradersURL = f"https://photon-sol.tinyastro.io/api/events/top_traders?order_by=timestamp&order_dir=desc&pool_id={pool_id}&page=1"
        
        response = session.get(grabTopTradersURL, headers=headers, cookies=cookies).json()

        totalTraders += len(response['data'])

        allData[contractAddress] = {}
        
        for index, topTrader in enumerate(response['data']):
            signer = topTrader['attributes']['signer']
            boughtUsd = float(topTrader['attributes']['boughtUsd'])
            soldUsd = float(topTrader['attributes']['soldUsd'])
            unrealizedTokens = float(topTrader['attributes']['remainingTokens'])
            pumpFunBuy = False

            if boughtUsd == 0.0:
                 pumpFunBuy = True
            

            allData[contractAddress][f"topTrader_{index + 1}"] = {
                "pumpFunBuy": pumpFunBuy,
                "maker": signer,
                "amountBought": boughtUsd,
                "amountSold": soldUsd,
                "unrealizedTokens": unrealizedTokens
            }
        
with open('top_traders.json', 'w') as fp:
    json.dump(allData, fp, indent=4)
    print(f"[✅] Dumped {totalTraders * len(contractAddresses)} top traders for {len(contractAddresses)} tokens..")