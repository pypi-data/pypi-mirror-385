import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import asyncio
import warnings
import os
import time
from tqdm import tqdm
import json
import gspread
from google.oauth2.service_account import Credentials
from oauth2client.service_account import ServiceAccountCredentials

warnings.filterwarnings('ignore')

# Data structures (unchanged)
class Alerts:
    def __init__(self):
        self.internal_bullish_bos = False
        self.internal_bearish_bos = False
        self.internal_bullish_choch = False
        self.internal_bearish_choch = False
        self.swing_bullish_bos = False
        self.swing_bearish_bos = False
        self.swing_bullish_choch = False
        self.swing_bearish_choch = False
        self.internal_bullish_order_block = False
        self.internal_bearish_order_block = False
        self.swing_bullish_order_block = False
        self.swing_bearish_order_block = False
        self.equal_highs = False
        self.equal_lows = False
        self.bullish_fair_value_gap = False
        self.bearish_fair_value_gap = False
        self.current_candle_swing_bullish_bos = False
        self.current_candle_swing_bearish_bos = False
        self.current_candle_swing_bullish_choch = False
        self.current_candle_swing_bearish_choch = False
        self.current_candle_internal_bullish_bos = False
        self.current_candle_internal_bearish_bos = False
        self.current_candle_internal_bullish_choch = False
        self.current_candle_internal_bearish_choch = False

class TrailingExtremes:
    def __init__(self):
        self.top = None
        self.bottom = None
        self.bar_time = None
        self.bar_index = None
        self.last_top_time = None
        self.last_bottom_time = None

class FairValueGap:
    def __init__(self, top: float, bottom: float, bias: int, start_time: int = None,
                 end_time: int = None, start_idx: int = None, width: int = 0):
        self.top = top
        self.bottom = bottom
        self.bias = bias
        self.start_time = start_time
        self.end_time = end_time
        self.start_idx = start_idx
        self.width = width
        self.top_box = None
        self.bottom_box = None

class Trend:
    def __init__(self, bias: int = 0):
        self.bias = bias

class EqualDisplay:
    def __init__(self):
        self.line = None
        self.label = None

class Pivot:
    def __init__(self, current_level: float = None, last_level: float = None,
                 crossed: bool = False, bar_time: int = None, bar_index: int = None):
        self.current_level = current_level
        self.last_level = last_level
        self.crossed = crossed
        self.bar_time = bar_time
        self.bar_index = bar_index

class OrderBlock:
    def __init__(self, bar_high: float, bar_low: float, bar_time: int, bias: int):
        self.bar_high = bar_high
        self.bar_low = bar_low
        self.bar_time = bar_time
        self.bias = bias

