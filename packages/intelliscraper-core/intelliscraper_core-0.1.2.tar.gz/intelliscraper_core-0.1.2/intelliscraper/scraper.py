import copy
import json
import logging
import random
from datetime import datetime, timedelta, timezone

from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

from intelliscraper.common.constants import (
    BROWSER_LAUNCH_OPTIONS,
    DEFAULT_BROWSER_FINGERPRINT,
    MAX_PAUSE_MS,
    MAX_SCROLL_WAIT_MS,
    MIN_PAUSE_MS,
    MIN_SCROLL_WAIT_MS,
)
from intelliscraper.common.models import (
    Proxy,
    RequestEvent,
    ScrapeRequest,
    ScrapeResponse,
    Session,
)
from intelliscraper.enums import BrowsingMode, ScrapStatus
from intelliscraper.proxy.base import ProxyProvider


class Scraper:
    """A web scraper that retrieves HTML content from a given URL."""

    def __init__(
        self,
        headless: bool = True,
        browser_launch_options: dict = BROWSER_LAUNCH_OPTIONS,
        proxy: Proxy | ProxyProvider | None = None,
        session_data: Session | None = None,
        browsing_mode: BrowsingMode | None = None,
    ):
        """Initialize the scraper with browser and session configuration.

        Args:
            headless: Run browser without UI. Defaults to True.
            browser_launch_options: Custom Chromium launch options. If None, uses
                default options. Defaults to None.
            proxy: Proxy configuration or ProxyProvider instance. Defaults to None.
            session_data: Pre-authenticated session with cookies, localStorage,
                sessionStorage, and browser fingerprint. Defaults to None.
            browsing_mode: Behavior mode - FAST (no human simulation) or HUMAN_LIKE
                (scrolling, delays). Auto-determined if None. Defaults to None.

        Note:
            Browsing mode is automatically set based on configuration:
            - With proxy: FAST mode (optimized for speed)
            - With session_data: HUMAN_LIKE mode (stealth)
            - Neither: HUMAN_LIKE mode (default)
        """

        logging.debug("Initializing Scraper")
        self.playwright = sync_playwright().start()
        browser_launch_options = copy.deepcopy(browser_launch_options)
        browser_launch_options.update({"headless": headless})
        self.browser_launch_options = browser_launch_options
        if proxy is not None and isinstance(proxy, ProxyProvider):
            logging.debug(
                f"Converting ProxyProvider to Proxy: {proxy.__class__.__name__}"
            )
            self.proxy = proxy.get_proxy()
        else:
            self.proxy = proxy
        self.session_data = session_data
        self._closed = False

        if self.proxy:
            logging.info(f"Using proxy: {self.proxy.server}")

        if session_data:
            logging.info("Using session data for authenticated scraping")

        logging.debug(f"Launching browser with options: {self.browser_launch_options}")
        self.browser = self.playwright.chromium.launch(**self.browser_launch_options)
        logging.debug(f"Browser launched successfully")

        browser_fingerprint = (
            self.session_data.fingerprint
            if self.session_data
            else DEFAULT_BROWSER_FINGERPRINT
        )
        logging.debug(
            "Creating browser context with fingerprint and proxy if available"
        )
        self._create_browser_context(
            browser_fingerprint=browser_fingerprint, proxy=self.proxy
        )

        # Determine browsing mode based on priority
        # Priority logic:
        # - If a proxy is provided, it takes priority (use proxy).
        # - If no proxy but session data is provided, load session cookies and metadata into the context.
        # - If neither proxy nor session data is provided, start a fresh context.
        self.pages: list[Page] = []
        if browsing_mode:
            self.browsing_mode = browsing_mode
        elif self.proxy:
            self.browsing_mode = BrowsingMode.FAST
        elif self.session_data:
            self.browsing_mode = BrowsingMode.HUMAN_LIKE
        else:
            self.browsing_mode = BrowsingMode.HUMAN_LIKE

        logging.info(f"Scraper initialized with browsing mode: {self.browsing_mode}")

        self._add_cookies()
        self._apply_anti_detection_scripts()

    def __enter__(self):
        """Context manager entry point."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit point - clean up resources."""
        self.close()
        return False

    def close(self):
        """Explicitly close browser and cleanup all resources."""
        if self._closed:
            return

        self._closed = True
        logging.debug("Starting cleanup...")

        try:
            # Close all pages
            for page in self.pages:
                try:
                    page.close()
                except Exception as e:
                    logging.debug(f"Failed to close page: {e}")
                    pass

            # Close context
            if hasattr(self, "context"):
                self.context.close()

            # Close browser
            if hasattr(self, "browser"):
                self.browser.close()

            # Stop playwright
            if hasattr(self, "playwright"):
                self.playwright.stop()

            logging.debug("Cleanup complete")

        except Exception as e:
            logging.error(f"Error during cleanup: {e}")

    def __del__(self):
        """Destructor for fallback cleanup.

        Note:
            This is a safety net. Prefer using context manager or explicit close().
        """
        try:
            self.close()
        except Exception:
            pass

    def _create_browser_context(
        self, browser_fingerprint: dict | None, proxy: Proxy | None
    ):
        """Create browser context with fingerprint and proxy configuration.

        Args:
            browser_fingerprint: Browser fingerprint for anti-detection.
            proxy: Proxy configuration.
        """
        logging.debug("Creating browser context")
        if browser_fingerprint is None:
            browser_fingerprint = DEFAULT_BROWSER_FINGERPRINT

        if proxy:
            proxy = proxy.model_dump()

        screen = browser_fingerprint.get("screenResolution", {})

        self.context = self.browser.new_context(
            # Screen & Viewport (from fingerprint)
            viewport={
                "width": screen.get("width", 1920),
                "height": screen.get("height", 1080),
            },
            screen={
                "width": screen.get("width", 1920),
                "height": screen.get("height", 1080),
            },
            proxy=proxy,
            geolocation={"latitude": 60, "longitude": 90},
            # Browser Identity (from fingerprint)
            user_agent=browser_fingerprint.get(
                "userAgent", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
            ),
            # Locale & Timezone (from fingerprint)
            locale=browser_fingerprint.get("language", "en-US"),
            timezone_id=browser_fingerprint.get("timezone", "Asia/Calcutta"),
            # Device Settings
            device_scale_factor=1,
            is_mobile=False,
            has_touch=False,
            color_scheme="light",
            # Security
            ignore_https_errors=True,
            # Extra Headers
            extra_http_headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": f"{browser_fingerprint.get("language", "en-US")},en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            },
        )
        logging.debug("Browser context created successfully")

    def _add_cookies(self):
        """Add cookies from session data to the browser context."""
        if self.session_data and self.session_data.cookies:
            logging.debug(f"Adding {len(self.session_data.cookies)} cookies")
            self.context.add_cookies(self.session_data.cookies)
            logging.debug("Cookies added successfully")

    def _apply_anti_detection_scripts(self):
        """Apply JavaScript scripts to mask automation and avoid bot detection."""
        logging.debug("Applying anti-detection scripts")
        browser_fingerprint = (
            self.session_data.fingerprint
            if self.session_data
            else DEFAULT_BROWSER_FINGERPRINT
        )
        self.context.add_init_script(
            f"""
            // Remove webdriver flag (MOST IMPORTANT!)
            Object.defineProperty(navigator, 'webdriver', {{
                get: () => undefined
            }});
            
            // Add chrome object
            window.chrome = {{
                runtime: {{}}
            }};
            
            // Override permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({{ state: Notification.permission }}) :
                    originalQuery(parameters)
            );
            
            // Spoof plugins
            Object.defineProperty(navigator, 'plugins', {{
                get: () => [
                    {{
                        0: {{type: "application/x-google-chrome-pdf", suffixes: "pdf"}},
                        description: "Portable Document Format",
                        filename: "internal-pdf-viewer",
                        length: 1,
                        name: "Chrome PDF Plugin"
                    }},
                    {{
                        0: {{type: "application/pdf", suffixes: "pdf"}},
                        description: "Portable Document Format",
                        filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
                        length: 1,
                        name: "Chrome PDF Viewer"
                    }}
                ]
            }});
            
            // Languages
            Object.defineProperty(navigator, 'languages', {{
                get: () => {json.dumps(browser_fingerprint.get('languages', ['en-US']))}
            }});
            
            // Hardware (from fingerprint)
            Object.defineProperty(navigator, 'hardwareConcurrency', {{
                get: () => {browser_fingerprint.get('hardwareConcurrency', 8)}
            }});
            
            Object.defineProperty(navigator, 'deviceMemory', {{
                get: () => {browser_fingerprint.get('deviceMemory', 8)}
            }});
            
            Object.defineProperty(navigator, 'platform', {{
                get: () => "{browser_fingerprint.get('platform', 'Linux x86_64')}"
            }});
            
            // Screen properties
            Object.defineProperty(screen, 'colorDepth', {{
                get: () => {browser_fingerprint.get("screenResolution", {}).get('colorDepth', 24)}
            }});
            
            Object.defineProperty(screen, 'pixelDepth', {{
                get: () => {browser_fingerprint.get("screenResolution", {}).get('colorDepth', 24)}
            }});
            
            // WebGL (from fingerprint)
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {{
                if (parameter === 37445) {{
                    return "{browser_fingerprint.get('webglVendor', 'Google Inc. (Intel)')}";
                }}
                if (parameter === 37446) {{
                    return "{browser_fingerprint.get('webglRenderer', 'ANGLE (Intel)')}";
                }}
                return getParameter.call(this, parameter);
            }};
        """
        )
        logging.debug("Anti-detection scripts applied")

    def _get_page(self) -> Page:
        """Get or create a page instance with session storage applied.

        Returns:
            Page: A Playwright page instance.
        """
        if not self.pages:
            logging.debug("Creating new page")
            page = self.context.new_page()
            # Required for BOTH storage types
            if self.session_data and (
                self.session_data.localStorage or self.session_data.sessionStorage
            ):
                logging.debug("Applying session | local storage")
                page.goto(self.session_data.base_url)
                if self.session_data.localStorage:
                    page.evaluate(
                        """
                    (items) => {
                        for (let key in items) {
                            try {
                                localStorage.setItem(key, items[key]);
                            } catch(e) {
                                console.error('Failed to set localStorage:', key, e);
                            }
                        }
                    }
                """,
                        self.session_data.localStorage,
                    )

                if self.session_data.sessionStorage:
                    page.evaluate(
                        """
                    (items) => {
                        for (let key in items) {
                            try {
                                sessionStorage.setItem(key, items[key]);
                            } catch(e) {
                                console.error('Failed to set sessionStorage:', key, e);
                            }
                        }
                    }
                """,
                        self.session_data.sessionStorage,
                    )
                logging.debug("Session storage applied successfully")
            self.pages.append(page)
            return page

        logging.debug("Reusing existing page")
        return self.pages[-1]

    def _validate_url(self, url: str):
        """Validate that the URL has a proper format."""
        if not url or not url.startswith(("http://", "https://")):
            raise ValueError(f"Invalid URL: {url}")

    def _record_event(self, status: ScrapStatus, sent_at: float):
        """Record a scraping event to the session statistics.

        If session data is configured, this method adds a new request event to the
        session's time-series statistics log. The event includes the timestamp and
        the outcome status of the scraping attempt.

        Use Cases:
            The recorded event data is valuable for:

            - **Rate Limiting Analysis**: Identify if too many requests are causing failures.
            By analyzing the time-series data, you can detect patterns like:
            - Sudden spike in failures after rapid requests
            - Consistent failures during specific time windows
            - Success rate degradation over time

        Note:
            If no session_data is configured for this scraper instance, this method
            does nothing (no-op). Events are only recorded when session tracking is enabled.

        Thread-safety:
            This method is thread-safe when session_data.stats uses proper locking
            (which it does via the internal Lock in SessionStats).
        """
        if self.session_data:
            self.session_data.stats.add_request_event(
                request_event=RequestEvent(sent_at=sent_at, request_status=status)
            )

    def _apply_human_like_behavior(self, page: Page) -> None:
        """
        Apply human-like scrolling behavior to avoid bot detection.

        Performs a smooth scroll to a random position on the page with
        realistic timing delays.

        Args:
            page: Playwright Page instance to apply behavior to

        """
        try:
            # Get page height
            page_height = page.evaluate("document.body.scrollHeight")

            if page_height <= 0:
                return

            # Random scroll position (20% to 80% of page)
            scroll_pos = int(page_height * random.uniform(0.2, 0.8))

            page.evaluate(
                f"""
                window.scrollTo({{
                    top: {scroll_pos},
                    behavior: 'smooth'
                }});
            """
            )

            # Wait for scroll animation (INTEGER milliseconds)
            page.wait_for_timeout(
                random.randint(MIN_SCROLL_WAIT_MS, MAX_SCROLL_WAIT_MS)
            )

            # Additional pause (humans pause after scrolling)
            page.wait_for_timeout(random.randint(MIN_PAUSE_MS, MAX_PAUSE_MS))

        except Exception as e:
            logging.debug(f"Human-like behavior failed: {e}")

    def scrape(
        self,
        url: str,
        timeout: timedelta = timedelta(seconds=30),
        page: Page | None = None,
    ) -> ScrapeResponse:
        """Scrape content from a URL.

        Navigates to the URL, waits for content to load, and returns the page HTML.
        Applies human-like behavior (scrolling, delays) if browsing mode is HUMAN_LIKE.

        Args:
            url: Target URL to scrape.
            timeout: Maximum time to wait for page load. Defaults to 30 seconds.
            page: Optional Playwright Page instance to use. If None, creates or reuses
                internal page. Defaults to None. the page should be created
                from the scraper's context (e.g., scraper.context.new_page())

        Returns:
            ScrapeResponse: Response object containing:
                - status: SUCCESS, PARTIAL_SUCCESS, or FAILED
                - scrap_html_content: Page HTML (if successful or partial)
                - error: Exception details (if failed or partial)
                - scrape_request: Original request parameters

        Examples:
            >>> scraper = Scraper()
            >>> response = scraper.scrape("https://example.com")
            >>> if response.status == ScrapStatus.COMPLETED:
            ...     print(response.scrap_html_content)

            >>> response = scraper.scrape("https://slow-site.com", timeout=timedelta(minutes=2))


            With session data for authenticated scraping:
            >>> import json
            >>> with open("himalayas_session.json") as f:
            ...     session = Session(**json.load(f))
            >>> scraper = Scraper(session_data=session)
            >>> response = scraper.scrape("https://himalayas.app/jobs/python?experience=entry-level%2Cmid-level")

            Using an externally created page:
            >>> with Scraper() as scraper:
            ...     my_page = scraper.context.new_page()
            ...     # Perform custom actions on my_page if needed
            ...     response = scraper.scrape("https://example.com", page=my_page)

            Scraping multiple URLs sequentially:
            >>> urls = ["https://example1.com", "https://example2.com"]
            >>> with Scraper() as scraper:
            ...     for url in urls:
            ...         response = scraper.scrape(url)
            ...         if response.status == ScrapStatus.COMPLETED:
            ...             print(f"Scraped: {url}")


        Note:
            - Returns PARTIAL status if timeout occurs (with partial content)
            - Returns FAILED status if other errors occur
            - Applies scrolling and delays in HUMAN_LIKE mode
            - For advanced behavior (mouse movements, clicks), extend this class
        """
        # TODO: If the page is JavaScript-heavy and content loads dynamically
        # upon user actions (like scrolling), add the required functionality.
        sent_at = datetime.now(timezone.utc).timestamp()
        try:
            if self._closed:
                logging.error("Cannot scrape: Scraper is closed")
                raise RuntimeError(
                    "Scraper is closed. Create a new instance or use context manager."
                )
            if self.session_data and not url.startswith(self.session_data.base_url):
                logging.warning(
                    f"URL {url} does not match session base URL {self.session_data.base_url}. "
                    "Scraping may fail due to invalid session."
                )
            self._validate_url(url=url)

            logging.info(f"Scraping: {url}")
            scrape_request = ScrapeRequest(
                url=url,
                timeout=timeout,
                browser_launch_options=self.browser_launch_options,
                proxy=self.proxy,
                session_data=self.session_data,
                browsing_mode=self.browsing_mode,
            )
            page_to_use = page if isinstance(page, Page) else self._get_page()

            logging.debug(f"Navigating to: {url}")

            page_to_use.goto(
                url=url,
                wait_until="networkidle",
                timeout=timeout.total_seconds() * 1000,
            )
            logging.debug(f"Page loaded successfully :{url}")

            # Simple scroll to simulate human-like behavior (helps avoid bot detection)
            # Scrolling also helps trigger lazy-loaded content on pages that load data dynamically
            if self.browsing_mode == BrowsingMode.HUMAN_LIKE:
                self._apply_human_like_behavior(page_to_use)

            html_content = page_to_use.content()
            elapsed_time = datetime.now(timezone.utc).timestamp() - sent_at
            logging.info(
                f"Scraping finished: {url} in {elapsed_time:.2f}s with status={ScrapStatus.SUCCESS.value}"
            )
            self._record_event(sent_at=sent_at, status=ScrapStatus.SUCCESS)
            return ScrapeResponse(
                scrape_request=scrape_request,
                status=ScrapStatus.SUCCESS,
                elapsed_time=elapsed_time,
                scrap_html_content=html_content,
            )
        except PlaywrightTimeoutError as e:
            logging.warning(
                f"Timeout while loading URL: {url}. "
                f"Waited {timeout.total_seconds()} seconds. Returning partial content."
            )
            html_content = page_to_use.content()
            elapsed_time = datetime.now(timezone.utc).timestamp() - sent_at
            self._record_event(sent_at=sent_at, status=ScrapStatus.PARTIAL_SUCCESS)
            logging.info(
                f"Scraping finished: {url} in {elapsed_time:.2f}s with status={ScrapStatus.PARTIAL_SUCCESS.value}"
            )
            return ScrapeResponse(
                scrape_request=scrape_request,
                status=ScrapStatus.PARTIAL_SUCCESS,
                elapsed_time=elapsed_time,
                scrap_html_content=html_content,
                error_msg=str(e),
            )
        except Exception as e:
            logging.error(f"Failed to scrape URL: {url}. Error: {e}", exc_info=True)
            self._record_event(sent_at=sent_at, status=ScrapStatus.FAILED)
            return ScrapeResponse(
                scrape_request=scrape_request,
                status=ScrapStatus.FAILED,
                error_msg=str(e),
            )
