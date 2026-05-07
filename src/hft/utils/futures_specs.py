"""
Futures Contract Specifications
Defines contract specs for various futures instruments
"""

FUTURES_CONTRACTS = {
    # E-mini S&P 500
    'ES': {
        'name': 'E-mini S&P 500',
        'multiplier': 50,
        'tick_size': 0.25,
        'tick_value': 12.50,
        'min_move': 0.25,
        'initial_margin': 13475,
        'maintenance_margin': 10780,
        'contract_size': 'E-mini',
        'description': 'E-mini S&P 500 Futures',
    },
    
    'MES': {
        'name': 'Micro E-mini S&P 500',
        'multiplier': 5,
        'tick_size': 0.25,
        'tick_value': 1.25,
        'min_move': 0.25,
        'initial_margin': 1348,
        'maintenance_margin': 1078,
        'contract_size': 'Micro',
        'description': 'Micro E-mini S&P 500 Futures (1/10 of ES)',
    },
    
    'NQ': {
        'name': 'E-mini NASDAQ 100',
        'multiplier': 20,
        'tick_size': 0.25,
        'tick_value': 5.00,
        'min_move': 0.25,
        'initial_margin': 12925,
        'maintenance_margin': 10340,
        'contract_size': 'E-mini',
        'description': 'E-mini NASDAQ 100 Futures',
    },
    
    'MNQ': {
        'name': 'Micro E-mini NASDAQ 100',
        'multiplier': 2,
        'tick_size': 0.25,
        'tick_value': 0.50,
        'min_move': 0.25,
        'initial_margin': 1293,
        'maintenance_margin': 1034,
        'contract_size': 'Micro',
        'description': 'Micro E-mini NASDAQ 100 Futures (1/10 of NQ)',
    },
    
    'YM': {
        'name': 'E-mini Dow Jones',
        'multiplier': 5,
        'tick_size': 1.0,
        'tick_value': 5.00,
        'min_move': 1.0,
        'initial_margin': 7700,
        'maintenance_margin': 6160,
        'contract_size': 'E-mini',
        'description': 'E-mini Dow Jones Futures',
    },
    
    'MYM': {
        'name': 'Micro E-mini Dow Jones',
        'multiplier': 0.5,
        'tick_size': 1.0,
        'tick_value': 0.50,
        'min_move': 1.0,
        'initial_margin': 770,
        'maintenance_margin': 616,
        'contract_size': 'Micro',
        'description': 'Micro E-mini Dow Jones Futures',
    },
    
    'CL': {
        'name': 'Crude Oil',
        'multiplier': 100,
        'tick_size': 0.01,
        'tick_value': 1.00,
        'min_move': 0.01,
        'initial_margin': 4730,
        'maintenance_margin': 3500,
        'contract_size': 'Standard',
        'description': 'WTI Crude Oil Futures',
    },
    
    'GC': {
        'name': 'Gold',
        'multiplier': 100,
        'tick_size': 0.10,
        'tick_value': 10.00,
        'min_move': 0.10,
        'initial_margin': 5500,
        'maintenance_margin': 5000,
        'contract_size': 'Standard',
        'description': 'Gold Futures',
    },
    
    'MGC': {
        'name': 'Micro Gold',
        'multiplier': 10,
        'tick_size': 0.10,
        'tick_value': 1.00,
        'min_move': 0.10,
        'initial_margin': 550,
        'maintenance_margin': 500,
        'contract_size': 'Micro',
        'description': 'Micro Gold Futures (1/10 of GC)',
    },
}


def get_contract_spec(symbol: str) -> dict:
    """Get contract specifications for a futures symbol"""
    if symbol not in FUTURES_CONTRACTS:
        raise ValueError(f"Unknown futures contract: {symbol}")
    return FUTURES_CONTRACTS[symbol]


def calculate_position_size_futures(
    account_balance: float,
    risk_pct: float,
    entry_price: float,
    stop_loss_price: float,
    contract_symbol: str
) -> tuple:
    """Calculate position size for futures based on risk percentage"""
    spec = get_contract_spec(contract_symbol)
    
    risk_amount = account_balance * risk_pct
    price_risk = abs(entry_price - stop_loss_price)
    
    dollar_risk_per_contract = price_risk * spec['multiplier']
    
    if dollar_risk_per_contract > 0:
        contracts = risk_amount / dollar_risk_per_contract
        contracts = max(1, int(contracts))
    else:
        contracts = 0
    
    return contracts, risk_amount, price_risk


def calculate_margin_requirement(
    contracts: int,
    contract_symbol: str,
    use_maintenance: bool = False
) -> float:
    """Calculate required margin for position"""
    spec = get_contract_spec(contract_symbol)
    
    if use_maintenance:
        margin_per_contract = spec['maintenance_margin']
    else:
        margin_per_contract = spec['initial_margin']
    
    return contracts * margin_per_contract


def calculate_profit_loss(
    entry_price: float,
    exit_price: float,
    contracts: int,
    contract_symbol: str,
    position_type: str = 'LONG'
) -> float:
    """Calculate P&L for futures trade"""
    spec = get_contract_spec(contract_symbol)
    
    price_diff = exit_price - entry_price
    if position_type == 'SHORT':
        price_diff = entry_price - exit_price
    
    return price_diff * spec['multiplier'] * contracts
