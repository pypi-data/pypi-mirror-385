import asyncio
import inspect
from dataclasses import dataclass, field
from typing import Callable, Type, Optional, Dict, List
import flet as ft

# Registry to store view configurations
_VIEW_REGISTRY: Dict[str, dict] = {}


def view(route: str, state_class: Type = None, on_load: Optional[Callable] = None, **view_kwargs):
    """
    Decorator to register a view with its route, state class, on_load handler, and view properties.

    Args:
        route: The route path for this view (e.g., '/', '/store', '/user/{user_id}')
        state_class: Optional dataclass for view-specific state (should be decorated with @ft.observable)
        on_load: Optional function to call before rendering the view (can be async).
                 Function can accept: state, page, view, and any URL parameters
        **view_kwargs: Additional keyword arguments to pass to ft.View (e.g., appbar, bgcolor, padding)
    """

    def decorator(func: Callable):
        _VIEW_REGISTRY[route] = {
            'func': func,
            'state_class': state_class,
            'on_load': on_load,
            'view_kwargs': view_kwargs,
            'route': route
        }
        return func

    return decorator


def match_route(pattern: str, path: str) -> Optional[Dict[str, str]]:
    """
    Match a route pattern against a path and extract parameters.

    Args:
        pattern: Route pattern like '/user/{user_id}'
        path: Actual path like '/user/123'

    Returns:
        Dictionary of parameters if matched, None otherwise
    """
    pattern_parts = pattern.split('/')
    path_parts = path.split('/')

    if len(pattern_parts) != len(path_parts):
        return None

    params = {}
    for pattern_part, path_part in zip(pattern_parts, path_parts):
        if pattern_part.startswith('{') and pattern_part.endswith('}'):
            param_name = pattern_part[1:-1]
            params[param_name] = path_part
        elif pattern_part != path_part:
            return None

    return params


def find_matching_route(path: str) -> Optional[tuple]:
    """
    Find a matching route pattern for the given path.

    Returns:
        Tuple of (route_pattern, params_dict) if found, None otherwise
    """
    for route_pattern in _VIEW_REGISTRY.keys():
        params = match_route(route_pattern, path)
        if params is not None:
            return (route_pattern, params)
    return None


def get_route_key(route: str, params: Dict[str, str]) -> str:
    """Generate a unique key for a route with its parameters."""
    if not params:
        return route
    param_str = ','.join(f"{k}={v}" for k, v in sorted(params.items()))
    return f"{route}?{param_str}"


class ViewProxy:
    """Proxy class to allow updating view properties in on_load."""

    def __init__(self, view_kwargs: dict):
        self._view_kwargs = view_kwargs

    def __setattr__(self, name, value):
        if name.startswith('_'):
            super().__setattr__(name, value)
        else:
            self._view_kwargs[name] = value

    def __getattr__(self, name):
        if name.startswith('_'):
            return super().__getattribute__(name)
        return self._view_kwargs.get(name)


async def call_on_load(on_load_func: Callable, state, page, view_proxy: ViewProxy, params: Dict[str, str]):
    """
    Call the on_load function with appropriate parameters based on its signature.

    Args:
        on_load_func: The on_load function to call
        state: The view state (if any)
        page: The Flet page object
        view_proxy: Proxy object to update view properties
        params: URL parameters extracted from the route
    """
    if on_load_func is None:
        return

    sig = inspect.signature(on_load_func)
    param_names = list(sig.parameters.keys())

    kwargs = {}
    for param_name in param_names:
        if param_name == 'state':
            kwargs['state'] = state
        elif param_name == 'page':
            kwargs['page'] = page
        elif param_name == 'view':
            kwargs['view'] = view_proxy
        elif param_name in params:
            kwargs[param_name] = params[param_name]

    if asyncio.iscoroutinefunction(on_load_func):
        await on_load_func(**kwargs)
    else:
        on_load_func(**kwargs)


