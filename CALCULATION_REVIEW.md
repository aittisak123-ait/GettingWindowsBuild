# Calculation Review for _start_manage_thread Function

## Overview
This document provides a detailed review of the calculations in the `_start_manage_thread` function, which manages trading positions with stop-loss and take-profit logic for UP/DOWN token trading.

## Issues Found

### 1. **Stop-Loss Calculation - INCORRECT** ❌

**Current Code:**
```python
if entry_price > 0 and cur_exit is not None:
    dd_pct = (entry_price - float(cur_exit)) / float(entry_price) * 100.0
else:
    dd_pct = 0.0
```

**Problem:**
- This calculation assumes the value always goes DOWN (entry_price > cur_exit means loss)
- But for DOWN positions, when price goes UP, you also lose money
- The formula doesn't account for the position direction

**Example:**
- Entry: BUY UP token @ 0.48
- Current UP bid: 0.40
- Calculation: (0.48 - 0.40) / 0.48 * 100 = 16.67% ✓ (Correct - showing loss)

- Entry: BUY DOWN token @ 0.52  
- Current DOWN bid: 0.60
- Calculation: (0.52 - 0.60) / 0.52 * 100 = -15.38% ✗ (Negative! Should be +15.38% loss)

**Correct Formula:**
```python
if entry_price > 0 and cur_exit is not None:
    if entry_side == 'UP':
        # For UP position: loss when current price < entry price
        dd_pct = (entry_price - float(cur_exit)) / float(entry_price) * 100.0
    else:  # entry_side == 'DOWN'
        # For DOWN position: loss when current price > entry price
        dd_pct = (float(cur_exit) - entry_price) / float(entry_price) * 100.0
else:
    dd_pct = 0.0
```

### 2. **Take-Profit Calculation - CORRECT** ✓

**Current Code:**
```python
cost_sum = float(entry_price) + float(hedge_px)
if cost_sum > 0:
    profit_pct = (1.0 - cost_sum) / cost_sum * 100.0
```

**Analysis:**
- This is correct for binary outcome tokens where UP + DOWN should sum to ~1.0
- If you hold both tokens, you get 1.0 payout regardless of outcome
- Profit = (Payout - Cost) / Cost = (1.0 - cost_sum) / cost_sum
- Example: UP @ 0.48 + DOWN @ 0.49 = 0.97 cost
  - Profit: (1.0 - 0.97) / 0.97 * 100 = 3.09% ✓

### 3. **Hedge Price Selection - CORRECT** ✓

**Current Code:**
```python
if entry_side == 'UP':
    cur_exit = upb  # Use UP bid for exit
    hedge_px = dna  # Use DOWN ask for hedge
else:
    cur_exit = dnb  # Use DOWN bid for exit
    hedge_px = upa  # Use UP ask for hedge
```

**Analysis:**
- Correctly uses BID for selling (exit) and ASK for buying (hedge)
- This represents realistic trading prices

## Summary

| Calculation | Status | Severity |
|-------------|--------|----------|
| Stop-Loss | ❌ INCORRECT | HIGH |
| Take-Profit | ✓ CORRECT | - |
| Hedge Price | ✓ CORRECT | - |

## Recommendation

**CRITICAL FIX REQUIRED**: The stop-loss calculation for DOWN positions is incorrect and will show negative drawdown percentages, preventing the stop-loss from triggering properly. This could lead to larger losses than intended.
