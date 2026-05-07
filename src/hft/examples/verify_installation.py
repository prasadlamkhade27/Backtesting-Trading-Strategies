"""
HFT Trading System - Installation Verification
Verify that all components are properly installed and working
"""

import sys
import os
from pathlib import Path


def check_files_exist():
    """Check that all required files exist"""
    print("\n" + "="*70)
    print("CHECKING FILE STRUCTURE")
    print("="*70)
    
    required_files = {
        'MT5/EA': [
            ('mt5_ea/HFTScalpingEA.mq5', 'MT5 Expert Advisor'),
            ('mt5_ea/HFT_EA_README.md', 'MT5 Documentation'),
        ],
        'Python/Strategies': [
            ('strategies/hft_scalping_strategy.py', 'HFT Strategy'),
        ],
        'Python/Utils': [
            ('utils/hft_backtest_engine.py', 'Backtesting Engine'),
        ],
        'Python/Config': [
            ('hft_config.py', 'Configuration Presets'),
        ],
        'Documentation': [
            ('HFT_SYSTEM_README.md', 'System Documentation'),
            ('INTEGRATION_GUIDE.md', 'Integration Guide'),
            ('HFT_TRADING_EXAMPLE.py', 'Code Examples'),
            ('HFT_QUICK_REFERENCE.py', 'Quick Reference'),
            ('HFT_IMPLEMENTATION_SUMMARY.md', 'Implementation Summary'),
        ]
    }
    
    all_exists = True
    for category, files in required_files.items():
        print(f"\n{category}:")
        for filepath, description in files:
            exists = os.path.exists(filepath)
            status = "✅" if exists else "❌"
            print(f"  {status} {filepath:<40} ({description})")
            if not exists:
                all_exists = False
    
    return all_exists


def check_python_imports():
    """Check that Python modules can be imported"""
    print("\n" + "="*70)
    print("CHECKING PYTHON IMPORTS")
    print("="*70)
    
    imports_to_check = [
        ('pandas', 'Data processing'),
        ('numpy', 'Numerical computing'),
    ]
    
    print("\nRequired Python packages:")
    all_imports_ok = True
    for module_name, description in imports_to_check:
        try:
            __import__(module_name)
            print(f"  ✅ {module_name:<20} ({description})")
        except ImportError:
            print(f"  ❌ {module_name:<20} ({description}) - NOT INSTALLED")
            all_imports_ok = False
    
    return all_imports_ok


def check_hft_modules():
    """Check that HFT modules can be imported"""
    print("\n" + "="*70)
    print("CHECKING HFT MODULES")
    print("="*70)
    
    hft_modules = [
        ('strategies.hft_scalping_strategy', 'HFTScalpingStrategy'),
        ('strategies.hft_scalping_strategy', 'HFTRiskManager'),
        ('strategies.hft_scalping_strategy', 'HFTPerformanceAnalyzer'),
        ('utils.hft_backtest_engine', 'HFTBacktestEngine'),
        ('utils.hft_backtest_engine', 'ExecutionParams'),
        ('utils.hft_backtest_engine', 'ExecutionVenue'),
        ('hft_config', 'CONFIG_PRESETS'),
    ]
    
    print("\nHFT Python modules:")
    all_ok = True
    
    for module_path, class_name in hft_modules:
        try:
            module = __import__(module_path, fromlist=[class_name])
            obj = getattr(module, class_name)
            print(f"  ✅ {class_name:<30} from {module_path}")
        except (ImportError, AttributeError) as e:
            print(f"  ❌ {class_name:<30} from {module_path} - {str(e)[:40]}")
            all_ok = False
    
    return all_ok


def verify_file_contents():
    """Verify key files have content"""
    print("\n" + "="*70)
    print("VERIFYING FILE CONTENTS")
    print("="*70)
    
    files_to_check = [
        ('mt5_ea/HFTScalpingEA.mq5', 'HFTScalpingEA', 500),
        ('strategies/hft_scalping_strategy.py', 'HFTScalpingStrategy', 100),
        ('utils/hft_backtest_engine.py', 'HFTBacktestEngine', 100),
        ('hft_config.py', 'CONFIG_PRESETS', 100),
    ]
    
    print("\nFile content verification:")
    all_ok = True
    
    for filepath, search_string, min_size in files_to_check:
        if not os.path.exists(filepath):
            print(f"  ❌ {filepath:<40} - File not found")
            all_ok = False
            continue
        
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        has_content = len(content) > min_size
        has_class = search_string in content
        
        if has_content and has_class:
            size_kb = len(content) / 1024
            print(f"  ✅ {filepath:<40} ({size_kb:.1f} KB, contains {search_string})")
        else:
            print(f"  ❌ {filepath:<40} - Content verification failed")
            all_ok = False
    
    return all_ok


