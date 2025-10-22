# DAS Trader Python API Client

<div align="center">

[![PyPI version](https://img.shields.io/pypi/v/das-bridge.svg)](https://pypi.org/project/das-bridge/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://img.shields.io/pypi/dm/das-bridge.svg)](https://pypi.org/project/das-bridge/)

[English](README.md) | [Español](README.es.md)

</div>

Complete Python client for the DAS Trader Pro CMD API that enables automated trading, real-time order management, position tracking, and market data streaming.

## 🚀 Key Features

### Core Trading Capabilities
- **Complete Trading**: Send, modify, and cancel orders (Market, Limit, Stop, Peg, etc.)
- **Real-Time Market Data**: Level 1, Level 2, and Time & Sales streaming
- **Position Management**: Automatic position tracking and real-time P&L
- **Historical Data**: Access to daily and minute charts
- **Specific Order Queries**: Get pending orders and executed orders separately

### 💰 Risk Management & Strategies (NEW!)
- **Dollar-Based Position Sizing**: Calculate shares to risk exact dollar amounts
- **Pre-Built Strategies**: Long/short with automatic stops and targets
- **Risk/Reward Calculations**: Built-in ratio calculations and validation
- **Scale-Out Support**: Exit positions at multiple target levels
- **Buying Power Validation**: Automatic position size validation
- **Slippage Modeling**: Conservative position sizing with slippage consideration

### Enhanced Features
- **Production-Grade Logging**: Structured logging with rotation and masking
- **Connection Resilience**: Circuit breaker pattern with exponential backoff
- **Configuration Management**: Environment variables and JSON config support
- **Enhanced Error Handling**: Categorized exceptions with recovery guidance
- **Multi-Format Parsing**: Handles various DAS response formats
- **Automatic Reconnection**: Robust connection handling with auto-reconnect
- **Native Asyncio**: High performance with concurrent operations
- **Type Safety**: Fully typed for better IDE support

## 📋 Requirements

- Python 3.8+
- DAS Trader Pro with CMD API enabled
- Valid DAS Trader account

## ⚡ Quick Installation

### From PyPI (Recommended)

```bash
pip install das-bridge
```

### From Source (Development)

```bash
git clone https://github.com/jefrnc/das-bridge.git
cd das-bridge
pip install -e .
```

### Optional Dependencies

```bash
# For notifications
pip install aiohttp

# For data analysis
pip install numpy pandas matplotlib

# For Windows desktop notifications
pip install win10toast  # Windows only

# For configuration management
pip install python-dotenv
```

## 🔧 Configuration

### 1. Environment Variables
```bash
cp .env.example .env
# Edit .env with your credentials
```

### 2. Basic Configuration
```python
# .env
DAS_HOST=localhost
DAS_PORT=9910
DAS_USERNAME=your_das_username
DAS_PASSWORD=your_das_password
DAS_ACCOUNT=your_das_account
```

## 🎯 Basic Usage

```python
import asyncio
from das_trader import DASTraderClient, OrderSide, OrderType, MarketDataLevel

async def main():
    # Create client
    client = DASTraderClient(host="localhost", port=9910)
    
    try:
        # Connect to DAS Trader
        await client.connect("your_username", "your_password", "your_account")
        
        # Get buying power
        bp = await client.get_buying_power()
        print(f"Buying Power: ${bp['buying_power']:,.2f}")
        
        # Subscribe to market data
        await client.subscribe_quote("AAPL", MarketDataLevel.LEVEL1)
        
        # Get quote
        quote = await client.get_quote("AAPL")
        print(f"AAPL: Bid ${quote.bid} | Ask ${quote.ask} | Last ${quote.last}")
        
        # Send order
        order_id = await client.send_order(
            symbol="AAPL",
            side=OrderSide.BUY,
            quantity=100,
            order_type=OrderType.LIMIT,
            price=150.00
        )
        print(f"Order sent: {order_id}")
        
        # Check positions
        positions = client.get_positions()
        for pos in positions:
            if not pos.is_flat():
                print(f"{pos.symbol}: {pos.quantity} shares, "
                      f"P&L: ${pos.unrealized_pnl:.2f}")
        
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

## 🔥 Enhanced Capabilities

### Advanced Order Management
```python
# Get specific order types
pending_orders = await client.get_pending_orders()
executed_orders = await client.get_executed_orders()

# Enhanced market data
level1_data = await client.get_level1_data("AAPL")
montage_data = await client.get_montage_data("AAPL")

# Robust buying power (handles multi-line responses)
bp_data = await client.get_buying_power()
```

### Production-Ready Features
```python
# Enhanced logging with rotation
from das_trader.enhanced_logger import EnhancedDASLogger

logger = EnhancedDASLogger(
    account_id="TRADER123",
    log_dir="logs/production",
    max_log_size=50*1024*1024  # 50MB rotation
)

# Connection resilience
from das_trader.connection_resilience import ConnectionResilientManager

resilient_mgr = ConnectionResilientManager(
    client.connection,
    max_reconnect_attempts=5,
    health_check_interval=60.0
)

# Configuration management
from das_trader.config_manager import load_das_config

config = load_das_config("config.json")
client = DASTraderClient(**config.get_client_config())
```

### Smart Locate Manager

das-bridge includes an intelligent locate manager that helps you analyze and request stock locates for short selling with volume and cost controls.

```python
# Analyze locate cost and availability
analysis = await client.locate_manager.analyze_locate(
    symbol="AAPL",
    desired_shares=500
)

print(f"Recommendation: {analysis['recommendation']}")
print(f"Locate Rate: ${analysis['locate_rate']:.4f}/share")
print(f"Total Cost: ${analysis['locate_total_cost']:.2f}")
print(f"Is ETB (Free): {analysis['is_etb']}")

# Check and optionally purchase locate
result = await client.locate_manager.ensure_locate(
    symbol="TSLA",
    shares_needed=100,
    auto_purchase=True  # Will purchase if approved
)

if result['success']:
    if result.get('purchase_confirmed'):
        print(f"Locate purchased! Cost: ${result['locate_total_cost']:.2f}")
    elif result.get('already_available'):
        print(f"Already have {result['current_locates']} shares located")

# Direct locate price inquiry
locate_info = await client.inquire_locate_price(
    symbol="NVDA",
    quantity=100,
    route="ALLROUTE"
)
```

**Features:**
- **Volume Control**: Limits shares to max % of daily volume (default 1%)
- **Cost Control**: Rejects locates above max cost thresholds
- **ETB Detection**: Identifies Easy to Borrow (free) stocks
- **Safety Checks**: Validates pricing data integrity
- **Block Sizing**: Always requests in 100-share blocks

**Configurable Parameters:**
- `max_volume_pct`: Maximum % of daily volume (default 1.0%)
- `max_cost_pct`: Maximum cost as % of position value (default 1.5%)
- `max_total_cost`: Maximum total cost per 100 shares (default $2.50)
- `block_size`: Share block size for locate requests (default 100)

See [examples/locate_example.py](examples/locate_example.py) for complete examples.

## 💰 Risk Management & Trading Strategies

das-bridge includes built-in risk management tools and pre-built trading strategies to help you trade safely and efficiently.

### Position Sizing Based on Dollar Risk

```python
# Calculate shares to risk exactly $200
entry_price = 150.00
stop_price = 149.00  # $1 stop
risk_amount = 200.00  # Risk exactly $200

shares = client.risk.calculate_shares_for_risk(
    entry_price=entry_price,
    stop_price=stop_price,
    risk_dollars=risk_amount
)
# Returns: 200 shares (200 / 1.00 = 200)

# With slippage consideration
shares = client.risk.calculate_shares_for_risk(
    entry_price=entry_price,
    stop_price=stop_price,
    risk_dollars=risk_amount,
    slippage=0.05  # Expect $0.05 slippage per share
)
# Returns: 190 shares (more conservative)
```

### Pre-Built Trading Strategies

#### Long Position with Automatic Stop
```python
# Buy AAPL with $200 risk, automatic position sizing and stop placement
result = await client.strategies.buy_with_risk_stop(
    symbol="AAPL",
    entry_price=150.00,
    stop_price=149.00,
    risk_amount=200.00,
    entry_type="mid",  # Enter at mid price
    target_price=152.00  # Optional profit target
)

if result.success:
    print(f"Position opened!")
    print(f"Entry Order: {result.entry_order_id}")
    print(f"Stop Order: {result.stop_order_id}")
    print(f"Target Order: {result.target_order_id}")
```

#### Short Position with Risk Management
```python
# Short TSLA with $300 risk
result = await client.strategies.sell_with_risk_stop(
    symbol="TSLA",
    entry_price=150.00,
    stop_price=151.00,  # Stop above entry for shorts
    risk_amount=300.00,
    target_price=147.00  # Target below entry
)
```

#### Close Position
```python
# Close entire position at market
result = await client.strategies.close_position("AAPL", exit_type="market")

# Close 50% at limit price
result = await client.strategies.close_position(
    "AAPL",
    exit_type="limit",
    limit_price=151.00,
    percentage=50.0
)
```

#### Scale Out Strategy
```python
# Scale out of position at multiple targets
result = await client.strategies.scale_out(
    symbol="AAPL",
    targets=[
        (151.00, 33.3),  # Sell 1/3 at $151
        (152.00, 33.3),  # Sell 1/3 at $152
        (153.00, 33.4)   # Sell remaining at $153
    ]
)
```

### Risk Calculations

```python
# Calculate risk/reward ratio
ratio = client.risk.calculate_risk_reward_ratio(
    entry_price=150.00,
    stop_price=149.00,  # $1 risk
    target_price=152.00  # $2 reward
)
# Returns: 2.0 (meaning 1:2 risk/reward ratio)

# Validate position against buying power
is_valid, msg = client.risk.validate_position_against_buying_power(
    entry_price=150.00,
    shares=500,
    buying_power=100000.00
)

# Calculate maximum shares for available capital
max_shares = client.risk.calculate_max_shares_for_buying_power(
    entry_price=150.00,
    buying_power=50000.00,
    margin_requirement=1.0  # 1.0 = cash account, 0.25 = 4x margin
)
```

See [examples/risk_based_trading.py](examples/risk_based_trading.py) for complete examples.

### ⏰ Extended Hours Trading

das-bridge validates trading sessions and handles order type restrictions automatically.

#### Session Restrictions

| Session | Hours (ET) | Allowed Orders | Strategies Default |
|---------|------------|----------------|-------------------|
| **Premarket** | 4:00 AM - 9:30 AM | ✅ Limit only | ❌ Blocked |
| **RTH** | 9:30 AM - 4:00 PM | ✅ All types | ✅ Full support |
| **After-Hours** | 4:00 PM - 8:00 PM | ✅ Limit only | ❌ Blocked |

**Important:** Stop orders are **NOT allowed** in premarket or after-hours.

#### Extended Hours Example

```python
# During premarket/after-hours - will be REJECTED by default
result = await client.strategies.buy_with_risk_stop(...)
# Returns: success=False, "Cannot execute strategy in premarket..."

# Enable extended hours mode (entry only, no stop)
result = await client.strategies.buy_with_risk_stop(
    symbol="AAPL",
    entry_price=150.0,
    stop_price=149.0,  # Used ONLY for position sizing
    risk_amount=200.0,
    entry_type="limit",
    allow_extended_hours=True  # ✅ Enable extended hours
)

if result.success:
    print(f"Entry placed: {result.entry_order_id}")
    print(f"Stop placed: {result.stop_order_id}")  # None
    print(result.message)
    # "Long position opened: 200 shares of AAPL
    #  WARNING: Stop order NOT placed (premarket restriction).
    #  Suggested stop: $149.00. You must manage stop manually."
```

See [docs/TRADING_SESSIONS.md](docs/TRADING_SESSIONS.md) for complete details.

## 📊 Supported Order Types

```python
# Market Order
await client.send_order("AAPL", OrderSide.BUY, 100, OrderType.MARKET)

# Limit Order
await client.send_order("AAPL", OrderSide.BUY, 100, OrderType.LIMIT, price=150.00)

# Stop Loss
await client.send_order("AAPL", OrderSide.SELL, 100, OrderType.STOP, stop_price=145.00)

# Stop Limit
await client.send_order("AAPL", OrderSide.SELL, 100, OrderType.STOP_LIMIT,
                       price=148.00, stop_price=145.00)

# Trailing Stop
await client.send_order("AAPL", OrderSide.SELL, 100, OrderType.TRAILING_STOP,
                       trail_amount=2.00)
```

## 📈 Callbacks and Events

```python
# Order callbacks
def on_order_filled(order):
    print(f"Order filled: {order.symbol}")

def on_order_rejected(order):
    print(f"Order rejected: {order.symbol}")

client.orders.register_callback("order_filled", on_order_filled)
client.orders.register_callback("order_rejected", on_order_rejected)

# Position callbacks
def on_position_update(position):
    print(f"Position updated: {position.symbol} P&L: ${position.unrealized_pnl:.2f}")

client.positions.register_callback("position_updated", on_position_update)

# Market data callbacks
def on_quote_update(quote):
    print(f"{quote.symbol}: ${quote.last}")

client.market_data.register_callback("quote_update", on_quote_update)
```

## 🤖 Advanced Examples

### Basic Trading Bot
```python
# See examples/trading_bot.py
python examples/trading_bot.py
```

### Portfolio Monitor
```python
# See examples/portfolio_monitor.py
python examples/portfolio_monitor.py
```

### Market Data Streaming
```python
# See examples/market_data_streaming.py
python examples/market_data_streaming.py
```

## 🛡️ Risk Management

```python
# Configuration in config.example.py
MAX_POSITION_SIZE = 1000
MAX_ORDER_VALUE = 50000.0
STOP_LOSS_PERCENT = 0.02  # 2%
TAKE_PROFIT_PERCENT = 0.04  # 4%

# Paper Trading Mode
PAPER_TRADING_MODE = True
PAPER_TRADING_INITIAL_BALANCE = 100000.0
```

## 📚 API Documentation

### Main Classes

- **`DASTraderClient`**: Main client for interacting with DAS Trader
- **`OrderManager`**: Order management and status tracking
- **`PositionManager`**: Position tracking and P&L
- **`MarketDataManager`**: Market data streaming and caching
- **`ConnectionManager`**: TCP connection handling and reconnection
- **`NotificationManager`**: Multi-platform notification system

### Main Enums

- **`OrderType`**: MARKET, LIMIT, STOP, STOP_LIMIT, PEG, TRAILING_STOP
- **`OrderSide`**: BUY, SELL, SHORT, COVER
- **`OrderStatus`**: PENDING, NEW, PARTIALLY_FILLED, FILLED, CANCELLED, REJECTED
- **`TimeInForce`**: DAY, GTC, IOC, FOK, MOO, MOC
- **`MarketDataLevel`**: LEVEL1, LEVEL2, TIME_SALES

## 🧪 Testing

```bash
# Run tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=das_trader --cov-report=html
```

## 🔐 Security

- **Never** commit credentials in code
- Use environment variables for sensitive configuration
- The `.env` file is in `.gitignore`
- Consider using paper trading mode for testing

## 📝 Logging

```python
import logging
logging.basicConfig(level=logging.INFO)

# The client includes detailed logging:
# - Connections and authentication
# - Sent and received orders
# - Market data streaming
# - Errors and reconnections
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a branch for your feature (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Open a Pull Request

## 📄 License

This project is under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This software is for educational and development purposes. Automated trading carries significant financial risks. Use at your own risk and always consider:

- Thorough testing in paper trading mode
- Proper risk management
- Constant position monitoring
- Compliance with local regulations

## 🔗 Related Projects

- **[das-api-examples](https://github.com/jefrnc/das-api-examples)**: Practical examples and tests for the DAS Trader Pro CMD API
  - Direct TCP connection tests
  - API feature verification
  - Configuration guides and troubleshooting

## 📚 Useful Links

- [DAS Trader Pro Documentation](https://dastrader.com)
- [CMD API Manual](CMD%20API%20Manual.pdf)
- [Usage Examples](examples/)
- [Tests](tests/)

## 📞 Support

To report bugs or request features:
- Open an [Issue](https://github.com/jefrnc/das-bridge/issues)
- Check the [documentation](examples/)
- Consult the [examples](examples/)

---

**Developed with ❤️ for the algorithmic trading community**