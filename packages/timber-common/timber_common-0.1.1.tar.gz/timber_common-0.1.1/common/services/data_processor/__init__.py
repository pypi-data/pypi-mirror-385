"""
Data Processor Package

Provides data processing and transformation functions for financial data.

This package is organized into modules:
- standardization: Data cleaning and formatting
- returns: Returns calculations
- risk_metrics: Volatility, drawdown, Sharpe ratio, etc.
- technical_indicators: Moving averages, RSI, Bollinger Bands, etc.
- portfolio_metrics: Beta, correlation, wealth index, etc.

Usage:
    # Option 1: Import specific functions
    from common.services.data_processor import calculate_returns, calculate_sharpe_ratio
    
    # Option 2: Import whole modules
    from common.services.data_processor import risk_metrics, technical_indicators
    
    # Option 3: Use the aggregated data_processor object (backward compatible)
    from common.services.data_processor import data_processor
    df = data_processor.calculate_returns(df)
"""

# Import all functions from sub-modules
from .standardization import (
    standardize_dataframe,
    clean_data,
    resample_data
)

from .returns import (
    calculate_returns,
    calculate_cumulative_returns,
    calculate_rolling_returns
)

from .risk_metrics import (
    calculate_volatility,
    calculate_drawdown,
    calculate_sharpe_ratio,
    calculate_sortino_ratio,
    calculate_max_drawdown,
    calculate_var
)

from .technical_indicators import (
    calculate_moving_averages,
    calculate_ema,
    calculate_rsi,
    calculate_macd,
    calculate_bollinger_bands,
    calculate_atr,
    calculate_stochastic
)

from .portfolio_metrics import (
    calculate_wealth_index,
    calculate_correlation,
    calculate_beta,
    calculate_alpha,
    calculate_information_ratio,
    calculate_treynor_ratio
)


# ============================================================================
# Aggregated Data Processor Class (for backward compatibility)
# ============================================================================

class DataProcessor:
    """
    Aggregated data processor that provides access to all functions.
    
    This class serves as a convenience wrapper around all the modular functions,
    allowing for object-oriented usage: data_processor.calculate_returns(df)
    """
    
    # Standardization
    @staticmethod
    def standardize_dataframe(df):
        return standardize_dataframe(df)
    
    @staticmethod
    def clean_data(df, method='forward'):
        return clean_data(df, method)
    
    @staticmethod
    def resample_data(df, freq='D', price_column='Close'):
        return resample_data(df, freq, price_column)
    
    # Returns
    @staticmethod
    def calculate_returns(df, price_column='Close', method='simple'):
        return calculate_returns(df, price_column, method)
    
    @staticmethod
    def calculate_cumulative_returns(df, returns_column='Returns'):
        return calculate_cumulative_returns(df, returns_column)
    
    @staticmethod
    def calculate_rolling_returns(df, window=20, returns_column='Returns', annualize=False, trading_days=252):
        return calculate_rolling_returns(df, window, returns_column, annualize, trading_days)
    
    # Risk Metrics
    @staticmethod
    def calculate_volatility(df, window=20, returns_column='Returns', annualize=True, trading_days=252):
        return calculate_volatility(df, window, returns_column, annualize, trading_days)
    
    @staticmethod
    def calculate_drawdown(df, price_column='Close'):
        return calculate_drawdown(df, price_column)
    
    @staticmethod
    def calculate_sharpe_ratio(df, risk_free_rate=0.02, window=252, returns_column='Returns', trading_days=252):
        return calculate_sharpe_ratio(df, risk_free_rate, window, returns_column, trading_days)
    
    @staticmethod
    def calculate_sortino_ratio(df, risk_free_rate=0.02, window=252, returns_column='Returns', trading_days=252):
        return calculate_sortino_ratio(df, risk_free_rate, window, returns_column, trading_days)
    
    @staticmethod
    def calculate_max_drawdown(df, price_column='Close'):
        return calculate_max_drawdown(df, price_column)
    
    @staticmethod
    def calculate_var(df, confidence_level=0.95, returns_column='Returns'):
        return calculate_var(df, confidence_level, returns_column)
    
    # Technical Indicators
    @staticmethod
    def calculate_moving_averages(df, windows=[20, 50, 200], price_column='Close'):
        return calculate_moving_averages(df, windows, price_column)
    
    @staticmethod
    def calculate_ema(df, windows=[12, 26], price_column='Close'):
        return calculate_ema(df, windows, price_column)
    
    @staticmethod
    def calculate_rsi(df, window=14, price_column='Close'):
        return calculate_rsi(df, window, price_column)
    
    @staticmethod
    def calculate_macd(df, fast=12, slow=26, signal=9, price_column='Close'):
        return calculate_macd(df, fast, slow, signal, price_column)
    
    @staticmethod
    def calculate_bollinger_bands(df, window=20, num_std=2.0, price_column='Close'):
        return calculate_bollinger_bands(df, window, num_std, price_column)
    
    @staticmethod
    def calculate_atr(df, window=14):
        return calculate_atr(df, window)
    
    @staticmethod
    def calculate_stochastic(df, k_window=14, d_window=3):
        return calculate_stochastic(df, k_window, d_window)
    
    # Portfolio Metrics
    @staticmethod
    def calculate_wealth_index(df, initial_investment=1000.0, returns_column='Returns'):
        return calculate_wealth_index(df, initial_investment, returns_column)
    
    @staticmethod
    def calculate_correlation(df1, df2, window=30, column='Returns'):
        return calculate_correlation(df1, df2, window, column)
    
    @staticmethod
    def calculate_beta(stock_df, market_df, window=252, returns_column='Returns'):
        return calculate_beta(stock_df, market_df, window, returns_column)
    
    @staticmethod
    def calculate_alpha(stock_df, market_df, risk_free_rate=0.02, window=252, returns_column='Returns', trading_days=252):
        return calculate_alpha(stock_df, market_df, risk_free_rate, window, returns_column, trading_days)
    
    @staticmethod
    def calculate_information_ratio(portfolio_df, benchmark_df, window=252, returns_column='Returns'):
        return calculate_information_ratio(portfolio_df, benchmark_df, window, returns_column)
    
    @staticmethod
    def calculate_treynor_ratio(df, risk_free_rate=0.02, window=252, returns_column='Returns', trading_days=252):
        return calculate_treynor_ratio(df, risk_free_rate, window, returns_column, trading_days)


# Create singleton instance for convenience
data_processor = DataProcessor()


# ============================================================================
# Exports
# ============================================================================

__all__ = [
    # Main object
    'data_processor',
    'DataProcessor',
    
    # Standardization
    'standardize_dataframe',
    'clean_data',
    'resample_data',
    
    # Returns
    'calculate_returns',
    'calculate_cumulative_returns',
    'calculate_rolling_returns',
    
    # Risk Metrics
    'calculate_volatility',
    'calculate_drawdown',
    'calculate_sharpe_ratio',
    'calculate_sortino_ratio',
    'calculate_max_drawdown',
    'calculate_var',
    
    # Technical Indicators
    'calculate_moving_averages',
    'calculate_ema',
    'calculate_rsi',
    'calculate_macd',
    'calculate_bollinger_bands',
    'calculate_atr',
    'calculate_stochastic',
    
    # Portfolio Metrics
    'calculate_wealth_index',
    'calculate_correlation',
    'calculate_beta',
    'calculate_alpha',
    'calculate_information_ratio',
    'calculate_treynor_ratio',
]