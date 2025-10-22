"""Options chain adapter with pacing controls and filtering."""

import asyncio
from datetime import datetime
from decimal import Decimal
from typing import Any

from ib_async import Option, Stock
from loguru import logger

from ..config import get_options_config
from ..models.errors import IBKRPacingError, IBKRUnavailable
from ..schemas.models import OptionChain, OptionContract
from ..utils.observability import metrics


class IBKROptionsAdapter:
    """Options chain adapter with pacing controls and filtering."""

    def __init__(self, ib_client: Any):
        self.ib_client = ib_client

        # Get configuration
        options_config = get_options_config()

        self._pacing_semaphore = asyncio.Semaphore(options_config["semaphore_size"])
        self._pacing_delay = options_config["base_delay"]
        self._max_contracts = options_config["max_contracts"]
        self._max_retries = options_config["max_retries"]
        self._backoff_multiplier = options_config["backoff_multiplier"]
        self._pacing_errors = 0

    async def get_options_chain(
        self,
        symbol: str,
        expiry: str | None = None,
        moneyness_range: float = 0.2,  # ±20% around spot
        max_contracts: int = 50,
        strike_range: tuple[float, float] | None = None,
    ) -> OptionChain:
        """Get options chain with pacing controls and filtering."""
        await self.ib_client.ensure_connection()

        try:
            # Get underlying price first
            underlying_price = await self._get_underlying_price(symbol)

            # Get option parameters
            option_params = await self.ib_client.ib.reqSecDefOptParamsAsync(symbol, "", "", 0)

            if not option_params:
                return OptionChain(
                    underlying_symbol=symbol,
                    underlying_price=Decimal(str(underlying_price)),
                    contracts=[],
                    delayed=False,
                )

            # Process option parameters to get contracts
            contracts = await self._process_option_parameters(
                option_params,
                symbol,
                expiry,
                underlying_price,
                moneyness_range,
                max_contracts,
                strike_range,
            )

            return OptionChain(
                underlying_symbol=symbol,
                underlying_price=Decimal(str(underlying_price)),
                contracts=contracts,
                delayed=False,
            )

        except Exception as e:
            if "pacing" in str(e).lower():
                raise IBKRPacingError(f"Pacing violation for options chain {symbol}: {e}") from e
            elif "connection" in str(e).lower():
                raise IBKRUnavailable(f"Connection lost for options chain {symbol}: {e}") from e
            raise

    async def _process_option_parameters(
        self,
        option_params: list,
        symbol: str,
        expiry: str | None,
        underlying_price: float,
        moneyness_range: float,
        max_contracts: int,
        strike_range: tuple[float, float] | None,
    ) -> list:
        """Process option parameters to fetch contracts."""
        contracts = []
        total_requests = 0

        for opt_param in option_params:
            if not opt_param.expirations or not opt_param.strikes:
                continue

            # Filter expirations if specified
            expirations = opt_param.expirations
            if expiry:
                expirations = [exp for exp in expirations if exp == expiry]

            # Filter strikes by moneyness and range
            strikes = self._filter_strikes(
                opt_param.strikes, underlying_price, moneyness_range, strike_range
            )

            # Process expirations and strikes
            contracts_batch, requests_count = await self._process_expirations_and_strikes(
                symbol, expirations, strikes, max_contracts, total_requests
            )

            contracts.extend(contracts_batch)
            total_requests += requests_count

            if total_requests >= max_contracts:
                break

        return contracts

    async def _process_expirations_and_strikes(
        self,
        symbol: str,
        expirations: list[str],
        strikes: list[float],
        max_contracts: int,
        current_requests: int,
    ) -> tuple[list, int]:
        """Process expirations and strikes to fetch contracts."""
        contracts = []
        total_requests = current_requests

        # Limit total contracts
        max_per_expiry = min(max_contracts // len(expirations), 20)

        for exp in expirations[:3]:  # Limit to 3 expirations
            for strike in strikes[:max_per_expiry]:
                for right in ["C", "P"]:  # Call and Put
                    if total_requests >= max_contracts:
                        break

                    try:
                        # Use semaphore to control pacing
                        async with self._pacing_semaphore:
                            contract = await self._fetch_option_contract(symbol, exp, strike, right)
                            if contract:
                                contracts.append(contract)
                                total_requests += 1

                            # Apply pacing delay
                            await asyncio.sleep(self._pacing_delay * self._backoff_multiplier)

                    except IBKRPacingError:
                        # Handle pacing violations
                        await self._handle_pacing_error()
                        continue
                    except Exception as e:
                        logger.warning(
                            f"Error fetching option {symbol} {exp} {strike} {right}: {e}"
                        )
                        continue

            if total_requests >= max_contracts:
                break

        return contracts, total_requests - current_requests

    async def _get_underlying_price(self, symbol: str) -> float:
        """Get underlying stock price."""
        try:
            contract = Stock(symbol, "SMART", "USD")
            ticker = self.ib_client.ib.reqMktData(contract)
            await asyncio.sleep(0.5)  # Wait for data
            return ticker.last if ticker.last else 0.0
        except Exception as e:
            if "pacing" in str(e).lower():
                raise IBKRPacingError(f"Pacing violation for underlying {symbol}: {e}") from e
            elif "connection" in str(e).lower():
                raise IBKRUnavailable(f"Connection lost for underlying {symbol}: {e}") from e
            logger.warning(f"Error getting underlying price for {symbol}: {e}")
            return 0.0

    def _filter_strikes(
        self,
        strikes: list[float],
        underlying_price: float,
        moneyness_range: float,
        strike_range: tuple[float, float] | None,
    ) -> list[float]:
        """Filter strikes by moneyness and range."""
        if not strikes or underlying_price <= 0:
            return strikes[:10]  # Return first 10 if no price

        # Filter by moneyness
        min_strike = underlying_price * (1 - moneyness_range)
        max_strike = underlying_price * (1 + moneyness_range)

        # Apply custom range if provided
        if strike_range:
            min_strike = max(min_strike, strike_range[0])
            max_strike = min(max_strike, strike_range[1])

        filtered_strikes = [strike for strike in strikes if min_strike <= strike <= max_strike]

        # Sort by distance from underlying price
        filtered_strikes.sort(key=lambda x: abs(x - underlying_price))

        return filtered_strikes[:20]  # Limit to 20 strikes

    async def _fetch_option_contract(
        self, symbol: str, expiry: str, strike: float, right: str
    ) -> OptionContract | None:
        """Fetch a single option contract with error handling."""
        try:
            option = Option(symbol, expiry, strike, right, "SMART")
            ticker = self.ib_client.ib.reqMktData(option)
            await asyncio.sleep(0.1)  # Brief wait for data

            return OptionContract(
                symbol=symbol,
                expiry=datetime.strptime(expiry, "%Y%m%d"),
                strike=Decimal(str(strike)),
                option_type=right,  # type: ignore[arg-type]
                bid=ticker.bid,
                ask=ticker.ask,
                last=ticker.last,
                volume=ticker.volume,
                open_interest=ticker.openInterest,
                implied_volatility=ticker.impliedVolatility,
                delta=ticker.delta,
                gamma=ticker.gamma,
                theta=ticker.theta,
                vega=ticker.vega,
                delayed=False,
            )
        except Exception as e:
            if "pacing" in str(e).lower():
                raise IBKRPacingError(
                    f"Pacing violation for {symbol} {expiry} {strike} {right}"
                ) from e
            return None

    async def _handle_pacing_error(self) -> None:
        """Handle pacing violations with exponential backoff."""
        self._pacing_errors += 1
        self._backoff_multiplier = min(self._backoff_multiplier * 1.5, 5.0)

        # Update metrics
        metrics.ib_pacing_violations.inc()
        metrics.ib_backoff_events.inc()

        backoff_delay = self._pacing_delay * self._backoff_multiplier
        logger.warning(f"Pacing error #{self._pacing_errors}, backing off for {backoff_delay:.2f}s")

        await asyncio.sleep(backoff_delay)

        # Reset backoff after successful requests
        if self._pacing_errors > 0:
            self._pacing_errors = max(0, self._pacing_errors - 1)
            if self._pacing_errors == 0:
                self._backoff_multiplier = 1.0

    def get_pacing_stats(self) -> dict[str, Any]:
        """Get pacing statistics."""
        return {
            "pacing_errors": self._pacing_errors,
            "backoff_multiplier": self._backoff_multiplier,
            "semaphore_available": self._pacing_semaphore._value,
            "max_contracts": self._max_contracts,
        }
