# Quick Reference: Stop-Loss Bug Fix

## The Problem

The original stop-loss calculation **ONLY works for UP positions** and produces **negative values for DOWN positions**, preventing the stop-loss from triggering.

---

## Side-by-Side Comparison

### ❌ ORIGINAL (BUGGY)
```python
# This formula works for UP but NOT for DOWN
if entry_price > 0 and cur_exit is not None:
    dd_pct = (entry_price - float(cur_exit)) / float(entry_price) * 100.0
else:
    dd_pct = 0.0

if dd_pct >= STOP_LOSS_PCT:  # This check fails for DOWN positions!
    # Trigger stop-loss
```

### ✅ FIXED
```python
# This formula works for BOTH UP and DOWN
if entry_price > 0 and cur_exit is not None:
    if entry_side == 'UP':
        dd_pct = (entry_price - float(cur_exit)) / float(entry_price) * 100.0
    else:  # entry_side == 'DOWN'
        dd_pct = (float(cur_exit) - entry_price) / float(entry_price) * 100.0
else:
    dd_pct = 0.0

if dd_pct >= STOP_LOSS_PCT:  # Now works correctly for both sides!
    # Trigger stop-loss
```

---

## Test Results

### Scenario: DOWN Position Losing Money

| Metric | Value |
|--------|-------|
| Entry Price | 0.50 |
| Current Price | 0.60 (price went UP = you lose) |
| Actual Loss | 20% |
| Stop-Loss Threshold | 10% |
| Should Trigger? | YES |

#### Original Calculation:
```python
dd_pct = (0.50 - 0.60) / 0.50 * 100
       = -0.10 / 0.50 * 100
       = -20.0%

# Check: -20.0% >= 10%?  FALSE ❌
# Stop-loss DOES NOT TRIGGER! (Bug!)
```

#### Fixed Calculation:
```python
dd_pct = (0.60 - 0.50) / 0.50 * 100
       = 0.10 / 0.50 * 100
       = 20.0%

# Check: 20.0% >= 10%?  TRUE ✅
# Stop-loss TRIGGERS correctly!
```

---

## Key Takeaway

**The bug causes DOWN positions to have NO stop-loss protection**, potentially leading to unlimited losses in DOWN trades while thinking you're protected!

---

## What Changed in Code

Only **3 lines changed** in the entire function:

```diff
  if entry_price > 0 and cur_exit is not None:
-     dd_pct = (entry_price - float(cur_exit)) / float(entry_price) * 100.0
+     if entry_side == 'UP':
+         dd_pct = (entry_price - float(cur_exit)) / float(entry_price) * 100.0
+     else:  # entry_side == 'DOWN'
+         dd_pct = (float(cur_exit) - entry_price) / float(entry_price) * 100.0
  else:
      dd_pct = 0.0
```

Everything else remains exactly the same!
