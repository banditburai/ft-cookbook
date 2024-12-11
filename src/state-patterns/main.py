# ============================================================================
#  Imports & Setup
# ============================================================================

from fasthtml.common import *
import uuid
import inspect
from functools import wraps
from typing import Dict, List, Tuple

# ============================================================================
#  Code Capture
# ============================================================================

class CodeCapture:
    def __init__(self, code: str, content: Any):
        self.code = code
        self.content = content

def show_ft(name: str = None):
    def decorator(f):
        # Get original source before any decorators
        try:
            source = inspect.getsource(f.__wrapped__ if hasattr(f, '__wrapped__') else f)
        except (AttributeError, TypeError):
            source = inspect.getsource(f)
            
        code = '\n'.join(source.split('\n')[1:])
        
        @wraps(f)
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)
        
        wrapper._source_code = code
        return wrapper
    return decorator

# ============================================================================
#  Ported PageManager
# ============================================================================
class Page:
    def __init__(self, app: FastHTML):
        self.app = app        
        self.elements = []
    
    def add(self, element):
        # print(f"Adding element: {type(element)}")  # Debug
        self.elements.append(element)
        return self
    
    def render(self):
        return Div(            
            *self.elements, 
            cls="page-content"
        )


# ============================================================================
#  App Headers
# ============================================================================
styles = Link(rel="stylesheet", href="/styles.css", type="text/css")
prism_resources = (
# Prism CSS
Link(rel="stylesheet", href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/themes/prism.min.css"),
Link(rel="stylesheet", href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/plugins/toolbar/prism-toolbar.min.css"),
Link(rel="stylesheet", href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/plugins/copy-to-clipboard/prism-copy-to-clipboard.min.css"),
Link(rel="stylesheet", href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/plugins/line-highlight/prism-line-highlight.min.css"),
Link(rel="stylesheet", href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/plugins/line-numbers/prism-line-numbers.min.css"),

# Prism JS
Script(src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/components/prism-core.min.js"),
Script(src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/components/prism-python.min.js"),
Script(src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/plugins/toolbar/prism-toolbar.min.js"),
Script(src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/plugins/copy-to-clipboard/prism-copy-to-clipboard.min.js"),
Script(src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/plugins/line-highlight/prism-line-highlight.min.js"),
Script(src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/plugins/line-numbers/prism-line-numbers.min.js"),    
)

app, rt = fast_app(
    pico=False,
    surreal=False,
    live=False,    
    hdrs=(styles, *prism_resources),       
    htmlkw=dict(lang="en", dir="ltr", cls=""),
    bodykw=dict(style="padding-bottom: 10vh",
        cls=""        
        )    
)

# ============================================================================
#  Main Page
# ============================================================================
home = Page(app) 

@rt('/')
def get():
    return Title("State Patterns"), home.render()          

home.add(    
    H1("State Patterns", 
       cls="page-title", 
       **{
           "data-date": "2024-12-10",
           "data-icon": "📁"
       })
)

# ============================================================================
#  Code Example
# ============================================================================
class CodeExample:
    # Class-level storage for all instances
    _code_blocks: Dict[str, str] = {}
    _code_tags: Dict[str, Dict[str, List[str]]] = {}
    
    @classmethod
    def create(cls, *, 
               title: str, 
               description: str, 
               code_title: str, 
               code: str, 
               key_points: List[Tuple[str, str]] = None, 
               instance_id: str | None = None) -> Div:
        """Factory method to create and render a code example"""
        instance = cls(
            title=title,
            description=description,
            code_title=code_title,
            code=code,
            key_points=key_points,
            instance_id=instance_id
        )
        return instance.render()

    def __init__(self, **kwargs):
        """Initialize but don't render yet"""
        self.instance_id = kwargs.get('instance_id') or str(uuid.uuid4())
        self.title = kwargs['title']
        self.description = kwargs['description']
        self.code_title = kwargs['code_title']
        self.key_points = kwargs.get('key_points') or []
        
        self._process_code(kwargs['code'])

    def _process_code(self, code: str) -> None:
        """Process code and extract show tags."""
        # Clean the code
        self.clean_code = '\n'.join(
            line.split('#: show-')[0].rstrip()
            for line in code.split('\n')
        )
        CodeExample._code_blocks[self.instance_id] = self.clean_code
        
        # Process tags
        tags_dict = {}
        for i, line in enumerate(code.split('\n')):
            if '#: show-' not in line:
                continue
                
            tags = [t.strip() for t in line.split('#: show-')[1:]]
            for tag in tags:
                if tag not in tags_dict:
                    tags_dict[tag] = []
                tags_dict[tag].append(str(i + 2))
                
        CodeExample._code_tags[self.instance_id] = tags_dict
    
    def _render_header(self) -> Div:
        """Render the title and description section."""
        return Div(
            H3(self.title, cls="explanation-title"),
            Div(
                P(self.description, cls="explanation-text"),
                cls="explanation-section"
            )
        )
    
    def _render_code_block(self, code_display_id: str) -> Div:
        """Render the code display section."""
        return Div(
            Div(
                Div("−", cls="header-control"),
                H4(self.code_title, cls="code-title"),
                Div("□", cls="header-control"),
                cls="code-header"
            ),
            Div(
                Pre(
                    Code(self.clean_code.strip(), cls="language-python"),
                    cls="line-numbers",
                    data_start="1"
                ),
                id=code_display_id
            ),
            cls="code-container"
        )
    
    def _render_key_points(self, code_display_id: str) -> FT | None:
        """Render the key points section if points exist."""
        if not self.key_points:
            return None
            
        return Div(
            Div("Key Points", cls="key-points-label"),
            Ul(*[
                self._render_key_point(text, tag, code_display_id)
                for text, tag in self.key_points
            ], cls="key-points"),
            cls="key-points-container"     
        )
    
    def _render_key_point(self, text: str, tag: str, code_display_id: str) -> Li:
        """Render a single key point with its checkbox."""
        return Li(
            Input(
                type="checkbox",
                id=f"toggle-{self.instance_id}-{tag}",
                name=f"toggle-{self.instance_id}",
                onclick=self._get_toggle_script(),
                hx_get=f"/highlight/{self.instance_id}/{tag}",
                hx_target=f"#{code_display_id}",                        
                hx_trigger="change",
                **{
                    "hx-swap-oob": "true",
                    "hx-on::after-request": self._get_highlight_script()
                },                        
                cls='toggle'
            ),
            Label(
                text,
                For=f"toggle-{self.instance_id}-{tag}",                       
                cls="key-point"
            ),
            cls="key-point-container"
        )
    
    def _get_toggle_script(self) -> str:
        """Get the JavaScript for toggling checkboxes."""
        return """if (this.checked) { 
            [...document.getElementsByName(this.name)]
                .forEach(cb => cb !== this && (cb.checked = false));
        }"""
    
    def _get_highlight_script(self) -> str:
        """Get the JavaScript for handling highlights."""
        return f"""
            Prism.highlightElement(document.querySelector('#code-display-{self.instance_id} code'));
            setTimeout(() => {{
                const highlight = document.querySelector('#code-display-{self.instance_id} .line-highlight');
                if (highlight) {{
                    highlight.scrollIntoView({{behavior: 'smooth', block: 'center'}});
                }}
            }}, 100);
        """
    
    def render(self) -> Div:
        """Render the complete tutorial card."""
        code_display_id = f"code-display-{self.instance_id}"
        
        return Div(
            self._render_header(),
            self._render_code_block(code_display_id),
            self._render_key_points(code_display_id),
            cls="tutorial-card",
            id=f"tutorial-card-{self.instance_id}"
        )
    
    def __call__(self):
        return self.render()

# ============================================================================
#  Code Example Highlight Endpoint
# ============================================================================
@rt("/highlight/{instance_id}/{tag}")
def get(instance_id: str, tag: str, request: Request):
    if instance_id not in CodeExample._code_blocks:
        raise HTTPException(status_code=404, detail="Code block not found")
    
    code = CodeExample._code_blocks[instance_id]    
    line_numbers = ','.join(CodeExample._code_tags[instance_id].get(tag, []))
    code_display_id = f"code-display-{instance_id}"    
    
    return Div(
        Pre(
            Code(code, cls="language-python"),
            cls="line-numbers",
            data_line=line_numbers if request.query_params else '',
            data_start="1"
        ),
        id=code_display_id,        
    )

# ============================================================================
#  Browser Window + Content Section
# ============================================================================
def BrowserWindow(*, title: str, children: list):
    return Div(
        # Browser chrome
        Div(
            # Title bar with controls
            Div(
                Span("○ ○ ○", cls="browser-controls"),
                Span(title, cls="browser-title"),
                cls="browser-bar"
            ),
            # URL bar
            Div(
                Span("🔒", cls="browser-secure"),
                Span("localhost:8000", cls="browser-url"),
                cls="browser-address"
            ),
            cls="browser-chrome"
        ),
        # Content area
        Div(children, cls="browser-content"),
        cls="browser-window"
    )

def ContentSection(*components, cls=""):
    """Creates a bordered section with consistent styling"""
    return Section(
        *components,
        cls=f"tutorial-section {cls}"
    )


# ============================================================================
#  Demo App Code
# ============================================================================

@show_ft()
def cart_ui():
    return Div(
        H1("Shopping Cart"),
        # Hidden fields for state
        Hidden(id="cart-count", value="1"), #: show-state-storage #: show-initialization 
        Hidden(id="item-price", value="29.99"), #: show-state-storage #: show-initialization
        
        # Cart item
        Div(
            H2("Premium Stuffs"),
            P("$29.99 each"),
            
            # Quantity controls
            Div(
                Button("-", #: show-targeting #: show-static-values #: show-state-inclusion #: show-response-targeting
                    hx_post="/cart/update", #: show-targeting #: show-state-inclusion
                    hx_include="#cart-count, #item-price", #: show-targeting #: show-state-inclusion
                    hx_vals='{"adjust": -1}', #: show-targeting #: show-static-values
                    hx_target="#response-target", #: show-targeting #: show-response-targeting
                    disabled="true", #: show-targeting
                    id="decrement-btn"), #: show-targeting
                Span("1", id="quantity-display"),  #: show-initialization
                Button("+", #: show-static-values #: show-response-targeting
                    hx_post="/cart/update", #: show-state-inclusion
                    hx_include="#cart-count, #item-price", #: show-state-inclusion
                    hx_vals='{"adjust": 1}', #: show-static-values
                    hx_target="#response-target"), #: show-response-targeting
                cls="quantity-controls"
            ),
            
            P("Subtotal: $", Span("29.99", id="subtotal-display")),  #: show-initialization
            cls="cart-item"
        ),
        
        # Order summary
        Div(
            H3("Order Summary"),
            P("Items: $", Span("29.99", id="items-total")),
            P("Shipping: $", Span("5.00", id="shipping-cost")),
            Hr(),
            P("Total: $", Span("34.99", id="total-display"), cls="font-bold"),
            cls="order-summary"
        ),
        
        # Discount tier indicator
        Div(
            P("Add $", Span("70.01", id="tier-remaining"), " more to qualify for free shipping!",
            id="tier-message"),
            id="tier-container",
            cls="discount-tier pending"
        ),
        
        # Cart badge in header
        Div(
            Span("1", id="cart-badge"),
            " items in cart",
            cls="cart-badge"
        ),
        
        # Response target
        Div(id="response-target"), #: show-response-targeting
    )

@show_ft()
def cart_constants():
    return dict(
        ITEM_PRICE = 29.99,
        FREE_SHIPPING_THRESHOLD = 100.00,
        SHIPPING_COST = 5.00
    )


@show_ft()
@rt("/cart/update", methods=["POST"])
async def cart_update(request):
    form = await request.form() #: show-form-processing
    data = dict(form) #: show-form-processing
    
    # Get current values #: show-form-processing
    count = int(data.get("cart-count", 1)) #: show-form-processing
    price = float(data.get("item-price", 29.99)) #: show-form-processing
    adjust = int(data.get("adjust", 0)) #: show-form-processing
    
    # Calculate new values
    new_count = max(1, count + adjust) #: show-calculations
    subtotal = new_count * price #: show-calculations
    shipping = 0 if subtotal >= 100 else 5.00 #: show-calculations
    total = subtotal + shipping #: show-calculations
    tier_remaining = max(0, 100 - subtotal) #: show-calculations
    
    # Determine if decrement should be disabled #: show-calculations
    decrement_disabled = new_count <= 1 #: show-calculations
    qualified = subtotal >= 100 #: show-calculations
    
    return ( #: show-oob-updates
        # Update hidden state #: show-oob-updates
        Hidden(id="cart-count", value=str(new_count), hx_swap_oob="true"), #: show-oob-updates
        
        # Update displays #: show-oob-updates
        Span(str(new_count), id="quantity-display", hx_swap_oob="true"), #: show-oob-updates
        Span(f"{subtotal:.2f}", id="subtotal-display", hx_swap_oob="true"), #: show-oob-updates
        Span(f"{subtotal:.2f}", id="items-total", hx_swap_oob="true"), #: show-oob-updates
        Span(f"{shipping:.2f}", id="shipping-cost", hx_swap_oob="true"), #: show-oob-updates
        Span(f"{total:.2f}", id="total-display", hx_swap_oob="true"), #: show-oob-updates
        
        # Update tier message and container               
        Div(
            P("You've qualified for free shipping!") if qualified else
            P("Add $", Span(f"{tier_remaining:.2f}", id="tier-remaining"), " more to qualify for free shipping!"),
            id="tier-container",
            cls=f"discount-tier {'qualified' if qualified else 'pending'}",
            hx_swap_oob="true"),
        
        Span(str(new_count), id="cart-badge", hx_swap_oob="true"),
        
        # Update decrement button state
        Button("-", 
            hx_post="/cart/update",
            hx_include="#cart-count, #item-price",
            hx_vals='{"adjust": -1}',
            hx_target="#response-target",
            disabled="true" if decrement_disabled else None,
            id="decrement-btn",
            hx_swap_oob="true")
    )


# ============================================================================
#  Page Content
# ============================================================================
home.add(
    ContentSection(
        H2("Managing State in FastHTML with HTMX"),                
            P("When building interactive web applications with HTMX, there are two main approaches to handling state:"),
            Ul(
                Li("Static Values (hx-vals) - For unchanging data and action indicators"),
                Li("Hidden Fields - For dynamic state that needs to persist")
            ),
            P("Let's build a shopping cart to demonstrate both approaches.")
        )    
)

home.add(
    BrowserWindow(
        title="Shopping Cart",
        children=cart_ui() 
    )
)

home.add(
    CodeExample.create(
        title="State Management in Interactive UIs",
        code_title="Shopping Cart UI",
        description="""
        This code demonstrates two complementary approaches to managing state:
        
        1. Traditional HTML Hidden Fields:
        - Store values that need to persist between requests
        - Provide server-rendered initial state
        - Can be accessed and updated via JavaScript/HTMX
        
        2. HTMX Enhancement Attributes:
        - Send static action values (hx-vals)
        - Include specific elements in requests (hx-include)
        - Target elements for updates (hx-target)
        
        Together, these create a robust state management system where hidden fields 
        store the dynamic state while HTMX attributes handle the interactions.
        """,
        code=cart_ui._source_code,
        key_points=[
            # HTML Hidden Fields
            ("Traditional hidden input fields", "state-storage"),
            ("Server-rendered initial values", "initialization"),
            
            # HTMX Attributes
            ("Static action values with hx-vals", "static-values"),
            ("State inclusion with hx-include", "state-inclusion"),
            ("Response targeting with hx-target", "response-targeting")
        ]
    )
)

home.add(
    CodeExample.create(
        title="Server-Side State Management",
        code_title="Cart Update Handler",
        description="""
        This route demonstrates how to:
        - Process both hidden state and static values
        - Calculate derived values (subtotal, shipping, etc.)
        - Return multiple OOB updates to maintain UI state
        """,
        code=cart_update._source_code,
        key_points=[
            ("Extract and process form data", "form-processing"),
            ("Calculate derived state", "calculations"),
            ("Return OOB swaps for UI updates", "oob-updates")
        ]
    )
)

home.add(
    ContentSection(
        H2("Shopping Cart Demo"),        
        P("This demo combines both approaches:"),
        Ul(
            Li("Hidden fields track the current state (quantity and price)"),
            Li("Buttons use hx-vals to indicate actions (increment/decrement)"),
            Li("Server-side logic handles calculations and updates")
        )
        )    
)

home.add(
    ContentSection(
        H2("Best Practices"),
        # hx-vals section
        H3("When to use hx-vals:"),
        Ul(
            Li("Static values that don't change during interaction"),
            Li("Action indicators or simple flags (like {'adjust': 1} or {'mode': 'delete'})"),
            Li("Data only needed for the request, not persisting in DOM"),
            Li("Values hardcoded in HTML templates")
        ),
        
        # Hidden fields section
        H3("When to use Hidden Fields:"),
        Ul(
            Li("Dynamic values that update during interaction"),
            Li("State that needs to persist between requests"),
            Li("Values needed by multiple different requests"),
            Li("Values that might need JavaScript access"),
            Li("Server-rendered initial state that needs client maintenance")
        ),
        
        # General guidelines
        H3("General Guidelines:"),
        Ul(
            Li("Prefer server-side state management when possible"),
            Li("Use hidden fields sparingly to avoid state management complexity"),
            Li("Combine both approaches when it makes sense for your use case")
        )
        
    )
)

# ============================================================================
#  Serve
# ============================================================================
# serve()

# Run the app
if __name__ == "__main__":
    serve(port=8080)

