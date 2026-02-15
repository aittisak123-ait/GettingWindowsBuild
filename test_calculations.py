"""
Test cases to demonstrate the stop-loss calculation bug and the fix.
"""

def test_stop_loss_calculation_original():
    """Test the ORIGINAL (buggy) stop-loss calculation"""
    print("=" * 70)
    print("ORIGINAL CALCULATION (BUGGY)")
    print("=" * 70)
    
    # Test Case 1: UP position with loss
    entry_side = 'UP'
    entry_price = 0.48
    cur_exit = 0.40
    dd_pct = (entry_price - float(cur_exit)) / float(entry_price) * 100.0
    print(f"\nTest 1: {entry_side} position")
    print(f"  Entry Price: {entry_price}")
    print(f"  Current Exit Price: {cur_exit}")
    print(f"  Drawdown: {dd_pct:.2f}%")
    print(f"  Expected: ~16.67% loss")
    print(f"  Result: {'✓ CORRECT' if dd_pct > 0 else '✗ WRONG'}")
    
    # Test Case 2: DOWN position with loss
    entry_side = 'DOWN'
    entry_price = 0.52
    cur_exit = 0.60
    dd_pct = (entry_price - float(cur_exit)) / float(entry_price) * 100.0
    print(f"\nTest 2: {entry_side} position")
    print(f"  Entry Price: {entry_price}")
    print(f"  Current Exit Price: {cur_exit}")
    print(f"  Drawdown: {dd_pct:.2f}%")
    print(f"  Expected: ~15.38% loss (positive)")
    print(f"  Result: {'✗ WRONG - NEGATIVE VALUE!' if dd_pct < 0 else '✓ CORRECT'}")
    
    # Test Case 3: DOWN position - stop loss won't trigger!
    entry_side = 'DOWN'
    entry_price = 0.50
    cur_exit = 0.60
    dd_pct = (entry_price - float(cur_exit)) / float(entry_price) * 100.0
    STOP_LOSS_PCT = 10.0
    print(f"\nTest 3: {entry_side} position - Stop Loss Check")
    print(f"  Entry Price: {entry_price}")
    print(f"  Current Exit Price: {cur_exit}")
    print(f"  Drawdown: {dd_pct:.2f}%")
    print(f"  Stop Loss Threshold: {STOP_LOSS_PCT}%")
    print(f"  Should Trigger: YES (20% loss)")
    print(f"  Actually Triggers: {'YES ✓' if dd_pct >= STOP_LOSS_PCT else 'NO ✗ BUG!'}")


def test_stop_loss_calculation_fixed():
    """Test the FIXED stop-loss calculation"""
    print("\n\n" + "=" * 70)
    print("FIXED CALCULATION")
    print("=" * 70)
    
    # Test Case 1: UP position with loss
    entry_side = 'UP'
    entry_price = 0.48
    cur_exit = 0.40
    if entry_side == 'UP':
        dd_pct = (entry_price - float(cur_exit)) / float(entry_price) * 100.0
    else:
        dd_pct = (float(cur_exit) - entry_price) / float(entry_price) * 100.0
    print(f"\nTest 1: {entry_side} position")
    print(f"  Entry Price: {entry_price}")
    print(f"  Current Exit Price: {cur_exit}")
    print(f"  Drawdown: {dd_pct:.2f}%")
    print(f"  Expected: ~16.67% loss")
    print(f"  Result: {'✓ CORRECT' if dd_pct > 0 else '✗ WRONG'}")
    
    # Test Case 2: DOWN position with loss
    entry_side = 'DOWN'
    entry_price = 0.52
    cur_exit = 0.60
    if entry_side == 'UP':
        dd_pct = (entry_price - float(cur_exit)) / float(entry_price) * 100.0
    else:
        dd_pct = (float(cur_exit) - entry_price) / float(entry_price) * 100.0
    print(f"\nTest 2: {entry_side} position")
    print(f"  Entry Price: {entry_price}")
    print(f"  Current Exit Price: {cur_exit}")
    print(f"  Drawdown: {dd_pct:.2f}%")
    print(f"  Expected: ~15.38% loss (positive)")
    print(f"  Result: {'✓ CORRECT' if dd_pct > 0 else '✗ WRONG'}")
    
    # Test Case 3: DOWN position - stop loss should trigger!
    entry_side = 'DOWN'
    entry_price = 0.50
    cur_exit = 0.60
    if entry_side == 'UP':
        dd_pct = (entry_price - float(cur_exit)) / float(entry_price) * 100.0
    else:
        dd_pct = (float(cur_exit) - entry_price) / float(entry_price) * 100.0
    STOP_LOSS_PCT = 10.0
    print(f"\nTest 3: {entry_side} position - Stop Loss Check")
    print(f"  Entry Price: {entry_price}")
    print(f"  Current Exit Price: {cur_exit}")
    print(f"  Drawdown: {dd_pct:.2f}%")
    print(f"  Stop Loss Threshold: {STOP_LOSS_PCT}%")
    print(f"  Should Trigger: YES (20% loss)")
    print(f"  Actually Triggers: {'YES ✓ FIXED!' if dd_pct >= STOP_LOSS_PCT else 'NO ✗'}")


