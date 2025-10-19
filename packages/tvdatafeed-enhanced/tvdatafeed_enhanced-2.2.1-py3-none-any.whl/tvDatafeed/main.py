"""TradingView data feed client for historical and real-time market data."""

from __future__ import annotations

import asyncio
import datetime
import enum
import json
import logging
import random
import re
import string
import threading
import webbrowser
from contextlib import contextmanager
from pathlib import Path
from typing import ClassVar, TYPE_CHECKING

import pandas as pd
import requests
from websockets import connect
from websocket import create_connection, WebSocket

if TYPE_CHECKING:
    from collections.abc import Generator

logger = logging.getLogger(__name__)


class Interval(enum.Enum):
    """Supported time intervals for market data."""

    in_1_minute = "1"
    in_3_minute = "3"
    in_5_minute = "5"
    in_15_minute = "15"
    in_30_minute = "30"
    in_45_minute = "45"
    in_1_hour = "1H"
    in_2_hour = "2H"
    in_3_hour = "3H"
    in_4_hour = "4H"
    in_daily = "1D"
    in_weekly = "1W"
    in_monthly = "1M"
    in_3_monthly = "3M"
    in_6_monthly = "6M"
    in_yearly = "12M"


class TvDatafeed:
    """TradingView data feed client for downloading historical market data.

    Supports both authenticated and anonymous access to TradingView data.
    Authenticated access provides more data and fewer restrictions.

    Args:
        username: TradingView username (optional for anonymous access)
        password: TradingView password (optional for anonymous access)
        token_cache_file: Path to cache authentication token
    """

    __user_url: ClassVar[str] = "https://www.tradingview.com/accounts/current/"
    __sign_in_url: ClassVar[str] = "https://www.tradingview.com/accounts/signin/"
    __search_url: ClassVar[str] = "https://symbol-search.tradingview.com/symbol_search/?text={}&hl=1&exchange={}&lang=en&type=&domain=production"
    __ws_headers: ClassVar[dict[str, str]] = {"Origin": "https://data.tradingview.com"}
    __signin_headers: ClassVar[dict[str, str]] = {"Referer": "https://www.tradingview.com"}
    __ws_timeout: ClassVar[int] = 30

    def __init__(
        self,
        username: str | None = None,
        password: str | None = None,
        token_cache_file: str | Path = "~/.tv_token.json",
    ) -> None:
        """Initialize TradingView data feed client."""
        self.ws_debug: bool = False
        self.token_cache_file = Path(token_cache_file).expanduser()
        self._lock = threading.Lock()
        self._ws_lock = threading.Lock()

        # Try to load cached token first
        token = self._load_token()

        if token:
            self.token: str | None = token
            logger.info("Using cached authentication token")
        elif username and password:
            self.token = self._login_and_get_token(username, password)
            self._save_token(self.token)
            logger.info("Logged in successfully and cached token")
        else:
            self.token = None
            logger.warning("Using anonymous access - data may be limited")

    def _load_token(self) -> str | None:
        """Load authentication token from cache file.

        Returns:
            Cached token if valid, None otherwise
        """
        if not self.token_cache_file.exists():
            return None

        try:
            data = json.loads(self.token_cache_file.read_text())
            token = data.get("token")

            if token and self._is_token_valid(token):
                return token
            else:
                logger.info("Cached token expired, removing")
                self.token_cache_file.unlink(missing_ok=True)
                return None
        except Exception as e:
            logger.debug("Failed to load token cache: %s", e)
            return None

    def _is_token_valid(self, token: str) -> bool:
        """Validate authentication token by checking JWT expiration.

        Args:
            token: Authentication token to validate

        Returns:
            True if token is valid and not expired, False otherwise
        """
        try:
            import base64

            # Decode JWT payload (middle part between dots)
            parts = token.split('.')
            if len(parts) != 3:
                logger.debug("Invalid JWT format")
                return False

            payload = parts[1]

            # Add padding if needed for base64 decoding
            padding = 4 - len(payload) % 4
            if padding != 4:
                payload += '=' * padding

            # Decode and parse payload
            decoded = base64.urlsafe_b64decode(payload)
            data = json.loads(decoded)

            # Check expiration
            exp = data.get('exp')
            if not exp:
                logger.debug("Token has no expiration claim")
                return False

            # Compare with current time (use timezone-aware datetime)
            exp_time = datetime.datetime.fromtimestamp(exp, tz=datetime.timezone.utc)
            now = datetime.datetime.now(datetime.timezone.utc)

            is_valid = now < exp_time
            if not is_valid:
                logger.debug("Token expired at %s", exp_time)

            return is_valid

        except Exception as e:
            logger.debug("Token validation failed: %s", e)
            return False

    def _save_token(self, token: str) -> None:
        """Save authentication token to cache file.

        Args:
            token: Authentication token to cache
        """
        try:
            self.token_cache_file.parent.mkdir(parents=True, exist_ok=True)
            self.token_cache_file.write_text(json.dumps({"token": token}))
        except Exception as e:
            logger.warning("Failed to save token: %s", e)

    def _login_and_get_token(self, username: str, password: str) -> str:
        """Authenticate with TradingView and get token.

        Args:
            username: TradingView username
            password: TradingView password

        Returns:
            Authentication token

        Raises:
            ValueError: If login fails
        """
        token = self.__auth(username, password)
        if not token:
            raise ValueError("Login failed - check your credentials")
        return token

    def _handle_captcha_login(self, username: str) -> str | None:
        """Handle login when CAPTCHA is required.

        Opens browser for user to complete CAPTCHA and login manually.
        Attempts to extract token from browser cookies or prompts user.

        Args:
            username: TradingView username

        Returns:
            Authentication token or None on failure
        """
        logger.info("Opening browser for manual login with CAPTCHA...")

        # Open TradingView login page in browser
        login_url = "https://www.tradingview.com/accounts/signin/"
        try:
            webbrowser.open(login_url)
            logger.info("Browser opened. Please complete login with CAPTCHA.")
        except Exception as e:
            logger.warning("Failed to open browser automatically: %s", e)
            logger.info("Please open this URL manually: %s", login_url)

        # Try to extract token from browser cookies
        token = self._extract_token_from_browser()
        if token:
            logger.info("Successfully extracted token from browser!")
            return token

        # Fallback: Instruct user to provide token manually
        print("\n" + "="*70)
        print("CAPTCHA REQUIRED - Manual Authentication Needed")
        print("="*70)
        print("\n⚠️  NOTE: Browser sessionid does NOT work for API authentication!")
        print("You need to extract the auth_token from the login API response.")
        print("\nA browser window has been opened (or open this URL manually):")
        print(f"  {login_url}")
        print("\nOption 1: Use Network Tab (Recommended):")
        print("  1. Open browser DevTools BEFORE logging in:")
        print("     - Chrome/Edge: Press F12 or Ctrl+Shift+I (Cmd+Option+I on Mac)")
        print("     - Firefox: Press F12 or Ctrl+Shift+I (Cmd+Option+I on Mac)")
        print("  2. Go to the 'Network' tab")
        print("  3. Keep DevTools open and complete CAPTCHA + login")
        print("  4. After login, find the 'signin' request in Network tab")
        print("  5. Click it, go to 'Response' tab")
        print("  6. Look for: {\"user\":{\"auth_token\":\"...\"")
        print("  7. Copy the auth_token value (long string)")
        print("\nOption 2: Use Console (if login already complete):")
        print("  1. Open browser DevTools")
        print("  2. Go to the 'Console' tab")
        print("  3. Paste and run this command:")
        print()
        print('     (function() {')
        print('       // Check cookies')
        print('       const cookieMatch = document.cookie.match(/authToken=([^;]+)/);')
        print('       if (cookieMatch) return cookieMatch[1];')
        print('       ')
        print('       // Check localStorage')
        print('       for (let key of Object.keys(localStorage)) {')
        print('         if (key.toLowerCase().includes("auth") || key.toLowerCase().includes("token")) {')
        print('           const val = localStorage.getItem(key);')
        print('           if (val && val.length > 50) return val;')
        print('         }')
        print('       }')
        print('       ')
        print('       // Check sessionStorage')
        print('       for (let key of Object.keys(sessionStorage)) {')
        print('         if (key.toLowerCase().includes("auth") || key.toLowerCase().includes("token")) {')
        print('           const val = sessionStorage.getItem(key);')
        print('           if (val && val.length > 50) return val;')
        print('         }')
        print('       }')
        print('       ')
        print('       return "Token not found. Run the commands below to see all storage.";')
        print('     })();')
        print()
        print("  5. If token not found, run these to see all storage:")
        print('     Object.keys(localStorage);')
        print('     Object.keys(sessionStorage);')
        print()
        print("  6. Copy the token (long string) that appears")
        print("     (If you see 'Token not found', look for keys with 'auth' or 'token')")
        print("\nAlternatively, if you have browser_cookie3 installed,")
        print("the token will be automatically extracted after you login.")
        print("="*70 + "\n")

        # Wait for user to complete login and optionally enter token
        try:
            user_input = input("Enter auth token (or press Enter to retry auto-extraction): ").strip()

            if user_input:
                # Validate token format (should be a long alphanumeric string)
                if len(user_input) > 20 and user_input.replace("-", "").replace("_", "").isalnum():
                    logger.info("Token received from user input")
                    return user_input
                else:
                    logger.error("Invalid token format")
                    return None
            else:
                # Retry extraction
                logger.info("Retrying token extraction from browser...")
                token = self._extract_token_from_browser()
                if token:
                    logger.info("Successfully extracted token on retry!")
                    return token
                else:
                    logger.error("Failed to extract token. Please try manual entry.")
                    return None

        except (KeyboardInterrupt, EOFError):
            logger.warning("Login cancelled by user")
            return None

    def _extract_token_from_browser(self) -> str | None:
        """Extract TradingView auth token from browser cookies.

        Requires browser_cookie3 package (optional dependency).
        Looks for: authToken or auth_token cookies.

        NOTE: sessionid is NOT extracted as it only works for browser sessions,
        not for API/WebSocket authentication. The API requires a specific
        auth_token which is only available in the POST response body.

        Returns:
            Auth token if found, None otherwise
        """
        try:
            import browser_cookie3

            # Try different browsers
            browsers = [
                ("Chrome", browser_cookie3.chrome),
                ("Firefox", browser_cookie3.firefox),
                ("Edge", browser_cookie3.edge),
                ("Safari", browser_cookie3.safari),
            ]

            for browser_name, browser_func in browsers:
                try:
                    logger.debug(f"Trying to extract token from {browser_name}...")
                    cookies = browser_func(domain_name=".tradingview.com")

                    # Look for various auth-related cookies in order of preference
                    auth_cookies = {}
                    for cookie in cookies:
                        auth_cookies[cookie.name] = cookie.value

                    # Priority order: authToken > auth_token
                    # NOTE: sessionid is NOT used - it's for browser only, doesn't work for API
                    if "authToken" in auth_cookies:
                        logger.info(f"Found authToken in {browser_name} cookies")
                        return auth_cookies["authToken"]
                    elif "auth_token" in auth_cookies:
                        logger.info(f"Found auth_token in {browser_name} cookies")
                        return auth_cookies["auth_token"]

                except Exception as e:
                    logger.debug(f"Could not access {browser_name} cookies: {e}")
                    continue

            logger.debug("No auth-related cookies found in browser")
            return None

        except ImportError:
            logger.debug(
                "browser_cookie3 not installed. Install with: "
                "pip install browser-cookie3"
            )
            return None
        except Exception as e:
            logger.debug(f"Error extracting token from browser: {e}")
            return None

    def __auth(self, username: str, password: str) -> str | None:
        """Authenticate with TradingView.

        Args:
            username: TradingView username
            password: TradingView password

        Returns:
            Authentication token or None on failure
        """
        try:
            response = requests.post(
                self.__sign_in_url,
                data={"username": username, "password": password, "remember": "on"},
                headers=self.__signin_headers,
                timeout=10,
            )
            response.raise_for_status()

            data = response.json()

            # Check for CAPTCHA requirement
            if "error" in data and "captcha" in str(data.get("error", "")).lower():
                logger.warning("CAPTCHA required for login")
                return self._handle_captcha_login(username)

            if "user" not in data or "auth_token" not in data["user"]:
                logger.error("Invalid login response format: %s", data)
                # Try browser-based fallback
                return self._handle_captcha_login(username)

            return data["user"]["auth_token"]

        except requests.RequestException as e:
            logger.error("Network error during authentication: %s", e)
            return None
        except (KeyError, ValueError) as e:
            logger.error("Authentication failed: %s", e)
            return None

    @contextmanager
    def _websocket_connection(self) -> Generator[WebSocket, None, None]:
        """Create and manage WebSocket connection lifecycle.

        Yields:
            Active WebSocket connection

        Example:
            with self._websocket_connection() as ws:
                ws.send(message)
        """
        ws = None
        try:
            with self._ws_lock:
                logger.debug("Creating WebSocket connection")
                ws = create_connection(
                    "wss://data.tradingview.com/socket.io/websocket",
                    header=self.__ws_headers,
                    timeout=self.__ws_timeout,
                )
            yield ws
        finally:
            if ws:
                try:
                    ws.close()
                except Exception as e:
                    logger.debug("Error closing WebSocket: %s", e)

    @staticmethod
    def __filter_raw_message(text: str) -> tuple[str, str] | None:
        """Filter and extract message components from raw WebSocket data.

        Args:
            text: Raw WebSocket message

        Returns:
            Tuple of (message_type, payload) or None on error
        """
        try:
            found = re.search('"m":"(.+?)",', text).group(1)
            found2 = re.search('"p":(.+?"}"])}', text).group(1)
            return found, found2
        except AttributeError:
            logger.error("Error parsing WebSocket message")
            return None

    @staticmethod
    def __generate_session() -> str:
        """Generate random session ID for quote session.

        Returns:
            Session ID string (format: qs_<random>)
        """
        random_string = "".join(random.choice(string.ascii_lowercase) for _ in range(12))
        return f"qs_{random_string}"

    @staticmethod
    def __generate_chart_session() -> str:
        """Generate random session ID for chart session.

        Returns:
            Chart session ID string (format: cs_<random>)
        """
        random_string = "".join(random.choice(string.ascii_lowercase) for _ in range(12))
        return f"cs_{random_string}"

    @staticmethod
    def __prepend_header(st: str) -> str:
        """Prepend TradingView protocol header to message.

        Args:
            st: Message string

        Returns:
            Message with protocol header
        """
        return f"~m~{len(st)}~m~{st}"

    @staticmethod
    def __construct_message(func: str, param_list: list) -> str:
        """Construct JSON message for WebSocket.

        Args:
            func: Function name
            param_list: List of parameters

        Returns:
            JSON-encoded message
        """
        return json.dumps({"m": func, "p": param_list}, separators=(",", ":"))

    def __create_message(self, func: str, param_list: list) -> str:
        """Create complete WebSocket message with header.

        Args:
            func: Function name
            param_list: List of parameters

        Returns:
            Complete message ready to send
        """
        return self.__prepend_header(self.__construct_message(func, param_list))

    def __send_message(self, ws: WebSocket, func: str, args: list) -> None:
        """Send message through WebSocket.

        Args:
            ws: WebSocket connection
            func: Function name
            args: Message arguments
        """
        message = self.__create_message(func, args)
        if self.ws_debug:
            print(f"Sending: {message}")
        ws.send(message)

    @staticmethod
    def __parse_data(raw_data: str, is_return_dataframe: bool) -> list[list]:
        """Parse raw WebSocket data into list of OHLCV rows.

        Args:
            raw_data: Raw WebSocket response data
            is_return_dataframe: Whether to format timestamp for DataFrame

        Returns:
            List of [timestamp, open, high, low, close, volume] rows

        Raises:
            AttributeError: If raw_data format is invalid
        """
        out = re.search('"s":\\[(.+?)\\}\\]', raw_data).group(1)
        x = out.split(',{"')
        data = []
        volume_data = True

        for xi in x:
            xi = re.split("\\[|:|,|\\]", xi)
            # Convert timestamp based on output format
            ts = (
                datetime.datetime.fromtimestamp(float(xi[4]), tz=datetime.timezone.utc)
                if is_return_dataframe
                else int(xi[4].split('.')[0])
            )

            row = [ts]
            for i in range(5, 10):
                # Skip converting volume data if it doesn't exist
                if not volume_data and i == 9:
                    row.append(0.0)
                    continue
                try:
                    row.append(float(xi[i]))
                except (ValueError, IndexError):
                    volume_data = False
                    row.append(0.0)
                    logger.debug("No volume data available")

            data.append(row)

        return data

    @staticmethod
    def __create_df(parsed_data: list[list], symbol: str) -> pd.DataFrame | None:
        """Create pandas DataFrame from parsed OHLCV data.

        Args:
            parsed_data: List of [timestamp, open, high, low, close, volume] rows
            symbol: Symbol name for the data

        Returns:
            DataFrame with OHLCV data or None on error
        """
        try:
            df = pd.DataFrame(
                parsed_data,
                columns=["datetime", "open", "high", "low", "close", "volume"]
            ).set_index("datetime")
            df.insert(0, "symbol", value=symbol)
            return df

        except (AttributeError, IndexError) as e:
            logger.error("Failed to create DataFrame - check exchange and symbol: %s", e)
            return None

    @staticmethod
    def __format_symbol(symbol: str, exchange: str, contract: int | None = None) -> str:
        """Format symbol string for TradingView.

        Args:
            symbol: Symbol name
            exchange: Exchange name
            contract: Futures contract number (None for spot)

        Returns:
            Formatted symbol string

        Raises:
            ValueError: If contract type is invalid
        """
        match (symbol, contract):
            case (s, _) if ":" in s:
                return s
            case (s, None):
                return f"{exchange}:{s}"
            case (s, c) if isinstance(c, int):
                return f"{exchange}:{s}{c}!"
            case _:
                raise ValueError("Invalid contract - must be int or None")

    def get_hist(
        self,
        symbol: str,
        exchange: str = "NSE",
        interval: Interval = Interval.in_daily,
        n_bars: int = 10,
        fut_contract: int | None = None,
        extended_session: bool = False,
    ) -> pd.DataFrame | None:
        """Get historical market data from TradingView.

        Args:
            symbol: Symbol name (e.g., 'NIFTY', 'AAPL')
            exchange: Exchange name (e.g., 'NSE', 'NASDAQ')
            interval: Time interval for bars
            n_bars: Number of bars to fetch
            fut_contract: Futures contract number (None for spot, 1 for front month)
            extended_session: Include extended trading hours

        Returns:
            DataFrame with columns: symbol, open, high, low, close, volume
            Returns None on error

        Raises:

        Example:
            >>> tv = TvDatafeed(username='user', password='pass')
            >>> data = tv.get_hist('AAPL', 'NASDAQ', Interval.in_1_hour, n_bars=100)
        """
        symbol = self.__format_symbol(
            symbol=symbol, exchange=exchange, contract=fut_contract
        )
        interval_value = interval.value

        # Generate fresh sessions for this request
        session = self.__generate_session()
        chart_session = self.__generate_chart_session()

        try:
            with self._websocket_connection() as ws:
                # Set up authentication and sessions
                auth_token = self.token if self.token else "unauthorized_user_token"
                self.__send_message(ws, "set_auth_token", [auth_token])
                self.__send_message(ws, "chart_create_session", [chart_session, ""])
                self.__send_message(ws, "quote_create_session", [session])

                # Configure quote fields
                self.__send_message(
                    ws,
                    "quote_set_fields",
                    [
                        session,
                        "ch", "chp", "current_session", "description",
                        "local_description", "language", "exchange", "fractional",
                        "is_tradable", "lp", "lp_time", "minmov", "minmove2",
                        "original_name", "pricescale", "pro_name", "short_name",
                        "type", "update_mode", "volume", "currency_code", "rchp", "rtc",
                    ],
                )

                # Add symbol and request data
                self.__send_message(
                    ws,
                    "quote_add_symbols",
                    [session, symbol, {"flags": ["force_permission"]}]
                )
                self.__send_message(ws, "quote_fast_symbols", [session, symbol])

                # Configure chart session
                session_type = "regular" if not extended_session else "extended"
                symbol_config = f'={{"symbol":"{symbol}","adjustment":"splits","session":"{session_type}"}}'

                self.__send_message(
                    ws,
                    "resolve_symbol",
                    [chart_session, "symbol_1", symbol_config],
                )
                self.__send_message(
                    ws,
                    "create_series",
                    [chart_session, "s1", "s1", "symbol_1", interval_value, n_bars],
                )
                self.__send_message(ws, "switch_timezone", [chart_session, "exchange"])

                # Collect response data
                raw_data = ""
                logger.debug("Fetching data for %s...", symbol)

                while True:
                    try:
                        result = ws.recv()
                        raw_data += result + "\n"

                        if "series_completed" in result:
                            break

                    except Exception as e:
                        logger.error("WebSocket receive error for %s: %s", symbol, e)
                        if "series_completed" not in raw_data:
                            return None
                        break

                # Check if we received valid data
                if not raw_data or "series_completed" not in raw_data:
                    logger.error("No valid data received for %s", symbol)
                    return None

                # Parse and create DataFrame
                parsed_data = self.__parse_data(raw_data, is_return_dataframe=True)
                return self.__create_df(parsed_data, symbol)

        except Exception as e:
            logger.error("Failed to get historical data for %s: %s", symbol, e)
            return None

    async def __fetch_symbol_data(
        self,
        symbol: str,
        exchange: str,
        interval: Interval,
        n_bars: int,
        fut_contract: int | None,
        extended_session: bool,
        dataFrame: bool,
        semaphore: asyncio.Semaphore | None = None
    ) -> pd.DataFrame | list[list] | None:
        """Asynchronously fetch historical data for a single symbol.

        Args:
            symbol: Symbol name
            exchange: Exchange name
            interval: Time interval
            n_bars: Number of bars to fetch
            fut_contract: Futures contract number
            extended_session: Include extended trading hours
            dataFrame: Return as DataFrame (True) or list (False)
            semaphore: Optional semaphore for rate limiting

        Returns:
            DataFrame or list of OHLCV data, or None on error
        """
        # Use semaphore if provided for rate limiting
        if semaphore:
            async with semaphore:
                return await self._do_fetch_symbol_data(
                    symbol, exchange, interval, n_bars, fut_contract, extended_session, dataFrame
                )
        else:
            return await self._do_fetch_symbol_data(
                symbol, exchange, interval, n_bars, fut_contract, extended_session, dataFrame
            )

    async def _do_fetch_symbol_data(
        self,
        symbol: str,
        exchange: str,
        interval: Interval,
        n_bars: int,
        fut_contract: int | None,
        extended_session: bool,
        dataFrame: bool
    ) -> pd.DataFrame | list[list] | None:
        """Internal method to actually fetch symbol data."""
        try:
            symbol_formatted = self.__format_symbol(symbol, exchange, fut_contract)
            interval_value = interval.value

            # Generate fresh sessions for this request
            session = self.__generate_session()
            chart_session = self.__generate_chart_session()

            async with connect(
                "wss://data.tradingview.com/socket.io/websocket",
                origin="https://data.tradingview.com"
            ) as websocket:
                # Authentication and session setup
                auth_token = self.token if self.token else "unauthorized_user_token"
                await websocket.send(self.__create_message("set_auth_token", [auth_token]))
                await websocket.send(self.__create_message("chart_create_session", [chart_session, ""]))
                await websocket.send(self.__create_message("quote_create_session", [session]))

                # Configure quote fields
                await websocket.send(self.__create_message(
                    "quote_set_fields",
                    [
                        session,
                        "ch", "chp", "current_session", "description",
                        "local_description", "language", "exchange", "fractional",
                        "is_tradable", "lp", "lp_time", "minmov", "minmove2",
                        "original_name", "pricescale", "pro_name", "short_name",
                        "type", "update_mode", "volume", "currency_code", "rchp", "rtc",
                    ]
                ))

                # Add symbol and request data
                await websocket.send(self.__create_message(
                    "quote_add_symbols",
                    [session, symbol_formatted, {"flags": ["force_permission"]}]
                ))
                await websocket.send(self.__create_message("quote_fast_symbols", [session, symbol_formatted]))

                # Symbol resolution and series creation
                session_type = "regular" if not extended_session else "extended"
                symbol_config = f'={{"symbol":"{symbol_formatted}","adjustment":"splits","session":"{session_type}"}}'

                await websocket.send(self.__create_message(
                    "resolve_symbol",
                    [chart_session, "symbol_1", symbol_config],
                ))
                await websocket.send(self.__create_message(
                    "create_series",
                    [chart_session, "s1", "s1", "symbol_1", interval_value, n_bars],
                ))
                await websocket.send(self.__create_message("switch_timezone", [chart_session, "exchange"]))

                # Fetch and parse raw data asynchronously
                raw_data = ""
                logger.debug("Fetching async data for %s...", symbol)

                while True:
                    try:
                        result = await websocket.recv()
                        raw_data += result + "\n"
                    except Exception as e:
                        logger.error("WebSocket receive error for %s: %s", symbol, e)
                        break

                    if "series_completed" in result:
                        break

                # Check if we received valid data
                if not raw_data or "series_completed" not in raw_data:
                    logger.error("No valid data received for %s", symbol)
                    return None

                # Return formatted data based on dataFrame parameter
                parsed_data = self.__parse_data(raw_data, dataFrame)
                if dataFrame:
                    return self.__create_df(parsed_data, symbol_formatted)
                else:
                    return parsed_data

        except Exception as e:
            logger.error(f"Error fetching async data for {symbol}: {e}")
            return None

    async def get_hist_async(
        self,
        symbols: list[str],
        exchange: str = "NSE",
        interval: Interval = Interval.in_daily,
        n_bars: int = 10,
        dataFrame: bool = True,
        fut_contract: int | None = None,
        extended_session: bool = False,
        max_concurrent: int = 20,
    ) -> dict[str, pd.DataFrame | list[list] | None]:
        """Fetch historical data for multiple symbols asynchronously.

        This method fetches data for all symbols concurrently, which is much
        faster than fetching them sequentially. Rate limiting prevents overwhelming
        the server or hitting API limits.

        Args:
            symbols: List of symbol names
            exchange: Exchange name (applies to all symbols)
            interval: Time interval for bars
            n_bars: Number of bars to fetch
            dataFrame: Return as DataFrame (True) or list (False)
            fut_contract: Futures contract number
            extended_session: Include extended trading hours
            max_concurrent: Maximum number of concurrent connections (default: 20)
                           Recommended values:
                           - Conservative: 10-15 (safest, unlikely to hit limits)
                           - Moderate: 20-30 (balanced, good for most use cases)
                           - Aggressive: 40-50 (faster but higher risk of rate limiting)

        Returns:
            Dictionary mapping symbol names to their DataFrames or lists

        Example:
            >>> tv = TvDatafeed()
            >>> symbols = ['AAPL', 'GOOGL', 'MSFT']
            >>> # Default rate limiting (20 concurrent)
            >>> data = asyncio.run(tv.get_hist_async(symbols, 'NASDAQ', n_bars=100))
            >>>
            >>> # Conservative rate limiting (10 concurrent)
            >>> data = asyncio.run(tv.get_hist_async(symbols, 'NASDAQ', n_bars=100, max_concurrent=10))
            >>>
            >>> # Or use the synchronous wrapper:
            >>> data = tv.get_hist_multi(symbols, 'NASDAQ', n_bars=100, max_concurrent=15)
        """
        # Create semaphore for rate limiting
        semaphore = asyncio.Semaphore(max_concurrent)
        logger.info(f"Fetching {len(symbols)} symbols with max {max_concurrent} concurrent connections")

        tasks = [
            self.__fetch_symbol_data(
                symbol, exchange, interval, n_bars, fut_contract, extended_session, dataFrame, semaphore
            )
            for symbol in symbols
        ]
        results = await asyncio.gather(*tasks)

        return {sym: data for sym, data in zip(symbols, results)}

    def get_hist_multi(
        self,
        symbols: list[str] | str,
        exchange: str = "NSE",
        interval: Interval = Interval.in_daily,
        n_bars: int = 10,
        dataFrame: bool = True,
        fut_contract: int | None = None,
        extended_session: bool = False,
        max_concurrent: int = 20,
    ) -> pd.DataFrame | dict[str, pd.DataFrame | list[list] | None] | list[list] | None:
        """Get historical data for single or multiple symbols.

        This method supports both single symbol and multiple symbols. When
        multiple symbols are provided, data is fetched concurrently for better
        performance with rate limiting to prevent API throttling.

        Args:
            symbols: Single symbol name or list of symbol names
            exchange: Exchange name (applies to all symbols)
            interval: Time interval for bars
            n_bars: Number of bars to fetch
            dataFrame: Return as DataFrame (True) or list (False)
            fut_contract: Futures contract number
            extended_session: Include extended trading hours
            max_concurrent: Maximum concurrent connections (default: 20)
                           **Recommended Settings:**
                           - **Conservative (10-15)**: Safest, unlikely to hit limits
                           - **Moderate (20-30)**: Balanced, good for most use cases
                           - **Aggressive (40-50)**: Faster but higher risk

        Returns:
            - Single symbol: DataFrame or list
            - Multiple symbols: Dict mapping symbol names to DataFrames or lists

        Raises:

        Examples:
            >>> tv = TvDatafeed()
            >>> # Single symbol
            >>> data = tv.get_hist_multi('AAPL', 'NASDAQ', n_bars=100)
            >>>
            >>> # Multiple symbols with default rate limiting (20 concurrent)
            >>> symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN']
            >>> data = tv.get_hist_multi(symbols, 'NASDAQ', n_bars=100)
            >>> # Returns: {'AAPL': DataFrame, 'GOOGL': DataFrame, ...}
            >>>
            >>> # Conservative rate limiting for large batches
            >>> symbols = [f'SYM{i}' for i in range(100)]
            >>> data = tv.get_hist_multi(symbols, 'NASDAQ', n_bars=100, max_concurrent=15)
            >>>
            >>> # Return as lists instead of DataFrames
            >>> data = tv.get_hist_multi(symbols, 'NASDAQ', n_bars=100, dataFrame=False)
            >>> # Returns: {'AAPL': [[ts, o, h, l, c, v], ...], 'GOOGL': [...], ...}
        """
        # Single symbol: use async method (no semaphore needed)
        if isinstance(symbols, str):
            return asyncio.run(
                self.__fetch_symbol_data(
                    symbols, exchange, interval, n_bars, fut_contract, extended_session, dataFrame
                )
            )

        # Multiple symbols: use async gather with rate limiting
        return asyncio.run(
            self.get_hist_async(
                symbols, exchange, interval, n_bars, dataFrame, fut_contract, extended_session, max_concurrent
            )
        )

    def search_symbol(self, text: str, exchange: str = "") -> list[dict]:
        """Search for symbols on TradingView.

        Args:
            text: Search text
            exchange: Filter by exchange (optional)

        Returns:
            List of matching symbols with metadata

        Example:
            >>> tv = TvDatafeed()
            >>> results = tv.search_symbol('CRUDE', 'MCX')
        """
        url = self.__search_url.format(text, exchange)

        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()

            # Remove HTML tags from response
            clean_text = resp.text.replace("</em>", "").replace("<em>", "")
            return json.loads(clean_text)

        except requests.RequestException as e:
            logger.error("Symbol search failed: %s", e)
            return []
        except json.JSONDecodeError as e:
            logger.error("Failed to parse search results: %s", e)
            return []

    def get_token(self) -> str | None:
        """Get current authentication token.

        Returns:
            Authentication token or None if not authenticated
        """
        return self.token


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    tv = TvDatafeed()
    print(tv.get_hist("CRUDEOIL", "MCX", fut_contract=1))
    print(tv.get_hist("NIFTY", "NSE", fut_contract=1))
    print(
        tv.get_hist(
            "EICHERMOT",
            "NSE",
            interval=Interval.in_1_hour,
            n_bars=500,
            extended_session=False,
        )
    )
