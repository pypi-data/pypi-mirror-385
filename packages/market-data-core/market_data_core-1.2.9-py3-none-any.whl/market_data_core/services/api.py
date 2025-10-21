"""Deprecated FastAPI service module.

This module is deprecated and will be removed in v2.0.
For new projects, use market_data_core contracts with your own API layer.
This module requires optional dependencies.

Install with: pip install 'market-data-core[compat]'
"""
import warnings

warnings.warn(
    "services.api module is deprecated and will be removed in v2.0. "
    "Install optional dependencies with: pip install 'market-data-core[compat]'",
    DeprecationWarning,
    stacklevel=2,
)

from datetime import UTC, datetime
from typing import Any

try:
    from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect
except ImportError as e:
    raise RuntimeError(
        "This deprecated module requires optional dependencies. "
        "Install with: pip install 'market-data-core[compat]'"
    ) from e

try:
    from fastapi.responses import JSONResponse
    from loguru import logger
except ImportError as e:
    raise RuntimeError(
        "This deprecated module requires optional dependencies. "
        "Install with: pip install 'market-data-core[compat]'"
    ) from e

from pydantic import BaseModel

from ..adapters.ibkr_adapter import IBKRPriceAdapter
from ..adapters.ibkr_streams import IBKRStreams
from ..models.errors import (
    ConnectionError,
    ConnectionException,
    ErrorDetail,
    IBKRPacingError,
    IBKRUnavailable,
    ProviderError,
    RateLimitError,
    ValidationError,
)
from ..schemas.models import AccountSummary, Health, OptionChain, Position, PriceBar
from ..utils.ibkr_mapping import validate_interval, validate_what_to_show
from ..utils.observability import log_operation, setup_observability
from .facade import DataFacade
from .ib_client import ib_client
from .websocket_manager import websocket_manager

app = FastAPI(
    title="market-data-core",
    version="0.1.0",
    description="Professional IBKR market data and trading platform",
    tags_metadata=[
        {"name": "Prices", "description": "Historical price data"},
        {"name": "Options", "description": "Options chains and Greeks"},
        {"name": "Accounts", "description": "Account and portfolio data"},
        {"name": "Health", "description": "System health and status"},
        {"name": "Streaming", "description": "Real-time data streams"},
    ],
)

# Wire the IBKR adapter with connection manager
ibkr_adapter = IBKRPriceAdapter()
ibkr_streams = IBKRStreams(ib_client)
facade = DataFacade(price_provider=ibkr_adapter)

# Setup observability
setup_observability(app)


class PricesResponse(BaseModel):
    data: list[PriceBar]


class OptionsResponse(BaseModel):
    data: OptionChain


class PositionsResponse(BaseModel):
    data: list[Position]


class AccountResponse(BaseModel):
    data: AccountSummary


@app.get("/health", response_model=Health, tags=["Health"])
async def health() -> Health:
    """Get system health and connection status."""
    return ib_client.get_health_stats()