def test_take_profit_calculation():
    """Test the take-profit calculation (already correct)"""
    print("\n\n" + "=" * 70)
    print("TAKE-PROFIT CALCULATION (Already Correct)")
    print("=" * 70)
    
    # Test Case 1: Profitable arbitrage opportunity
    entry_price = 0.48
    hedge_px = 0.49
    cost_sum = float(entry_price) + float(hedge_px)
    profit_pct = (1.0 - cost_sum) / cost_sum * 100.0
    print(f"\nTest 1: Profitable scenario")
    print(f"  Entry Price: {entry_price}")
    print(f"  Hedge Price: {hedge_px}")
    print(f"  Total Cost: {cost_sum}")
    print(f"  Guaranteed Payout: 1.0")
    print(f"  Profit: {profit_pct:.2f}%")
    print(f"  Calculation: (1.0 - {cost_sum}) / {cost_sum} * 100 = {profit_pct:.2f}%")
    
    # Test Case 2: Break-even
    entry_price = 0.50
    hedge_px = 0.50
    cost_sum = float(entry_price) + float(hedge_px)
    profit_pct = (1.0 - cost_sum) / cost_sum * 100.0
    print(f"\nTest 2: Break-even scenario")
    print(f"  Entry Price: {entry_price}")
    print(f"  Hedge Price: {hedge_px}")
    print(f"  Total Cost: {cost_sum}")
    print(f"  Guaranteed Payout: 1.0")
    print(f"  Profit: {profit_pct:.2f}%")
    
    # Test Case 3: Loss scenario (shouldn't happen in real market)
    entry_price = 0.52
    hedge_px = 0.51
    cost_sum = float(entry_price) + float(hedge_px)
    profit_pct = (1.0 - cost_sum) / cost_sum * 100.0
    print(f"\nTest 3: Loss scenario")
    print(f"  Entry Price: {entry_price}")
    print(f"  Hedge Price: {hedge_px}")
    print(f"  Total Cost: {cost_sum}")
    print(f"  Guaranteed Payout: 1.0")
    print(f"  Profit: {profit_pct:.2f}% (negative = loss)")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("STOP-LOSS CALCULATION TEST SUITE")
    print("Testing Original vs Fixed Implementation")
    print("=" * 70)
    
    test_stop_loss_calculation_original()
    test_stop_loss_calculation_fixed()
    test_take_profit_calculation()
    
    print("\n\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("""
The CRITICAL BUG is in the stop-loss calculation for DOWN positions:

ORIGINAL CODE (BUGGY):
  dd_pct = (entry_price - float(cur_exit)) / float(entry_price) * 100.0

This formula only works for UP positions. For DOWN positions, when the 
price increases (you lose money), the result is NEGATIVE, so the stop-loss
never triggers!

FIXED CODE:
  if entry_side == 'UP':
      dd_pct = (entry_price - float(cur_exit)) / float(entry_price) * 100.0
  else:  # entry_side == 'DOWN'
      dd_pct = (float(cur_exit) - entry_price) / float(entry_price) * 100.0

This correctly handles both position types.

TAKE-PROFIT CALCULATION: Already correct, no changes needed.
    """)