@ft.observable
@dataclass
class AppModel:
    """
    Main application model that manages routing state.

    Attributes:
        routes: Stack of routes for navigation history
        view_states: Dictionary storing state instances for each route
        view_kwargs_cache: Dictionary storing updated view kwargs for each route
        loaded_routes: Set of routes that have completed their on_load
        loading_counter: Counter to track loading operations
        initialized: Flag to track if initial route has been set
    """
    routes: List[str] = field(default_factory=list)
    view_states: Dict[str, any] = field(default_factory=dict)
    view_kwargs_cache: Dict[str, dict] = field(default_factory=dict)
    loaded_routes: set = field(default_factory=set)
    loading_counter: int = 0
    initialized: bool = False

    def initialize_with_route(self, initial_route: str):
        """Initialize the app with a specific route."""
        if not self.initialized:
            self.routes = [initial_route]
            self.initialized = True
            # Trigger initial on_load
            asyncio.create_task(self.handle_on_load(initial_route))

    def route_change(self, e: ft.RouteChangeEvent):
        """Handle route changes by maintaining a navigation stack."""
        new_route = e.route

        # If not initialized yet, initialize with this route
        if not self.initialized:
            self.initialize_with_route(new_route)
            return

        # Prevent adding duplicate consecutive routes
        if self.routes and self.routes[-1] == new_route:
            return

        # Append new route to the stack
        self.routes.append(new_route)

        # Handle on_load for the new route
        asyncio.create_task(self.handle_on_load(new_route))

    async def handle_on_load(self, route: str):
        """Handle on_load for the current route."""
        config = None
        params = {}

        if route in _VIEW_REGISTRY:
            config = _VIEW_REGISTRY[route]
        else:
            match_result = find_matching_route(route)
            if match_result:
                route_pattern, params = match_result
                config = _VIEW_REGISTRY[route_pattern]

        if config:
            route_key = get_route_key(config['route'], params)

            # Only call on_load if it hasn't been called for this route instance
            if route_key not in self.loaded_routes and config.get('on_load'):
                state = self.get_or_create_state(config['route'], config['state_class'])
                page = ft.context.page

                # Create a copy of view_kwargs for this route instance
                view_kwargs = config['view_kwargs'].copy()
                view_proxy = ViewProxy(view_kwargs)

                await call_on_load(config['on_load'], state, page, view_proxy, params)

                # Store the updated view_kwargs for this route
                self.view_kwargs_cache[route_key] = view_kwargs

                self.loaded_routes.add(route_key)
                self.loading_counter += 1

    async def view_popped(self, e: ft.ViewPopEvent):
        """Handle back navigation by popping from the routes stack."""
        if len(self.routes) > 1:
            # Remove the last route from the stack
            self.routes.pop()

            # Navigate to the new top of the stack
            new_route = self.routes[-1]
            await ft.context.page.push_route(new_route)

    def get_or_create_state(self, route: str, state_class: Type):
        """Get existing state or create new one for a route."""
        if state_class is None:
            return None

        if route not in self.view_states:
            self.view_states[route] = state_class()
        return self.view_states[route]

    def get_view_kwargs(self, route_key: str, default_kwargs: dict) -> dict:
        """Get view kwargs for a route, using cached version if available."""
        if route_key in self.view_kwargs_cache:
            return self.view_kwargs_cache[route_key]
        return default_kwargs.copy()


def render_view_for_route(route: str, app: AppModel) -> ft.View:
    """
    Helper function to render a single view for a given route.

    Args:
        route: The route path to render
        app: The AppModel instance managing application state

    Returns:
        ft.View instance for the route
    """
    config = None
    params = {}

    # Try exact match first
    if route in _VIEW_REGISTRY:
        config = _VIEW_REGISTRY[route]
    else:
        # Try pattern matching
        match_result = find_matching_route(route)
        if match_result:
            route_pattern, params = match_result
            config = _VIEW_REGISTRY[route_pattern]

    if not config:
        # No matching route found, show 404
        return ft.View(
            route=route,
            appbar=ft.AppBar(),
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.ERROR_OUTLINE, size=100, color=ft.Colors.RED_400),
                ft.Text("404 - Page Not Found", size=32, weight=ft.FontWeight.BOLD),
            ]
        )

    route_key = get_route_key(config['route'], params)

    # Check if on_load has completed (or doesn't exist)
    if config.get('on_load') and route_key not in app.loaded_routes:
        # Show loading view
        return ft.View(
            route=route,
            controls=[ft.ProgressRing()],
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )

    # Get state
    state = app.get_or_create_state(config['route'], config['state_class'])

    # Get view_kwargs - use cached version if available (may be modified by on_load)
    view_kwargs = app.get_view_kwargs(route_key, config['view_kwargs'])

    # Call view function with appropriate parameters
    if params:
        # Parameterized route
        if state is None:
            controls = config['func'](**params)
        else:
            controls = config['func'](state, **params)
    else:
        # Static route
        if state is None:
            controls = config['func']()
        else:
            controls = config['func'](state)

    return ft.View(
        route=route,
        controls=controls,
        **view_kwargs
    )


@ft.component
def FletStack():
    """
    Main component that manages the routing stack and renders views.

    Usage:
        ft.run(lambda page: page.render_views(FletStack))

        or

        def main(page: ft.Page):
            page.route = "/login"  # Set initial route
            page.render_views(FletStack)
        ft.run(main)
    """
    app, _ = ft.use_state(AppModel())

    # Check for initial route from page.route
    if not app.initialized:
        initial_route = ft.context.page.route
        if initial_route and initial_route != "/":
            app.initialize_with_route(initial_route)
        else:
            app.initialize_with_route("/")

    # Subscribe to page events
    ft.context.page.on_route_change = app.route_change
    ft.context.page.on_view_pop = app.view_popped

    # Render all views in the routes stack
    views = []
    for route in app.routes:
        views.append(render_view_for_route(route, app))

    return views