import inspect  
import os  
from typing import Any, Type  
from markdown import markdown  
from graphviz import Digraph

class APIDocumentationGenerator:  
    """Generates API documentation from docstrings and type hints."""

    def \_\_init\_\_(self, module: Any):  
        self.module \= module

    def generate\_markdown(self) \-\> str:  
        """Generates Markdown documentation for the module."""  
        markdown\_doc \= "\# API Documentation\\n\\n"  
        for name, obj in inspect.getmembers(self.module):  
            if inspect.isfunction(obj) or inspect.isclass(obj):  
                markdown\_doc \+= self.\_document\_object(name, obj)  
        return markdown\_doc

    def generate\_html(self) \-\> str:  
        """Generates HTML documentation from Markdown."""  
        markdown\_doc \= self.generate\_markdown()  
        return markdown(markdown\_doc)

    def generate\_integration\_diagram(self, output\_path: str \= "integration\_diagram.gv") \-\> None:  
        """Generates a module integration diagram using Graphviz."""  
        graph \= Digraph(comment="Module Integration Diagram")  
        for name, obj in inspect.getmembers(self.module):  
            if inspect.isclass(obj):  
                graph.node(name, label=name)  
                for base in obj.\_\_bases\_\_:  
                    graph.edge(base.\_\_name\_\_, name)  
        graph.render(output\_path, format="png", cleanup=True)

    def \_document\_object(self, name: str, obj: Any) \-\> str:  
        """Generates documentation for a single object."""  
        doc \= f"\#\# {name}\\n\\n"  
        if obj.\_\_doc\_\_:  
            doc \+= f"{obj.\_\_doc\_\_}\\n\\n"  
        if inspect.isfunction(obj):  
            doc \+= self.\_document\_function(obj)  
        elif inspect.isclass(obj):  
            doc \+= self.\_document\_class(obj)  
        return doc

    def \_document\_function(self, func: Any) \-\> str:  
        """Generates documentation for a function."""  
        doc \= "\#\#\# Function Signature\\n\\n"  
        doc \+= f"\`\`\`python\\n{inspect.signature(func)}\\n\`\`\`\\n\\n"  
        return doc

    def \_document\_class(self, cls: Type) \-\> str:  
        """Generates documentation for a class."""  
        doc \= "\#\#\# Methods\\n\\n"  
        for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):  
            doc \+= self.\_document\_object(name, method)  
        return doc

\# Unit tests  
def test\_generate\_markdown():  
    """Test Markdown generation."""  
    import example\_module  \# Replace with an actual module  
    generator \= APIDocumentationGenerator(example\_module)  
    markdown\_doc \= generator.generate\_markdown()  
    assert "\# API Documentation" in markdown\_doc, "Markdown header missing."

def test\_generate\_html():  
    """Test HTML generation."""  
    import example\_module  \# Replace with an actual module  
    generator \= APIDocumentationGenerator(example\_module)  
    html\_doc \= generator.generate\_html()  
    assert "\<h1\>API Documentation\</h1\>" in html\_doc, "HTML header missing."

def test\_generate\_integration\_diagram():  
    """Test integration diagram generation."""  
    import example\_module  \# Replace with an actual module  
    generator \= APIDocumentationGenerator(example\_module)  
    output\_path \= "test\_diagram.gv"  
    generator.generate\_integration\_diagram(output\_path)  
    assert os.path.exists(output\_path \+ ".png"), "Integration diagram not generated."

if \_\_name\_\_ \== "\_\_main\_\_":  
    test\_generate\_markdown()  
    test\_generate\_html()  
    test\_generate\_integration\_diagram()  
    print("All tests passed.")

