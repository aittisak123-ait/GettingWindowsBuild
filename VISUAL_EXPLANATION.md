# Visual Explanation of the Stop-Loss Bug

```
═══════════════════════════════════════════════════════════════════════════════
                    STOP-LOSS CALCULATION BUG EXPLAINED
═══════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│                         UP POSITION (Works Correctly)                        │
└─────────────────────────────────────────────────────────────────────────────┘

Entry: BUY UP @ 0.48          →  You own UP token
                                  You profit if price goes UP
                                  You lose if price goes DOWN

Price Movement: 0.48 → 0.40   →  Price went DOWN
                                  YOU ARE LOSING MONEY! 📉

Original Formula:
  dd_pct = (0.48 - 0.40) / 0.48 × 100
         = 0.08 / 0.48 × 100
         = 16.67%                ✅ POSITIVE (Correct!)

Stop-Loss Check:
  if 16.67% >= 10%:             ✅ TRUE → Stop-loss TRIGGERS!
    → System hedges position
    → Loss is limited


┌─────────────────────────────────────────────────────────────────────────────┐
│                       DOWN POSITION (BUG! Broken!)                          │
└─────────────────────────────────────────────────────────────────────────────┘

Entry: BUY DOWN @ 0.50        →  You own DOWN token
                                  You profit if price goes DOWN
                                  You lose if price goes UP

Price Movement: 0.50 → 0.60   →  Price went UP
                                  YOU ARE LOSING MONEY! 📈

Original Formula (BUGGY):
  dd_pct = (0.50 - 0.60) / 0.50 × 100
         = -0.10 / 0.50 × 100
         = -20.00%               ❌ NEGATIVE (Wrong!)

Stop-Loss Check:
  if -20.00% >= 10%:            ❌ FALSE → Stop-loss DOES NOT TRIGGER!
    → System does NOTHING
    → Losses continue to grow
    → No protection!


═══════════════════════════════════════════════════════════════════════════════
                                 THE FIX
═══════════════════════════════════════════════════════════════════════════════

Fixed Formula:
  if entry_side == 'UP':
      dd_pct = (entry_price - cur_exit) / entry_price × 100
  else:  # entry_side == 'DOWN'
      dd_pct = (cur_exit - entry_price) / entry_price × 100
               └─────────┬────────┘
                    Subtraction order reversed!

DOWN Position with Fix:
  dd_pct = (0.60 - 0.50) / 0.50 × 100
         = 0.10 / 0.50 × 100
         = 20.00%                ✅ POSITIVE (Correct!)

Stop-Loss Check:
  if 20.00% >= 10%:             ✅ TRUE → Stop-loss TRIGGERS!
    → System hedges position
    → Loss is limited
    → Protection works!


═══════════════════════════════════════════════════════════════════════════════
                           WHY THIS MATTERS
═══════════════════════════════════════════════════════════════════════════════

Without Fix:                     With Fix:
┌─────────────────────┐         ┌─────────────────────┐
│   UP Positions:     │         │   UP Positions:     │
│   ✅ Protected      │         │   ✅ Protected      │
│                     │         │                     │
│   DOWN Positions:   │         │   DOWN Positions:   │
│   ❌ NOT Protected  │         │   ✅ Protected      │
│   (Bug!)            │         │   (Fixed!)          │
└─────────────────────┘         └─────────────────────┘

🔴 RISK: Unlimited losses        🟢 SAFE: Losses limited
   on DOWN positions                on both positions


═══════════════════════════════════════════════════════════════════════════════
                          REAL-WORLD EXAMPLE
═══════════════════════════════════════════════════════════════════════════════

Scenario: Bitcoin price prediction market
- You buy DOWN token @ $0.50 (betting price will go down)
- Stop-loss set at 10% loss
- Expected: If losing > 10%, system auto-hedges

What Actually Happens:

  Bitcoin price goes UP (you're wrong):
  ├─ Your DOWN token value: 0.50 → 0.60 → 0.70 → 0.80
  ├─ Your loss: 20% → 40% → 60%
  ├─ Without fix: Stop-loss NEVER triggers ❌
  └─ With fix: Stop-loss triggers at 10% ✅

Result without fix: 60% loss instead of 10% maximum! 💸
Result with fix: 10% maximum loss as intended 💰


═══════════════════════════════════════════════════════════════════════════════
```

## Key Insights

1. **The bug is subtle** - it only affects DOWN positions, so if you only tested with UP positions, you wouldn't notice it.

2. **The bug is dangerous** - it completely disables stop-loss protection for half of your possible trades.

3. **The fix is simple** - just 3 lines of code change, but critical for safety.

4. **The impact is severe** - without this fix, you could lose significantly more than your intended stop-loss threshold on any DOWN position trade.

## Mathematical Explanation

For UP positions:
- You lose when: entry_price > current_price
- Formula: (entry - current) / entry → **positive when losing** ✓

For DOWN positions:
- You lose when: current_price > entry_price
- Wrong formula: (entry - current) / entry → **negative when losing** ❌
- Correct formula: (current - entry) / entry → **positive when losing** ✓

The key insight: For DOWN positions, you need to reverse the subtraction because you're betting on the opposite direction!
