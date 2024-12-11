# ============================================================================
#  Imports & Setup
# ============================================================================

from fasthtml.common import *
from typing import Dict, List, Tuple

@dataclass
class Example:
    title: str
    path: str = "#"
    date: str = "2024-03-14"
    disabled: bool = False
    icon: str = "📄"

@dataclass
class Folder:
    title: str
    examples: List[Example]
    icon: str = "📁"
    
# ============================================================================
#  Recipes!
# ============================================================================

COOKBOOK_STRUCTURE = [
    Folder("State Management", [
        Example("State Patterns", "https://state-patterns.fly.dev/", "2024-12-11"),
        Example("Form Validation", disabled=True),
    ]),
    Folder("UI Patterns", [
        Example("Infinite Scroll", disabled=True),
        Example("Modal Dialogs", disabled=True),
    ]),
]

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
#  Helper Functions
# ============================================================================
def get_latest_publish_date():
    # Get all non-disabled examples across all folders
    all_examples = [
        example 
        for folder in COOKBOOK_STRUCTURE
        for example in folder.examples
        if not example.disabled
    ]
    
    # Return most recent date, or fallback if no published examples
    return max((ex.date for ex in all_examples), default="2024-03-14")

# ============================================================================
#  App Headers
# ============================================================================
styles = Link(rel="stylesheet", href="/styles.css", type="text/css")

app, rt = fast_app(
    pico=False,
    surreal=False,
    live=False,    
    hdrs=(styles, ),       
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
    return Title("ft-Cookbook"), home.render()          

home.add(
    H1("FastHTML Cookbook", 
       cls="page-title", 
       **{
           "data-date": get_latest_publish_date(),
           "data-icon": "👩‍🍳"
       })
)

# ============================================================================
#  Components
# ============================================================================
def ExampleLink(*, title: str, path: str = "#", icon: str = "📄", date: str = "2024-03-14", disabled: bool = False):
    """Create a Windows Explorer style link to an example"""
    attrs = {
        "data-icon": icon,
    }
    
    if disabled:
        attrs["data-status"] = "🚧"
    else:
        attrs["data-date"] = date

    return A(
        title + (" (Coming Soon)" if disabled else ""),
        href=path if not disabled else "javascript:void(0)",
        cls=f"example-link {'disabled' if disabled else ''}",
        **attrs
    )

def ExampleFolder(*, title: str, examples: list, icon: str = "📁"):
    """Create a Windows Explorer style folder"""
    return Div(
        H2(title, cls="folder-title", **{"data-icon": icon}),
        Div(*examples, _class="folder-content"),
        cls="example-folder",
        **{"data-item-count": len(examples)}
    )

for folder in COOKBOOK_STRUCTURE:
    home.add(
        ExampleFolder(
            title=folder.title,
            examples=[
                ExampleLink(
                    title=ex.title,
                    path=ex.path,
                    date=ex.date,
                    disabled=ex.disabled,
                    icon=ex.icon
                ) for ex in folder.examples
            ],
            icon=folder.icon
        )
    )
# ============================================================================
#  Serve
# ============================================================================
# serve()

# Run the app
if __name__ == "__main__":
    serve(port=8080)