class SmartMoneyConcepts:
    def __init__(self, stock_code: str, period: str = "1y", interval: str = "1d", auto_adjust: bool =False, 
                 print_details: bool = True, fetch_csv_data: bool = False, csv_path: str = None,
                 column_mapping: dict = None):
        """Smart Money Concepts Indicator - Python Implementation.

        Args:
            stock_code (str): Stock ticker symbol (e.g., 'RELIANCE.NS' for NSE).
            period (str): Period for yfinance data (e.g., '1y' for 1 year).
            interval (str): Interval for yfinance data (e.g., '1d' for daily).
            print_details (bool): Whether to print detailed analysis logs.
            fetch_csv_data (bool): If True, fetch data from CSV instead of yfinance.
            csv_path (str): Path to CSV file containing OHLCV data.
            column_mapping (dict, optional): Custom column mapping for renaming DataFrame columns.
        """
        self.stock_code = stock_code
        self.period = period
        self.interval = interval
        self.auto_adjust = auto_adjust
        self.print_details = print_details
        self.fetch_csv_data = fetch_csv_data
        self.csv_path = csv_path
        self.column_mapping = column_mapping

        # Initialize data containers
        self.df = None
        self.ohlcv_data = None

        # Initialize the indicator
        self.setup_constants()
        self.setup_variables()

    def setup_constants(self):
        self.BULLISH_LEG = 1
        self.BEARISH_LEG = 0
        self.BULLISH = 1
        self.BEARISH = -1
        self.GREEN = '#089981'
        self.RED = '#F23645'
        self.BLUE = '#2157f3'
        self.GRAY = '#878b94'
        self.MONO_BULLISH = '#b2b5be'
        self.MONO_BEARISH = '#5d606b'
        self.HISTORICAL = 'Historical'
        self.PRESENT = 'Present'
        self.COLORED = 'Colored'
        self.MONOCHROME = 'Monochrome'
        self.ALL = 'All'
        self.BOS = 'BOS'
        self.CHOCH = 'CHOCH'
        self.ATR = 'Atr'
        self.RANGE = 'Cumulative Mean Range'
        self.CLOSE = 'Close'
        self.HIGHLOW = 'High/Low'
        self.mode_input = self.HISTORICAL
        self.style_input = self.COLORED
        self.show_trend_input = False
        self.show_internals_input = True
        self.show_internal_bull_input = self.ALL
        self.internal_bull_color_input = self.GREEN
        self.show_internal_bear_input = self.ALL
        self.internal_bear_color_input = self.RED
        self.internal_filter_confluence_input = False
        self.show_structure_input = True
        self.show_swing_bull_input = self.ALL
        self.swing_bull_color_input = self.GREEN
        self.show_swing_bear_input = self.ALL
        self.swing_bear_color_input = self.RED
        self.show_swings_input = False
        self.swings_length_input = 50
        self.show_high_low_swings_input = True
        self.show_internal_order_blocks_input = True
        self.internal_order_blocks_size_input = 5
        self.show_swing_order_blocks_input = True
        self.swing_order_blocks_size_input = 5
        self.order_block_filter_input = self.ATR
        self.order_block_mitigation_input = self.HIGHLOW
        self.internal_bullish_order_block_color = "#3179f580"
        self.internal_bearish_order_block_color = "#f77c8080"
        self.swing_bullish_order_block_color = "#1848cc80"
        self.swing_bearish_order_block_color = "#b2283380"
        self.show_equal_highs_lows_input = True
        self.equal_highs_lows_length_input = 3
        self.equal_highs_lows_threshold_input = 0.1
        self.show_fair_value_gaps_input = True
        self.fair_value_gaps_threshold_input = True
        self.fair_value_gaps_timeframe_input = ''
        self.fair_value_gaps_bull_color_input = "#00ff6870"
        self.fair_value_gaps_bear_color_input = "#ff000870"
        self.fair_value_gaps_extend_input = 5
        self.show_premium_discount_zones_input = True
        self.premium_zone_color_input = self.RED
        self.equilibrium_zone_color_input = self.GRAY
        self.discount_zone_color_input = self.GREEN

    def setup_variables(self):
        self.parsed_highs = []
        self.parsed_lows = []
        self.highs = []
        self.lows = []
        self.times = []
        self.swing_high = Pivot()
        self.swing_low = Pivot()
        self.internal_high = Pivot()
        self.internal_low = Pivot()
        self.equal_high = Pivot()
        self.equal_low = Pivot()
        self.swing_trend = Trend(0)
        self.internal_trend = Trend(0)
        self.equal_high_display = EqualDisplay()
        self.equal_low_display = EqualDisplay()
        self.fair_value_gaps = []
        self.swing_order_blocks = []
        self.internal_order_blocks = []
        self.trailing = TrailingExtremes()
        self.current_bar_index = 0
        self.last_bar_index = 0
        self.current_alerts = Alerts()
        self.initial_time = None
        self.swing_bullish_color = self.MONO_BULLISH if self.style_input == self.MONOCHROME else self.swing_bull_color_input
        self.swing_bearish_color = self.MONO_BEARISH if self.style_input == self.MONOCHROME else self.swing_bear_color_input
        self.fair_value_gap_bullish_color = f"{self.MONO_BULLISH}70" if self.style_input == self.MONOCHROME else self.fair_value_gaps_bull_color_input
        self.fair_value_gap_bearish_color = f"{self.MONO_BEARISH}70" if self.style_input == self.MONOCHROME else self.fair_value_gaps_bear_color_input
        self.premium_zone_color = self.MONO_BEARISH if self.style_input == self.MONOCHROME else self.premium_zone_color_input
        self.discount_zone_color = self.MONO_BULLISH if self.style_input == self.MONOCHROME else self.discount_zone_color_input

    async def fetch_ohlcv(self, column_mapping=None):
        """Fetch OHLCV data from yfinance or CSV.

        Args:
            column_mapping (dict, optional): Custom column mapping for renaming DataFrame columns.
        """
        try:
            # Default column mapping for yfinance
            default_yfinance_mapping = {
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close'
            }
            # Use provided column_mapping or fallback to default
            active_mapping = column_mapping or default_yfinance_mapping
            # Determine the date column name for CSV parsing
            date_column = next((k for k, v in active_mapping.items() if v == 'Date'), None) if column_mapping else None

            if self.fetch_csv_data:
                if not self.csv_path or not os.path.exists(self.csv_path):
                    if self.print_details:
                        print(f"CSV file not found at {self.csv_path}")
                    return False
                if self.print_details:
                    print(f"Fetching data for {self.stock_code} from CSV at {self.csv_path}...")
                # Use the date column from mapping (e.g., 'DATE1') for parsing
                parse_dates = [date_column] if date_column else False
                self.df = pd.read_csv(self.csv_path, parse_dates=parse_dates)
                if date_column in self.df.columns:
                    self.df.set_index(date_column, inplace=True)
                    # Remove date_column from mapping to avoid duplicate renaming
                    active_mapping = {k: v for k, v in active_mapping.items() if v != 'Date'}
                else:
                    self.df.index = pd.to_datetime(self.df.index)
            else:
                if self.print_details:
                    print(f"Fetching data for {self.stock_code} using yfinance...")
                ticker = yf.Ticker(self.stock_code)
                self.df = ticker.history(period=self.period, interval=self.interval , auto_adjust=self.auto_adjust)
                self.df.index = pd.to_datetime(self.df.index)

            required_columns = [k for k, v in active_mapping.items() if v in ['open', 'high', 'low', 'close']]
            if not all(col in self.df.columns for col in required_columns):
                if self.print_details:
                    print(f"Data for {self.stock_code} missing required columns: {required_columns}")
                return False

            self.df = self.df.rename(columns=active_mapping)
            self.df = self.df.sort_index()
            self.df = self.df.dropna(subset=['open', 'high', 'low', 'close'])
            self.ohlcv_data = self.df[['open', 'high', 'low', 'close']].copy()
            if self.print_details:
                print(f"Successfully fetched {len(self.df)} bars")
                print(f"Data range: {self.df.index[0].date()} to {self.df.index[-1].date()}")
            return True
        except Exception as e:
            if self.print_details:
                print(f"Error fetching data for {self.stock_code}: {e}")
            return False

    def prepare_data(self):
        if self.df is None:
            raise ValueError("No data available. Please fetch data first.")
        self.df['tr'] = np.maximum(
            self.df['high'] - self.df['low'],
            np.maximum(
                abs(self.df['high'] - self.df['close'].shift(1)),
                abs(self.df['low'] - self.df['close'].shift(1))
            )
        )
        self.df['atr'] = self.df['tr'].rolling(window=200, min_periods=1).mean()
        self.df['volatility_measure'] = self.df['atr'] if self.order_block_filter_input == self.ATR else self.df['tr'].expanding().mean()
        self.df['high_volatility_bar'] = (self.df['high'] - self.df['low']) >= (2 * self.df['volatility_measure'])
        self.df['parsed_high'] = np.where(self.df['high_volatility_bar'], self.df['low'], self.df['high'])
        self.df['parsed_low'] = np.where(self.df['high_volatility_bar'], self.df['high'], self.df['low'])
        self.highs = self.df['high'].values
        self.lows = self.df['low'].values
        self.parsed_highs = self.df['parsed_high'].values
        self.parsed_lows = self.df['parsed_low'].values
        self.times = self.df.index.values
        self.initial_time = self.times[0]
        if self.print_details:
            print("Data preparation completed")

    def leg(self, size: int, current_bar: int) -> int:
        if not hasattr(self, "_leg_vars"):
            self._leg_vars = {}
        if size not in self._leg_vars:
            self._leg_vars[size] = 0

        if current_bar < size:
            return self._leg_vars[size]

        high_size_ago = self.highs[current_bar - size]
        low_size_ago = self.lows[current_bar - size]
        highest_high = np.max(self.highs[current_bar - size + 1: current_bar + 1])
        lowest_low = np.min(self.lows[current_bar - size + 1: current_bar + 1])
        new_leg_high = high_size_ago > highest_high
        new_leg_low = low_size_ago < lowest_low

        if new_leg_high:
            self._leg_vars[size] = self.BEARISH_LEG
        elif new_leg_low:
            self._leg_vars[size] = self.BULLISH_LEG

        return self._leg_vars[size]

    def get_current_structure(self, size: int, equal_high_low: bool = False, internal: bool = False):
        if not hasattr(self, '_prev_legs'):
            self._prev_legs = {}
        if size not in self._prev_legs:
            self._prev_legs[size] = []

        for current_bar in range(len(self.highs)):
            current_leg = self.leg(size, current_bar)
            if len(self._prev_legs[size]) == 0:
                previous_leg = 0
            else:
                previous_leg = self._prev_legs[size][-1]
            self._prev_legs[size].append(current_leg)
            leg_change = current_leg - previous_leg
            new_pivot = leg_change != 0
            pivot_low = leg_change == 1
            pivot_high = leg_change == -1

            if new_pivot:
                if pivot_low:
                    if equal_high_low:
                        pivot_obj = self.equal_low
                    elif internal:
                        pivot_obj = self.internal_low
                    else:
                        pivot_obj = self.swing_low

                    if current_bar >= size:
                        low_value = self.lows[current_bar - size]
                        time_value = self.times[current_bar - size]
                        if equal_high_low and pivot_obj.current_level is not None:
                            atr_value = self.df.iloc[min(current_bar, len(self.df) - 1)]['atr']
                            if abs(pivot_obj.current_level - low_value) < self.equal_highs_lows_threshold_input * atr_value:
                                self.draw_equal_high_low(pivot_obj, low_value, size, False, current_bar)
                        pivot_obj.last_level = pivot_obj.current_level
                        pivot_obj.current_level = low_value
                        pivot_obj.crossed = False
                        pivot_obj.bar_time = time_value
                        pivot_obj.bar_index = current_bar - size
                        if not equal_high_low and not internal:
                            self.trailing.bottom = pivot_obj.current_level
                            self.trailing.bar_time = pivot_obj.bar_time
                            self.trailing.bar_index = pivot_obj.bar_index
                            self.trailing.last_bottom_time = pivot_obj.bar_time

                elif pivot_high:
                    if equal_high_low:
                        pivot_obj = self.equal_high
                    elif internal:
                        pivot_obj = self.internal_high
                    else:
                        pivot_obj = self.swing_high

                    if current_bar >= size:
                        high_value = self.highs[current_bar - size]
                        time_value = self.times[current_bar - size]
                        if equal_high_low and pivot_obj.current_level is not None:
                            atr_value = self.df.iloc[min(current_bar, len(self.df) - 1)]['atr']
                            if abs(pivot_obj.current_level - high_value) < self.equal_highs_lows_threshold_input * atr_value:
                                self.draw_equal_high_low(pivot_obj, high_value, size, True, current_bar)
                        pivot_obj.last_level = pivot_obj.current_level
                        pivot_obj.current_level = high_value
                        pivot_obj.crossed = False
                        pivot_obj.bar_time = time_value
                        pivot_obj.bar_index = current_bar - size
                        if not equal_high_low and not internal:
                            self.trailing.top = pivot_obj.current_level
                            self.trailing.bar_time = pivot_obj.bar_time
                            self.trailing.bar_index = pivot_obj.bar_index
                            self.trailing.last_top_time = pivot_obj.bar_time

    def draw_equal_high_low(self, pivot_obj: Pivot, level: float, size: int, equal_high: bool, index: int):
        equal_data = {
            "type": "EQH" if equal_high else "EQL",
            "start_time": pivot_obj.bar_time,
            "start_level": pivot_obj.current_level,
            "end_time": self.times[index],
            "end_level": level,
            "color": self.swing_bearish_color if equal_high else self.swing_bullish_color,
        }
        if not hasattr(self, "equal_structures"):
            self.equal_structures = []
        self.equal_structures.append(equal_data)
        if equal_high:
            self.current_alerts.equal_highs = True
        else:
            self.current_alerts.equal_lows = True

    def delete_order_blocks(self, internal: bool = False):
        order_blocks = self.internal_order_blocks if internal else self.swing_order_blocks
        bearish_mitigation_source = self.df['close'] if self.order_block_mitigation_input == self.CLOSE else self.df['high']
        bullish_mitigation_source = self.df['close'] if self.order_block_mitigation_input == self.CLOSE else self.df['low']
        blocks_to_remove = []
        for i, order_block in enumerate(order_blocks):
            crossed_order_block = False
            if order_block.bias == 'BEARISH':
                if bearish_mitigation_source.iloc[-1] > order_block.bar_high:
                    crossed_order_block = True
                    if internal:
                        self.current_alerts.internal_bearish_order_block = True
                    else:
                        self.current_alerts.swing_bearish_order_block = True
            elif order_block.bias == 'BULLISH':
                if bullish_mitigation_source.iloc[-1] < order_block.bar_low:
                    crossed_order_block = True
                    if internal:
                        self.current_alerts.internal_bullish_order_block = True
                    else:
                        self.current_alerts.swing_bullish_order_block = True
            if crossed_order_block:
                blocks_to_remove.append(i)
        for i in reversed(blocks_to_remove):
            order_blocks.pop(i)

    def store_order_block(self, pivot_obj, internal: bool = False, bias: int = None):
        if (not internal and self.show_swing_order_blocks_input) or (internal and self.show_internal_order_blocks_input):
            if bias == self.BEARISH:
                start_idx = max(0, pivot_obj.bar_index)
                end_idx = min(len(self.parsed_highs), len(self.highs))
                if start_idx < end_idx:
                    slice_highs = self.parsed_highs[start_idx:end_idx]
                    if len(slice_highs) > 0:
                        max_idx = np.argmax(slice_highs)
                        parsed_index = start_idx + max_idx
                    else:
                        parsed_index = start_idx
                else:
                    parsed_index = start_idx
            else:
                start_idx = max(0, pivot_obj.bar_index)
                end_idx = min(len(self.parsed_lows), len(self.lows))
                if start_idx < end_idx:
                    slice_lows = self.parsed_lows[start_idx:end_idx]
                    if len(slice_lows) > 0:
                        min_idx = np.argmin(slice_lows)
                        parsed_index = start_idx + min_idx
                    else:
                        parsed_index = start_idx
                else:
                    parsed_index = start_idx
            if parsed_index < len(self.parsed_highs) and parsed_index < len(self.parsed_lows):
                order_block = OrderBlock(
                    bar_high=self.parsed_highs[parsed_index],
                    bar_low=self.parsed_lows[parsed_index],
                    bar_time=self.times[parsed_index],
                    bias=bias
                )
                order_blocks = self.internal_order_blocks if internal else self.swing_order_blocks
                if len(order_blocks) >= 100:
                    order_blocks.pop()
                order_blocks.insert(0, order_block)

    def display_structure(self, internal: bool = False):
        bullish_bar = True
        bearish_bar = True
        for i in range(1, len(self.df)):
            current_close = self.df.iloc[i]['close']
            current_open = self.df.iloc[i]['open']
            current_high = self.df.iloc[i]['high']
            current_low = self.df.iloc[i]['low']
            previous_close = self.df.iloc[i - 1]['close']
            if self.internal_filter_confluence_input:
                bullish_bar = (current_high - max(current_close, current_open)) > min(current_close, current_open - current_low)
                bearish_bar = (current_high - max(current_close, current_open)) < min(current_close, current_open - current_low)
            pivot_high = self.internal_high if internal else self.swing_high
            trend_obj = self.internal_trend if internal else self.swing_trend
            if (pivot_high.current_level is not None and
                current_close > pivot_high.current_level and
                previous_close <= pivot_high.current_level and
                not pivot_high.crossed):
                extra_condition = True
                if internal:
                    extra_condition = (pivot_high.current_level != self.swing_high.current_level and bullish_bar)
                if extra_condition:
                    tag = self.CHOCH if trend_obj.bias == self.BEARISH else self.BOS
                    if internal:
                        self.current_alerts.internal_bullish_choch = (tag == self.CHOCH)
                        self.current_alerts.internal_bullish_bos = (tag == self.BOS)
                    else:
                        self.current_alerts.swing_bullish_choch = (tag == self.CHOCH)
                        self.current_alerts.swing_bullish_bos = (tag == self.BOS)
                    pivot_high.crossed = True
                    trend_obj.bias = self.BULLISH
                    structure_data = {
                        'type': tag,
                        'bias': self.BULLISH,
                        'level': pivot_high.current_level,
                        'time': pivot_high.bar_time,
                        'break_time': self.times[i],
                        'color': self.swing_bullish_color,
                        'internal': internal
                    }
                    if not hasattr(self, 'structure_breaks'):
                        self.structure_breaks = []
                    self.structure_breaks.append(structure_data)
                    if (internal and self.show_internal_order_blocks_input) or (not internal and self.show_swing_order_blocks_input):
                        self.store_order_block(pivot_high, internal, self.BULLISH)
            pivot_low = self.internal_low if internal else self.swing_low
            if (pivot_low.current_level is not None and
                current_close < pivot_low.current_level and
                previous_close >= pivot_low.current_level and
                not pivot_low.crossed):
                extra_condition = True
                if internal:
                    extra_condition = (pivot_low.current_level != self.swing_low.current_level and bearish_bar)
                if extra_condition:
                    tag = self.CHOCH if trend_obj.bias == self.BULLISH else self.BOS
                    if internal:
                        self.current_alerts.internal_bearish_choch = (tag == self.CHOCH)
                        self.current_alerts.internal_bearish_bos = (tag == self.BOS)
                    else:
                        self.current_alerts.swing_bearish_choch = (tag == self.CHOCH)
                        self.current_alerts.swing_bearish_bos = (tag == self.BOS)
                    pivot_low.crossed = True
                    trend_obj.bias = self.BEARISH
                    structure_data = {
                        'type': tag,
                        'bias': self.BEARISH,
                        'level': pivot_low.current_level,
                        'time': pivot_low.bar_time,
                        'break_time': self.times[i],
                        'color': self.swing_bearish_color,
                        'internal': internal
                    }
                    if not hasattr(self, 'structure_breaks'):
                        self.structure_breaks = []
                    self.structure_breaks.append(structure_data)
                    if (internal and self.show_internal_order_blocks_input) or (not internal and self.show_swing_order_blocks_input):
                        self.store_order_block(pivot_low, internal, self.BEARISH)

    def delete_fair_value_gaps(self):
        gaps_to_remove = []
        current_high = self.df.iloc[-1]['high']
        current_low = self.df.iloc[-1]['low']
        for i, gap in enumerate(self.fair_value_gaps):
            if gap.bias == self.BULLISH and current_low < gap.bottom:
                gaps_to_remove.append(i)
            elif gap.bias == self.BEARISH and current_high > gap.top:
                gaps_to_remove.append(i)
        for idx in reversed(gaps_to_remove):
            self.fair_value_gaps.pop(idx)

    def detect_fair_value_gaps(self):
        if not self.show_fair_value_gaps_input:
            return
        for i in range(2, len(self.df)):
            current_high = self.highs[i]
            current_low = self.lows[i]
            last_high = self.highs[i - 1]
            last_low = self.lows[i - 1]
            last_close = self.df.iloc[i - 1]['close']
            last_open = self.df.iloc[i - 1]['open']
            last2_high = self.highs[i - 2]
            last2_low = self.lows[i - 2]
            bar_delta_percent = (last_close - last_open) / last_open if last_open != 0 else 0
            threshold = abs(bar_delta_percent) * 2 if self.fair_value_gaps_threshold_input else 0
            bullish_fvg = (current_low > last2_high and
                           last_close > last2_high and
                           bar_delta_percent > threshold)
            bearish_fvg = (current_high < last2_low and
                           last_close < last2_low and
                           -bar_delta_percent > threshold)
            if bullish_fvg:
                self.current_alerts.bullish_fair_value_gap = True
                fvg = FairValueGap(
                    top=current_low,
                    bottom=last2_high,
                    bias=self.BULLISH
                )
                self.fair_value_gaps.insert(0, fvg)
            elif bearish_fvg:
                self.current_alerts.bearish_fair_value_gap = True
                fvg = FairValueGap(
                    top=current_high,
                    bottom=last2_low,
                    bias=self.BEARISH
                )
                self.fair_value_gaps.insert(0, fvg)

    def update_trailing_extremes(self):
        for i in range(len(self.df)):
            current_high = self.highs[i]
            current_low = self.lows[i]
            if self.trailing.top is None or current_high > self.trailing.top:
                self.trailing.top = current_high
                self.trailing.last_top_time = self.times[i]
            if self.trailing.bottom is None or current_low < self.trailing.bottom:
                self.trailing.bottom = current_low
                self.trailing.last_bottom_time = self.times[i]

    def calculate_premium_discount_zones(self):
        if not self.show_premium_discount_zones_input:
            return
        if self.trailing.top is None or self.trailing.bottom is None:
            return
        premium_top = self.trailing.top
        premium_bottom = 0.95 * self.trailing.top + 0.05 * self.trailing.bottom
        equilibrium_top = 0.525 * self.trailing.top + 0.475 * self.trailing.bottom
        equilibrium_bottom = 0.525 * self.trailing.bottom + 0.475 * self.trailing.top
        discount_top = 0.95 * self.trailing.bottom + 0.05 * self.trailing.top
        discount_bottom = self.trailing.bottom
        self.premium_discount_zones = {
            'premium': {
                'top': premium_top,
                'bottom': premium_bottom,
                'color': self.premium_zone_color
            },
            'equilibrium': {
                'top': equilibrium_top,
                'bottom': equilibrium_bottom,
                'color': self.equilibrium_zone_color_input
            },
            'discount': {
                'top': discount_top,
                'bottom': discount_bottom,
                'color': self.discount_zone_color
            }
        }

    def run_smc_analysis(self):
        if self.print_details:
            print("Running Smart Money Concepts analysis...")
        self.structure_breaks = []
        self.equal_structures = []
        for current_bar in range(len(self.df)):
            self.current_bar_index = current_bar
            self.last_bar_index = current_bar - 1 if current_bar > 0 else 0
            self.current_bar_time = self.times[current_bar]
            current_high = self.highs[current_bar]
            current_low = self.lows[current_bar]
            current_close = self.df.iloc[current_bar]['close']
            current_open = self.df.iloc[current_bar]['open']
            atr_measure = self.df.iloc[current_bar]['atr']
            volatility_measure = atr_measure if self.order_block_filter_input == self.ATR else self.df.iloc[current_bar]['volatility_measure']
            high_volatility_bar = (current_high - current_low) >= (2 * volatility_measure)
            self.parsed_highs[current_bar] = current_low if high_volatility_bar else current_high
            self.parsed_lows[current_bar] = current_high if high_volatility_bar else current_low
            if self.order_block_filter_input or self.show_premium_discount_zones_input:
                self.update_trailing_extremes_bar(current_bar)
                if self.show_premium_discount_zones_input:
                    self.calculate_premium_discount_zones_bar(current_bar)
            if self.show_fair_value_gaps_input:
                self.delete_fair_value_gaps_bar(current_bar)
            self.get_current_structure_bar(self.swings_length_input, False, False, current_bar)
            self.get_current_structure_bar(5, False, True, current_bar)
            if self.show_equal_highs_lows_input:
                self.get_current_structure_bar(self.equal_highs_lows_length_input, True, False, current_bar)
            if self.show_internals_input or self.show_internal_order_blocks_input or self.show_trend_input:
                self.display_structure_bar(True, current_bar)
            if self.show_structure_input or self.show_swing_order_blocks_input or self.show_high_low_swings_input:
                self.display_structure_bar(False, current_bar)
            if self.show_internal_order_blocks_input:
                self.delete_order_blocks_bar(True, current_bar)
            if self.show_swing_order_blocks_input:
                self.delete_order_blocks_bar(False, current_bar)
            if self.show_fair_value_gaps_input:
                self.detect_fair_value_gaps_bar(current_bar)
            if current_bar == len(self.df) - 1:
                if self.show_internal_order_blocks_input:
                    self.draw_order_blocks_final(True)
                if self.show_swing_order_blocks_input:
                    self.draw_order_blocks_final(False)
        if self.print_details:
            print("Smart Money Concepts analysis completed!")
            print("Final Results:")
            print(f"Swing high: {self.swing_high.current_level:.2f}")
            print(f"Swing low: {self.swing_low.current_level:.2f}")
            print(f"Internal high: {self.internal_high.current_level:.2f}")
            print(f"Internal low: {self.internal_low.current_level:.2f}")
            print(f"Swing trend: {self.swing_trend.bias}")
            print(f"Internal trend: {self.internal_trend.bias}")
            print(f"Structure breaks: {len(self.structure_breaks)}")
            print(f"Order blocks: {len(self.internal_order_blocks) + len(self.swing_order_blocks)}")
            print(f"Equal structures: {len(self.equal_structures)}")

    def leg_bar(self, size: int, current_bar: int) -> int:
        if not hasattr(self, "_leg_vars"):
            self._leg_vars = {}
        if size not in self._leg_vars:
            self._leg_vars[size] = 0
        if current_bar < size:
            return self._leg_vars[size]
        high_size_ago = self.highs[current_bar - size]
        low_size_ago = self.lows[current_bar - size]
        highest_high = np.max(self.highs[current_bar - size + 1: current_bar + 1])
        lowest_low = np.min(self.lows[current_bar - size + 1: current_bar + 1])
        new_leg_high = high_size_ago > highest_high
        new_leg_low = low_size_ago < lowest_low
        if new_leg_high:
            self._leg_vars[size] = self.BEARISH_LEG
        elif new_leg_low:
            self._leg_vars[size] = self.BULLISH_LEG
        return self._leg_vars[size]

    def ta_change(self, value: int, size: int, current_bar: int) -> int:
        if not hasattr(self, '_prev_values'):
            self._prev_values = {}
        key = f"{size}_{current_bar}"
        if key not in self._prev_values:
            self._prev_values[key] = value
            return 0
        prev_value = self._prev_values[key]
        self._prev_values[key] = value
        return value - prev_value

    def get_current_structure_bar(self, size: int, equal_high_low: bool, internal: bool, current_bar: int):
        current_leg = self.leg_bar(size, current_bar)
        if not hasattr(self, '_leg_history'):
            self._leg_history = {}
        if size not in self._leg_history:
            self._leg_history[size] = []
        if len(self._leg_history[size]) == 0:
            leg_change = 0
        else:
            leg_change = current_leg - self._leg_history[size][-1]
        self._leg_history[size].append(current_leg)
        new_pivot = leg_change != 0
        pivot_low = leg_change == 1
        pivot_high = leg_change == -1
        if new_pivot:
            if pivot_low:
                if equal_high_low:
                    pivot_obj = self.equal_low
                elif internal:
                    pivot_obj = self.internal_low
                else:
                    pivot_obj = self.swing_low
                if current_bar >= size:
                    low_value = self.lows[current_bar - size]
                    time_value = self.times[current_bar - size]
                    if pivot_obj.bar_index != current_bar - size or pivot_obj.current_level != low_value:
                        if equal_high_low and pivot_obj.current_level is not None:
                            atr_value = self.df.iloc[current_bar]['atr']
                            if abs(pivot_obj.current_level - low_value) < self.equal_highs_lows_threshold_input * atr_value:
                                self.draw_equal_high_low_bar(pivot_obj, low_value, size, False, current_bar)
                        pivot_obj.last_level = pivot_obj.current_level
                        pivot_obj.current_level = low_value
                        pivot_obj.crossed = False
                        pivot_obj.bar_time = time_value
                        pivot_obj.bar_index = current_bar - size
                        if not equal_high_low and not internal:
                            self.trailing.bottom = pivot_obj.current_level
                            self.trailing.bar_time = pivot_obj.bar_time
                            self.trailing.bar_index = pivot_obj.bar_index
                            self.trailing.last_bottom_time = pivot_obj.bar_time
            elif pivot_high:
                if equal_high_low:
                    pivot_obj = self.equal_high
                elif internal:
                    pivot_obj = self.internal_high
                else:
                    pivot_obj = self.swing_high
                if current_bar >= size:
                    high_value = self.highs[current_bar - size]
                    time_value = self.times[current_bar - size]
                    if pivot_obj.bar_index != current_bar - size or pivot_obj.current_level != high_value:
                        if equal_high_low and pivot_obj.current_level is not None:
                            atr_value = self.df.iloc[current_bar]['atr']
                            if abs(pivot_obj.current_level - high_value) < self.equal_highs_lows_threshold_input * atr_value:
                                self.draw_equal_high_low_bar(pivot_obj, high_value, size, True, current_bar)
                        pivot_obj.last_level = pivot_obj.current_level
                        pivot_obj.current_level = high_value
                        pivot_obj.crossed = False
                        pivot_obj.bar_time = time_value
                        pivot_obj.bar_index = current_bar - size
                        if not equal_high_low and not internal:
                            self.trailing.top = pivot_obj.current_level
                            self.trailing.bar_time = pivot_obj.bar_time
                            self.trailing.bar_index = pivot_obj.bar_index
                            self.trailing.last_top_time = pivot_obj.bar_time

    def display_structure_bar(self, internal: bool, current_bar: int):
        current_high = self.highs[current_bar]
        current_low = self.lows[current_bar]
        current_close = self.df.iloc[current_bar]['close']
        current_open = self.df.iloc[current_bar]['open']
        if not hasattr(self, '_bullish_bar'):
            self._bullish_bar = True
            self._bearish_bar = True
        if self.internal_filter_confluence_input:
            self._bullish_bar = current_high - max(current_close, current_open) > min(current_close, current_open - current_low)
            self._bearish_bar = current_high - max(current_close, current_open) < min(current_close, current_open - current_low)
        pivot_obj = self.internal_high if internal else self.swing_high
        trend_obj = self.internal_trend if internal else self.swing_trend
        extra_condition = True
        if internal:
            extra_condition = (self.internal_high.current_level != self.swing_high.current_level and self._bullish_bar)
        
        if (pivot_obj.current_level is not None and
            current_close > pivot_obj.current_level and
            not pivot_obj.crossed and
            extra_condition):
            if current_bar > 0:
                prev_close = self.df.iloc[current_bar - 1]['close']
                if prev_close <= pivot_obj.current_level:
                    tag = self.CHOCH if trend_obj.bias != self.BULLISH else self.BOS
                    is_current_candle = (current_bar == len(self.df) - 1)
                    if internal:
                        if tag == self.CHOCH:
                            self.current_alerts.internal_bullish_choch = True
                            if is_current_candle:
                                self.current_alerts.current_candle_internal_bullish_choch = True
                        else:
                            self.current_alerts.internal_bullish_bos = True
                            if is_current_candle:
                                self.current_alerts.current_candle_internal_bullish_bos = True
                    else:
                        if tag == self.CHOCH:
                            self.current_alerts.swing_bullish_choch = True
                            if is_current_candle:
                                self.current_alerts.current_candle_swing_bullish_choch = True
                        else:
                            self.current_alerts.swing_bullish_bos = True
                            if is_current_candle:
                                self.current_alerts.current_candle_swing_bullish_bos = True
                    pivot_obj.crossed = True
                    trend_obj.bias = self.BULLISH
                    self.structure_breaks.append({
                        'type': tag,
                        'direction': 'bullish',
                        'internal': internal,
                        'price': pivot_obj.current_level,
                        'time': pivot_obj.bar_time,
                        'bar_index': pivot_obj.bar_index,
                        'break_time': self.times[current_bar],
                        'break_bar_index': current_bar,
                        'current_candle': is_current_candle
                    })
                    self.store_order_block_bar(pivot_obj, internal, self.BULLISH, current_bar)
        
        pivot_obj = self.internal_low if internal else self.swing_low
        extra_condition = True
        if internal:
            extra_condition = (self.internal_low.current_level != self.swing_low.current_level and self._bearish_bar)
        if (pivot_obj.current_level is not None and
            current_close < pivot_obj.current_level and
            not pivot_obj.crossed and
            extra_condition):
            if current_bar > 0:
                prev_close = self.df.iloc[current_bar - 1]['close']
                if prev_close >= pivot_obj.current_level:
                    tag = self.CHOCH if trend_obj.bias != self.BEARISH else self.BOS
                    is_current_candle = (current_bar == len(self.df) - 1)
                    if internal:
                        if tag == self.CHOCH:
                            self.current_alerts.internal_bearish_choch = True
                            if is_current_candle:
                                self.current_alerts.current_candle_internal_bearish_choch = True
                        else:
                            self.current_alerts.internal_bearish_bos = True
                            if is_current_candle:
                                self.current_alerts.current_candle_internal_bearish_bos = True
                    else:
                        if tag == self.CHOCH:
                            self.current_alerts.swing_bearish_choch = True
                            if is_current_candle:
                                self.current_alerts.current_candle_swing_bearish_choch = True
                        else:
                            self.current_alerts.swing_bearish_bos = True
                            if is_current_candle:
                                self.current_alerts.current_candle_swing_bearish_bos = True
                    pivot_obj.crossed = True
                    trend_obj.bias = self.BEARISH
                    self.structure_breaks.append({
                        'type': tag,
                        'direction': 'bearish',
                        'internal': internal,
                        'price': pivot_obj.current_level,
                        'time': pivot_obj.bar_time,
                        'bar_index': pivot_obj.bar_index,
                        'break_time': self.times[current_bar],
                        'break_bar_index': current_bar,
                        'current_candle': is_current_candle
                    })
                    self.store_order_block_bar(pivot_obj, internal, self.BEARISH, current_bar)

    def store_order_block_bar(self, pivot_obj: Pivot, internal: bool, bias: int, current_bar: int):
        if ((not internal and self.show_swing_order_blocks_input) or
            (internal and self.show_internal_order_blocks_input)):
            if pivot_obj.bar_index is not None and pivot_obj.bar_index >= 0:
                start_idx = pivot_obj.bar_index
                end_idx = current_bar
                if start_idx < end_idx and end_idx < len(self.parsed_highs):
                    if bias == self.BEARISH:
                        array_slice = self.parsed_highs[start_idx:end_idx]
                        max_idx = np.argmax(array_slice)
                        parsed_index = start_idx + max_idx
                    else:
                        array_slice = self.parsed_lows[start_idx:end_idx]
                        min_idx = np.argmin(array_slice)
                        parsed_index = start_idx + min_idx
                    order_block = OrderBlock(
                        bar_high=self.parsed_highs[parsed_index],
                        bar_low=self.parsed_lows[parsed_index],
                        bar_time=self.times[parsed_index],
                        bias=bias
                    )
                    order_blocks = self.internal_order_blocks if internal else self.swing_order_blocks
                    if len(order_blocks) >= 100:
                        order_blocks.pop()
                    order_blocks.insert(0, order_block)

    def delete_order_blocks_bar(self, internal: bool, current_bar: int):
        order_blocks = self.internal_order_blocks if internal else self.swing_order_blocks
        current_high = self.highs[current_bar]
        current_low = self.lows[current_bar]
        current_close = self.df.iloc[current_bar]['close']
        bearish_mitigation_source = current_close if self.order_block_mitigation_input == self.CLOSE else current_high
        bullish_mitigation_source = current_close if self.order_block_mitigation_input == self.CLOSE else current_low
        blocks_to_remove = []
        for i, order_block in enumerate(order_blocks):
            crossed_order_block = False
            if order_block.bias == self.BEARISH:
                if bearish_mitigation_source > order_block.bar_high:
                    crossed_order_block = True
                    if internal:
                        self.current_alerts.internal_bearish_order_block = True
                    else:
                        self.current_alerts.swing_bearish_order_block = True
            elif order_block.bias == self.BULLISH:
                if bullish_mitigation_source < order_block.bar_low:
                    crossed_order_block = True
                    if internal:
                        self.current_alerts.internal_bullish_order_block = True
                    else:
                        self.current_alerts.swing_bullish_order_block = True
            if crossed_order_block:
                blocks_to_remove.append(i)
        for i in reversed(blocks_to_remove):
            order_blocks.pop(i)

    def update_trailing_extremes_bar(self, current_bar: int):
        current_high = self.highs[current_bar]
        current_low = self.lows[current_bar]
        current_time = self.times[current_bar]
        if self.trailing.top is None or current_high > self.trailing.top:
            self.trailing.top = current_high
            self.trailing.last_top_time = current_time
        if self.trailing.bottom is None or current_low < self.trailing.bottom:
            self.trailing.bottom = current_low
            self.trailing.last_bottom_time = current_time

    def calculate_premium_discount_zones_bar(self, current_bar: int):
        if self.trailing.top is not None and self.trailing.bottom is not None:
            premium_top = self.trailing.top
            premium_bottom = 0.95 * self.trailing.top + 0.05 * self.trailing.bottom
            equilibrium_top = 0.525 * self.trailing.top + 0.475 * self.trailing.bottom
            equilibrium_bottom = 0.525 * self.trailing.bottom + 0.475 * self.trailing.top
            discount_top = 0.95 * self.trailing.bottom + 0.05 * self.trailing.top
            discount_bottom = self.trailing.bottom
            self.premium_discount_zones = {
                'premium': {'top': premium_top, 'bottom': premium_bottom},
                'equilibrium': {'top': equilibrium_top, 'bottom': equilibrium_bottom},
                'discount': {'top': discount_top, 'bottom': discount_bottom}
            }

    def delete_fair_value_gaps_bar(self, current_bar: int):
        if not self.show_fair_value_gaps_input:
            return
        current_high = self.highs[current_bar]
        current_low = self.lows[current_bar]
        fvgs_to_remove = []
        for i, fvg in enumerate(self.fair_value_gaps):
            if ((current_low < fvg.bottom and fvg.bias == self.BULLISH) or
                (current_high > fvg.top and fvg.bias == self.BEARISH)):
                fvgs_to_remove.append(i)
        for i in reversed(fvgs_to_remove):
            self.fair_value_gaps.pop(i)

    def detect_fair_value_gaps_bar(self, current_bar: int):
        if not self.show_fair_value_gaps_input or current_bar < 2:
            return
        current_high = self.highs[current_bar]
        current_low = self.lows[current_bar]
        current_time = self.times[current_bar]
        last_close = self.df.iloc[current_bar-1]['close']
        last_open = self.df.iloc[current_bar-1]['open']
        last_time = self.times[current_bar-1]
        last2_high = self.highs[current_bar-2]
        last2_low = self.lows[current_bar-2]
        bar_delta_percent = (last_close - last_open) / last_open if last_open != 0 else 0
        threshold = 0.002
        
        bullish_fvg = (current_low > last2_high and last_close > last2_high and bar_delta_percent > threshold)
        bearish_fvg = (current_high < last2_low and last_close < last2_low and -bar_delta_percent > threshold)
        
        if bullish_fvg:
            self.current_alerts.bullish_fair_value_gap = True
            fvg = FairValueGap(
                top=current_low,
                bottom=last2_high,
                bias=self.BULLISH,
                start_time=last_time,
                end_time=current_time + self.fair_value_gaps_extend_input,
                start_idx=current_bar - 1,
                width=self.fair_value_gaps_extend_input + 1
            )
            self.fair_value_gaps.insert(0, fvg)
        elif bearish_fvg:
            self.current_alerts.bearish_fair_value_gap = True
            fvg = FairValueGap(
                top=current_high,
                bottom=last2_low,
                bias=self.BEARISH,
                start_time=last_time,
                end_time=current_time + self.fair_value_gaps_extend_input,
                start_idx=current_bar - 1,
                width=self.fair_value_gaps_extend_input + 1
            )
            self.fair_value_gaps.insert(0, fvg)

    def draw_equal_high_low_bar(self, pivot_obj: Pivot, level: float, size: int, equal_high: bool, current_bar: int):
        equal_data = {
            'type': 'EQH' if equal_high else 'EQL',
            'start_time': pivot_obj.bar_time,
            'start_level': pivot_obj.current_level,
            'end_time': self.times[current_bar],
            'end_level': level,
            'color': self.swing_bearish_color if equal_high else self.swing_bullish_color
        }
        if not hasattr(self, 'equal_structures'):
            self.equal_structures = []
        self.equal_structures.append(equal_data)
        if equal_high:
            self.current_alerts.equal_highs = True
        else:
            self.current_alerts.equal_lows = True

    def draw_order_blocks_final(self, internal: bool):
        pass

    async def run_analysis(self):
        if not await self.fetch_ohlcv():
            return False
        self.prepare_data()
        self.run_smc_analysis()
        print("Smart Money Concepts analysis completed")
        return True

    def plot_candlestick_chart(self, ax, start_idx: int = 0, end_idx: int = None):
        if end_idx is None:
            end_idx = len(self.df)
        df_slice = self.df.iloc[start_idx:end_idx]
        for i, (idx, row) in enumerate(df_slice.iterrows()):
            color = self.swing_bullish_color if row['close'] > row['open'] else self.swing_bearish_color
            body_height = abs(row['close'] - row['open'])
            body_bottom = min(row['close'], row['open'])
            ax.add_patch(patches.Rectangle(
                (i, body_bottom), 0.8, body_height,
                facecolor=color, edgecolor='black', linewidth=0.5
            ))
            ax.plot([i+0.4, i+0.4], [row['low'], row['high']],
                    color='black', linewidth=0.5)

    def plot_structure_breaks(self, ax, start_idx: int = 0, end_idx: int = None):
        if not hasattr(self, 'structure_breaks') or not self.structure_breaks:
            return
        if end_idx is None:
            end_idx = len(self.df)
        for structure in self.structure_breaks:
            pivot_time = structure['time']
            time_diff = np.abs(self.times - pivot_time)
            pivot_time_idx = np.argmin(time_diff)
            plot_start_idx = pivot_time_idx - start_idx
            if plot_start_idx < -50:
                continue
            if structure['internal']:
                color = self.internal_bull_color_input if structure['direction'] == 'bullish' else self.internal_bear_color_input
            else:
                color = self.swing_bull_color_input if structure['direction'] == 'bullish' else self.swing_bear_color_input
            line_style = '--' if structure['internal'] else '-'
            detection_time = structure.get('break_time', pivot_time)
            detection_time_diff = np.abs(self.times - detection_time)
            detection_time_idx = np.argmin(detection_time_diff)
            plot_end_idx = detection_time_idx - start_idx
            actual_start = max(0, plot_start_idx)
            actual_end = min(end_idx - start_idx, plot_end_idx)
            if actual_start < actual_end:
                ax.plot([actual_start, actual_end],
                        [structure['price'], structure['price']],
                        color=color, linestyle=line_style, alpha=0.8, linewidth=1.5)
                label_x = (actual_start + actual_end) / 2
                label_y_offset = (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.005
                if structure['direction'] == 'bullish':
                    label_y = structure['price'] + label_y_offset
                    va = 'bottom'
                else:
                    label_y = structure['price'] - label_y_offset
                    va = 'top'
                ax.text(label_x, label_y, structure['type'],
                        color=color, fontsize=9, ha='center', va=va, weight='bold',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor=color, alpha=0.3))

        all_start_indices = [max(0, pivot_time_idx - start_idx) for structure in self.structure_breaks 
                            if (pivot_time_idx - start_idx) >= -50 and (detection_time_idx - start_idx) < end_idx]
        all_end_indices = [min(end_idx - start_idx, detection_time_idx - start_idx) for structure in self.structure_breaks 
                        if (pivot_time_idx - start_idx) >= -50 and (detection_time_idx - start_idx) < end_idx]
        if all_start_indices and all_end_indices:
            min_x = min(all_start_indices)
            max_x = max(all_end_indices)
            x_range = max_x - min_x
            ax.set_xlim(min_x - x_range * 0.1, max_x + x_range * 0.1)

    def plot_order_blocks(self, ax, start_idx: int = 0, end_idx: int = None):
        if end_idx is None:
            end_idx = len(self.df)
        for i, ob in enumerate(self.swing_order_blocks):
            if i >= self.swing_order_blocks_size_input:
                break
            time_idx = np.where(self.times == ob.bar_time)[0]
            if len(time_idx) > 0:
                time_idx = time_idx[0]
                plot_start_idx = time_idx - start_idx
                if plot_start_idx <= end_idx - start_idx:
                    color = self.swing_bullish_order_block_color if ob.bias == self.BULLISH else self.swing_bearish_order_block_color
                    actual_start = max(0, plot_start_idx)
                    width = (end_idx - start_idx) - actual_start
                    height = ob.bar_high - ob.bar_low
                    if width > 0:
                        ax.add_patch(patches.Rectangle(
                            (actual_start, ob.bar_low), width, height,
                            facecolor=color, edgecolor=color,
                            alpha=0.3, linewidth=1
                        ))
        for i, ob in enumerate(self.internal_order_blocks):
            if i >= self.internal_order_blocks_size_input:
                break
            time_idx = np.where(self.times == ob.bar_time)[0]
            if len(time_idx) > 0:
                time_idx = time_idx[0]
                plot_start_idx = time_idx - start_idx
                if plot_start_idx <= end_idx - start_idx:
                    color = self.internal_bullish_order_block_color if ob.bias == self.BULLISH else self.internal_bearish_order_block_color
                    actual_start = max(0, plot_start_idx)
                    width = (end_idx - start_idx) - actual_start
                    height = ob.bar_high - ob.bar_low
                    if width > 0:
                        ax.add_patch(patches.Rectangle(
                            (actual_start, ob.bar_low), width, height,
                            facecolor=color, edgecolor=color,
                            alpha=0.3, linewidth=1
                        ))

    def plot_equal_highs_lows(self, ax, start_idx: int = 0, end_idx: int = None):
        if not hasattr(self, 'equal_structures'):
            return
        if end_idx is None:
            end_idx = len(self.df)
        for equal in self.equal_structures:
            start_time_idx = np.where(self.times == equal['start_time'])[0]
            end_time_idx = np.where(self.times == equal['end_time'])[0]
            if len(start_time_idx) > 0 and len(end_time_idx) > 0:
                start_plot_idx = start_time_idx[0] - start_idx
                end_plot_idx = end_time_idx[0] - start_idx
                if start_plot_idx < end_idx - start_idx and end_plot_idx > 0:
                    actual_start = max(0, start_plot_idx)
                    actual_end = min(end_idx - start_idx, end_plot_idx)
                    ax.plot([actual_start, actual_end],
                            [equal['start_level'], equal['end_level']],
                            color=equal['color'], linewidth=1.5, linestyle=':', alpha=0.8)
                    mid_x = (actual_start + actual_end) / 2
                    mid_y = (equal['start_level'] + equal['end_level']) / 2
                    ax.text(mid_x, mid_y,
                            equal['type'], color=equal['color'],
                            fontsize=8, ha='center', va='center', weight='bold',
                            bbox=dict(boxstyle="round,pad=0.2", facecolor=equal['color'], alpha=0.3))

    def plot_fair_value_gaps(self, ax, start_idx: int = 0, end_idx: int = None):
        if not self.show_fair_value_gaps_input or not hasattr(self, 'fair_value_gaps'):
            return
        if end_idx is None:
            end_idx = len(self.df)
        for fvg in self.fair_value_gaps:
            if hasattr(fvg, 'start_idx') and fvg.start_idx is not None:
                plot_start_idx = fvg.start_idx - start_idx
                plot_width = fvg.width
            else:
                plot_start_idx = 0
                plot_width = 10
            if plot_start_idx <= end_idx - start_idx and plot_start_idx + plot_width >= 0:
                actual_start = max(0, plot_start_idx)
                actual_width = min(plot_width, end_idx - start_idx - actual_start)
                if actual_width > 0:
                    color = self.fair_value_gap_bullish_color if fvg.bias == self.BULLISH else self.fair_value_gap_bearish_color
                    height = fvg.top - fvg.bottom
                    ax.add_patch(patches.Rectangle(
                        (actual_start, fvg.bottom), actual_width, height,
                        facecolor=color, edgecolor=color,
                        alpha=0.3, linewidth=1
                    ))
                    label_text = 'FVG' if fvg.bias == self.BULLISH else 'FVG'
                    mid_x = actual_start + actual_width / 2
                    mid_y = (fvg.top + fvg.bottom) / 2
                    ax.text(mid_x, mid_y, label_text,
                            color=color[:-2] if len(color) > 7 else color,
                            fontsize=6, ha='center', va='center', weight='bold',
                            bbox=dict(boxstyle="round,pad=0.2", facecolor=color, alpha=0.5))

    def plot_premium_discount_zones(self, ax, start_idx: int = 0, end_idx: int = None):
        if not self.show_premium_discount_zones_input or not hasattr(self, 'premium_discount_zones'):
            return
        if end_idx is None:
            end_idx = len(self.df)
        zone_colors = {
            'premium': self.premium_zone_color,
            'equilibrium': self.equilibrium_zone_color_input,
            'discount': self.discount_zone_color
        }
        for zone_name, zone_data in self.premium_discount_zones.items():
            base_color = zone_colors.get(zone_name, '#808080')
            ax.axhspan(zone_data['bottom'], zone_data['top'],
                       facecolor=base_color, alpha=0.15, zorder=1)
            mid_price = (zone_data['top'] + zone_data['bottom']) / 2
            ax.text(end_idx - start_idx - 5, mid_price, zone_name.capitalize(),
                    color=base_color, fontsize=10, ha='right', va='center',
                    weight='bold',
                    bbox=dict(boxstyle="round,pad=0.3", facecolor=base_color, alpha=0.3))

    def plot_trailing_extremes(self, ax, start_idx: int = 0, end_idx: int = None):
        if not self.show_high_low_swings_input:
            return
        if end_idx is None:
            end_idx = len(self.df)
        bars_to_extend = 20
        right_time_bar = end_idx - start_idx + bars_to_extend
        if hasattr(self.trailing, 'last_top_time') and self.trailing.last_top_time is not None:
            top_time_idx = np.where(self.times == self.trailing.last_top_time)[0]
            if len(top_time_idx) > 0:
                plot_start_idx = top_time_idx[0] - start_idx
                if plot_start_idx <= end_idx - start_idx:
                    actual_start = max(0, plot_start_idx)
                    actual_end = min(right_time_bar, end_idx - start_idx)
                    ax.plot([actual_start, actual_end],
                            [self.trailing.top, self.trailing.top],
                            color=self.swing_bearish_color, linewidth=2, linestyle='-', alpha=0.8)
                    trend_label = 'Strong High' if self.swing_trend.bias == self.BEARISH else 'Weak High'
                    ax.text(actual_end - 2, self.trailing.top, trend_label,
                            color=self.swing_bearish_color, fontsize=9,
                            ha='right', va='bottom', weight='bold')
        if hasattr(self.trailing, 'last_bottom_time') and self.trailing.last_bottom_time is not None:
            bottom_time_idx = np.where(self.times == self.trailing.last_bottom_time)[0]
            if len(bottom_time_idx) > 0:
                plot_start_idx = bottom_time_idx[0] - start_idx
                if plot_start_idx <= end_idx - start_idx:
                    actual_start = max(0, plot_start_idx)
                    actual_end = min(right_time_bar, end_idx - start_idx)
                    ax.plot([actual_start, actual_end],
                            [self.trailing.bottom, self.trailing.bottom],
                            color=self.swing_bullish_color, linewidth=2, linestyle='-', alpha=0.8)
                    trend_label = 'Strong Low' if self.swing_trend.bias == self.BULLISH else 'Weak Low'
                    ax.text(actual_end - 2, self.trailing.bottom, trend_label,
                            color=self.swing_bullish_color, fontsize=9,
                            ha='right', va='top', weight='bold')

    def visualize_smc(self, bars_to_show: int = 1000):
        if self.df is None:
            print("No data available for visualization")
            return
        total_bars = len(self.df)
        start_idx = max(0, total_bars - bars_to_show)
        end_idx = total_bars
        fig, ax = plt.subplots(figsize=(15, 10))
        self.plot_candlestick_chart(ax, start_idx, end_idx)
        self.plot_premium_discount_zones(ax, start_idx, end_idx)
        self.plot_fair_value_gaps(ax, start_idx, end_idx)
        self.plot_order_blocks(ax, start_idx, end_idx)
        self.plot_structure_breaks(ax, start_idx, end_idx)
        self.plot_equal_highs_lows(ax, start_idx, end_idx)
        self.plot_trailing_extremes(ax, start_idx, end_idx)
        ax.set_xlim(0, bars_to_show)
        ax.set_ylim(self.df.iloc[start_idx:end_idx]['low'].min() * 0.995,
                    self.df.iloc[start_idx:end_idx]['high'].max() * 1.005)
        ax.set_title(f"{self.stock_code} - Smart Money Concepts",
                     fontsize=16, fontweight='bold')
        ax.set_xlabel("Bars", fontsize=12)
        ax.set_ylabel("Price", fontsize=12)
        ax.grid(True, alpha=0.3)
        legend_elements = [
            plt.Line2D([0], [0], color=self.swing_bullish_color, lw=2, label='Bullish Structure'),
            plt.Line2D([0], [0], color=self.swing_bearish_color, lw=2, label='Bearish Structure'),
            patches.Patch(color=self.swing_bullish_order_block_color, alpha=0.3, label='Swing Order Blocks'),
            patches.Patch(color=self.internal_bullish_order_block_color, alpha=0.3, label='Internal Order Blocks')
        ]
        if self.show_equal_highs_lows_input:
            legend_elements.append(plt.Line2D([0], [0], color=self.swing_bullish_color,
                                              lw=1, linestyle=':', label='Equal Highs/Lows'))
        if self.show_fair_value_gaps_input:
            legend_elements.append(patches.Patch(color=self.fair_value_gap_bullish_color,
                                                alpha=0.2, label='Fair Value Gaps'))
        if self.show_premium_discount_zones_input:
            legend_elements.append(patches.Patch(color=self.premium_zone_color,
                                                alpha=0.1, label='Premium/Discount Zones'))
        ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1, 1))
        plt.tight_layout()
        plt.show()
        self.print_analysis_summary()

    def print_analysis_summary(self):
        if not self.print_details:
            summary_data, levels_data = self._generate_analysis_summary()
            return summary_data, levels_data

        print("\n" + "="*80)
        print("\nSMART MONEY CONCEPTS ANALYSIS SUMMARY")
        print("\n" + "="*80)
        print(f"Stock Code: {self.stock_code}")
        print(f"Total Bars Analyzed: {len(self.df)}")
        print(f"Data Range: {self.df.index[0]} to {self.df.index[-1]}")
        print("-" * 80)

        summary_data, levels_data = self._generate_analysis_summary()
        current_price = summary_data['Current_Price']

        print("\nSTRUCTURE ANALYSIS:")
        print(f"Swing BOS: {summary_data['Swing_BOS']}")
        print(f"Swing CHoCH: {summary_data['Swing_CHoCH']}")
        print(f"Internal BOS: {summary_data['Internal_BOS']}")
        print(f"Internal CHoCH: {summary_data['Internal_CHoCH']}")

        print("\nORDER BLOCKS:")
        print(f"Swing Order Blocks: {summary_data['Swing_Order_Blocks']}")
        print(f"Internal Order Blocks: {summary_data['Internal_Order_Blocks']}")

        print("\nEQUAL HIGHS/LOWS:")
        print(f"Equal Highs (EQH): {summary_data['Equal_Highs']}")
        print(f"Equal Lows (EQL): {summary_data['Equal_Lows']}")

        if self.show_fair_value_gaps_input:
            print("\nFAIR VALUE GAPS:")
            print(f"Bullish FVG: {summary_data['Bullish_FVG']}")
            print(f"Bearish FVG: {summary_data['Bearish_FVG']}")

        print("\nTRAILING EXTREMES:")
        if summary_data['Trailing_High'] is not None:
            print(f"Trailing High: {summary_data['Trailing_High']}")
        if summary_data['Trailing_Low'] is not None:
            print(f"Trailing Low: {summary_data['Trailing_Low']}")

        if self.show_premium_discount_zones_input and hasattr(self, 'premium_discount_zones'):
            print("\nPREMIUM/DISCOUNT ZONES:")
            for zone_name in ['premium', 'equilibrium', 'discount']:
                bottom = summary_data[f"{zone_name.capitalize()}_Bottom"]
                top = summary_data[f"{zone_name.capitalize()}_Top"]
                print(f"{zone_name.capitalize()}: Bottom = {bottom}, Top = {top}")

        print("\nPRICE ANALYSIS:")
        print(f"Current Price: {current_price}")
        if summary_data['Current_Zone'] is not None:
            print(f"Current Zone: {summary_data['Current_Zone']}")

        print("=" * 80)
        print("Analysis completed successfully!")
        print("=" * 80 + "\n")
        return summary_data, levels_data

    def _generate_analysis_summary(self):
        current_price = round(self.df.iloc[-1]['close'], 2)
        summary_data = {
            'Stock_Code': self.stock_code,
            'Total_Bars': len(self.df),
            'Data_Start': str(self.df.index[0]),
            'Data_End': str(self.df.index[-1]),
            'Swing_High': round(self.swing_high.current_level, 2) if self.swing_high.current_level is not None else None,
            'Swing_Low': round(self.swing_low.current_level, 2) if self.swing_low.current_level is not None else None,
            'Internal_High': round(self.internal_high.current_level, 2) if self.internal_high.current_level is not None else None,
            'Internal_Low': round(self.internal_low.current_level, 2) if self.internal_low.current_level is not None else None,
            'Swing_Trend': "Bullish" if self.swing_trend.bias == self.BULLISH else "Bearish" if self.swing_trend.bias == self.BEARISH else "Neutral",
            'Internal_Trend': "Bullish" if self.internal_trend.bias == self.BULLISH else "Bearish" if self.internal_trend.bias == self.BEARISH else "Neutral",
            'Current_Price': current_price,
        }

        if hasattr(self, 'structure_breaks'):
            summary_data.update({
                'Swing_BOS': len([s for s in self.structure_breaks if s['type'] == self.BOS and not s['internal']]),
                'Swing_CHoCH': len([s for s in self.structure_breaks if s['type'] == self.CHOCH and not s['internal']]),
                'Internal_BOS': len([s for s in self.structure_breaks if s['type'] == self.BOS and s['internal']]),
                'Internal_CHoCH': len([s for s in self.structure_breaks if s['type'] == self.CHOCH and s['internal']])
            })
        else:
            summary_data.update({
                'Swing_BOS': 0,
                'Swing_CHoCH': 0,
                'Internal_BOS': 0,
                'Internal_CHoCH': 0
            })

        summary_data.update({
            'Swing_Order_Blocks': len(self.swing_order_blocks),
            'Internal_Order_Blocks': len(self.internal_order_blocks)
        })

        if hasattr(self, 'equal_structures'):
            summary_data.update({
                'Equal_Highs': len([e for e in self.equal_structures if e['type'] == 'EQH']),
                'Equal_Lows': len([e for e in self.equal_structures if e['type'] == 'EQL'])
            })
        else:
            summary_data.update({
                'Equal_Highs': 0,
                'Equal_Lows': 0
            })

        if self.show_fair_value_gaps_input:
            summary_data.update({
                'Bullish_FVG': len([f for f in self.fair_value_gaps if f.bias == self.BULLISH]),
                'Bearish_FVG': len([f for f in self.fair_value_gaps if f.bias == self.BEARISH])
            })
        else:
            summary_data.update({
                'Bullish_FVG': 0,
                'Bearish_FVG': 0
            })

        summary_data.update({
            'Trailing_High': round(self.trailing.top, 2) if self.trailing.top is not None else None,
            'Trailing_Low': round(self.trailing.bottom, 2) if self.trailing.bottom is not None else None
        })

        if self.show_premium_discount_zones_input and hasattr(self, 'premium_discount_zones'):
            for zone_name, zone_data in self.premium_discount_zones.items():
                summary_data.update({
                    f"{zone_name.capitalize()}_Bottom": round(zone_data['bottom'], 2),
                    f"{zone_name.capitalize()}_Top": round(zone_data['top'], 2)
                })

        if self.show_premium_discount_zones_input and hasattr(self, 'premium_discount_zones'):
            if current_price >= self.premium_discount_zones['premium']['bottom']:
                summary_data['Current_Zone'] = "Premium"
            elif current_price <= self.premium_discount_zones['discount']['top']:
                summary_data['Current_Zone'] = "Discount"
            else:
                summary_data['Current_Zone'] = "Equilibrium"
        else:
            summary_data['Current_Zone'] = None

        levels_data = []
        # Swing High
        if self.swing_high.current_level is not None:
            level = round(self.swing_high.current_level, 2)
            midpoint = level
            distance = abs(current_price - midpoint) / midpoint * 100 if midpoint else None
            levels_data.append({
                'Stock_Code': self.stock_code,
                'Level_Type': 'Swing_High',
                'Top': level,
                'Bottom': level,
                'Midpoint': midpoint,
                'Time': self.swing_high.bar_time,
                'Current_Price': current_price,
                'Distance_To_Midpoint_Percent': round(distance, 2) if distance is not None else None
            })
        # Swing Low
        if self.swing_low.current_level is not None:
            level = round(self.swing_low.current_level, 2)
            midpoint = level
            distance = abs(current_price - midpoint) / midpoint * 100 if midpoint else None
            levels_data.append({
                'Stock_Code': self.stock_code,
                'Level_Type': 'Swing_Low',
                'Top': level,
                'Bottom': level,
                'Midpoint': midpoint,
                'Time': self.swing_low.bar_time,
                'Current_Price': current_price,
                'Distance_To_Midpoint_Percent': round(distance, 2) if distance is not None else None
            })
        # Internal High
        if self.internal_high.current_level is not None:
            level = round(self.internal_high.current_level, 2)
            midpoint = level
            distance = abs(current_price - midpoint) / midpoint * 100 if midpoint else None
            levels_data.append({
                'Stock_Code': self.stock_code,
                'Level_Type': 'Internal_High',
                'Top': level,
                'Bottom': level,
                'Midpoint': midpoint,
                'Time': self.internal_high.bar_time,
                'Current_Price': current_price,
                'Distance_To_Midpoint_Percent': round(distance, 2) if distance is not None else None
            })
        # Internal Low
        if self.internal_low.current_level is not None:
            level = round(self.internal_low.current_level, 2)
            midpoint = level
            distance = abs(current_price - midpoint) / midpoint * 100 if midpoint else None
            levels_data.append({
                'Stock_Code': self.stock_code,
                'Level_Type': 'Internal_Low',
                'Top': level,
                'Bottom': level,
                'Midpoint': midpoint,
                'Time': self.internal_low.bar_time,
                'Current_Price': current_price,
                'Distance_To_Midpoint_Percent': round(distance, 2) if distance is not None else None
            })
        # Swing Order Blocks
        for ob in self.swing_order_blocks:
            top = round(ob.bar_high, 2)
            bottom = round(ob.bar_low, 2)
            midpoint = (top + bottom) / 2
            distance = abs(current_price - midpoint) / midpoint * 100 if midpoint else None
            levels_data.append({
                'Stock_Code': self.stock_code,
                'Level_Type': f"Swing_Order_Block_{'Bullish' if ob.bias == self.BULLISH else 'Bearish'}",
                'Top': top,
                'Bottom': bottom,
                'Midpoint': round(midpoint, 2),
                'Time': ob.bar_time,
                'Current_Price': current_price,
                'Distance_To_Midpoint_Percent': round(distance, 2) if distance is not None else None
            })
        # Internal Order Blocks
        for ob in self.internal_order_blocks:
            top = round(ob.bar_high, 2)
            bottom = round(ob.bar_low, 2)
            midpoint = (top + bottom) / 2
            distance = abs(current_price - midpoint) / midpoint * 100 if midpoint else None
            levels_data.append({
                'Stock_Code': self.stock_code,
                'Level_Type': f"Internal_Order_Block_{'Bullish' if ob.bias == self.BULLISH else 'Bearish'}",
                'Top': top,
                'Bottom': bottom,
                'Midpoint': round(midpoint, 2),
                'Time': ob.bar_time,
                'Current_Price': current_price,
                'Distance_To_Midpoint_Percent': round(distance, 2) if distance is not None else None
            })
        # Fair Value Gaps
        for fvg in self.fair_value_gaps:
            top = round(fvg.top, 2)
            bottom = round(fvg.bottom, 2)
            midpoint = (top + bottom) / 2
            distance = abs(current_price - midpoint) / midpoint * 100 if midpoint else None
            levels_data.append({
                'Stock_Code': self.stock_code,
                'Level_Type': f"Fair_Value_Gap_{'Bullish' if fvg.bias == self.BULLISH else 'Bearish'}",
                'Top': top,
                'Bottom': bottom,
                'Midpoint': round(midpoint, 2),
                'Time': fvg.start_time,
                'Current_Price': current_price,
                'Distance_To_Midpoint_Percent': round(distance, 2) if distance is not None else None
            })

        return summary_data, levels_data
    
