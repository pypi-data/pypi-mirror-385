"""Market data management for DAS Trader API."""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable, Set
from datetime import datetime, date
from decimal import Decimal
from dataclasses import dataclass, field
from collections import defaultdict, deque
import threading

from .constants import (
    Commands, MessagePrefix, MarketDataLevel, ChartType
)
from .exceptions import DASMarketDataError, DASInvalidSymbolError
from .utils import parse_decimal, validate_symbol, parse_timestamp
from .parsers import DASResponseParser, SmallCapsParser, ParsedQuote

logger = logging.getLogger(__name__)


@dataclass
class Quote:
    # Basic quote data
    symbol: str
    bid: Decimal
    ask: Decimal
    last: Decimal
    bid_size: int
    ask_size: int
    volume: int
    high: Optional[Decimal] = None
    low: Optional[Decimal] = None
    open: Optional[Decimal] = None
    close: Optional[Decimal] = None
    prev_close: Optional[Decimal] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def spread(self) -> Decimal:
        return self.ask - self.bid
    
    @property
    def mid_price(self) -> Decimal:
        # Midpoint calculation
        return (self.bid + self.ask) / 2
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "bid": float(self.bid),
            "ask": float(self.ask),
            "last": float(self.last),
            "bid_size": self.bid_size,
            "ask_size": self.ask_size,
            "volume": self.volume,
            "spread": float(self.spread),
            "mid_price": float(self.mid_price),
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class Level2Quote:
    """Level 2 market depth data."""
    symbol: str
    side: str  # "BID" or "ASK"
    price: Decimal
    size: int
    mmid: str  # Market maker ID
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class TimeSale:
    symbol: str
    price: Decimal
    size: int
    timestamp: datetime
    condition: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "price": float(self.price),
            "size": self.size,
            "timestamp": self.timestamp.isoformat(),
            "condition": self.condition,
        }


@dataclass
class ChartBar:
    """Chart bar data."""
    # TODO: Add support for extended hours bars
    symbol: str
    chart_type: ChartType
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "chart_type": self.chart_type.value,
            "open": float(self.open),
            "high": float(self.high),
            "low": float(self.low),
            "close": float(self.close),
            "volume": self.volume,
            "timestamp": self.timestamp.isoformat(),
        }


