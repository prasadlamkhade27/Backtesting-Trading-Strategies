import sys
sys.path.insert(0, '.')

try:
    print("Testing futures imports...")
    from strategies import AVAILABLE_STRATEGIES, get_strategy
    from utils.futures import (FUTURES_CONTRACTS, get_contract_spec, run_futures_backtest,
                               calculate_futures_metrics)
    
    print("\n All imports successful!")
    
    print("\nAvailable Futures Contracts:")
    for contract in ['ES', 'MES', 'NQ', 'MNQ', 'YM', 'MYM']:
        if contract in FUTURES_CONTRACTS:
            spec = get_contract_spec(contract)
            print(f"   {contract}: {spec['name']}")
    
    print("\nAvailable Futures Strategies:")
    for name in AVAILABLE_STRATEGIES:
        if 'Futures' in name:
            print(f"   {name}")
    
    print("\nInstantiating strategies...")
    es_strat = get_strategy('ES Futures - Mean Reversion + Trend')
    nq_strat = get_strategy('NQ Futures - Momentum')
    ym_strat = get_strategy('YM Futures - Trend Following')
    print("   ES Strategy initialized")
    print("   NQ Strategy initialized")
    print("   YM Strategy initialized")
    
    print("\n FUTURES SYSTEM READY FOR TRADING ")
    
except Exception as e:
    print(f" Error: {e}")
    import traceback
    traceback.print_exc()