async def main(
    stock_codes: List[str],
    csv_directory: str = "data",
    fetch_csv_data: bool = True,  # Respect the user's True setting
    csv_column_mapping: dict = None,   # <-- New parameter
    spreadsheet_id: str = None,   # Reinstated as requested
    period: str = "max",
    interval: str = "1d",
    auto_adjust: bool =False,
    batch_size: int = 10,         # Used only when fetch_csv_data=False or CSV missing
    delay: float = 2.0,           # Used only when fetch_csv_data=False or CSV missing
    visualize: bool = False,
    print_details: bool = True,
    clear: bool = True,
    output_format: str = "csv",
    use_colab: bool = False       # Reinstated as requested
):
    # Remove duplicates from stock_codes
    stock_codes = list(set(stock_codes))
    if not stock_codes:
        stock_codes = ["RELIANCE.NS"]

    # Fallback mapping if not provided
    if csv_column_mapping is None:
        csv_column_mapping = {
            'OPEN_PRICE': 'open',
            'HIGH_PRICE': 'high',
            'LOW_PRICE': 'low',
            'CLOSE_PRICE': 'close',
            'DATE1': 'Date'
        }

    # Create stock_csv_map
    stock_csv_map = {}
    os.makedirs(csv_directory, exist_ok=True)
    for stock_code in stock_codes:
        base_name = stock_code.replace(".NS", "")
        csv_path = os.path.join(csv_directory, f"{base_name}.csv")
        if fetch_csv_data and os.path.exists(csv_path):
            stock_csv_map[stock_code] = csv_path
            if print_details:
                print(f"Mapped {stock_code} to {csv_path}")
        elif print_details:
            print(f"⚠️ CSV file for {stock_code} not found at {csv_path}. Using yfinance.")

    # Initialize CSV output
    output_dir = "analysis"
    os.makedirs(output_dir, exist_ok=True)
    summary_file = os.path.join(output_dir, 'smc_analysis_summaries.csv')
    levels_file = os.path.join(output_dir, 'smc_analysis_levels.csv')
    filtered_file = os.path.join(output_dir, 'current_candle_breaks.csv')

    if clear:
        for file in [summary_file, levels_file, filtered_file]:
            if os.path.exists(file):
                os.remove(file)

    summary_file_exists = os.path.exists(summary_file)
    levels_file_exists = os.path.exists(levels_file)
    filtered_file_exists = os.path.exists(filtered_file)

    # Google Sheets setup (only if output_format includes google_sheets)
    spreadsheet_url, summary_worksheet, levels_worksheet, filtered_worksheet = None, None, None, None
    gspread_client, summary_rows, levels_rows, filtered_rows = None, [], [], []
    summary_headers, levels_headers, filtered_headers = None, None, None
    processed_summary, processed_levels, processed_filtered = set(), set(), set()

    if output_format in ["google_sheets", "both"]:
        creds = None
        try:
            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive"
            ]
            if use_colab:
                try:
                    from google.colab import userdata
                    SERVICE_ACCOUNT_CREDS = userdata.get("SERVICE_ACCOUNT_CREDS")
                    if SERVICE_ACCOUNT_CREDS:
                        SERVICE_ACCOUNT_CREDS = json.loads(SERVICE_ACCOUNT_CREDS)
                        creds = Credentials.from_service_account_info(SERVICE_ACCOUNT_CREDS, scopes=scope)
                except ImportError:
                    print("⚠️ Not running in Colab. Falling back to local credentials.")
            if creds is None:
                local_cred_path = "Credentials/credentials.json"
                if os.path.exists(local_cred_path):
                    creds = ServiceAccountCredentials.from_json_keyfile_name(local_cred_path, scope)
                else:
                    print(f"⚠️ Local credentials.json not found at {local_cred_path}. Falling back to CSV output.")
                    output_format = "csv"
            if creds:
                gspread_client = gspread.authorize(creds)
                spreadsheet = gspread_client.open_by_key(spreadsheet_id)
                spreadsheet_url = spreadsheet.url
                summary_worksheet = spreadsheet.worksheet("Summaries")
                levels_worksheet = spreadsheet.worksheet("Levels")
                try:
                    filtered_worksheet = spreadsheet.worksheet("Current_Candle_Breaks")
                except gspread.exceptions.WorksheetNotFound:
                    filtered_worksheet = spreadsheet.add_worksheet(title="Current_Candle_Breaks", rows=1000, cols=20)
                if clear:
                    summary_worksheet.clear()
                    levels_worksheet.clear()
                    filtered_worksheet.clear()
                if not clear:
                    existing_summary = {tuple(row) for row in summary_worksheet.get_all_values()}
                    existing_levels = {tuple(row) for row in levels_worksheet.get_all_values()}
                    existing_filtered = {tuple(row) for row in filtered_worksheet.get_all_values()}
                    processed_summary.update(existing_summary)
                    processed_levels.update(existing_levels)
                    processed_filtered.update(existing_filtered)
        except Exception as e:
            print(f"Failed to initialize Google Sheets: {e}")
            if output_format == "google_sheets":
                return
            output_format = "csv"

    # Stock analysis loop
    filtered_stocks = []
    yfinance_stocks_processed = 0  # Track stocks processed via yfinance
    for stock_code in tqdm(stock_codes, desc="Analyzing stocks", unit="stock"):
        if print_details:
            print(f"\n==============================")
            print(f"🔍 Analyzing stock: {stock_code}")
            print(f"==============================")

        # Determine data source
        fetch_csv_data_stock = fetch_csv_data and stock_code in stock_csv_map
        csv_path = stock_csv_map.get(stock_code, None)
        column_mapping = csv_column_mapping if fetch_csv_data_stock else None

        smc = SmartMoneyConcepts(
            stock_code=stock_code,
            period=period,
            interval=interval,
            auto_adjust=auto_adjust,
            print_details=print_details,
            fetch_csv_data=fetch_csv_data_stock,
            csv_path=csv_path,
            column_mapping=column_mapping
        )

        max_retries = 3 if not fetch_csv_data_stock else 1  # No retries needed for CSV
        for attempt in range(max_retries):
            try:
                success = await smc.fetch_ohlcv(column_mapping=column_mapping)
                if success:
                    smc.prepare_data()
                    smc.run_smc_analysis()
                    if visualize:
                        smc.visualize_smc(bars_to_show=500)

                    summary_data, levels_data = smc.print_analysis_summary()

                    if output_format in ["csv", "both"] and summary_data:
                        pd.DataFrame([summary_data]).to_csv(
                            summary_file,
                            mode='a',
                            index=False,
                            header=not summary_file_exists
                        )
                        summary_file_exists = True
                    if output_format in ["csv", "both"] and levels_data:
                        pd.DataFrame(levels_data).to_csv(
                            levels_file,
                            mode='a',
                            index=False,
                            header=not levels_file_exists
                        )
                        levels_file_exists = True

                    if hasattr(smc.current_alerts, 'current_candle_swing_bullish_bos'):
                        if any([
                            smc.current_alerts.current_candle_swing_bullish_bos,
                            smc.current_alerts.current_candle_swing_bearish_bos,
                            smc.current_alerts.current_candle_swing_bullish_choch,
                            smc.current_alerts.current_candle_swing_bearish_choch,
                            smc.current_alerts.current_candle_internal_bullish_bos,
                            smc.current_alerts.current_candle_internal_bearish_bos,
                            smc.current_alerts.current_candle_internal_bullish_choch,
                            smc.current_alerts.current_candle_internal_bearish_choch
                        ]):
                            filtered_stocks.append({
                                'Stock_Code': stock_code,
                                'Swing_Bullish_CHoCH': smc.current_alerts.current_candle_swing_bullish_choch,
                                'Swing_Bearish_CHoCH': smc.current_alerts.current_candle_swing_bearish_choch,
                                'Swing_Bullish_BOS': smc.current_alerts.current_candle_swing_bullish_bos,
                                'Swing_Bearish_BOS': smc.current_alerts.current_candle_swing_bearish_bos,
                                'Internal_Bullish_CHoCH': smc.current_alerts.current_candle_internal_bullish_choch,
                                'Internal_Bearish_CHoCH': smc.current_alerts.current_candle_internal_bearish_choch,
                                'Internal_Bullish_BOS': smc.current_alerts.current_candle_internal_bullish_bos,
                                'Internal_Bearish_BOS': smc.current_alerts.current_candle_internal_bearish_bos,
                                'Timestamp': str(datetime.now())
                            })

                    if output_format in ["google_sheets", "both"] and gspread_client:
                        if summary_data:
                            normalized_summary = {k: str(v) if v is not None else "" for k, v in summary_data.items()}
                            row_tuple = tuple(normalized_summary.get(h, "") for h in (summary_headers or normalized_summary.keys()))
                            if summary_headers is None:
                                summary_headers = list(normalized_summary.keys())
                                summary_rows.append(summary_headers)
                            if row_tuple not in processed_summary:
                                summary_rows.append([normalized_summary.get(h, "") for h in summary_headers])
                                processed_summary.add(row_tuple)
                        if levels_data:
                            if not levels_headers:
                                levels_headers = list(levels_data[0].keys())
                                levels_rows.append(levels_headers)
                            for level in levels_data:
                                normalized_level = {k: str(v) if v is not None else "" for k, v in level.items()}
                                row_tuple = tuple(normalized_level.get(h, "") for h in levels_headers)
                                if row_tuple not in processed_levels:
                                    levels_rows.append([normalized_level.get(h, "") for h in levels_headers])
                                    processed_levels.add(row_tuple)
                        if filtered_stocks:
                            if not filtered_headers:
                                filtered_headers = list(filtered_stocks[-1].keys())
                                filtered_rows.append(filtered_headers)
                            for stock in filtered_stocks:
                                normalized_filtered = {k: str(v) if v is not None else "" for k, v in stock.items()}
                                row_tuple = tuple(normalized_filtered.get(h, "") for h in filtered_headers)
                                if row_tuple not in processed_filtered:
                                    filtered_rows.append([normalized_filtered.get(h, "") for h in filtered_headers])
                                    processed_filtered.add(row_tuple)

                    break
                else:
                    if print_details:
                        print(f"❌ Analysis failed for {stock_code}!")
                    break
            except Exception as e:
                if "429" in str(e) and not fetch_csv_data_stock:
                    if print_details:
                        print(f"Rate limit hit for {stock_code}. Retrying ({attempt + 1}/{max_retries}) after 5s...")
                    await asyncio.sleep(5)
                else:
                    if print_details:
                        print(f"Error for {stock_code}: {e}")
                    break
            if attempt == max_retries - 1:
                if print_details:
                    print(f"❌ Failed to fetch data for {stock_code} after {max_retries} attempts.")

        # Apply batch delay only for yfinance stocks when fetch_csv_data=False or CSV not found
        if not fetch_csv_data_stock:
            yfinance_stocks_processed += 1
            if yfinance_stocks_processed % batch_size == 0 and yfinance_stocks_processed < len(stock_codes):
                if print_details:
                    print(f"Pausing for {delay} seconds after processing {batch_size} yfinance stocks...")
                await asyncio.sleep(delay)

    # Save filtered stocks to CSV
    if output_format in ["csv", "both"] and filtered_stocks:
        pd.DataFrame(filtered_stocks).to_csv(
            filtered_file,
            mode='a',
            index=False,
            header=not filtered_file_exists
        )
        if print_details:
            print(f"Filtered stocks with current candle CHoCH/BOS saved to {filtered_file}")

    # Write to Google Sheets
    if output_format in ["google_sheets", "both"] and gspread_client and (summary_rows or levels_rows or filtered_rows):
        try:
            if summary_rows and len(summary_rows) > 1:
                summary_worksheet.update("A1", summary_rows)
                if print_details:
                    print(f"Updated Summaries worksheet with {len(summary_rows)-1} rows")
            if levels_rows and len(levels_rows) > 1:
                levels_worksheet.update("A1", levels_rows)
                if print_details:
                    print(f"Updated Levels worksheet with {len(levels_rows)-1} rows")
            if filtered_rows and len(filtered_rows) > 1:
                filtered_worksheet.update("A1", filtered_rows)
                if print_details:
                    print(f"Updated Current_Candle_Breaks worksheet with {len(filtered_rows)-1} rows")
            time.sleep(1)
        except Exception as e:
            print(f"Error updating Google Sheets: {e}")

    # Print output locations
    if output_format in ["csv", "both"] and (summary_file_exists or clear):
        print(f"\nSummaries saved to {summary_file}")
    if output_format in ["csv", "both"] and (levels_file_exists or clear):
        print(f"Levels saved to {levels_file}")  # Fixed from previous incorrect reference
    if output_format in ["csv", "both"] and (filtered_file_exists or clear):
        print(f"Current candle breaks saved to {filtered_file}")
    if output_format in ["google_sheets", "both"] and gspread_client:
        print(f"\nData saved to Google Sheets: {spreadsheet_url}")