class MarketDataManager:
    """Manages market data subscriptions and data."""
    
    def __init__(self, connection_manager):
        self.connection = connection_manager
        
        self._quotes: Dict[str, Quote] = {}
        self._level2_data: Dict[str, Dict[str, List[Level2Quote]]] = defaultdict(lambda: {"BID": [], "ASK": []})
        self._time_sales: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self._chart_data: Dict[str, Dict[ChartType, List[ChartBar]]] = defaultdict(dict)
        
        self._quote_subscriptions: Set[str] = set()
        self._level2_subscriptions: Set[str] = set()
        self._time_sales_subscriptions: Set[str] = set()
        
        self._callbacks: Dict[str, List[Callable]] = {
            "quote_update": [],
            "level2_update": [],
            "time_sales": [],
            "chart_update": [],
        }
        
        self._data_lock = threading.RLock()
        
        self._register_handlers()
    
    def _register_handlers(self):
        self.connection.register_handler("QUOTE", self._handle_quote_message)
        self.connection.register_handler("LEVEL2", self._handle_level2_message)
        self.connection.register_handler("TIME_SALES", self._handle_time_sales_message)
        self.connection.register_handler("CHART", self._handle_chart_message)
    
    async def subscribe_quote(self, symbol: str, level: MarketDataLevel = MarketDataLevel.LEVEL1):
        """Subscribe to quote data for a symbol."""
        if not validate_symbol(symbol):
            raise DASInvalidSymbolError(f"Invalid symbol: {symbol}")
        
        symbol = symbol.upper()
        
        try:
            command = f"{Commands.SUBSCRIBE} {symbol} {level.value}"
            await self.connection.send_command(command, wait_response=False)
            
            with self._data_lock:
                if level == MarketDataLevel.LEVEL1:
                    self._quote_subscriptions.add(symbol)
                elif level == MarketDataLevel.LEVEL2:
                    self._level2_subscriptions.add(symbol)
                elif level == MarketDataLevel.TIME_SALES:
                    self._time_sales_subscriptions.add(symbol)
            
            logger.info(f"Subscribed to {level.value} data for {symbol}")
            
        except Exception as e:
            raise DASMarketDataError(f"Failed to subscribe to {symbol}: {e}")
    
    async def unsubscribe_quote(self, symbol: str, level: MarketDataLevel = MarketDataLevel.LEVEL1):
        """Unsubscribe from quote data for a symbol."""
        symbol = symbol.upper()
        
        try:
            command = f"{Commands.UNSUBSCRIBE} {symbol} {level.value}"
            await self.connection.send_command(command, wait_response=False)
            
            with self._data_lock:
                if level == MarketDataLevel.LEVEL1:
                    self._quote_subscriptions.discard(symbol)
                elif level == MarketDataLevel.LEVEL2:
                    self._level2_subscriptions.discard(symbol)
                    if symbol in self._level2_data:
                        del self._level2_data[symbol]
                elif level == MarketDataLevel.TIME_SALES:
                    self._time_sales_subscriptions.discard(symbol)
                    if symbol in self._time_sales:
                        del self._time_sales[symbol]
            
            logger.info(f"Unsubscribed from {level.value} data for {symbol}")
            
        except Exception as e:
            logger.error(f"Failed to unsubscribe from {symbol}: {e}")
    
    async def get_quote(self, symbol: str) -> Optional[Quote]:
        """Get current quote for a symbol."""
        symbol = symbol.upper()

        with self._data_lock:
            if symbol in self._quotes:
                return self._quotes[symbol]

        try:
            command = f"{Commands.GET_QUOTE} {symbol}"
            response = await self.connection.send_command(
                command,
                wait_response=True,
                response_type="QUOTE"
            )

            if response and response.get("type") == "QUOTE":
                quote = self._create_quote_from_message(response)
                if quote:
                    with self._data_lock:
                        self._quotes[symbol] = quote
                    return quote

            return None

        except Exception as e:
            logger.error(f"Failed to get quote for {symbol}: {e}")
            return None

    async def get_level1_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get Level 1 market data using correct DAS format like short-fade-das."""
        if not validate_symbol(symbol):
            raise DASInvalidSymbolError(f"Invalid symbol: {symbol}")

        symbol = symbol.upper()

        # Try multiple command formats like short-fade-das does
        commands_to_try = [
            f"{Commands.GET_LV1} {symbol}",        # GET Lv1 SYMBOL (documented format)
            f"{Commands.GET_LEVEL1} {symbol}",     # GET LEVEL1 SYMBOL (full name)
            f"{Commands.GET_MONTAGE} {symbol}",    # GET MONTAGE SYMBOL (DAS montage)
            f"{Commands.GET_MARKET} {symbol}",     # GET MARKET SYMBOL (market data)
            f"{Commands.GET_QUOTE} {symbol}",      # GETQUOTE SYMBOL (original format)
        ]

        logger.info(f"🔍 Getting Level 1 data for {symbol}")

        for i, command in enumerate(commands_to_try, 1):
            try:
                logger.info(f"   {i}. Trying: {command}")

                response = await self.connection.send_command(
                    command,
                    wait_response=True,
                    timeout=5.0
                )

                if response:
                    logger.info(f"   ✅ Command {i} successful: {command}")

                    # Parse response based on format
                    if isinstance(response, dict):
                        return response
                    else:
                        # Parse raw response text
                        return {
                            "symbol": symbol,
                            "command": command,
                            "raw_response": str(response),
                            "success": True
                        }

            except Exception as e:
                logger.warning(f"   ❌ Command {i} failed: {e}")
                continue

        logger.error(f"❌ All Level 1 commands failed for {symbol}")
        return None

    async def get_montage_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get montage data for symbol using DAS montage command."""
        if not validate_symbol(symbol):
            raise DASInvalidSymbolError(f"Invalid symbol: {symbol}")

        symbol = symbol.upper()

        try:
            command = f"{Commands.GET_MONTAGE} {symbol}"
            response = await self.connection.send_command(
                command,
                wait_response=True,
                timeout=5.0
            )

            if response:
                return {
                    "symbol": symbol,
                    "montage_data": response,
                    "success": True
                }

            return None

        except Exception as e:
            logger.error(f"Failed to get montage data for {symbol}: {e}")
            return None
    
    async def get_chart_data(
        self,
        symbol: str,
        chart_type: ChartType,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        bars: int = 100
    ) -> List[ChartBar]:
        """Get historical chart data.

        Note: Chart data is obtained via subscription (SB Symbol ChartType).
        The old GETCHART command is invalid and has been replaced with the subscription model.
        """
        if not validate_symbol(symbol):
            raise DASInvalidSymbolError(f"Invalid symbol: {symbol}")

        symbol = symbol.upper()

        try:
            # Use subscription command: SB Symbol ChartType (e.g., "SB AAPL Minchart")
            command = f"{Commands.SUBSCRIBE} {symbol} {chart_type.value}"

            # Note: start_date, end_date, and bars parameters are not supported
            # by the DAS API subscription model. These would need to be handled
            # differently (e.g., filtering received data on the client side)
            if start_date or end_date or bars != 100:
                logger.warning(
                    f"Chart subscription does not support start_date, end_date, or bars parameters. "
                    f"All available chart data will be received for {symbol}"
                )

            await self.connection.send_command(command, wait_response=False)

            await asyncio.sleep(1.0)

            with self._data_lock:
                return self._chart_data.get(symbol, {}).get(chart_type, [])

        except Exception as e:
            raise DASMarketDataError(f"Failed to get chart data for {symbol}: {e}")
    
    def get_level2_book(self, symbol: str) -> Dict[str, List[Level2Quote]]:
        """Get current Level 2 order book."""
        symbol = symbol.upper()
        
        with self._data_lock:
            if symbol in self._level2_data:
                return {
                    "bids": sorted(self._level2_data[symbol]["BID"], 
                                 key=lambda x: x.price, reverse=True),
                    "asks": sorted(self._level2_data[symbol]["ASK"], 
                                 key=lambda x: x.price),
                }
            return {"bids": [], "asks": []}
    
    def get_time_sales(self, symbol: str, limit: int = 100) -> List[TimeSale]:
        """Get recent time and sales data."""
        symbol = symbol.upper()
        
        with self._data_lock:
            if symbol in self._time_sales:
                sales = list(self._time_sales[symbol])
                return sales[-limit:] if len(sales) > limit else sales
            return []
    
    def register_callback(self, event: str, callback: Callable):
        """Register a callback for market data events."""
        if event in self._callbacks:
            self._callbacks[event].append(callback)
            logger.debug(f"Registered callback for event: {event}")
    
    def unregister_callback(self, event: str, callback: Callable):
        """Unregister a callback for market data events."""
        if event in self._callbacks and callback in self._callbacks[event]:
            self._callbacks[event].remove(callback)
            logger.debug(f"Unregistered callback for event: {event}")
    
    async def _handle_quote_message(self, message: Dict[str, Any]):
        """Handle quote update messages."""
        quote = self._create_quote_from_message(message)
        if not quote:
            return
        
        with self._data_lock:
            self._quotes[quote.symbol] = quote
        
        await self._trigger_callbacks("quote_update", quote)
    
    async def _handle_level2_message(self, message: Dict[str, Any]):
        """Handle Level 2 update messages."""
        symbol = message.get("symbol")
        if not symbol:
            return
        
        symbol = symbol.upper()
        side = message.get("side", "").upper()
        
        if side not in ["BID", "ASK"]:
            return
        
        # Create Level 2 quote
        level2_quote = Level2Quote(
            symbol=symbol,
            side=side,
            price=message.get("price", Decimal("0")),
            size=message.get("size", 0),
            mmid=message.get("mmid", ""),
            timestamp=message.get("timestamp", datetime.now())
        )
        
        with self._data_lock:
            book = self._level2_data[symbol][side]
            
            book = [q for q in book if q.mmid != level2_quote.mmid]
            
            if level2_quote.size > 0:
                book.append(level2_quote)
            
            self._level2_data[symbol][side] = book
        
        await self._trigger_callbacks("level2_update", {
            "symbol": symbol,
            "quote": level2_quote,
            "book": self.get_level2_book(symbol)
        })
    
    async def _handle_time_sales_message(self, message: Dict[str, Any]):
        """Handle time and sales messages."""
        symbol = message.get("symbol")
        if not symbol:
            return
        
        symbol = symbol.upper()
        
        time_sale = TimeSale(
            symbol=symbol,
            price=message.get("price", Decimal("0")),
            size=message.get("size", 0),
            timestamp=message.get("timestamp", datetime.now()),
            condition=message.get("condition")
        )
        
        with self._data_lock:
            self._time_sales[symbol].append(time_sale)
        
        await self._trigger_callbacks("time_sales", time_sale)
    
    async def _handle_chart_message(self, message: Dict[str, Any]):
        """Handle chart data messages."""
        symbol = message.get("symbol")
        chart_type_str = message.get("chart_type")
        
        if not symbol or not chart_type_str:
            return
        
        symbol = symbol.upper()
        
        try:
            chart_type = ChartType(chart_type_str)
        except ValueError:
            return
        
        chart_bar = ChartBar(
            symbol=symbol,
            chart_type=chart_type,
            open=message.get("open", Decimal("0")),
            high=message.get("high", Decimal("0")),
            low=message.get("low", Decimal("0")),
            close=message.get("close", Decimal("0")),
            volume=message.get("volume", 0),
            timestamp=message.get("timestamp", datetime.now())
        )
        
        with self._data_lock:
            if symbol not in self._chart_data:
                self._chart_data[symbol] = {}
            if chart_type not in self._chart_data[symbol]:
                self._chart_data[symbol][chart_type] = []
            
            self._chart_data[symbol][chart_type].append(chart_bar)
        
        await self._trigger_callbacks("chart_update", chart_bar)
    
    def _create_quote_from_message(self, message: Dict[str, Any]) -> Optional[Quote]:
        symbol = message.get("symbol")
        if not symbol:
            return None
        
        return Quote(
            symbol=symbol.upper(),
            bid=message.get("bid", Decimal("0")),
            ask=message.get("ask", Decimal("0")),
            last=message.get("last", Decimal("0")),
            bid_size=message.get("bid_size", 0),
            ask_size=message.get("ask_size", 0),
            volume=message.get("volume", 0),
            high=message.get("high"),
            low=message.get("low"),
            open=message.get("open"),
            close=message.get("close"),
            prev_close=message.get("prev_close"),
            timestamp=message.get("timestamp", datetime.now())
        )
    
    async def _trigger_callbacks(self, event: str, data: Any):
        callbacks = self._callbacks.get(event, [])
        for callback in callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(data)
                else:
                    callback(data)
            except Exception as e:
                logger.error(f"Error in callback for {event}: {e}")
    
    def clear_all_data(self):
        with self._data_lock:
            self._quotes.clear()
            self._level2_data.clear()
            self._time_sales.clear()
            self._chart_data.clear()
            logger.info("Cleared all market data from memory")
    
    # New methods for parsing raw CMD API responses
    def process_raw_response(self, response: str) -> Dict[str, Any]:
        """
        Process raw response from CMD API using the new parsers.
        Used especially for small caps data from Zimtra.
        """
        parsed_data = DASResponseParser.parse_response(response)
        
        # Process quotes
        for quote_data in parsed_data.get('quotes', []):
            if isinstance(quote_data, ParsedQuote):
                quote = Quote(
                    symbol=quote_data.symbol,
                    bid=Decimal(str(quote_data.bid)),
                    ask=Decimal(str(quote_data.ask)),
                    last=Decimal(str(quote_data.last)),
                    bid_size=quote_data.bid_size,
                    ask_size=quote_data.ask_size,
                    volume=quote_data.volume,
                    timestamp=datetime.now()
                )
                with self._data_lock:
                    self._quotes[quote.symbol] = quote
        
        # Return parsed data for further processing
        return parsed_data
    
    def process_small_caps_data(self, response: str) -> Dict[str, Any]:
        """
        Process small caps data specifically.
        Filters and processes data for Zimtra small caps.
        """
        parsed_data = SmallCapsParser.parse_response(response)
        filtered_data = SmallCapsParser.filter_small_caps(parsed_data)
        
        # Process each small cap symbol
        for symbol in SmallCapsParser.SMALL_CAPS_SYMBOLS:
            summary = SmallCapsParser.get_symbol_summary(filtered_data, symbol)
            if summary['total_orders'] > 0:
                logger.info(f"Small cap {symbol}: {summary['total_orders']} orders, "
                          f"avg price: ${summary['avg_price']:.2f}")
        
        return filtered_data
    
    async def subscribe_small_caps(self, symbols: Optional[List[str]] = None):
        """
        Subscribe to small caps symbols.
        If no symbols provided, subscribes to default Zimtra small caps.
        """
        if symbols is None:
            symbols = SmallCapsParser.SMALL_CAPS_SYMBOLS
        
        for symbol in symbols:
            await self.subscribe_quote(symbol, MarketDataLevel.LEVEL1)
            logger.info(f"Subscribed to small cap: {symbol}")
    
    async def unsubscribe_all(self):
        with self._data_lock:
            quote_subs = list(self._quote_subscriptions)
            level2_subs = list(self._level2_subscriptions)
            ts_subs = list(self._time_sales_subscriptions)
        
        for symbol in quote_subs:
            await self.unsubscribe_quote(symbol, MarketDataLevel.LEVEL1)
        
        for symbol in level2_subs:
            await self.unsubscribe_quote(symbol, MarketDataLevel.LEVEL2)
        
        for symbol in ts_subs:
            await self.unsubscribe_quote(symbol, MarketDataLevel.TIME_SALES)
        
        logger.info("Unsubscribed from all market data")
    
    def get_subscriptions(self) -> Dict[str, List[str]]:
        """Get current subscriptions."""
        with self._data_lock:
            return {
                "level1": list(self._quote_subscriptions),
                "level2": list(self._level2_subscriptions),
                "time_sales": list(self._time_sales_subscriptions),
            }