"""
Corrected Trading Manager - _start_manage_thread Function

This module contains the corrected version of the _start_manage_thread function
with fixed stop-loss calculation for both UP and DOWN positions.
"""

import threading
import time

# Constants (these should be defined in your actual code)
# HEDGE_POLL_SEC = 0.5
# STOP_LOSS_PCT = 10.0
# TAKE_PROFIT_PCT = 2.0

# Global state (these should be defined in your actual code)
# _manage_active = False
# _manage_lock = threading.Lock()


def _start_manage_thread(entry_side: str, entry_price: float, size: float, on_complete=None):
    """
    Start a background thread to manage a position with stop-loss and take-profit.
    
    Args:
        entry_side: 'UP' or 'DOWN' - the side of the entry position
        entry_price: The price at which the position was entered
        size: The size of the position
        on_complete: Callback function when position is closed
    """
    nonlocal _manage_active
    with _manage_lock:
        if _manage_active:
            return
        _manage_active = True

    def _worker():
        nonlocal _manage_active
        try:
            opp_side = 'DOWN' if entry_side == 'UP' else 'UP'
            # We hold entry_side token after fill. Use BID as the 'exit' reference.
            while True:
                upb, upa, dnb, dna = _get_px_state()
                if upb is None:
                    time.sleep(HEDGE_POLL_SEC)
                    continue

                if entry_side == 'UP':
                    cur_exit = upb
                    hedge_px = dna  # buy opposite (DOWN) at ask for best chance to fill
                else:
                    cur_exit = dnb
                    hedge_px = upa  # buy opposite (UP) at ask

                # ============================================================
                # CORRECTED: Stop-loss calculation for both UP and DOWN sides
                # ============================================================
                if entry_price > 0 and cur_exit is not None:
                    if entry_side == 'UP':
                        # For UP position: loss when current price < entry price
                        # Example: Entry @ 0.48, Current @ 0.40 => (0.48-0.40)/0.48 = 16.67% loss
                        dd_pct = (entry_price - float(cur_exit)) / float(entry_price) * 100.0
                    else:  # entry_side == 'DOWN'
                        # For DOWN position: loss when current price > entry price
                        # Example: Entry @ 0.52, Current @ 0.60 => (0.60-0.52)/0.52 = 15.38% loss
                        dd_pct = (float(cur_exit) - entry_price) / float(entry_price) * 100.0
                else:
                    dd_pct = 0.0

                if dd_pct >= STOP_LOSS_PCT:
                    print(f"\n🔴 STOP LOSS TRIGGERED | entry={entry_price:.2f} cur_bid={cur_exit:.2f} dd={dd_pct:.2f}% => HEDGE {opp_side}@{hedge_px:.2f}", flush=True)
                    # Keep trying until hedge leg is actually filled (avoid unpaired positions)
                    while True:
                        _hedged = _try_place_fok_until_filled(opp_side, hedge_px, size)
                        if _hedged:
                            if callable(on_complete):
                                try:
                                    on_complete(entry_side, entry_price, opp_side, float(hedge_px), float(size))
                                except Exception as _ce:
                                    print(f"⚠️ on_complete error: {_ce}", flush=True)
                            break
                        print(f"⚠️ HEDGE not filled yet. Retrying {opp_side}@{hedge_px:.2f} ...", flush=True)
                        # refresh latest hedge ask before retry
                        upb, upa, dnb, dna = _get_px_state()
                        hedge_px = dna if entry_side == 'UP' else upa
                        time.sleep(max(0.05, HEDGE_POLL_SEC))
                    break

                # Take-profit (arbitrage cost): profit% = (1 - (entry + opp_ask)) / (entry + opp_ask) * 100
                # This calculation is CORRECT - no changes needed
                cost_sum = None
                profit_pct = 0.0
                if hedge_px is not None:
                    cost_sum = float(entry_price) + float(hedge_px)
                    if cost_sum > 0:
                        profit_pct = (1.0 - cost_sum) / cost_sum * 100.0

                if cost_sum is not None and profit_pct >= TAKE_PROFIT_PCT:
                    print(
                        f"🟢 TAKE PROFIT | entry={entry_price:.2f} hedge_ask={hedge_px:.2f} "
                        f"cost_sum={cost_sum:.2f} profit={profit_pct:.2f}% target>={TAKE_PROFIT_PCT:.2f}% "
                        f"=> HEDGE {opp_side}@{hedge_px:.2f}",
                        flush=True,
                    )
                    # Keep trying until hedge leg is actually filled (avoid unpaired positions)
                    while True:
                        _hedged = _try_place_fok_until_filled(opp_side, hedge_px, size)
                        if _hedged:
                            if callable(on_complete):
                                try:
                                    on_complete(entry_side, entry_price, opp_side, float(hedge_px), float(size))
                                except Exception as _ce:
                                    print(f"⚠️ on_complete error: {_ce}", flush=True)
                            break
                        print(f"⚠️ HEDGE not filled yet. Retrying {opp_side}@{hedge_px:.2f} ...", flush=True)
                        # refresh latest hedge ask before retry
                        upb, upa, dnb, dna = _get_px_state()
                        hedge_px = dna if entry_side == 'UP' else upa
                        time.sleep(max(0.05, HEDGE_POLL_SEC))
                    break

                time.sleep(HEDGE_POLL_SEC)
        finally:
            with _manage_lock:
                _manage_active = False

    threading.Thread(target=_worker, daemon=True).start()


# Example helper functions that would need to be defined in actual implementation:
def _get_px_state():
    """Get current price state (upb, upa, dnb, dna)"""
    # This should return: up_bid, up_ask, down_bid, down_ask
    pass


def _try_place_fok_until_filled(side: str, price: float, size: float) -> bool:
    """Try to place a Fill-Or-Kill order until filled"""
    # This should return True if filled, False otherwise
    pass
