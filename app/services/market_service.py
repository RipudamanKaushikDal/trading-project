from typing import Optional

from domain.entities import Candles
import asyncio
import ccxt.async_support as ccxt



class MarketDataService:
    def __init__(self, exchange_name: str = 'kraken', timeframe: str = '1h'):
        self.exchange_name = exchange_name
        self.timeframe = timeframe
        self.exchange = getattr(ccxt, exchange_name)()

    async def resolve_symbol(self, markets: dict,  symbol: str) -> Optional[str]: 
        if symbol in markets:
            return symbol

        return None
       
    
    async def fetch_candles(self, symbol: str, limit: int = 100) -> list[Candles]:
        try:
            ohlcv = await self.exchange.fetch_ohlcv(symbol, timeframe=self.timeframe, limit=limit)
            candles = [Candles(
                timestamp=str(candle[0]),
                symbol=symbol,
                open=candle[1],
                high=candle[2],
                low=candle[3],
                close=candle[4],
                volume=candle[5]
            ) for candle in ohlcv]
            return candles
        except Exception as e:
            print(f"Error fetching candles: {e}")
            return []
        
    async def get_crypto_data(self) -> dict[str, list[Candles]]:
        try:
            markets = await self.exchange.load_markets()
            btc_symbol = await self.resolve_symbol(markets, "BTC/CAD") 
            eth_symbol = await self.resolve_symbol(markets, "ETH/CAD")

            if not btc_symbol or not eth_symbol:
                print("Available CAD markets sample:")
                cad = [m for m in self.exchange.symbols if "/CAD" in m]
                print(cad[:30])
                raise ValueError("BTC/CAD or ETH/CAD market not found on this exchange.")
            
            ohclv_tasks = [
                self.fetch_candles(btc_symbol, limit=100),
                self.fetch_candles(eth_symbol, limit=100)
            ]

            btc_candles, eth_candles = await asyncio.gather(*ohclv_tasks)
            return {
                "BTC/CAD": btc_candles,
                "ETH/CAD": eth_candles
            }
        finally:
            await self.exchange.close()

    def get_data(self):
        return asyncio.run(self.get_crypto_data())