def check_presets():
    """Check configuration presets"""
    print("\n" + "="*70)
    print("CHECKING CONFIGURATION PRESETS")
    print("="*70)
    
    try:
        from hft_config import CONFIG_PRESETS, get_preset
        
        print(f"\nTotal presets: {len(CONFIG_PRESETS)}")
        print("\nAvailable presets:")
        
        for i, (name, config) in enumerate(CONFIG_PRESETS.items(), 1):
            strategy = config.get('strategy_type', 'unknown')
            risk = config.get('risk_percent_per_trade', '?')
            print(f"  {i:2}. {name:<35} ({strategy} @ {risk}% risk)")
        
        # Test loading a preset
        print("\nTesting preset loading:")
        preset = get_preset('MODERATE_SCALPING')
        print(f"  ✅ Loaded: {preset.name}")
        print(f"     Risk: {preset.get('risk_percent_per_trade')}%")
        print(f"     Strategy: {preset.get('strategy_type')}")
        
        return True
    
    except Exception as e:
        print(f"  ❌ Preset check failed: {str(e)}")
        return False


def generate_report():
    """Generate installation report"""
    print("\n" + "="*70)
    print("GENERATING INSTALLATION REPORT")
    print("="*70)
    
    results = {
        'Files': check_files_exist(),
        'Python Packages': check_python_imports(),
        'HFT Modules': check_hft_modules(),
        'File Contents': verify_file_contents(),
        'Configuration Presets': check_presets(),
    }
    
    print("\n" + "="*70)
    print("INSTALLATION SUMMARY")
    print("="*70)
    
    for check_name, status in results.items():
        status_str = "✅ PASS" if status else "❌ FAIL"
        print(f"{check_name:<30} {status_str}")
    
    all_pass = all(results.values())
    
    print("\n" + "="*70)
    if all_pass:
        print("✅ ALL CHECKS PASSED - System is ready!")
        print("="*70)
        print("\nNext steps:")
        print("  1. Read HFT_QUICK_REFERENCE.py for quick commands")
        print("  2. Read HFT_SYSTEM_README.md for complete documentation")
        print("  3. Run Python backtest: see HFT_TRADING_EXAMPLE.py")
        print("  4. Copy HFTScalpingEA.mq5 to MT5 experts folder")
        print("  5. Demo trade for 1-2 weeks")
    else:
        print("❌ SOME CHECKS FAILED - See above for details")
        print("="*70)
        print("\nTroubleshooting:")
        print("  - Ensure all files are in correct locations")
        print("  - Install pandas: pip install pandas numpy")
        print("  - Check Python path and imports")
    
    print("="*70)
    return all_pass


def print_quick_start():
    """Print quick start information"""
    print("\n" + "="*70)
    print("QUICK START")
    print("="*70)
    
    quick_start = """
PYTHON BACKTESTING - 30 SECONDS:
──────────────────────────────────

# 1. Import components
from hft.strategies.hft_scalping_strategy import HFTScalpingStrategy
from hft.utils.hft_backtest_engine import HFTBacktestEngine, ExecutionParams
import pandas as pd

# 2. Load data (OHLC format)
data = pd.read_csv('eurusd_data.csv')

# 3. Create strategy
strategy = HFTScalpingStrategy(strategy_type='scalping')

# 4. Generate signals
signals = strategy.generate_signals(data)

# 5. Run backtest
exec_params = ExecutionParams(base_spread_pips=1.0)
engine = HFTBacktestEngine(10000, exec_params)
results = engine.backtest(data, signals)

# 6. View results
print(f"Win Rate: {results['win_rate']:.1f}%")
print(f"Return: {results['total_return_percent']:.2f}%")
print(f"Drawdown: {results['max_drawdown_percent']:.2f}%")


MT5 DEPLOYMENT - 5 MINUTES:
──────────────────────────

1. Copy HFTScalpingEA.mq5 to MQL5/Experts folder
2. Compile in MetaEditor (F5)
3. Attach to EURUSD M5 chart
4. Backtest in Strategy Tester (Ctrl+R)
5. Start trading on demo


CONFIGURATION PRESETS:
──────────────────────

from hft_config import get_preset

# Conservative
config = get_preset('CONSERVATIVE_SCALPING')

# Moderate (Recommended)
config = get_preset('MODERATE_SCALPING')

# Aggressive
config = get_preset('AGGRESSIVE_SCALPING')


FOR MORE INFORMATION:
─────────────────────

- HFT_SYSTEM_README.md: Complete documentation
- HFT_QUICK_REFERENCE.py: Commands and workflows  
- INTEGRATION_GUIDE.md: How to integrate components
- HFT_TRADING_EXAMPLE.py: Code examples
"""
    
    print(quick_start)


if __name__ == '__main__':
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + " "*15 + "HFT TRADING SYSTEM - VERIFICATION" + " "*20 + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")
    
    # Run all checks
    all_ok = generate_report()
    
    # Print quick start
    print_quick_start()
    
    # Exit with appropriate code
    sys.exit(0 if all_ok else 1)
