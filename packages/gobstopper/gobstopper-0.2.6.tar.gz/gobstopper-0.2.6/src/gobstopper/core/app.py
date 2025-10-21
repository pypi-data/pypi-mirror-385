"""
Main Gobstopper application class
"""

import asyncio
import re
import uuid
import traceback
import inspect
import os
import msgspec
from urllib.parse import unquote
from pathlib import Path
from types import SimpleNamespace
from typing import Callable, Dict, List, Optional, Tuple, Any, Awaitable

# Helper to map Python-style <type:name> or <name> to Rust router format
# Old router used :name, new router uses <type:name> or <name>
# For backward compatibility, we keep the pattern but now just pass through
_PARAM_TO_NAME = re.compile(r'<(?:[^:>]+:)?([^>]+)>')

from ..log import log
from ..http.request import Request
from ..http.response import Response, JSONResponse, FileResponse, StreamResponse
from ..http.routing import RouteHandler
from ..websocket.connection import WebSocket
from ..tasks.queue import TaskQueue, TaskPriority
from ..middleware.static import StaticFileMiddleware

# Try to import Rust template engine
try:
    from ..templates import RustTemplateEngineWrapper, RUST_AVAILABLE
except ImportError:
    RustTemplateEngineWrapper = None
    RUST_AVAILABLE = False

# Try to import Jinja2 template engine (optional, for error pages fallback)
try:
    from ..templates.engine import TemplateEngine
    JINJA2_TEMPLATE_ENGINE_AVAILABLE = True
except ImportError:
    TemplateEngine = None
    JINJA2_TEMPLATE_ENGINE_AVAILABLE = False

# Type aliases (compatible with Python 3.10+)
Handler = Callable[..., Any]
ErrorHandler = Callable[[Request, Exception], Response]
RouteResult = tuple[Optional[RouteHandler], dict[str, str]]
Middleware = Callable[[Request, Callable[[Request], Awaitable[Any]]], Awaitable[Response]]
MiddlewareTuple = tuple[Middleware, int]

try:
    from gobstopper._core import Router
    RUST_ROUTER_AVAILABLE = True
except ImportError:
    RUST_ROUTER_AVAILABLE = False

try:
    from granian.rsgi import Scope, HTTPProtocol, WebsocketProtocol
except ImportError:
    from typing import TypedDict
    # Fallback types for development without Granian
    class Scope(TypedDict, total=True):
        proto: str
        method: str
        path: str
        query_string: str
        headers: Any

    class HTTPProtocol:
        async def __call__(self): pass
        def response_str(self, status, headers, body): pass
        def response_bytes(self, status, headers, body): pass
        def response_file(self, status, headers, file): pass
        def response_stream(self, status, headers): pass
    
    class WebsocketProtocol:
        async def accept(self): pass