@app.get("/prices", response_model=PricesResponse, tags=["Prices"])
async def prices(
    symbol: str = Query(..., min_length=1, description="Ticker symbol"),
    interval: str = Query("1d", description="Time interval (1s, 5s, 1m, 5m, 15m, 1h, 1d)"),
    limit: int = Query(50, ge=1, le=1000, description="Number of bars to return"),
    what: str = Query("TRADES", description="Data type (TRADES, MIDPOINT, BID, ASK)"),
) -> PricesResponse | JSONResponse:
    """Get historical price data for a symbol."""
    async with log_operation(
        "get_prices", symbol=symbol, interval=interval, limit=limit, what=what
    ):
        try:
            # Validate parameters
            interval = validate_interval(interval)
            what = validate_what_to_show(what)

            # Ensure connection
            await ib_client.ensure_connection()

            bars = await facade.get_price_bars(symbol=symbol, interval=interval, limit=limit)
            return PricesResponse(data=list(bars))

        except ValueError as e:
            return JSONResponse(
                status_code=422,
                content=ValidationError(
                    error=ErrorDetail(
                        type="validation_error",
                        message=str(e),
                        provider_code=None,
                        retry_after=None,
                    )
                ).model_dump(),
            )
        except ConnectionException as e:
            return JSONResponse(
                status_code=503,
                content=ConnectionError(
                    error=ErrorDetail(
                        type="connection_error",
                        message=str(e),
                        provider_code=None,
                        retry_after=None,
                    )
                ).model_dump(),
            )
        except Exception as e:
            # Check for IBKR pacing errors
            error_msg = str(e).lower()
            if "pacing" in error_msg or "rate" in error_msg or "throttle" in error_msg:
                return JSONResponse(
                    status_code=429,
                    content=RateLimitError(
                        error=ErrorDetail(
                            type="rate_limit_error",
                            message="Rate limit exceeded - please retry after delay",
                            provider_code=None,
                            retry_after=60,
                        )
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=502,
                content=ProviderError(
                    error=ErrorDetail(
                        type="provider_error",
                        message=str(e),
                        provider_code="IBKR_ERROR",
                        retry_after=None,
                    )
                ).model_dump(),
            )


@app.get("/options", response_model=OptionsResponse, tags=["Options"])
async def options(
    symbol: str = Query(..., min_length=1, description="Underlying symbol"),
    expiry: str | None = Query(None, description="Expiry date (YYYYMMDD format)"),
) -> OptionsResponse | JSONResponse:
    """Get options chain for a symbol."""
    try:
        # Ensure connection
        await ib_client.ensure_connection()

        chain = await ibkr_adapter.get_options_chain(symbol=symbol, expiry=expiry)
        return OptionsResponse(data=chain)

    except ConnectionException as e:
        return JSONResponse(
            status_code=503,
            content=ConnectionError(
                error=ErrorDetail(
                    type="connection_error",
                    message=str(e),
                    provider_code=None,
                    retry_after=None,
                )
            ).model_dump(),
        )
    except Exception as e:
        return JSONResponse(
            status_code=502,
            content=ProviderError(
                error=ErrorDetail(
                    type="provider_error",
                    message=str(e),
                    provider_code="IBKR_ERROR",
                    retry_after=None,
                )
            ).model_dump(),
        )


@app.get("/positions", response_model=PositionsResponse, tags=["Accounts"])
async def positions() -> PositionsResponse | JSONResponse:
    """Get current account positions."""
    try:
        # Ensure connection
        await ib_client.ensure_connection()

        positions = await ibkr_adapter.get_positions()
        return PositionsResponse(data=positions)

    except ConnectionException as e:
        return JSONResponse(
            status_code=503,
            content=ConnectionError(
                error=ErrorDetail(
                    type="connection_error",
                    message=str(e),
                    provider_code=None,
                    retry_after=None,
                )
            ).model_dump(),
        )
    except Exception as e:
        return JSONResponse(
            status_code=502,
            content=ProviderError(
                error=ErrorDetail(
                    type="provider_error",
                    message=str(e),
                    provider_code="IBKR_ERROR",
                    retry_after=None,
                )
            ).model_dump(),
        )


@app.get("/account", response_model=AccountResponse, tags=["Accounts"])
async def account(
    account_id: str = Query(..., description="Account ID")
) -> AccountResponse | JSONResponse:
    """Get account summary."""
    try:
        # Ensure connection
        await ib_client.ensure_connection()

        summary = await ibkr_adapter.get_account_summary(account_id=account_id)
        return AccountResponse(data=summary)

    except ConnectionException as e:
        return JSONResponse(
            status_code=503,
            content=ConnectionError(
                error=ErrorDetail(
                    type="connection_error",
                    message=str(e),
                    provider_code=None,
                    retry_after=None,
                )
            ).model_dump(),
        )
    except Exception as e:
        return JSONResponse(
            status_code=502,
            content=ProviderError(
                error=ErrorDetail(
                    type="provider_error",
                    message=str(e),
                    provider_code="IBKR_ERROR",
                    retry_after=None,
                )
            ).model_dump(),
        )


@app.get("/contracts/resolve", tags=["Contracts"], response_model=None)
async def resolve_contract(
    symbol: str = Query(..., min_length=1, description="Symbol to resolve"),
    sec_type: str = Query("STK", description="Security type"),
    exchange: str = Query("SMART", description="Exchange"),
    currency: str = Query("USD", description="Currency"),
) -> dict[str, Any] | JSONResponse:
    """Resolve contract details for a symbol."""
    try:
        # Ensure connection
        await ib_client.ensure_connection()

        # This would need to be implemented in the adapter
        # For now, return a placeholder
        return {
            "conid": 12345,
            "symbol": symbol,
            "primary_exchange": exchange,
            "currency": currency,
            "sec_type": sec_type,
        }

    except ConnectionException as e:
        return JSONResponse(
            status_code=503,
            content=ConnectionError(
                error=ErrorDetail(
                    type="connection_error",
                    message=str(e),
                    provider_code=None,
                    retry_after=None,
                )
            ).model_dump(),
        )
    except Exception as e:
        return JSONResponse(
            status_code=502,
            content=ProviderError(
                error=ErrorDetail(
                    type="provider_error",
                    message=str(e),
                    provider_code="IBKR_ERROR",
                    retry_after=None,
                )
            ).model_dump(),
        )


# WebSocket streaming endpoints
@app.websocket("/ws/quotes/{symbol}")
async def websocket_quotes(websocket: WebSocket, symbol: str) -> None:
    """Stream real-time quotes for a symbol using async generators."""
    await websocket_manager.connect(websocket, "quotes")
    try:
        # Ensure connection
        await ib_client.ensure_connection()

        # Stream quotes using async generator
        async for quote in ibkr_streams.stream_quotes(symbol):
            # Broadcast to all quote subscribers
            await websocket_manager.broadcast_quote(symbol, quote)
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, "quotes")
    except IBKRPacingError as e:
        logger.warning(f"Pacing error in quote stream for {symbol}: {e}")
        websocket_manager.disconnect(websocket, "quotes")
    except IBKRUnavailable as e:
        logger.error(f"IBKR unavailable for quote stream {symbol}: {e}")
        websocket_manager.disconnect(websocket, "quotes")
    except Exception as e:
        logger.error(f"Error in quote stream for {symbol}: {e}")
        websocket_manager.disconnect(websocket, "quotes")
    finally:
        # Stop the stream when WebSocket disconnects
        await ibkr_streams.stop_stream("quotes", symbol)


