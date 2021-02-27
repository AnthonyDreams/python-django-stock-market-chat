import requests
from operator import itemgetter

class InvalidStock(Exception):
    pass

class StockService:
    def getStock(self, stock_code):
        response = requests.get(f"https://stooq.com/q/l/?s={stock_code}&f=sd2t2ohlcv&h&e=csv")
        response.raise_for_status()
        return StockService.get_response_message(response)
            
 
    @staticmethod
    def get_response_message(csv_):
        try:
            clean_data = csv_.text.split()
            columns = clean_data[0].split(",")
            data = {k: v for k, v in zip(columns, clean_data[1].split(","))}
            share_columns = ["High", "Low", "Open", "Close"]
            per_share = list(map(float, itemgetter(*share_columns)(data)))
        except:
            raise InvalidStock
        

        
        return f"{data['Symbol']} quote is {sum(per_share)} per share."