class Gobstopper:
    def _precompute_middleware_chain(self, route: RouteHandler):
        """Pre-compute and cache the complete middleware chain for a route.

        This optimization moves middleware chain computation from request-time
        to route registration time, eliminating 10-15% per-request overhead.
        Now builds the actual compiled chain function, not just the stack.
        """
        if route._cached_middleware_stack is not None:
            return route._cached_middleware_stack

        collected: list[tuple[Callable, int, int, int]] = []  # (mw, prio, depth, idx)
        idx_counter = 0

        # App-level (depth 0)
        for mw, prio in self.middleware:
            collected.append((mw, prio, 0, idx_counter))
            idx_counter += 1

        # Blueprint chain (depth increases)
        depth = 1
        for bp in getattr(route, 'blueprint_chain', []) or []:
            for mw, prio in getattr(bp, 'middleware', []) or []:
                collected.append((mw, prio, depth, idx_counter))
                idx_counter += 1
            depth += 1

        # Sort with deterministic tiebreakers: priority desc, depth asc, index asc
        collected.sort(key=lambda t: (-t[1], t[2], t[3]))

        # Dedupe by identity, preserve first occurrence
        seen_ids: set[int] = set()
        ordered_stack: list[MiddlewareTuple] = []
        for mw, prio, _, _ in collected:
            if id(mw) not in seen_ids:
                seen_ids.add(id(mw))
                ordered_stack.append((mw, prio))

        # Route middleware goes innermost (preserve their own priority order)
        route_mw = getattr(route, 'middleware', []) or []
        stack: list[MiddlewareTuple] = ordered_stack + route_mw

        # Cache on route
        route._cached_middleware_stack = stack
        return stack

    def _check_conflicts(self, new_handler: RouteHandler):
        """Collect conflicts between new route and existing ones for diagnostics.

        Analyzes a new route handler against all previously registered routes to detect
        potential conflicts such as duplicate static routes, dynamic routes that shadow
        static routes, or overlapping patterns. Conflicts are collected for logging
        but do not prevent route registration.

        Args:
            new_handler: The RouteHandler being registered to check for conflicts.

        Note:
            This is a best-effort analysis. Exceptions during conflict detection
            are silently caught to avoid breaking application startup.
            Detected conflicts are stored in self._conflicts for logging.
        """
        try:
            new_is_ws = bool(new_handler.is_websocket)
            new_static = '<' not in new_handler.pattern and '>' not in new_handler.pattern and ':' not in new_handler.pattern
            new_regex = new_handler.regex
            for existing in self._all_routes:
                if bool(existing.is_websocket) != new_is_ws:
                    continue
                # Method intersection (ignore if none)
                if not new_is_ws:
                    if not set(m.upper() for m in new_handler.methods) & set(m.upper() for m in existing.methods):
                        continue
                exist_static = '<' not in existing.pattern and '>' not in existing.pattern and ':' not in existing.pattern
                # Duplicate static route
                if new_static and exist_static and existing.pattern == new_handler.pattern:
                    self._conflicts.append({
                        'existing': f"{existing.methods or ['WS']} {existing.pattern}",
                        'new': f"{new_handler.methods or ['WS']} {new_handler.pattern}",
                        'reason': 'duplicate static route for same path/method'
                    })
                # Dynamic shadows static
                if new_regex and exist_static and new_regex.match(existing.pattern):
                    self._conflicts.append({
                        'existing': f"{existing.methods or ['WS']} {existing.pattern}",
                        'new': f"{new_handler.methods or ['WS']} {new_handler.pattern}",
                        'reason': 'dynamic route may shadow a more specific static route'
                    })
                # Static shadows dynamic (reverse)
                if existing.regex and new_static and existing.regex.match(new_handler.pattern):
                    self._conflicts.append({
                        'existing': f"{existing.methods or ['WS']} {existing.pattern}",
                        'new': f"{new_handler.methods or ['WS']} {new_handler.pattern}",
                        'reason': 'dynamic route may shadow a more specific static route'
                    })
        except Exception:
            # Best-effort conflict collection; do not break app
            pass
    """High-performance async web framework for RSGI protocol.
    
    Gobstopper is a hybrid Python/Rust web framework built specifically for Granian's 
    RSGI interface. It combines Flask-like developer experience with performance
    optimizations through optional Rust components.
    
    The framework automatically detects and uses Rust components when available,
    falling back gracefully to Python implementations. This hybrid architecture
    provides optimal performance while maintaining compatibility.
    
    Args:
        name: Application name, typically ``__name__`` of the calling module.
            Used for logging and debugging purposes.
        
    Attributes:
        name (str): Application identifier
        logger: Structured logger with request context and tracing support
        routes (List[RouteHandler]): Registered HTTP and WebSocket route handlers
        error_handlers (Dict[int, ErrorHandler]): HTTP status code to handler mapping
        middleware (List[MiddlewareTuple]): Middleware functions with priority ordering
        template_engine: Jinja2 or Rust template engine instance (None until initialized)
        task_queue (TaskQueue): Background task queue with DuckDB persistence
        rust_router_available (bool): Whether Rust routing components are available
        
    Examples:
        Basic application setup:
        
        >>> from gobstopper import Gobstopper, Request
        >>> app = Gobstopper(__name__)
        >>> 
        >>> @app.get("/")
        >>> async def hello(request: Request):
        ...     return {"message": "Hello World"}
        
        With template engine:
        
        >>> app = Gobstopper(__name__)
        >>> app.init_templates("templates")
        >>> 
        >>> @app.get("/page")
        >>> async def page(request: Request):
        ...     return await app.render_template("page.html", title="Gobstopper")
        
        Background task setup:
        
        >>> @app.task("send_email", category="notifications") 
        >>> async def send_email(to: str, subject: str):
        ...     return {"status": "sent"}
        
    Note:
        Gobstopper uses RSGI protocol (not ASGI) and requires Granian server.
        Run with: ``granian --interface rsgi app:app``
        
    See Also:
        :meth:`init_templates`: Initialize template engine
        :meth:`add_middleware`: Add middleware functions  
        :meth:`add_background_task`: Queue background tasks
    """
    
    def __init__(self, name: str = __name__, debug: bool = False, slash_policy: str = 'strict'):
        self.name = name
        self.debug = debug
        self.logger = log
        self.routes: list[RouteHandler] = []
        self._all_routes: list[RouteHandler] = []
        self.error_handlers: dict[int, ErrorHandler] = {}
        self.before_request_handlers: list[Handler] = []
        self.after_request_handlers: list[Handler] = []
        self.middleware: list[MiddlewareTuple] = []
        self.template_context_processors: list[Callable[[], dict]] = []
        # Registered blueprints
        self.blueprints: list[Any] = []
        
        # Routing policy
        self.slash_policy: str = slash_policy  # 'strict' | 'add_slash' | 'remove_slash'
        self._conflicts: list[dict[str, str]] = []
        
        # Initialize components
        self.template_engine = None
        self.task_queue = TaskQueue()

        # Internal template engine for themed error pages
        # Prefer Rust templates, fallback to Jinja2 if available, otherwise None
        _core_dir = Path(__file__).parent.resolve()
        _internal_templates_path = _core_dir.parent / "templates"
        self._error_template_engine = None

        if RUST_AVAILABLE:
            try:
                self._error_template_engine = RustTemplateEngineWrapper(
                    str(_internal_templates_path),
                    fallback_to_jinja=False
                )
            except Exception:
                pass

        if self._error_template_engine is None and JINJA2_TEMPLATE_ENGINE_AVAILABLE:
            try:
                self._error_template_engine = TemplateEngine(str(_internal_templates_path))
            except Exception:
                pass

        # Track startup state
        self._startup_complete = False
        self._startup_lock = asyncio.Lock()

        # Graceful shutdown state
        self._accepting_requests = True
        self._inflight_requests = 0
        self._inflight_zero = asyncio.Event()
        self._inflight_zero.set()
        self._shutdown_hooks: list[Callable[[], Any] | Callable[[], Awaitable[Any]]] = []

        # Routing
        self.rust_router_available = RUST_ROUTER_AVAILABLE
        if self.rust_router_available:
            self.http_router = Router()
            self.websocket_router = Router()
            self.logger.info("🚀 Found Rust extensions, using high-performance router.")
        else:
            self.http_router = None
            self.websocket_router = None
            self.logger.info("⚠️ Rust extensions not found, using Python-based router.")
        
        # Mounts (sub-apps)
        self.mounts: list[tuple[str, Any]] = []
        
        # Default error handlers
        self.error_handlers[404] = self._default_404_handler
        self.error_handlers[500] = self._default_500_handler

        # Log any collected routing conflicts at startup
        @self.on_startup
        def _log_conflicts():
            if self._conflicts:
                self.logger.warning("⚠️ Routing conflicts detected:")
                for c in self._conflicts:
                    self.logger.warning(f" - {c['reason']}: existing={c['existing']} new={c['new']}")
    
    def init_templates(self, template_folder: str = "templates", use_rust: bool = None, **kwargs):
        """Initialize template engine with Jinja2 or Rust backend.
        
        Configures the template rendering system with either the Python Jinja2 
        engine or the high-performance Rust template engine. The Rust engine
        provides significant performance improvements and supports streaming
        template rendering for large datasets.
        
        Args:
            template_folder: Directory path containing template files.
                Must be relative to application root or absolute path.
            use_rust: Template engine selection:
                - ``None``: Auto-detect (uses Rust if available)
                - ``True``: Force Rust engine (raises ImportError if unavailable)  
                - ``False``: Force Python Jinja2 engine
            **kwargs: Additional template engine options:
                - auto_reload (bool): Watch templates for changes (default: True)
                - cache_size (int): Template cache size (default: 400)
                - enable_streaming (bool): Enable streaming rendering (Rust only)
                - enable_hot_reload (bool): Hot reload templates (Rust only)
                
        Raises:
            ImportError: If Jinja2 is not installed or Rust engine requested but unavailable
            FileNotFoundError: If template_folder does not exist
            
        Examples:
            Auto-detection (recommended):
            
            >>> app.init_templates("templates")  # Uses Rust if available
            
            Force specific engine:
            
            >>> app.init_templates("templates", use_rust=True)   # Rust only
            >>> app.init_templates("templates", use_rust=False)  # Jinja2 only
            
            With custom options:
            
            >>> app.init_templates(
            ...     "templates",
            ...     auto_reload=False,     # Disable file watching
            ...     cache_size=1000,       # Larger cache
            ...     enable_streaming=True  # Rust streaming (if available)
            ... )
            
        Note:
            Must be called before using :meth:`render_template`.
            Rust engine provides 2-5x performance improvement over Jinja2.
            
        See Also:
            :meth:`render_template`: Render templates
            :meth:`context_processor`: Add global template context
        """
        
        # Determine which engine to use
        if use_rust is None:
            use_rust = RUST_AVAILABLE  # Auto-detect
        elif use_rust and not RUST_AVAILABLE:
            self.logger.warning("Rust template engine requested but not available, falling back to Jinja2")
            use_rust = False
        
        if use_rust and RUST_AVAILABLE:
            # Initialize Rust template engine
            self.template_engine = RustTemplateEngineWrapper(
                template_folder, 
                enable_streaming=kwargs.pop('enable_streaming', True),
                enable_hot_reload=kwargs.pop('enable_hot_reload', True),
                **kwargs
            )
            self.logger.info("🦀 Initialized Rust-powered template engine")
        else:
            # Initialize traditional Jinja2 engine
            # Remove Rust-specific kwargs that TemplateEngine doesn't accept
            kwargs.pop('enable_streaming', None)
            kwargs.pop('enable_hot_reload', None)
            self.template_engine = TemplateEngine(template_folder, **kwargs)
            self.logger.info("📄 Initialized Jinja2 template engine")
    
    def add_middleware(self, middleware: Middleware, priority: int = 0):
        """Add middleware to the application with priority-based execution order.

        Registers middleware functions that intercept HTTP requests and responses.
        Middleware executes in priority order (highest first) and can modify requests,
        responses, or short-circuit the handler chain. This is the primary mechanism
        for cross-cutting concerns like authentication, logging, and request preprocessing.

        Args:
            middleware: Callable accepting (request, next_handler) and returning Response.
                Can be sync or async. Must call next_handler(request) to continue the chain
                or return a Response directly to short-circuit.
            priority: Execution priority (default: 0). Higher values execute first.
                Use negative priorities for post-processing middleware.

        Examples:
            Basic middleware:

            >>> async def auth_middleware(request, next_handler):
            ...     if not request.headers.get('authorization'):
            ...         return Response("Unauthorized", status=401)
            ...     return await next_handler(request)
            >>> app.add_middleware(auth_middleware, priority=100)

            Logging middleware:

            >>> async def log_middleware(request, next_handler):
            ...     start = time.time()
            ...     response = await next_handler(request)
            ...     duration = time.time() - start
            ...     app.logger.info(f"{request.method} {request.path} - {duration:.3f}s")
            ...     return response
            >>> app.add_middleware(log_middleware, priority=50)

        Note:
            Middleware execution order:
            1. Application-level (highest priority first)
            2. Blueprint-level (outer to inner, by priority)
            3. Route-level (as registered)

            Middleware can be sync or async. The framework handles both transparently.

        See Also:
            :meth:`register_blueprint`: Blueprint middleware composition
            :class:`gobstopper.middleware.cors.CORSMiddleware`: Built-in CORS middleware
            :class:`gobstopper.middleware.security.SecurityMiddleware`: Security headers
        """
        self.middleware.append((middleware, priority))
        # Sort middleware by priority, descending
        self.middleware.sort(key=lambda item: item[1], reverse=True)

    def route(self, path: str, methods: list[str] = None, name: str = None):
        """Decorator to register HTTP routes with path parameters and method filtering.

        Primary routing decorator that maps URL patterns to handler functions. Supports
        static paths, path parameters with optional type conversion, and multiple HTTP
        methods. This is the foundation of Gobstopper's routing system.

        Args:
            path: URL pattern to match. Supports formats:
                - Static: ``"/users"``
                - Path parameters: ``"/users/<user_id>"`` or ``"/users/<int:user_id>"``
                - Multiple params: ``"/posts/<post_id>/comments/<comment_id>"``
                Supported parameter types: str (default), int, float, uuid, path, date
            methods: List of HTTP methods (default: ['GET']).
                Common values: GET, POST, PUT, DELETE, PATCH, OPTIONS
            name: Optional name for reverse routing with url_for(). Defaults to function name.

        Returns:
            Decorator function that registers the handler and returns it unchanged.

        Examples:
            Simple GET route:

            >>> @app.route("/")
            >>> async def home(request):
            ...     return {"message": "Welcome"}

            Multiple methods:

            >>> @app.route("/api/data", methods=['GET', 'POST'])
            >>> async def data_handler(request):
            ...     if request.method == 'GET':
            ...         return {"data": [...]}
            ...     return {"created": True}

            Path parameters with type conversion:

            >>> @app.route("/users/<int:user_id>")
            >>> async def get_user(request, user_id: int):
            ...     # user_id is automatically converted to int
            ...     return {"user_id": user_id}

            Complex patterns:

            >>> @app.route("/blog/<date:pub_date>/posts/<uuid:post_id>")
            >>> async def get_post(request, pub_date, post_id):
            ...     return {"date": pub_date, "id": post_id}

        Note:
            - Route conflicts are detected and logged but do not prevent registration
            - Routes are matched in registration order when using Python router
            - Rust router provides O(1) lookup for static routes
            - Path parameters are automatically decoded from URL encoding
            - Type conversion errors return 400 Bad Request automatically

        See Also:
            :meth:`get`: Convenience decorator for GET routes
            :meth:`post`: Convenience decorator for POST routes
            :meth:`put`: Convenience decorator for PUT routes
            :meth:`delete`: Convenience decorator for DELETE routes
            :meth:`websocket`: WebSocket route registration
        """
        if methods is None:
            methods = ['GET']
        
        def decorator(func: Handler) -> Handler:
            handler = RouteHandler(path, func, methods)
            for mw, prio in getattr(func, '__route_middleware__', []) or []:
                handler.use(mw, prio)
            # conflict detection
            self._check_conflicts(handler)
            # register
            if self.rust_router_available:
                # New Rust router accepts Python path syntax directly (no conversion needed)
                for method in methods:
                    # New signature: insert(path, method, value, name)
                    # Use provided name or fall back to function name
                    route_name = name if name else getattr(func, '__name__', None)
                    self.http_router.insert(path, method.upper(), handler, route_name)
            else:
                self.routes.append(handler)
            self._all_routes.append(handler)
            return func
        return decorator

    def get(self, path: str, name: str = None):
        """Convenience decorator for registering GET routes.

        Shorthand for ``@app.route(path, methods=['GET'])``. Use for read-only
        operations that retrieve data without side effects.

        Args:
            path: URL pattern to match (same format as :meth:`route`).

        Returns:
            Decorator function that registers the GET handler.

        Examples:
            >>> @app.get("/users")
            >>> async def list_users(request):
            ...     return {"users": [...]}

        See Also:
            :meth:`route`: Full routing documentation and path parameter syntax
        """
        return self.route(path, ['GET'], name)

    def post(self, path: str, name: str = None):
        """Convenience decorator for registering POST routes.

        Shorthand for ``@app.route(path, methods=['POST'])``. Use for creating
        resources or submitting data with side effects.

        Args:
            path: URL pattern to match (same format as :meth:`route`).

        Returns:
            Decorator function that registers the POST handler.

        Examples:
            >>> @app.post("/users")
            >>> async def create_user(request):
            ...     data = await request.json()
            ...     return {"id": new_user_id}, 201

        See Also:
            :meth:`route`: Full routing documentation
        """
        return self.route(path, ['POST'], name)

    def put(self, path: str, name: str = None):
        """Convenience decorator for registering PUT routes.

        Shorthand for ``@app.route(path, methods=['PUT'])``. Use for full resource
        updates (replacing entire resource).

        Args:
            path: URL pattern to match (same format as :meth:`route`).

        Returns:
            Decorator function that registers the PUT handler.

        Examples:
            >>> @app.put("/users/<int:user_id>")
            >>> async def update_user(request, user_id: int):
            ...     data = await request.json()
            ...     return {"updated": True}

        See Also:
            :meth:`route`: Full routing documentation
            :meth:`patch`: Partial resource updates
        """
        return self.route(path, ['PUT'], name)

    def delete(self, path: str, name: str = None):
        """Convenience decorator for registering DELETE routes.

        Shorthand for ``@app.route(path, methods=['DELETE'])``. Use for removing
        resources.

        Args:
            path: URL pattern to match (same format as :meth:`route`).

        Returns:
            Decorator function that registers the DELETE handler.

        Examples:
            >>> @app.delete("/users/<int:user_id>")
            >>> async def delete_user(request, user_id: int):
            ...     return {"deleted": True}, 204

        See Also:
            :meth:`route`: Full routing documentation
        """
        return self.route(path, ['DELETE'], name)

    def patch(self, path: str, name: str = None):
        """Convenience decorator for registering PATCH routes.

        Shorthand for ``@app.route(path, methods=['PATCH'])``. Use for partial
        resource updates (modifying specific fields).

        Args:
            path: URL pattern to match (same format as :meth:`route`).

        Returns:
            Decorator function that registers the PATCH handler.

        Examples:
            >>> @app.patch("/users/<int:user_id>")
            >>> async def patch_user(request, user_id: int):
            ...     data = await request.json()  # Only changed fields
            ...     return {"updated": True}

        See Also:
            :meth:`route`: Full routing documentation
            :meth:`put`: Full resource updates
        """
        return self.route(path, ['PATCH'], name)

    def options(self, path: str, name: str = None):
        """Convenience decorator for registering OPTIONS routes.

        Shorthand for ``@app.route(path, methods=['OPTIONS'])``. Use for CORS
        preflight requests or capability discovery.

        Args:
            path: URL pattern to match (same format as :meth:`route`).

        Returns:
            Decorator function that registers the OPTIONS handler.

        Examples:
            >>> @app.options("/api/data")
            >>> async def data_options(request):
            ...     return Response("", headers={"Allow": "GET, POST"})

        See Also:
            :meth:`route`: Full routing documentation
            :class:`gobstopper.middleware.cors.CORSMiddleware`: Automatic CORS handling
        """
        return self.route(path, ['OPTIONS'], name)
    
    def mount(self, path: str, app: 'Gobstopper'):
        """Mount a sub-application at the given path prefix.

        Registers a complete Gobstopper application to handle requests under a specific
        path prefix. This enables modular application architecture where different
        subsystems can be developed independently and composed together.

        Args:
            path: URL prefix for the sub-application. Must start with '/'.
                Trailing slashes are automatically normalized.
                Examples: "/api", "/admin", "/v1"
            app: Gobstopper application instance to mount. All routes in the mounted
                app will be accessible under the specified prefix.

        Returns:
            The mounted application instance (for chaining).

        Examples:
            Basic mounting:

            >>> # Create admin sub-application
            >>> admin_app = Gobstopper("admin")
            >>> @admin_app.get("/dashboard")
            >>> async def admin_dashboard(request):
            ...     return {"admin": True}
            >>>
            >>> # Mount under /admin prefix
            >>> app.mount("/admin", admin_app)
            >>> # Now accessible at: /admin/dashboard

            Multiple mounts:

            >>> api_v1 = Gobstopper("api_v1")
            >>> api_v2 = Gobstopper("api_v2")
            >>> app.mount("/api/v1", api_v1)
            >>> app.mount("/api/v2", api_v2)

            Mounting with separate configurations:

            >>> debug_app = Gobstopper("debug", debug=True)
            >>> @debug_app.get("/info")
            >>> async def debug_info(request):
            ...     return {"debug": True}
            >>> app.mount("/_debug", debug_app)

        Note:
            - Mounted apps maintain their own middleware, error handlers, and configuration
            - Path stripping is automatic: mounted app sees paths relative to mount point
            - Mount order matters: earlier mounts are checked first
            - Mount points should not overlap with main app routes

        See Also:
            :meth:`register_blueprint`: Alternative for simpler route grouping
        """
        if not path.startswith('/'):
            path = '/' + path
        if path.endswith('/'):
            path = path[:-1]
        self.mounts.append((path, app))
        return app
    
    def register_blueprint(self, blueprint, url_prefix: str | None = None):
        """Register a Blueprint on this app with an optional URL prefix.

        Blueprints provide a structured way to organize related routes, middleware,
        and handlers into reusable components. They support nesting, scoped middleware,
        and can have their own template and static file directories.

        Args:
            blueprint: Blueprint instance to register. The blueprint contains routes,
                middleware, hooks (before_request, after_request), and optional
                template/static folder configurations.
            url_prefix: Optional URL prefix for all blueprint routes (default: None).
                If provided, overrides blueprint's own url_prefix. Must start with '/'.
                Examples: "/api", "/admin", "/v1"

        Examples:
            Basic blueprint registration:

            >>> from gobstopper.core.blueprint import Blueprint
            >>> api = Blueprint("api", url_prefix="/api")
            >>>
            >>> @api.get("/users")
            >>> async def list_users(request):
            ...     return {"users": [...]}
            >>>
            >>> app.register_blueprint(api)
            >>> # Route available at: /api/users

            Override prefix at registration:

            >>> admin_bp = Blueprint("admin", url_prefix="/admin")
            >>> app.register_blueprint(admin_bp, url_prefix="/dashboard")
            >>> # Routes use /dashboard instead of /admin

            Nested blueprints:

            >>> api = Blueprint("api", url_prefix="/api")
            >>> v1 = Blueprint("v1", url_prefix="/v1")
            >>> v1.get("/users")(user_handler)
            >>> api.register_blueprint(v1)
            >>> app.register_blueprint(api)
            >>> # Route available at: /api/v1/users

            Blueprint with middleware:

            >>> auth_bp = Blueprint("auth")
            >>> auth_bp.add_middleware(auth_middleware, priority=100)
            >>> @auth_bp.get("/profile")
            >>> async def profile(request):
            ...     return {"user": request.user}
            >>> app.register_blueprint(auth_bp, url_prefix="/secure")

        Note:
            Middleware execution order with blueprints:
            1. Application-level middleware (highest priority first)
            2. Parent blueprint middleware (outer to inner)
            3. Child blueprint middleware
            4. Route-level middleware (innermost)

            Before/after request handlers from blueprints are attached to the app.
            Blueprint template folders are added to template search paths.
            Blueprint static folders automatically get static file middleware.

        See Also:
            :class:`gobstopper.core.blueprint.Blueprint`: Blueprint class documentation
            :meth:`add_middleware`: Adding middleware to applications
            :meth:`mount`: Alternative for mounting complete sub-applications
        """
        base_prefix = url_prefix if url_prefix is not None else getattr(blueprint, 'url_prefix', None)

        def _join(prefix: str | None, path: str) -> str:
            if not prefix:
                return path
            if not prefix.startswith('/'):
                prefix_local = '/' + prefix
            else:
                prefix_local = prefix
            if prefix_local.endswith('/'):
                prefix_local = prefix_local[:-1]
            if not path.startswith('/'):
                path = '/' + path
            return prefix_local + path

        def _register(bp, acc_prefix: str | None, chain: list[Any]):
            # Attach hooks to app with signature validation
            for h in getattr(bp, 'before_request_handlers', []) or []:
                sig = inspect.signature(h)
                if len(sig.parameters) != 1:
                    raise TypeError(f"Blueprint before_request handler '{getattr(h, '__name__', h)}' must accept exactly 1 argument: (request)")
                self.before_request(h)
            for h in getattr(bp, 'after_request_handlers', []) or []:
                sig = inspect.signature(h)
                if len(sig.parameters) != 2:
                    raise TypeError(f"Blueprint after_request handler '{getattr(h, '__name__', h)}' must accept exactly 2 arguments: (request, response)")
                self.after_request(h)
            # Per-blueprint templates
            tpl = getattr(bp, 'template_folder', None)
            if tpl and self.template_engine:
                ns = getattr(bp, 'name', None) or (Path(tpl).name if isinstance(tpl, (str, Path)) else None)
                try:
                    self.template_engine.add_search_path(tpl, namespace=ns)
                except TypeError:
                    # Backward compatibility if add_search_path has old signature
                    self.template_engine.add_search_path(tpl)
            # Per-blueprint static
            static_dir = getattr(bp, 'static_folder', None)
            if static_dir:
                static_prefix = _join(acc_prefix or '', '/static')
                self.add_middleware(StaticFileMiddleware(static_dir, url_prefix=static_prefix), priority=0)

            # Register routes for this blueprint
            for route in getattr(bp, 'routes', []) or []:
                full_path = _join(acc_prefix, route.pattern)
                if route.is_websocket:
                    handler = RouteHandler(full_path, route.handler, [], is_websocket=True)
                else:
                    handler = RouteHandler(full_path, route.handler, route.methods)
                # copy route-level middleware and set chain for scoped middleware
                for mw, prio in getattr(route, 'middleware', []) or []:
                    handler.use(mw, prio)
                handler.blueprint_chain = chain + [bp]

                # conflict detection
                self._check_conflicts(handler)

                if self.rust_router_available:
                    # New Rust router accepts Python path syntax directly
                    # Build qualified route name: blueprint.function_name
                    func_name = getattr(route.handler, '__name__', None)
                    bp_name = getattr(bp, 'name', None)
                    if bp_name and func_name:
                        route_name = f"{bp_name}.{func_name}"
                    else:
                        route_name = func_name

                    if route.is_websocket:
                        # WebSocket routes use "WEBSOCKET" as the method
                        self.websocket_router.insert(full_path, "WEBSOCKET", handler, route_name)
                    else:
                        for method in route.methods:
                            # New signature: insert(path, method, value, name)
                            self.http_router.insert(full_path, method.upper(), handler, route_name)
                else:
                    self.routes.append(handler)
                self._all_routes.append(handler)

            # Recurse into children
            for child, child_prefix in getattr(bp, 'children', []) or []:
                next_prefix = _join(acc_prefix, child_prefix if child_prefix is not None else getattr(child, 'url_prefix', None) or '')
                _register(child, next_prefix, chain + [bp])

        # Track blueprint root and register
        try:
            self.blueprints.append(blueprint)
        except Exception:
            pass
        _register(blueprint, base_prefix, [])

    def websocket(self, path: str):
        """Decorator for registering WebSocket routes with path parameters.

        Registers WebSocket connection handlers that manage bidirectional communication
        channels. WebSocket routes support the same path parameter syntax as HTTP routes
        but use a different protocol lifecycle (connect, message exchange, disconnect).

        Args:
            path: URL pattern to match. Supports same format as HTTP routes:
                - Static: ``"/ws/chat"``
                - Path parameters: ``"/ws/room/<room_id>"``
                - Type conversion: ``"/ws/user/<int:user_id>"``

        Returns:
            Decorator function that registers the WebSocket handler.

        Examples:
            Basic WebSocket echo:

            >>> @app.websocket("/ws/echo")
            >>> async def echo_handler(websocket):
            ...     await websocket.accept()
            ...     async for message in websocket:
            ...         await websocket.send(f"Echo: {message}")

            WebSocket with path parameters:

            >>> @app.websocket("/ws/room/<room_id>")
            >>> async def room_handler(websocket, room_id: str):
            ...     await websocket.accept()
            ...     # Join room
            ...     async for message in websocket:
            ...         # Broadcast to room
            ...         await broadcast_to_room(room_id, message)

            WebSocket with authentication:

            >>> @app.websocket("/ws/notifications")
            >>> async def notifications(websocket):
            ...     token = websocket.query_params.get('token')
            ...     if not validate_token(token):
            ...         await websocket.close(code=1008)  # Policy violation
            ...         return
            ...     await websocket.accept()
            ...     # Send notifications
            ...     while True:
            ...         notification = await get_next_notification()
            ...         await websocket.send_json(notification)

        Note:
            - WebSocket handlers must call ``await websocket.accept()`` before communication
            - Handlers should handle connection cleanup (use try/finally)
            - Path parameters work identically to HTTP routes
            - WebSocket middleware is not yet supported (use before_request for auth)
            - Connection errors are logged automatically

        See Also:
            :class:`gobstopper.websocket.connection.WebSocket`: WebSocket connection API
            :meth:`route`: HTTP route registration for comparison
        """
        def decorator(func: Handler) -> Handler:
            handler = RouteHandler(path, func, [], is_websocket=True)
            for mw, prio in getattr(func, '__route_middleware__', []) or []:
                handler.use(mw, prio)
            if self.rust_router_available:
                # New Rust router signature: insert(path, method, value, name)
                # Use "WEBSOCKET" as method for WebSocket routes
                route_name = getattr(func, '__name__', None)
                self.websocket_router.insert(path, "WEBSOCKET", handler, route_name)
            else:
                self.routes.append(handler)
            self._all_routes.append(handler)
            return func
        return decorator

    def url_for(self, name: str, **params) -> str:
        """Build a URL for a named route with parameters (reverse routing).

        Flask/Quart-style reverse routing that generates URLs from route names.
        Routes are automatically named with their function name, or you can provide
        a custom name using the ``name`` parameter in route decorators. Blueprint
        routes are qualified with the blueprint name (e.g., 'admin.login').

        Args:
            name: Route name (function name, custom name, or 'blueprint.function')
            **params: URL parameters to substitute into the route pattern

        Returns:
            Generated URL path as a string

        Raises:
            ValueError: If the named route doesn't exist or parameters are missing

        Examples:
            Basic usage:

            >>> @app.get('/users/<int:id>', name='user_detail')
            >>> async def get_user(request):
            ...     return {"user": ...}
            >>>
            >>> app.url_for('user_detail', id=123)
            '/users/123'

            With multiple parameters:

            >>> @app.get('/posts/<int:year>/<int:month>')
            >>> async def posts_archive(request):
            ...     return {"posts": ...}
            >>>
            >>> app.url_for('posts_archive', year=2024, month=12)
            '/posts/2024/12'

            Blueprint routes (Flask-style):

            >>> admin = Blueprint('admin', __name__)
            >>> @admin.get('/login')
            >>> async def login(request):
            ...     return {"login": True}
            >>>
            >>> app.register_blueprint(admin, url_prefix='/admin')
            >>> app.url_for('admin.login')  # Returns '/admin/login'
            '/admin/login'

            In request handlers with redirect:

            >>> @app.post('/users')
            >>> async def create_user(request):
            ...     new_id = save_user()
            ...     return redirect(app.url_for('user_detail', id=new_id))

        Note:
            - Requires Rust router for best performance
            - Falls back to route scanning if Rust router unavailable
            - Route names default to function names
            - Custom names provided via decorator ``name`` parameter

        See Also:
            :func:`redirect`: Convenience function for redirecting to URLs
            :meth:`route`: How to register named routes
        """
        if self.rust_router_available:
            # Use Rust router's url_for
            url = self.http_router.url_for(name, params if params else None)
            if url is None:
                raise ValueError(f"No route named '{name}' found")
            return url
        else:
            # Fallback: scan Python routes
            for route in self._all_routes:
                handler_name = getattr(route.handler, '__name__', None)

                # Check for exact match (function name)
                if handler_name == name:
                    # Build URL by replacing parameters in pattern
                    url = route.pattern
                    for key, value in params.items():
                        # Try different parameter formats
                        url = url.replace(f"<{key}>", str(value))
                        url = url.replace(f"<int:{key}>", str(value))
                        url = url.replace(f"<uuid:{key}>", str(value))
                        url = url.replace(f"<date:{key}>", str(value))
                        url = url.replace(f"<path:{key}>", str(value))
                    return url

                # Check for blueprint-qualified name (blueprint.function)
                if '.' in name and route.blueprint_chain:
                    # Get the last blueprint in the chain (closest to route)
                    bp = route.blueprint_chain[-1] if route.blueprint_chain else None
                    bp_name = getattr(bp, 'name', None) if bp else None
                    if bp_name and handler_name:
                        qualified_name = f"{bp_name}.{handler_name}"
                        if qualified_name == name:
                            url = route.pattern
                            for key, value in params.items():
                                url = url.replace(f"<{key}>", str(value))
                                url = url.replace(f"<int:{key}>", str(value))
                                url = url.replace(f"<uuid:{key}>", str(value))
                                url = url.replace(f"<date:{key}>", str(value))
                                url = url.replace(f"<path:{key}>", str(value))
                            return url
            raise ValueError(f"No route named '{name}' found")

    def task(self, name: str = None, category: str = "default"):
        """Decorator to register background task handlers with categorization.

        Registers async functions as background tasks that can be queued and executed
        asynchronously. Tasks are persisted to DuckDB, support retries, priority levels,
        and progress tracking. Tasks are organized by category for separate worker pools.

        Args:
            name: Task identifier (default: function name). Used when queuing tasks
                via :meth:`add_background_task`. Must be unique within category.
            category: Task category for worker pool isolation (default: "default").
                Tasks in different categories run in separate worker pools.
                Examples: "email", "data_processing", "notifications"

        Returns:
            Decorator function that registers the task handler.

        Examples:
            Basic task registration:

            >>> @app.task("send_email", category="notifications")
            >>> async def send_email(to: str, subject: str, body: str):
            ...     await email_client.send(to, subject, body)
            ...     return {"sent": True}

            Task with default name (uses function name):

            >>> @app.task(category="data")
            >>> async def process_upload(file_path: str):
            ...     data = await read_file(file_path)
            ...     result = await process_data(data)
            ...     return {"rows": len(result)}

            Task with progress tracking:

            >>> @app.task("import_data", category="imports")
            >>> async def import_large_dataset(source_url: str):
            ...     total = await get_row_count(source_url)
            ...     for i, batch in enumerate(fetch_batches(source_url)):
            ...         await process_batch(batch)
            ...         # Progress tracked automatically
            ...     return {"imported": total}

            Queuing registered tasks:

            >>> # In a request handler
            >>> task_id = await app.add_background_task(
            ...     "send_email",
            ...     category="notifications",
            ...     priority=TaskPriority.HIGH,
            ...     to="user@example.com",
            ...     subject="Welcome",
            ...     body="Hello!"
            ... )
            >>> return {"task_id": task_id}

        Note:
            - Tasks must be async functions
            - Task return values are stored and can be retrieved later
            - Failed tasks can be automatically retried based on max_retries
            - Tasks persist across application restarts (stored in DuckDB)
            - Each category needs worker processes started via :meth:`start_task_workers`

        See Also:
            :meth:`add_background_task`: Queue tasks for execution
            :meth:`start_task_workers`: Start worker pools for task categories
            :class:`gobstopper.tasks.queue.TaskQueue`: Task queue implementation
            :class:`gobstopper.tasks.queue.TaskPriority`: Priority levels (LOW, NORMAL, HIGH, URGENT)
        """
        def decorator(func: Handler) -> Handler:
            task_name = name or func.__name__
            self.task_queue.register_task(task_name, category)(func)
            return func
        return decorator
    
    def before_request(self, func: Handler) -> Handler:
        """Register a before-request handler that runs before each HTTP request.

        Before-request handlers execute after middleware but before the route handler.
        They can perform request validation, inject request-scoped data, or short-circuit
        the request by returning a Response directly.

        Args:
            func: Callable accepting (request) and optionally returning Response.
                Can be sync or async. If it returns a Response, the route handler
                is skipped and that response is returned immediately.

        Returns:
            The handler function (for decorator chaining).

        Examples:
            Request logging:

            >>> @app.before_request
            >>> async def log_requests(request):
            ...     app.logger.info(f"Request: {request.method} {request.path}")
            ...     # No return - continues to handler

            Authentication check:

            >>> @app.before_request
            >>> async def require_auth(request):
            ...     if not request.headers.get('authorization'):
            ...         return Response("Unauthorized", status=401)
            ...     # Auth successful - continues to handler

            Inject request-scoped data:

            >>> @app.before_request
            >>> async def add_user_context(request):
            ...     token = request.headers.get('authorization')
            ...     request.user = await validate_and_get_user(token)

        Note:
            - Runs for every HTTP request (not WebSocket)
            - Multiple handlers run in registration order
            - First handler to return a Response short-circuits the chain
            - Exceptions propagate and trigger error handlers

        See Also:
            :meth:`after_request`: Post-processing hook
            :meth:`add_middleware`: Alternative for cross-cutting concerns
        """
        self.before_request_handlers.append(func)
        return func

    def after_request(self, func: Handler) -> Handler:
        """Register an after-request handler that runs after each HTTP request.

        After-request handlers execute after the route handler but before sending
        the response. They can modify responses, add headers, or perform logging.
        Must accept both request and response parameters.

        Args:
            func: Callable accepting (request, response) and optionally returning
                modified Response. Can be sync or async. If it returns a Response,
                that replaces the original. If it returns None, original is used.

        Returns:
            The handler function (for decorator chaining).

        Examples:
            Add response headers:

            >>> @app.after_request
            >>> async def add_headers(request, response):
            ...     response.headers['X-Processed-By'] = 'Gobstopper'
            ...     return response

            Response logging:

            >>> @app.after_request
            >>> async def log_response(request, response):
            ...     app.logger.info(f"Response: {response.status}")
            ...     # No return - original response used

            Security headers:

            >>> @app.after_request
            >>> def add_security_headers(request, response):
            ...     response.headers['X-Content-Type-Options'] = 'nosniff'
            ...     response.headers['X-Frame-Options'] = 'DENY'
            ...     return response

        Note:
            - Runs for every successful HTTP request (not WebSocket)
            - Multiple handlers run in registration order
            - Each handler receives the response from the previous handler
            - Does not run if an exception occurs (use error handlers instead)

        See Also:
            :meth:`before_request`: Pre-processing hook
            :meth:`error_handler`: Handle exceptions
        """
        self.after_request_handlers.append(func)
        return func

    def context_processor(self, func: Callable[[], dict]) -> Callable[[], dict]:
        """Register a template context processor for global template variables.

        Context processors provide variables that are automatically available in all
        rendered templates. They run before each template render and can inject
        dynamic global context like current user, configuration, or request data.

        Args:
            func: Callable returning a dictionary of template variables. Can be sync
                or async. The returned dict is merged into every template's context.
                Should be idempotent and fast.

        Returns:
            The processor function (for decorator chaining).

        Examples:
            Add global template variables:

            >>> @app.context_processor
            >>> def inject_globals():
            ...     return {
            ...         'app_name': 'Gobstopper',
            ...         'version': '1.0.0',
            ...         'current_year': 2025
            ...     }

            Inject current user:

            >>> @app.context_processor
            >>> async def inject_user():
            ...     # Access request context if available
            ...     return {'user': getattr(request, 'user', None)}

            Configuration values:

            >>> @app.context_processor
            >>> def inject_config():
            ...     return {
            ...         'debug': app.debug,
            ...         'site_name': os.getenv('SITE_NAME', 'Gobstopper App')
            ...     }

        Note:
            - Runs before every template render
            - Multiple processors are merged in registration order
            - Later processors can override earlier ones
            - Should be fast - runs on every template render
            - Only affects templates, not JSON responses

        See Also:
            :meth:`render_template`: Template rendering
            :meth:`init_templates`: Template engine initialization
            :meth:`template_filter`: Custom template filters
            :meth:`template_global`: Custom template globals
        """
        self.template_context_processors.append(func)
        return func
    
    def template_filter(self, name: str = None):
        """Decorator to register template filter
        
        Note: When using the Rust template engine, custom filters are not
        supported. In that case this becomes a no-op to avoid noisy warnings.
        """
        def decorator(func):
            if self.template_engine:
                filter_name = name or func.__name__
                # Skip registration for Rust engine (not supported)
                if getattr(self.template_engine, 'using_rust', False):
                    return func
                self.template_engine.add_filter(filter_name, func)
            return func
        return decorator
    
    def template_global(self, name: str = None):
        """Decorator to register template global
        
        Note: When using the Rust template engine, custom globals are not
        supported. In that case this becomes a no-op to avoid noisy warnings.
        """
        def decorator(func):
            if self.template_engine:
                global_name = name or func.__name__
                # Skip registration for Rust engine (not supported)
                if getattr(self.template_engine, 'using_rust', False):
                    return func
                self.template_engine.add_global(global_name, func)
            return func
        return decorator
    
    def error_handler(self, status_code: int):
        """Decorator to register custom error handlers for HTTP status codes.

        Registers handlers that customize error responses for specific HTTP status codes.
        Error handlers receive the request and exception, allowing for custom error pages,
        logging, or error tracking integration.

        Args:
            status_code: HTTP status code to handle (e.g., 404, 500, 403, 429).
                Common codes: 400 (Bad Request), 401 (Unauthorized), 403 (Forbidden),
                404 (Not Found), 500 (Internal Server Error).

        Returns:
            Decorator function that registers the error handler.

        Examples:
            Custom 404 page:

            >>> @app.error_handler(404)
            >>> async def not_found(request, error):
            ...     return await app.render_template(
            ...         "errors/404.html",
            ...         path=request.path
            ...     )

            Custom 500 with error tracking:

            >>> @app.error_handler(500)
            >>> async def server_error(request, error):
            ...     # Log to error tracking service
            ...     await error_tracker.capture(error, request)
            ...     return JSONResponse(
            ...         {"error": "Internal server error", "request_id": request.id},
            ...         status=500
            ...     )

            Rate limit exceeded:

            >>> @app.error_handler(429)
            >>> async def rate_limited(request, error):
            ...     return JSONResponse(
            ...         {"error": "Too many requests", "retry_after": 60},
            ...         status=429,
            ...         headers={"Retry-After": "60"}
            ...     )

            Unauthorized with custom message:

            >>> @app.error_handler(401)
            >>> async def unauthorized(request, error):
            ...     return JSONResponse(
            ...         {
            ...             "error": "Authentication required",
            ...             "login_url": "/auth/login"
            ...         },
            ...         status=401
            ...     )

        Note:
            - Default handlers for 404 and 500 use themed error pages
            - Error handlers run outside middleware chain
            - Exceptions in error handlers fall back to basic text responses
            - Error handlers can be sync or async

        See Also:
            :meth:`before_request`: Pre-request validation
            :class:`gobstopper.http.response.Response`: Response construction
            :class:`gobstopper.http.response.JSONResponse`: JSON error responses
        """
        def decorator(func: ErrorHandler) -> ErrorHandler:
            self.error_handlers[status_code] = func
            return func
        return decorator
    
    async def render_template(self, template_name: str, stream: bool = False, **context) -> Response:
        """Render template with context data and return HTTP response.
        
        Renders the specified template file with provided context variables,
        returning a properly formatted HTTP response. Supports both traditional
        rendering and progressive streaming for large datasets.
        
        Args:
            template_name: Name of template file relative to template folder.
                Must include file extension (e.g., "page.html", "email.txt").
            stream: Enable progressive rendering (Rust engine only):
                - ``False``: Traditional rendering - template fully rendered before response
                - ``True``: Streaming rendering - template chunks sent as generated
            **context: Template context variables passed to template.
                Variables become available in template as ``{{ variable_name }}``.
                
        Returns:
            Response: HTTP response with rendered HTML content.
            StreamResponse: For streaming renders (when stream=True).
            
        Raises:
            RuntimeError: If template engine not initialized with :meth:`init_templates`
            FileNotFoundError: If template file does not exist
            TemplateRenderError: If template rendering fails (syntax errors, missing variables)
            
        Examples:
            Basic template rendering:
            
            >>> @app.get("/")
            >>> async def index(request):
            ...     return await app.render_template("index.html", 
            ...                                    title="Home Page",
            ...                                    user_name="Alice")
            
            With complex context:
            
            >>> @app.get("/dashboard")  
            >>> async def dashboard(request):
            ...     users = await get_users()
            ...     return await app.render_template("dashboard.html",
            ...                                    users=users,
            ...                                    page_title="Dashboard")
            
            Streaming large datasets (Rust only):
            
            >>> @app.get("/report")
            >>> async def large_report(request):
            ...     big_data = await get_large_dataset()
            ...     return await app.render_template("report.html",
            ...                                    stream=True,
            ...                                    data=big_data)
            
        Note:
            Context processors are automatically applied to provide global variables.
            Streaming requires Rust template engine and compatible templates.
            
        See Also:
            :meth:`init_templates`: Initialize template system
            :meth:`context_processor`: Add global template context  
            :class:`gobstopper.http.Response`: Response objects
        """
        if not self.template_engine:
            raise RuntimeError("Template engine not initialized. Call init_templates() first.")
        
        # Apply context processors
        for processor in self.template_context_processors:
            if asyncio.iscoroutinefunction(processor):
                context.update(await processor() or {})
            else:
                context.update(processor() or {})
        
        # Check if we're using the Rust template engine
        if isinstance(self.template_engine, RustTemplateEngineWrapper):
            # Use Rust template engine
            result = await self.template_engine.render_template(template_name, context, stream=stream)
            
            if stream and hasattr(result, '__aiter__'):
                # Return streaming response for progressive rendering
                async def generate_chunks():
                    async for chunk in result:
                        yield chunk
                
                return StreamResponse(generate_chunks(), content_type='text/html')
            else:
                # Regular response
                return Response(result, content_type='text/html')
        else:
            # Use traditional Jinja2 engine (ignore stream parameter)
            html = await self.template_engine.render_template_async(template_name, **context)
            return Response(html, content_type='text/html')
    
    async def add_background_task(self, name: str, category: str = "default",
                                 priority: TaskPriority = TaskPriority.NORMAL,
                                 max_retries: int = 0, *args, **kwargs) -> str:
        """Add a background task to the queue for asynchronous execution.

        Queues a registered task for execution by worker processes. Tasks are persisted
        to DuckDB immediately and executed based on priority and worker availability.
        Returns a task ID for tracking progress and retrieving results.

        Args:
            name: Name of the registered task (as specified in :meth:`task` decorator).
            category: Task category (default: "default"). Must match task registration.
                Category determines which worker pool executes the task.
            priority: Execution priority (default: TaskPriority.NORMAL).
                Options: TaskPriority.LOW, NORMAL, HIGH, URGENT.
                Higher priority tasks execute before lower priority.
            max_retries: Maximum retry attempts on failure (default: 0).
                Task will be retried up to this many times if it raises an exception.
            *args: Positional arguments passed to task handler.
            **kwargs: Keyword arguments passed to task handler.

        Returns:
            Task ID (UUID string) for tracking and result retrieval.

        Raises:
            KeyError: If task name is not registered in the specified category.
            Exception: If task queueing fails (database error, etc.).

        Examples:
            Queue a simple task:

            >>> task_id = await app.add_background_task(
            ...     "send_email",
            ...     to="user@example.com",
            ...     subject="Welcome",
            ...     body="Hello!"
            ... )
            >>> return {"task_id": task_id}

            High-priority task with retries:

            >>> task_id = await app.add_background_task(
            ...     "process_payment",
            ...     category="payments",
            ...     priority=TaskPriority.HIGH,
            ...     max_retries=3,
            ...     payment_id=123,
            ...     amount=99.99
            ... )

            Urgent task (process immediately):

            >>> task_id = await app.add_background_task(
            ...     "send_alert",
            ...     category="notifications",
            ...     priority=TaskPriority.URGENT,
            ...     message="System alert",
            ...     recipients=["admin@example.com"]
            ... )

            Track task status:

            >>> # In route handler
            >>> task_id = await app.add_background_task("long_process", data=data)
            >>> # Later, check status
            >>> task_info = await app.task_queue.get_task(task_id)
            >>> return {
            ...     "status": task_info.status,
            ...     "progress": task_info.progress,
            ...     "result": task_info.result
            ... }

        Note:
            - Tasks execute asynchronously in separate worker processes
            - Task parameters are serialized to JSON (must be JSON-serializable)
            - Workers must be started via :meth:`start_task_workers` for execution
            - Task status can be queried using the returned task_id
            - Failed tasks remain in database for inspection

        See Also:
            :meth:`task`: Register task handlers
            :meth:`start_task_workers`: Start worker pools
            :class:`gobstopper.tasks.queue.TaskPriority`: Priority levels
            :class:`gobstopper.tasks.queue.TaskQueue`: Task queue operations
        """
        return await self.task_queue.add_task(name, category, priority, max_retries, *args, **kwargs)
    
    async def start_task_workers(self, category: str = "default", worker_count: int = 1):
        """Start background worker processes for task execution.

        Launches worker processes that poll for and execute queued tasks in the specified
        category. Workers run continuously until application shutdown. Multiple workers
        can process tasks concurrently within the same category.

        Args:
            category: Task category to process (default: "default"). Workers only
                execute tasks queued in this category. Must match category used
                in :meth:`task` decorator and :meth:`add_background_task`.
            worker_count: Number of concurrent workers to start (default: 1).
                More workers enable parallel task processing. Consider CPU-bound
                vs I/O-bound tasks when sizing worker pools.

        Examples:
            Start default workers:

            >>> # In startup handler
            >>> @app.on_startup
            >>> async def start_workers():
            ...     await app.start_task_workers("default", worker_count=4)

            Multiple categories with different worker counts:

            >>> @app.on_startup
            >>> async def start_all_workers():
            ...     # I/O-bound tasks (email, API calls)
            ...     await app.start_task_workers("notifications", worker_count=10)
            ...     # CPU-bound tasks (image processing)
            ...     await app.start_task_workers("processing", worker_count=2)
            ...     # Critical tasks
            ...     await app.start_task_workers("payments", worker_count=4)

            Single worker for sequential processing:

            >>> @app.on_startup
            >>> async def start_sequential_worker():
            ...     # Process tasks one at a time
            ...     await app.start_task_workers("imports", worker_count=1)

        Note:
            - Workers run as background asyncio tasks
            - Each worker polls the database for pending tasks
            - Workers respect task priority (URGENT > HIGH > NORMAL > LOW)
            - Workers automatically retry failed tasks based on max_retries
            - Workers shut down gracefully on application shutdown
            - This should be called in :meth:`on_startup` handlers

        See Also:
            :meth:`task`: Register task handlers
            :meth:`add_background_task`: Queue tasks
            :meth:`on_startup`: Application startup hooks
        """
        await self.task_queue.start_workers(category, worker_count)
    
    async def _ensure_startup_complete(self):
        """Ensure startup tasks are completed (called lazily on first request).

        Executes registered startup handlers on first request with thread-safe locking.
        Uses double-checked locking pattern to avoid unnecessary lock acquisition.
        If startup fails, the completion flag is not set, allowing retry on next request.

        Note:
            - Called automatically by :meth:`_handle_http` before processing requests
            - Startup handlers registered via :meth:`on_startup` run here
            - Protected by asyncio.Lock for concurrent request safety
            - Failures are logged but startup can be retried
            - Runs only once successfully per application instance
        """
        if self._startup_complete:
            return
        
        async with self._startup_lock:
            if self._startup_complete:  # Double-check after acquiring lock
                return
            
            try:
                # Call any registered startup handlers
                if hasattr(self, '_startup_handlers'):
                    for handler in self._startup_handlers:
                        if asyncio.iscoroutinefunction(handler):
                            await handler()
                        else:
                            handler()
                
                self._startup_complete = True
                self.logger.debug("Application startup completed")
                
            except Exception as e:
                self.logger.error(f"Error during application startup: {e}", exc_info=True)
                # Don't mark as complete so it will be retried
    
    def on_startup(self, func):
        """Decorator to register startup handlers that run once before first request.

        Registers functions to execute during application initialization. Startup handlers
        run lazily on the first request (not at module import time), allowing for async
        resource initialization like database connections, cache warming, or worker startup.

        Args:
            func: Callable to run at startup. Can be sync or async.
                Should handle its own exceptions or allow them to propagate
                to prevent startup completion.

        Returns:
            The handler function (for decorator chaining).

        Examples:
            Initialize database connection:

            >>> @app.on_startup
            >>> async def init_database():
            ...     app.db = await create_db_pool(DATABASE_URL)
            ...     app.logger.info("Database connected")

            Start background workers:

            >>> @app.on_startup
            >>> async def start_workers():
            ...     await app.start_task_workers("default", worker_count=4)
            ...     await app.start_task_workers("email", worker_count=2)

            Warm up caches:

            >>> @app.on_startup
            >>> async def warm_cache():
            ...     app.config = await load_config()
            ...     app.cache = await init_redis_cache()

            Load ML models:

            >>> @app.on_startup
            >>> def load_models():
            ...     app.ml_model = load_pretrained_model("model.pkl")
            ...     app.logger.info("Model loaded")

        Note:
            - Handlers run once on first request, not at import time
            - Multiple handlers run in registration order
            - Startup is protected by asyncio.Lock for thread safety
            - Exceptions prevent startup completion and will be retried
            - All handlers must complete before first request proceeds

        See Also:
            :meth:`on_shutdown`: Cleanup handlers
            :meth:`start_task_workers`: Starting background workers
        """
        if not hasattr(self, '_startup_handlers'):
            self._startup_handlers = []
        self._startup_handlers.append(func)
        return func

    def on_shutdown(self, func):
        """Decorator to register shutdown handlers for graceful cleanup.

        Registers functions to execute during application shutdown. Shutdown handlers
        run after the application stops accepting new requests and in-flight requests
        complete, allowing for resource cleanup like closing database connections,
        flushing caches, or stopping background workers.

        Args:
            func: Callable to run at shutdown. Can be sync or async.
                Exceptions are logged but do not prevent other shutdown handlers
                from running.

        Returns:
            The handler function (for decorator chaining).

        Examples:
            Close database connections:

            >>> @app.on_shutdown
            >>> async def close_database():
            ...     await app.db.close()
            ...     app.logger.info("Database connection closed")

            Flush caches and save state:

            >>> @app.on_shutdown
            >>> async def save_state():
            ...     await app.cache.flush()
            ...     await save_application_state()
            ...     app.logger.info("State saved")

            Stop external services:

            >>> @app.on_shutdown
            >>> async def stop_services():
            ...     await app.websocket_manager.close_all()
            ...     await app.metrics_client.close()

            Cleanup temporary files:

            >>> @app.on_shutdown
            >>> def cleanup_temp_files():
            ...     import shutil
            ...     shutil.rmtree("/tmp/app_uploads", ignore_errors=True)

        Note:
            - Handlers run after server stops accepting new requests
            - In-flight requests are allowed to complete (with timeout)
            - Multiple handlers run in registration order
            - Exceptions in handlers are logged but don't stop other handlers
            - Task queue shutdown happens automatically after custom handlers
            - Default shutdown timeout is 10 seconds (configurable via WOPR_SHUTDOWN_TIMEOUT)

        See Also:
            :meth:`on_startup`: Initialization handlers
            :meth:`shutdown`: Programmatic shutdown trigger
        """
        self._shutdown_hooks.append(func)
        return func
    
    def _find_route(self, path: str, method: str, is_websocket: bool = False) -> RouteResult:
        """Find matching route and extract path parameters.

        Internal route matching method that searches registered routes for a match
        and extracts typed path parameters. Uses Rust router if available for O(1)
        static route lookup, otherwise falls back to Python linear search with regex.

        Args:
            path: Request path to match (e.g., "/users/123").
            method: HTTP method (e.g., "GET", "POST") or "WEBSOCKET".
            is_websocket: Whether to search WebSocket routes (default: False).

        Returns:
            Tuple of (RouteHandler, params_dict) where params_dict contains
            extracted and type-converted path parameters. Returns (None, {})
            if no match found.

        Note:
            - Rust router provides O(1) lookup for static routes
            - Path parameter type conversion is automatic (int, uuid, date, etc.)
            - Conversion errors are flagged with '__conversion_error__' key
            - Python fallback uses linear search with regex matching
        """
        if self.rust_router_available:
            if is_websocket:
                router = self.websocket_router
                # WebSocket routes use "WEBSOCKET" as method
                try:
                    match = router.get_with_params(path, "WEBSOCKET")
                except AttributeError:
                    # Fallback for old router
                    match = router.get(path)
            else:
                router = self.http_router
                # New router signature: get_with_params(path, method)
                try:
                    match = router.get_with_params(path, method.upper())
                except AttributeError:
                    # Fallback for old router
                    match = router.get(f"{method.upper()}{path}")

            if match:
                handler, raw_params = match
                # Apply converters based on handler's compiled param specs
                typed: dict[str, Any] = {}
                try:
                    for name, conv in handler._compiled_param_specs:
                        if name in raw_params:
                            val = unquote(raw_params[name])
                            typed[name] = conv(val) if conv else val
                    return handler, typed
                except Exception:
                    return handler, {'__conversion_error__': True}
            return None, {}

        # Fallback to original python implementation
        for route in self.routes:
            if route.is_websocket == is_websocket:
                params = route.match(path, method)
                if params is not None:
                    return route, params
        return None, {}
    
    async def _apply_middleware(self, request: Request, stack: list[MiddlewareTuple], final_handler: Callable[[Request], Any]) -> Response:
        """Compose and execute middleware chain around final handler.

        Builds and executes a middleware chain by wrapping the final handler with
        each middleware function in reverse order (inner to outer). This creates
        an onion-like structure where outer middleware calls inner middleware.

        Args:
            request: HTTP request being processed.
            stack: List of (middleware, priority) tuples ordered outer→inner.
                Outer middleware executes first and has higher priority.
            final_handler: The innermost handler (route handler + hooks).

        Returns:
            Response from either middleware (short-circuit) or final handler.

        Note:
            - Middleware stack is built in reverse (inner→outer)
            - Each middleware can call next_handler or return directly
            - Supports both sync and async middleware transparently
            - Middleware can inspect/modify requests and responses
        """
        handler: Callable[[Request], Any] = final_handler

        # Build middleware chain inner→outer (reverse apply)
        for middleware_func, _ in reversed(stack):
            def make_next_handler(mw: Middleware, next_h: Callable[[Request], Any]) -> Callable[[Request], Any]:
                async def created(req: Request) -> Any:
                    # Support both sync and async middleware, and allow sync middleware
                    # to return either a Response or an awaitable from calling next_h.
                    try:
                        result = mw(req, next_h)
                    except Exception:
                        # If the middleware itself is async, call accordingly
                        # (this branch is unlikely triggered; keep simple)
                        result = mw(req, next_h)
                    if inspect.isawaitable(result):
                        return await result
                    return result
                return created
            handler = make_next_handler(middleware_func, handler)
        # Execute chain (handler is always async wrapper)
        result = await handler(request)
        return result
    
    async def _default_404_handler(self, request: Request, error: Exception) -> Response:
        """Default 404 handler that renders a themed error page.

        Internal error handler for 404 Not Found responses. Renders a professional
        themed error page using the framework's internal template engine. Shows
        request details in debug mode.

        Args:
            request: The HTTP request that resulted in 404.
            error: Exception that triggered the 404 (typically generic "Not Found").

        Returns:
            Response with 404 status and HTML error page.

        Note:
            - Uses internal template engine (separate from app templates)
            - Shows request path, ID, and traceback if debug=True
            - Can be overridden by registering custom handler via :meth:`error_handler`
        """
        # Use themed error page if template engine is available, otherwise plain text
        if self._error_template_engine:
            context = {
                "status_code": 404,
                "error_title": "Resource Not Found",
                "error_description": f"The resource at path '{request.path}' could not be found.",
                "debug": self.debug,
                "request_id": getattr(request, 'id', 'N/A'),
                "request_path": request.path,
                "request": request,
                "traceback": None,
            }
            body = await self._error_template_engine.render_template_async("wopr_error.html", **context)
            return Response(body, status=404, content_type='text/html')
        else:
            # Fallback to plain text if no template engine available
            body = f"404 Not Found\n\nThe resource at path '{request.path}' could not be found."
            return Response(body, status=404, content_type='text/plain')

    async def _default_500_handler(self, request: Request, error: Exception) -> Response:
        """Default 500 handler that renders a themed error page with traceback.

        Internal error handler for 500 Internal Server Error responses. Renders
        a professional themed error page with full traceback information when
        debug mode is enabled. Provides request context for error investigation.

        Args:
            request: The HTTP request that caused the error.
            error: The exception that was raised during request processing.

        Returns:
            Response with 500 status and HTML error page including traceback.

        Note:
            - Traceback shown only when app.debug=True
            - Uses internal template engine (separate from app templates)
            - Shows request ID for error correlation
            - Can be overridden by registering custom handler via :meth:`error_handler`
            - In production, hides sensitive traceback details
        """
        # Use themed error page if template engine is available, otherwise plain text
        tb_str = traceback.format_exc()

        if self._error_template_engine:
            context = {
                "status_code": 500,
                "error_title": "Internal System Error",
                "error_description": "An unexpected error occurred. The system has logged the incident.",
                "debug": self.debug,
                "request_id": getattr(request, 'id', 'N/A'),
                "request_path": request.path,
                "request": request,
                "traceback": tb_str,
            }
            body = await self._error_template_engine.render_template_async("wopr_error.html", **context)
            return Response(body, status=500, content_type='text/html')
        else:
            # Fallback to plain text if no template engine available
            body = "500 Internal Server Error\n\nAn unexpected error occurred."
            if self.debug:
                body += f"\n\n{tb_str}"
            return Response(body, status=500, content_type='text/plain')
    
    def _problem(self, detail: str, status: int) -> Response:
        """Create a standardized problem+json response (internal helper).

        Internal method that creates RFC 7807 Problem Details responses. This
        is a convenience wrapper that delegates to the public problem() function.

        Args:
            detail: Human-readable error description.
            status: HTTP status code.

        Returns:
            JSONResponse with application/problem+json content type.

        Note:
            Deprecated: This is an internal helper. Application code should use
            :func:`gobstopper.http.problem.problem` directly for RFC 7807 responses.

        See Also:
            :func:`gobstopper.http.problem.problem`: Public RFC 7807 problem response creator
        """
        from ..http.problem import problem as _p
        return _p(detail, status)

    async def _handle_http(self, scope: Scope, protocol: HTTPProtocol):
        """Handle HTTP request with scoped middleware and typed params.

        Primary HTTP request handler implementing the RSGI protocol. Manages the complete
        request lifecycle including startup, routing, middleware execution, handler invocation,
        error handling, and graceful shutdown. This is called by the RSGI server for each
        incoming HTTP request.

        Args:
            scope: RSGI scope containing request metadata (method, path, headers, etc.).
            protocol: RSGI HTTP protocol object for sending responses.

        Note:
            This is an internal method called by the RSGI protocol handler.
            Request lifecycle:
            1. Ensure startup handlers have completed
            2. Check if accepting requests (graceful shutdown)
            3. Check for mounted sub-applications
            4. Find matching route (with trailing slash policy)
            5. Build middleware stack (app → blueprints → route)
            6. Execute before_request handlers
            7. Execute route handler with path parameter coercion
            8. Execute after_request handlers
            9. Send response via protocol
            10. Handle errors via registered error handlers

        See Also:
            :meth:`__rsgi__`: RSGI entry point
            :meth:`_handle_websocket`: WebSocket protocol handler
            :meth:`_apply_middleware`: Middleware composition
        """
        # Ensure startup is complete before handling requests
        await self._ensure_startup_complete()

        # If shutting down, refuse new requests gracefully
        if not self._accepting_requests:
            resp = Response("Server is shutting down", status=503, headers={"connection": "close"})
            await self._send_response(protocol, resp)
            return
        
        request = Request(scope, protocol)
        request_id = str(uuid.uuid4())
        request.id = request_id
        # Attach app reference for handlers/blueprints to access app context
        setattr(request, 'app', self)
        
        # Apply request limits from env
        try:
            max_bytes_env = os.getenv("WOPR_JSON_MAX_BYTES")
            if max_bytes_env:
                setattr(request, 'max_body_bytes', int(max_bytes_env))
        except Exception:
            pass
        try:
            max_depth_env = os.getenv("WOPR_JSON_MAX_DEPTH")
            if max_depth_env:
                setattr(request, 'max_json_depth', int(max_depth_env))
        except Exception:
            pass

        # Track in-flight for graceful shutdown
        self._inflight_requests += 1
        self._inflight_zero.clear()
        with self.logger.contextualize(request_id=request_id):
            try:
                
                if self.debug:
                    self.logger.debug(f"-> {request.method} {request.path} from {request.client_ip}")
                
                # Delegate to mounted sub-apps if path matches
                for mount_prefix, subapp in self.mounts:
                    pref = mount_prefix.rstrip('/')
                    if request.path == pref or request.path.startswith(pref + '/'):
                        sub_scope = dict(scope)
                        new_path = request.path[len(pref):] or '/'
                        if not new_path.startswith('/'):
                            new_path = '/' + new_path
                        sub_scope['path'] = new_path
                        await subapp._handle_http(sub_scope, protocol)
                        return
                
                # Find route early for scoped middleware
                route, path_params = self._find_route(request.path, request.method)

                # Populate Flask/Quart-style request attributes
                if route:
                    request.view_args = path_params or {}
                    request.endpoint = getattr(route.handler, '__name__', None)
                    request.url_rule = route.pattern

                if not route:
                    # Trailing slash redirect policy
                    alt_path = None
                    if self.slash_policy == 'add_slash' and not request.path.endswith('/'):
                        alt_path = request.path + '/'
                    elif self.slash_policy == 'remove_slash' and request.path != '/' and request.path.endswith('/'):
                        alt_path = request.path[:-1] or '/'
                    if alt_path:
                        alt_route, _ = self._find_route(alt_path, request.method)
                        if alt_route:
                            # Issue 308 Permanent Redirect
                            resp = Response('', status=308, headers={'location': alt_path})
                            await self._send_response(protocol, resp)
                            return
                    # Distinguish 404 vs 405 by probing allowed methods
                    allowed = self._allowed_methods_for_path(request.path, is_websocket=False)
                    if allowed:
                        # 405 Method Not Allowed
                        resp = self._problem("Method Not Allowed", 405)
                        resp.headers['Allow'] = ', '.join(sorted(set(allowed)))
                        await self._send_response(protocol, resp)
                        return
                    # No matching route; run global middleware around a 404 responder
                    async def not_found_handler(req: Request) -> Response:
                        return await self.error_handlers[404](req, Exception("Not Found"))
                    stack = self.middleware[:]  # only app-level
                    response = await self._apply_middleware(request, stack, not_found_handler)
                    await self._send_response(protocol, response)
                    return
                
                # If router flagged conversion error from converter, return 400
                if isinstance(path_params, dict) and path_params.get('__conversion_error__'):
                    await self._send_response(protocol, self._problem("Invalid path parameter", 400))
                    return
                
                # Prepare kwargs and body model
                kwargs = dict(path_params)
                error_response: Response | None = None

                # Coerce based on handler annotations for path params (use cached signature)
                try:
                    if route.signature and route._param_annotations:
                        # Use pre-cached annotations for faster lookup
                        for name, ann in route._param_annotations.items():
                            if name == 'request' or name not in kwargs:
                                continue
                            try:
                                # Only coerce if still a string (converters already applied to path params)
                                if isinstance(kwargs[name], str):
                                    if ann is int:
                                        kwargs[name] = int(kwargs[name])
                                    elif ann is uuid.UUID or (hasattr(ann, '__name__') and ann.__name__ == 'UUID'):
                                        kwargs[name] = uuid.UUID(kwargs[name])
                                    elif hasattr(ann, '__name__') and ann.__name__ == 'date':
                                        from datetime import date, datetime as _dt
                                        if not isinstance(kwargs[name], date):
                                            kwargs[name] = _dt.strptime(kwargs[name], "%Y-%m-%d").date()
                                # else leave as-is
                            except Exception:
                                error_response = self._problem(f"Invalid value for path parameter '{name}'", 400)
                                break
                
                    # Decode at most one msgspec Struct from body
                    if error_response is None and route.signature:
                        for param_name, param in route.signature.parameters.items():
                            if param_name == 'request' or param_name in kwargs:
                                continue
                            if inspect.isclass(param.annotation) and issubclass(param.annotation, msgspec.Struct):
                                try:
                                    # Delegate to Request.json for unified content-type checks and caching
                                    kwargs[param.name] = await request.json(model=param.annotation)
                                except Exception as e:
                                    from ..http.errors import UnsupportedMediaType, BodyValidationError
                                    if isinstance(e, UnsupportedMediaType):
                                        error_response = self._problem(str(e) or "Unsupported Media Type", 415)
                                    elif isinstance(e, BodyValidationError):
                                        payload = {"detail": "Validation Failed"}
                                        if getattr(e, 'message', None):
                                            payload["message"] = e.message
                                        if getattr(e, 'errors', None):
                                            payload["errors"] = e.errors
                                        resp = JSONResponse(payload, status=422)
                                        resp.headers['content-type'] = 'application/problem+json'
                                        error_response = resp
                                    else:
                                        # Non-mapped error; re-raise
                                        raise
                                break
                except (TypeError, ValueError):
                    pass

                # Get pre-computed middleware stack (or compute and cache if not done yet)
                stack = route._cached_middleware_stack
                if stack is None:
                    stack = self._precompute_middleware_chain(route)

                # Define final handler to run before/after handlers and the route
                async def final_handler(req: Request) -> Response:
                    # before_request handlers
                    for h in self.before_request_handlers:
                        result = await h(req) if asyncio.iscoroutinefunction(h) else h(req)
                        if isinstance(result, Response):
                            return result
                    if error_response:
                        resp = error_response
                    else:
                        try:
                            resp = await route.handler(req, **kwargs) if asyncio.iscoroutinefunction(route.handler) else route.handler(req, **kwargs)
                        except Exception as e:
                            # Map known body/media errors to problem+json
                            from ..http.errors import UnsupportedMediaType, BodyValidationError, RequestTooLarge, HTTPException
                            if isinstance(e, HTTPException):
                                # Handle abort() calls - use custom response if provided
                                if e.response:
                                    resp = e.response
                                elif e.status in self.error_handlers:
                                    # Use registered error handler
                                    handler = self.error_handlers[e.status]
                                    resp = await handler(req, e) if asyncio.iscoroutinefunction(handler) else handler(req, e)
                                else:
                                    # Default error response
                                    resp = JSONResponse(
                                        {"error": e.description or f"HTTP {e.status}"},
                                        status=e.status
                                    )
                            elif isinstance(e, UnsupportedMediaType):
                                resp = self._problem(str(e) or "Unsupported Media Type", 415)
                            elif isinstance(e, BodyValidationError):
                                # Include detail and optional errors
                                payload = {"detail": "Validation Failed"}
                                if getattr(e, 'message', None):
                                    payload["message"] = e.message
                                if getattr(e, 'errors', None):
                                    payload["errors"] = e.errors
                                resp = JSONResponse(payload, status=422)
                                resp.headers['content-type'] = 'application/problem+json'
                            elif isinstance(e, RequestTooLarge):
                                resp = self._problem("Request body too large", 413)
                            else:
                                raise
                        if not isinstance(resp, (Response, FileResponse, StreamResponse)):
                            resp = JSONResponse(resp) if isinstance(resp, (dict, list)) else Response(str(resp))
                    # ensure request id header without mutating global handlers
                    if hasattr(resp, 'headers'):
                        resp.headers['x-request-id'] = req.id
                    # after_request handlers
                    for h in self.after_request_handlers:
                        resp = (await h(req, resp) or resp) if asyncio.iscoroutinefunction(h) else (h(req, resp) or resp)
                    return resp

                response = await self._apply_middleware(request, stack, final_handler)
                await self._send_response(protocol, response)
                
            except Exception as e:
                self.logger.exception(
                    "Unhandled exception during HTTP request processing",
                    extra={
                        "request_path": request.path,
                        "request_method": request.method,
                        "request_headers": dict(request.headers),
                        "client_ip": request.client_ip,
                        "exception_type": type(e).__name__,
                    }
                )
                try:
                    handler = self.error_handlers.get(500, self._default_500_handler)
                    response = await handler(request, e)
                    await self._send_response(protocol, response)
                except Exception as inner_e:
                    self.logger.exception(
                        "Critical error in 500 error handler",
                        extra={"original_exception": str(e)}
                    )
                    protocol.response_str(500, [], f"Internal Server Error: {str(inner_e)}")
            finally:
                try:
                    self._inflight_requests -= 1
                    if self._inflight_requests <= 0:
                        self._inflight_zero.set()
                except Exception:
                    pass

    async def _handle_websocket(self, scope: Scope, protocol: WebsocketProtocol):
        """Handle WebSocket connection with path parameter support.

        WebSocket protocol handler implementing the RSGI WebSocket protocol. Routes
        incoming WebSocket connections to registered handlers, extracts path parameters,
        and manages connection lifecycle including error handling.

        Args:
            scope: RSGI scope containing WebSocket metadata (path, headers, etc.).
            protocol: RSGI WebSocket protocol object for managing the connection.

        Note:
            This is an internal method called by the RSGI protocol handler.
            WebSocket lifecycle:
            1. Create WebSocket wrapper around protocol
            2. Find matching WebSocket route
            3. Extract path parameters
            4. Invoke handler with websocket and parameters
            5. Handle errors and close connection appropriately

            WebSocket handlers must call ``await websocket.accept()`` before
            sending or receiving messages. Connection cleanup is automatic.

        See Also:
            :meth:`__rsgi__`: RSGI entry point
            :meth:`_handle_http`: HTTP protocol handler
            :meth:`websocket`: WebSocket route decorator
            :class:`gobstopper.websocket.connection.WebSocket`: WebSocket API
        """
        websocket = WebSocket(scope, protocol)
        route, path_params = self._find_route(scope.path, 'WEBSOCKET', is_websocket=True)

        if not route:
            log.warning(f"No WebSocket route found for path: {scope.path}")
            # Ensure protocol has a close method before calling it.
            if hasattr(protocol, 'close'):
                await protocol.close(1001) # 1001: "Going Away"
            return

        try:
            handler_coro = route.handler(websocket, **path_params)
            await handler_coro
        except Exception as e:
            log.error(f"Error in WebSocket handler for {scope['path']}: {e}", exc_info=True)
            if hasattr(protocol, 'close'):
                await protocol.close(1011) # 1011: "Internal Error"
    
    async def _send_response(self, protocol: HTTPProtocol, response: Response):
        """Send response using RSGI protocol with appropriate method.

        Dispatches responses to the correct RSGI protocol method based on response
        type. Handles regular responses, file responses, and streaming responses
        with proper content type handling.

        Args:
            protocol: RSGI HTTP protocol object for sending the response.
            response: Response object (Response, FileResponse, or StreamResponse).

        Note:
            - FileResponse uses protocol.response_file (zero-copy serving)
            - StreamResponse uses protocol.response_stream (chunked transfer)
            - Regular Response uses protocol.response_str or response_bytes
            - Headers are converted to RSGI format (list of tuples)
        """
        if isinstance(response, FileResponse):
            protocol.response_file(response.status, response.to_rsgi_headers(), response.file_path)
        elif isinstance(response, StreamResponse):
            transport = protocol.response_stream(response.status, [(k, v) for k, v in response.headers.items()])
            async for chunk in response.generator():
                if isinstance(chunk, str):
                    await transport.send_str(chunk)
                else:
                    await transport.send_bytes(chunk)
        else:
            if isinstance(response.body, str):
                protocol.response_str(response.status, response.to_rsgi_headers(), response.body)
            else:
                protocol.response_bytes(response.status, response.to_rsgi_headers(), response.body)
    
    def visualize_routing(self):
        """Print a detailed visualization of application routing structure.

        Logs a comprehensive view of the routing hierarchy including mounts,
        blueprints, middleware ordering, and effective middleware chains for
        each route. Useful for debugging routing issues, understanding middleware
        execution order, and verifying blueprint composition.

        Examples:
            Call during startup:

            >>> @app.on_startup
            >>> def show_routes():
            ...     app.visualize_routing()

            Output shows:

            >>> # === Routing Visualization ===
            >>> # Mount: /api -> api_v1
            >>> # Blueprint: auth prefix=/auth
            >>> #   MW(prio=100): auth_middleware
            >>> #   Blueprint: admin prefix=/admin
            >>> #     MW(prio=50): admin_check
            >>> # Route ['GET'] /api/users -> MW order: ['cors', 'auth', 'rate_limit']
            >>> # === End Visualization ===

        Note:
            - Shows mounts, blueprints hierarchy, and middleware
            - Displays effective middleware order for each route
            - Middleware order reflects actual execution (app → blueprints → route)
            - Useful for debugging middleware composition issues
            - Output goes to application logger at INFO level

        See Also:
            :meth:`register_blueprint`: Blueprint registration
            :meth:`mount`: Sub-application mounting
            :meth:`add_middleware`: Middleware registration
        """
        self.logger.info("=== Routing Visualization ===")
        if self.mounts:
            for prefix, sub in self.mounts:
                self.logger.info(f"Mount: {prefix} -> {getattr(sub, 'name', repr(sub))}")
        if self.blueprints:
            def _bp_tree(bp, indent=0):
                self.logger.info("  "*indent + f"Blueprint: {bp.name} prefix={getattr(bp, 'url_prefix', None)}")
                for mw, prio in getattr(bp, 'middleware', []) or []:
                    self.logger.info("  "*(indent+1) + f"MW(prio={prio}): {getattr(mw, '__name__', repr(mw))}")
                for child, _ in getattr(bp, 'children', []) or []:
                    _bp_tree(child, indent+1)
            for bp in self.blueprints:
                _bp_tree(bp)
        # List routes and their effective middleware order
        for route in self._all_routes:
            chain = getattr(route, 'blueprint_chain', []) or []
            collected: list[tuple[Middleware, int, int, int]] = []
            idx_counter = 0
            for mw, prio in self.middleware:
                collected.append((mw, prio, 0, idx_counter)); idx_counter += 1
            depth = 1
            for bp in chain:
                for mw, prio in getattr(bp, 'middleware', []) or []:
                    collected.append((mw, prio, depth, idx_counter)); idx_counter += 1
                depth += 1
            collected.sort(key=lambda t: (-t[1], t[2], t[3]))
            seen_ids: set[int] = set()
            ordered_stack: list[MiddlewareTuple] = []
            for mw, prio, _, _ in collected:
                if id(mw) in seen_ids:
                    continue
                seen_ids.add(id(mw))
                ordered_stack.append((mw, prio))
            eff = [getattr(mw, '__name__', repr(mw)) for mw, _ in ordered_stack] + [getattr(mw, '__name__', repr(mw)) for mw, _ in (getattr(route, 'middleware', []) or [])]
            self.logger.info(f"Route {route.methods or ['WS']} {route.pattern} -> MW order: {eff}")
        self.logger.info("=== End Visualization ===")
    
    async def shutdown(self, timeout: float | None = None):
        """Initiate graceful application shutdown with in-flight request handling.

        Performs a graceful shutdown sequence: stops accepting new requests, waits
        for in-flight requests to complete (with timeout), runs shutdown hooks,
        and closes the task queue. This ensures no requests are abruptly terminated
        and resources are properly cleaned up.

        Args:
            timeout: Maximum seconds to wait for in-flight requests (default: None).
                If None, reads from environment variable WOPR_SHUTDOWN_TIMEOUT
                (default: 10 seconds). After timeout, shutdown proceeds anyway.

        Examples:
            Manual shutdown:

            >>> # In a special endpoint
            >>> @app.post("/admin/shutdown")
            >>> async def trigger_shutdown(request):
            ...     asyncio.create_task(app.shutdown(timeout=30))
            ...     return {"status": "shutting down"}

            Signal handler:

            >>> import signal
            >>> def handle_sigterm(signum, frame):
            ...     asyncio.create_task(app.shutdown())
            >>> signal.signal(signal.SIGTERM, handle_sigterm)

            Custom timeout:

            >>> await app.shutdown(timeout=60)  # Wait up to 60s

        Note:
            Shutdown sequence:
            1. Stop accepting new requests (503 responses)
            2. Wait for in-flight requests to complete (up to timeout)
            3. Run registered shutdown hooks via :meth:`on_shutdown`
            4. Shutdown task queue and workers
            5. Log any errors but continue shutdown

            Environment variable WOPR_SHUTDOWN_TIMEOUT (seconds) sets default timeout.
            In-flight request count is tracked automatically.
            Shutdown hooks run even if timeout expires.

        See Also:
            :meth:`on_shutdown`: Register cleanup handlers
            :meth:`start_task_workers`: Background workers
        """
        self._accepting_requests = False
        to = timeout
        if to is None:
            try:
                to = float(os.getenv("WOPR_SHUTDOWN_TIMEOUT", "10"))
            except Exception:
                to = 10.0
        # Wait for in-flight requests
        try:
            await asyncio.wait_for(self._inflight_zero.wait(), timeout=to)
        except asyncio.TimeoutError:
            self.logger.warning("Graceful shutdown timeout reached; continuing shutdown with %d in-flight", self._inflight_requests)
        # Run shutdown hooks
        for hook in self._shutdown_hooks:
            if asyncio.iscoroutinefunction(hook):
                try:
                    await hook()
                except Exception:
                    self.logger.exception("Error in shutdown hook")
            else:
                try:
                    hook()
                except Exception:
                    self.logger.exception("Error in shutdown hook")
        # Shutdown task queue last
        try:
            await self.task_queue.shutdown()
        except Exception:
            self.logger.exception("Error shutting down task queue")
    
    async def __rsgi__(self, scope: Scope, protocol):
        """RSGI application entry point called by Granian server.

        Main entry point for the RSGI (Rust Server Gateway Interface) protocol.
        This method is called by the Granian server for each incoming connection
        and routes to the appropriate protocol handler (HTTP or WebSocket).

        Args:
            scope: RSGI scope object containing request metadata. Expected to have
                a 'proto' field indicating protocol type ('http' or 'ws'/'websocket').
            protocol: RSGI protocol object (HTTPProtocol or WebsocketProtocol) for
                managing the connection and sending responses.

        Note:
            This is the application's RSGI interface. The ``__rsgi__`` name is
            required by the RSGI specification and is automatically detected by
            Granian when you run: ``granian --interface rsgi app:app``

            Protocol dispatch:
            - 'http' → :meth:`_handle_http`
            - 'ws'/'websocket' → :meth:`_handle_websocket`

            The scope is converted to a SimpleNamespace if provided as dict
            (for test client compatibility).

        Examples:
            Run with Granian:

            >>> # In your app.py
            >>> from gobstopper import Gobstopper
            >>> app = Gobstopper(__name__)
            >>> @app.get("/")
            >>> async def hello(request):
            ...     return {"message": "Hello"}

            Command line:

            >>> # granian --interface rsgi app:app
            >>> # granian --interface rsgi --reload app:app  # With hot reload

        See Also:
            :meth:`_handle_http`: HTTP request handler
            :meth:`_handle_websocket`: WebSocket connection handler
        """
        # If the scope is a dict (from a test client), convert it to an object
        # so the rest of the app can use consistent attribute access.
        if isinstance(scope, dict):
            # The ASGI test client scope doesn't have 'proto', so we add it.
            scope.setdefault('proto', scope.get('type', 'http'))
            scope = SimpleNamespace(**scope)

        if scope.proto == 'http':
            await self._handle_http(scope, protocol)
        elif scope.proto in ('ws', 'websocket'):
            await self._handle_websocket(scope, protocol)
    def _allowed_methods_for_path(self, path: str, is_websocket: bool = False) -> list[str]:
        """Return list of allowed HTTP methods for a given path.

        Determines which HTTP methods are supported for a specific path by checking
        all registered routes. Used to generate proper 405 Method Not Allowed responses
        with the Allow header listing valid methods.

        Args:
            path: Request path to check (e.g., "/users/123").
            is_websocket: Whether to check WebSocket routes (default: False).
                Generally returns empty list for WebSocket checks.

        Returns:
            Sorted list of allowed HTTP method strings (e.g., ["GET", "POST"]).
            Empty list if no routes match the path or if is_websocket=True.

        Note:
            - With Rust router: Uses built-in allowed_methods() or probes common methods
            - With Python router: Scans all routes for regex matches
            - Used to distinguish 404 (no route) from 405 (wrong method)
            - Result is sorted alphabetically for consistency
        """
        if is_websocket:
            return []
        allowed: set[str] = set()
        if self.rust_router_available:
            try:
                methods = self.http_router.allowed_methods(path)
                for m in methods:
                    allowed.add(m)
            except Exception:
                # Fallback probing if older router doesn't have allowed_methods
                methods = ['GET','POST','PUT','DELETE','PATCH','OPTIONS']
                for m in methods:
                    try:
                        match = self.http_router.get_with_params(path, m)
                    except AttributeError:
                        # Very old router
                        match = self.http_router.get(f"{m}{path}")
                    if match:
                        handler, _ = match
                        for hm in handler.methods:
                            allowed.add(hm)
        else:
            for route in self.routes:
                if route.is_websocket:
                    continue
                # Try to match path regardless of method
                if route.regex and route.regex.match(path):
                    for hm in route.methods:
                        allowed.add(hm)
        # Do not include pseudo WEBSOCKET
        return sorted(allowed)