@app.websocket("/ws/depth/{symbol}")
async def websocket_depth(websocket: WebSocket, symbol: str) -> None:
    """Stream market depth (Level 2) for a symbol using async generators."""
    await websocket_manager.connect(websocket, "depth")
    try:
        # Ensure connection
        await ib_client.ensure_connection()

        # Stream depth using async generator
        async for depth in ibkr_streams.stream_depth(symbol):
            # Broadcast to all depth subscribers
            await websocket_manager.broadcast_depth(symbol, depth)
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, "depth")
    except IBKRPacingError as e:
        logger.warning(f"Pacing error in depth stream for {symbol}: {e}")
        websocket_manager.disconnect(websocket, "depth")
    except IBKRUnavailable as e:
        logger.error(f"IBKR unavailable for depth stream {symbol}: {e}")
        websocket_manager.disconnect(websocket, "depth")
    except Exception as e:
        logger.error(f"Error in depth stream for {symbol}: {e}")
        websocket_manager.disconnect(websocket, "depth")
    finally:
        # Stop the stream when WebSocket disconnects
        await ibkr_streams.stop_stream("depth", symbol)


@app.websocket("/ws/portfolio/{account_id}")
async def websocket_portfolio(websocket: WebSocket, account_id: str) -> None:
    """Stream portfolio updates for an account using async generators."""
    await websocket_manager.connect(websocket, "portfolio")
    try:
        # Ensure connection
        await ib_client.ensure_connection()

        # Stream portfolio using async generator
        async for portfolio in ibkr_streams.stream_portfolio(account_id):
            # Broadcast to all portfolio subscribers
            await websocket_manager.broadcast_portfolio(account_id, portfolio)
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, "portfolio")
    except IBKRPacingError as e:
        logger.warning(f"Pacing error in portfolio stream for {account_id}: {e}")
        websocket_manager.disconnect(websocket, "portfolio")
    except IBKRUnavailable as e:
        logger.error(f"IBKR unavailable for portfolio stream {account_id}: {e}")
        websocket_manager.disconnect(websocket, "portfolio")
    except Exception as e:
        logger.error(f"Error in portfolio stream for {account_id}: {e}")
        websocket_manager.disconnect(websocket, "portfolio")
    finally:
        # Stop the stream when WebSocket disconnects
        await ibkr_streams.stop_stream("portfolio", account_id)


@app.get("/healthz")
async def healthz() -> dict[str, Any]:
    """Health check endpoint - IB client connected + heartbeat timestamp."""
    try:
        # Check IBKR connection status
        is_connected = await ib_client.is_connected_async()

        # Get connection heartbeat timestamp
        heartbeat_timestamp = ib_client.get_last_heartbeat()

        # Get WebSocket stats
        ws_stats = websocket_manager.get_stats()

        return {
            "status": "healthy" if is_connected else "unhealthy",
            "ibkr_connected": is_connected,
            "heartbeat_timestamp": heartbeat_timestamp.isoformat() if heartbeat_timestamp else None,
            "websocket_connections": ws_stats["total_connections"],
            "timestamp": datetime.now(UTC).isoformat(),
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now(UTC).isoformat(),
        }


@app.get("/readyz")
async def readyz() -> dict[str, Any]:
    """Readiness check endpoint - streaming registry rehydrated (after reconnect)."""
    try:
        # Check if IBKR is connected and ready
        is_connected = await ib_client.is_connected_async()

        # Check if streaming registry is properly rehydrated
        registry_status = ib_client.get_registry_status()

        # Get active subscriptions
        active_subscriptions = ib_client.get_active_subscriptions()

        return {
            "status": "ready" if is_connected and registry_status["rehydrated"] else "not_ready",
            "ibkr_connected": is_connected,
            "registry_rehydrated": registry_status["rehydrated"],
            "active_subscriptions": len(active_subscriptions),
            "subscription_types": list(active_subscriptions.keys()),
            "timestamp": datetime.now(UTC).isoformat(),
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {
            "status": "not_ready",
            "error": str(e),
            "timestamp": datetime.now(UTC).isoformat(),
        }


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Clean up IBKR connection and streams on shutdown."""
    await ibkr_streams.stop_all_streams()
    await ibkr_adapter.disconnect()
