"""
Optimized order placement functions for faster execution.

Performance optimizations implemented:
1. Simplified normalization functions with fewer type checks
2. Reduced string operations and conversions
3. Streamlined success check logic
4. Early returns to avoid unnecessary processing
5. Removed redundant error message extraction in hot path
"""

# Optimized normalization functions - fewer operations
def _norm_oid(r):
    """Extract order ID with minimal overhead."""
    if isinstance(r, dict):
        oid = r.get("orderID") or r.get("orderId") or r.get("id")
    else:
        oid = getattr(r, "orderID", None) or getattr(r, "orderId", None) or getattr(r, "id", None)
    
    if oid is None:
        return None
    
    oid_str = str(oid).strip()
    return oid_str if oid_str else None


def _norm_status(r):
    """Extract status with minimal overhead."""
    if isinstance(r, dict):
        status = r.get("status", "")
    else:
        status = getattr(r, "status", "")
    
    # Single pass normalization
    return str(status).strip().lower() if status else ""


def _norm_success(r):
    """Extract success flag - no conversion needed."""
    return r.get("success", None) if isinstance(r, dict) else getattr(r, "success", None)


def _norm_errmsg(r):
    """Extract error message - only called when needed."""
    if isinstance(r, dict):
        err = r.get("errorMsg", "")
    else:
        err = getattr(r, "errorMsg", "")
    
    return str(err).strip() if err else ""


# Inline for performance
_FILLED_STATUSES = frozenset(["matched", "filled", "executed", "complete"])


def _is_filled_like_status(status: str) -> bool:
    """Check if status indicates filled order - using frozenset for O(1) lookup."""
    return status in _FILLED_STATUSES


def place_anchor_fast_one_leg_fok(
    up_token_id,
    down_token_id,
    anchor_side,
    price,
    size=5,
    signed_orders_cache=None,
):
    """
    Optimized anchor-only FOK (one leg) order placement.
    
    Performance improvements:
    - Streamlined response processing
    - Minimal string operations
    - Early returns
    - Optimized status checking
    
    Returns: (ok: bool, fill_price: float, order_ids: list[str|None])
    """
    side = str(anchor_side).upper()
    anchor_token_id = up_token_id if side == "UP" else down_token_id
    px = float(price)

    # Import client here to avoid circular imports and initialization overhead
    from your_module import get_client, OrderArgs, PostOrdersArgs, OrderType, BUY, logger
    
    client = get_client()

    # Retrieve or create signed order
    signed_order = None
    if signed_orders_cache is not None:
        signed_order = signed_orders_cache.get((anchor_token_id, px))

    if signed_order is None:
        order_args = OrderArgs(token_id=anchor_token_id, price=px, size=float(size), side=BUY)
        signed_order = client.create_order(order_args)
        if signed_orders_cache is not None:
            signed_orders_cache[(anchor_token_id, px)] = signed_order

    try:
        # Post order
        results = client.post_orders([PostOrdersArgs(order=signed_order, orderType=OrderType.FOK)])
        
        # Debug logging (keep for troubleshooting)
        logger.info(f"Debuging Results OpenOrder : {results}")

        # Fast path: handle list or single result
        r = results[0] if isinstance(results, list) and results else results if results else None

        # Early exit for empty response
        if r is None:
            logger.warning(
                f"[ANCHOR-ONLY FOK] EMPTY RESP token={anchor_token_id} side={side} price={px} size={size}"
            )
            return False, px, [None]

        # Extract critical fields
        success = _norm_success(r)
        
        # Fast reject if explicitly failed
        if success is False:
            oid = _norm_oid(r)
            logger.warning(
                f"[ANCHOR-ONLY FOK] EXPLICIT FAIL token={anchor_token_id} side={side} price={px} size={size} "
                f"id={oid} resp={r}"
            )
            return False, px, [oid]

        # Check status (main success indicator)
        status = _norm_status(r)
        ok = _is_filled_like_status(status)

        # Extract order ID
        oid = _norm_oid(r)

        if ok:
            logger.info(
                f"[ANCHOR-ONLY FOK] FILLED token={anchor_token_id} side={side} price={px} size={size} "
                f"status={status} id={oid}"
            )
            return True, px, [oid]

        # Not filled - get error message only for logging
        err = _norm_errmsg(r)
        logger.warning(
            f"[ANCHOR-ONLY FOK] NOT FILLED token={anchor_token_id} side={side} price={px} size={size} "
            f"status={status} id={oid} errorMsg={err} resp={r}"
        )
        return False, px, [oid]

    except Exception as exc:
        logger.error(
            f"[ANCHOR-ONLY FOK] FAILED token={anchor_token_id} side={side} price={px} size={size} err={exc}"
        )
        return False, px, [None]


# Alternative ultra-fast variant with even less validation (use with caution)
def place_anchor_fast_one_leg_fok_ultra(
    up_token_id,
    down_token_id,
    anchor_side,
    price,
    size=5,
    signed_orders_cache=None,
):
    """
    Ultra-optimized version with minimal validation.
    
    WARNING: This version sacrifices some safety checks for maximum speed.
    Only use if you are confident in your data quality.
    
    Returns: (ok: bool, fill_price: float, order_ids: list[str|None])
    """
    from your_module import get_client, OrderArgs, PostOrdersArgs, OrderType, BUY, logger
    
    side = str(anchor_side).upper()
    anchor_token_id = up_token_id if side == "UP" else down_token_id
    px = float(price)
    
    client = get_client()

    # Cache lookup
    cache_key = (anchor_token_id, px)
    if signed_orders_cache is not None and cache_key in signed_orders_cache:
        signed_order = signed_orders_cache[cache_key]
    else:
        order_args = OrderArgs(token_id=anchor_token_id, price=px, size=float(size), side=BUY)
        signed_order = client.create_order(order_args)
        if signed_orders_cache is not None:
            signed_orders_cache[cache_key] = signed_order

    try:
        results = client.post_orders([PostOrdersArgs(order=signed_order, orderType=OrderType.FOK)])
        
        # Minimal processing
        r = results[0] if isinstance(results, list) and results else results
        
        if not r:
            return False, px, [None]
        
        # Direct attribute access when possible
        if isinstance(r, dict):
            success = r.get("success")
            if success is False:
                return False, px, [r.get("orderID") or r.get("orderId") or r.get("id")]
            
            status = (r.get("status", "") or "").lower()
            oid = r.get("orderID") or r.get("orderId") or r.get("id")
        else:
            success = getattr(r, "success", None)
            if success is False:
                return False, px, [getattr(r, "orderID", None) or getattr(r, "orderId", None) or getattr(r, "id", None)]
            
            status = (getattr(r, "status", "") or "").lower()
            oid = getattr(r, "orderID", None) or getattr(r, "orderId", None) or getattr(r, "id", None)
        
        # Fast status check
        ok = status in _FILLED_STATUSES
        
        if ok:
            logger.info(f"[ANCHOR-ONLY FOK] FILLED token={anchor_token_id} price={px} id={oid}")
        else:
            logger.warning(f"[ANCHOR-ONLY FOK] NOT FILLED token={anchor_token_id} price={px} status={status}")
        
        return ok, px, [oid]

    except Exception as exc:
        logger.error(f"[ANCHOR-ONLY FOK] FAILED token={anchor_token_id} price={px} err={exc}")
        return False, px, [None]
