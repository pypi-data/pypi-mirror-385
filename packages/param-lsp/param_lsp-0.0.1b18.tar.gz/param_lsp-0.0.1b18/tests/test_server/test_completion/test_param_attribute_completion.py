"""Test param attribute access completion functionality."""

from __future__ import annotations

import pytest
from lsprotocol.types import CompletionItemKind, Position

from param_lsp.server import ParamLanguageServer


class TestParamAttributeCompletion:
    """Test param attribute access completion like P().param.x."""

    def test_param_attribute_completion_basic(self):
        """Test basic param attribute completion functionality."""
        server = ParamLanguageServer("test-server", "1.0.0")

        code_py = """\
import param

class P(param.Parameterized):
    x = param.Integer(default=1, doc="An integer parameter")
    y = param.String(default="hello", doc="A string parameter")

# Test param attribute completion
P().param."""

        # Simulate document analysis
        server._analyze_document("file:///test.py", code_py)

        # Test completion at end of P().param.
        position = Position(line=7, character=10)  # After "P().param."
        completions = server._get_param_attribute_completions(
            "file:///test.py", "P().param.", position.character
        )

        # Should have completions for both parameters and methods
        assert len(completions) == 5, (
            f"Expected 5 completions (3 methods + 2 parameters), got {len(completions)}"
        )

        completion_labels = [item.label for item in completions]
        assert "x" in completion_labels, "Should suggest 'x' parameter"
        assert "y" in completion_labels, "Should suggest 'y' parameter"
        assert "objects()" in completion_labels, "Should suggest 'objects()' method"
        assert "values()" in completion_labels, "Should suggest 'values()' method"
        assert "update()" in completion_labels, "Should suggest 'update()' method"

        # Check that documentation includes type information
        x_completion = next((c for c in completions if c.label == "x"), None)
        y_completion = next((c for c in completions if c.label == "y"), None)

        assert x_completion is not None, "Should have completion for x"
        assert y_completion is not None, "Should have completion for y"

        assert isinstance(x_completion.documentation, str), "Documentation should be a string"
        assert isinstance(y_completion.documentation, str), "Documentation should be a string"
        assert "Integer" in x_completion.documentation, "Should include parameter type for x"
        assert "String" in y_completion.documentation, "Should include parameter type for y"

    def test_param_attribute_completion_partial_typing(self):
        """Test param attribute completion with partial parameter typing."""
        server = ParamLanguageServer("test-server", "1.0.0")

        code_py = """\
import param

class P(param.Parameterized):
    x_value = param.Integer(default=1)
    y_value = param.String(default="hello")
    z_other = param.Boolean(default=True)

# Test partial typing
P().param.x"""

        # Simulate document analysis
        server._analyze_document("file:///test.py", code_py)

        # Test completion after partial typing "x"
        position = Position(line=8, character=11)  # After "P().param.x"
        completions = server._get_param_attribute_completions(
            "file:///test.py", "P().param.x", position.character
        )

        # Should only suggest parameter that starts with "x"
        assert len(completions) == 1, f"Expected 1 completion, got {len(completions)}"
        assert completions[0].label == "x_value", "Should suggest 'x_value' parameter"

    def test_param_attribute_completion_inheritance(self):
        """Test param attribute completion with inherited parameters."""
        server = ParamLanguageServer("test-server", "1.0.0")

        code_py = """\
import param

class Base(param.Parameterized):
    base_param = param.String(default="base")

class Child(Base):
    child_param = param.Integer(default=42)

# Test completion with inheritance
Child().param."""

        # Simulate document analysis
        server._analyze_document("file:///test.py", code_py)

        # Test completion for Child instance
        position = Position(line=9, character=14)  # After "Child().param."
        completions = server._get_param_attribute_completions(
            "file:///test.py", "Child().param.", position.character
        )

        # Should suggest both inherited and own parameters plus methods
        assert len(completions) == 5, (
            f"Expected 5 completions (3 methods + 2 parameters), got {len(completions)}"
        )

        completion_labels = [item.label for item in completions]
        assert "base_param" in completion_labels, "Should suggest inherited parameter"
        assert "child_param" in completion_labels, "Should suggest own parameter"
        assert "objects()" in completion_labels, "Should suggest 'objects()' method"
        assert "values()" in completion_labels, "Should suggest 'values()' method"
        assert "update()" in completion_labels, "Should suggest 'update()' method"

    def test_param_attribute_completion_constructor_call(self):
        """Test param attribute completion on constructor call result."""
        server = ParamLanguageServer("test-server", "1.0.0")

        code_py = """\
import param

class P(param.Parameterized):
    x = param.Integer(default=1, bounds=(0, 10))
    y = param.String(default="hello")

# Test completion on constructor call
P().param."""

        # Simulate document analysis
        server._analyze_document("file:///test.py", code_py)

        # Test completion after P().param.
        position = Position(line=7, character=10)  # After "P().param."
        completions = server._get_param_attribute_completions(
            "file:///test.py", "P().param.", position.character
        )

        # Should have completions for parameters and methods
        assert len(completions) == 5, (
            f"Expected 5 completions (3 methods + 2 parameters), got {len(completions)}"
        )

        completion_labels = [item.label for item in completions]
        assert "x" in completion_labels, "Should suggest 'x' parameter"
        assert "y" in completion_labels, "Should suggest 'y' parameter"
        assert "objects()" in completion_labels, "Should suggest 'objects()' method"
        assert "values()" in completion_labels, "Should suggest 'values()' method"
        assert "update()" in completion_labels, "Should suggest 'update()' method"

        # Check that documentation includes bounds for x
        x_completion = next((c for c in completions if c.label == "x"), None)
        assert x_completion is not None, "Should have completion for x"
        assert isinstance(x_completion.documentation, str), "Documentation should be a string"
        assert "Bounds: [0, 10]" in x_completion.documentation, "Should include bounds info for x"

    def test_param_attribute_completion_with_args(self):
        """Test param attribute completion on constructor with arguments."""
        server = ParamLanguageServer("test-server", "1.0.0")

        code_py = """\
import param

class P(param.Parameterized):
    x = param.Integer(default=1)
    y = param.String(default="hello")

# Test completion on constructor call with arguments
P(x=5).param."""

        # Simulate document analysis
        server._analyze_document("file:///test.py", code_py)

        # Test completion after P(x=5).param.
        position = Position(line=7, character=13)  # After "P(x=5).param."
        completions = server._get_param_attribute_completions(
            "file:///test.py", "P(x=5).param.", position.character
        )

        # Should have completions for all parameters and methods
        assert len(completions) == 5, (
            f"Expected 5 completions (3 methods + 2 parameters), got {len(completions)}"
        )

        completion_labels = [item.label for item in completions]
        assert "x" in completion_labels, "Should suggest 'x' parameter"
        assert "y" in completion_labels, "Should suggest 'y' parameter"
        assert "objects()" in completion_labels, "Should suggest 'objects()' method"
        assert "values()" in completion_labels, "Should suggest 'values()' method"
        assert "update()" in completion_labels, "Should suggest 'update()' method"

    def test_param_attribute_completion_external_class(self):
        """Test param attribute completion for external classes."""
        pytest.importorskip("holoviews")

        server = ParamLanguageServer("test-server", "1.0.0")

        code_py = """\
import holoviews as hv

# Test completion on external class
hv.Curve().param."""

        # Simulate document analysis
        server._analyze_document("file:///test.py", code_py)

        # Test completion after hv.Curve().param.
        position = Position(line=3, character=16)  # After "hv.Curve().param."
        completions = server._get_param_attribute_completions(
            "file:///test.py", "hv.Curve().param.", position.character
        )

        # Should have completions for hv.Curve parameters
        assert len(completions) > 0, "Should have completions for hv.Curve parameters"

        completion_labels = [item.label for item in completions]
        # HoloViews Curve should have parameters like 'label', 'group', etc.
        assert any("label" in label for label in completion_labels), (
            "Should suggest label parameter for hv.Curve"
        )

    def test_param_attribute_completion_no_match(self):
        """Test that no completions are returned when not in param attribute context."""
        server = ParamLanguageServer("test-server", "1.0.0")

        code_py = """\
import param

class P(param.Parameterized):
    x = param.Integer(default=1)

# Not in param attribute context
obj = P()
obj."""

        # Simulate document analysis
        server._analyze_document("file:///test.py", code_py)

        # Test completion after just "obj."
        position = Position(line=7, character=4)  # After "obj."
        completions = server._get_param_attribute_completions(
            "file:///test.py", "obj.", position.character
        )

        # Should not have any completions
        assert len(completions) == 0, f"Expected 0 completions, got {len(completions)}"

    def test_param_attribute_completion_unknown_class(self):
        """Test param attribute completion for unknown class."""
        server = ParamLanguageServer("test-server", "1.0.0")

        code_py = """\
# Unknown class
UnknownClass().param."""

        # Simulate document analysis
        server._analyze_document("file:///test.py", code_py)

        # Test completion for unknown class
        position = Position(line=1, character=21)  # After "UnknownClass().param."
        completions = server._get_param_attribute_completions(
            "file:///test.py", "UnknownClass().param.", position.character
        )

        # Should not have any completions for unknown class
        assert len(completions) == 0, f"Expected 0 completions, got {len(completions)}"

    def test_param_attribute_completion_with_defaults_and_bounds(self):
        """Test that completion includes default values and bounds in documentation."""
        server = ParamLanguageServer("test-server", "1.0.0")

        code_py = """\
import param

class P(param.Parameterized):
    x = param.Integer(default=5, bounds=(0, 10), doc="An integer with bounds")
    y = param.Number(default=1.5, bounds=(0.0, 5.0), inclusive_bounds=(False, True))
    z = param.String(default="test", allow_None=True, doc="A string parameter")

# Test completion
P().param."""

        # Simulate document analysis
        server._analyze_document("file:///test.py", code_py)

        # Test completion
        position = Position(line=7, character=10)  # After "P().param."
        completions = server._get_param_attribute_completions(
            "file:///test.py", "P().param.", position.character
        )

        # Should have completions for all parameters and methods
        assert len(completions) == 6, (
            f"Expected 6 completions (3 methods + 3 parameters), got {len(completions)}"
        )

        # Check specific parameter documentation
        x_completion = next((c for c in completions if c.label == "x"), None)
        y_completion = next((c for c in completions if c.label == "y"), None)
        z_completion = next((c for c in completions if c.label == "z"), None)

        assert x_completion is not None, "Should have completion for x"
        assert y_completion is not None, "Should have completion for y"
        assert z_completion is not None, "Should have completion for z"

        # Check x documentation
        assert isinstance(x_completion.documentation, str), "Documentation should be a string"
        assert "Type: Integer" in x_completion.documentation, "Should include type info for x"
        assert "Bounds: [0, 10]" in x_completion.documentation, "Should include bounds info for x"
        assert "Default: 5" in x_completion.documentation, "Should include default value for x"
        assert "An integer with bounds" in x_completion.documentation, (
            "Should include description for x"
        )

        # Check y documentation (different bounds format)
        assert isinstance(y_completion.documentation, str), "Documentation should be a string"
        assert "Bounds: (0.0, 5.0]" in y_completion.documentation, (
            "Should include bounds info for y"
        )
        assert "Default: 1.5" in y_completion.documentation, "Should include default value for y"

        # Check z documentation (allow_None)
        assert isinstance(z_completion.documentation, str), "Documentation should be a string"
        assert "Allows None" in z_completion.documentation, "Should include allow_None info for z"
        assert "A string parameter" in z_completion.documentation, (
            "Should include description for z"
        )

    def test_param_attribute_completion_methods(self):
        """Test param attribute completion includes objects() and values() methods."""
        server = ParamLanguageServer("test-server", "1.0.0")

        code_py = """\
import param

class P(param.Parameterized):
    x = param.Integer(default=1)
    y = param.String(default="hello")

# Test param method completion
P().param."""

        # Simulate document analysis
        server._analyze_document("file:///test.py", code_py)

        # Test completion at end of P().param.
        position = Position(line=7, character=10)  # After "P().param."
        completions = server._get_param_attribute_completions(
            "file:///test.py", "P().param.", position.character
        )

        # Should have completions for both parameters and methods
        assert len(completions) == 5, (
            f"Expected 5 completions (3 methods + 2 parameters), got {len(completions)}"
        )

        completion_labels = [item.label for item in completions]

        # Check that methods are included
        assert "objects()" in completion_labels, "Should suggest 'objects()' method"
        assert "values()" in completion_labels, "Should suggest 'values()' method"
        assert "update()" in completion_labels, "Should suggest 'update()' method"

        # Check that parameters are still included
        assert "x" in completion_labels, "Should suggest 'x' parameter"
        assert "y" in completion_labels, "Should suggest 'y' parameter"

        # Check method completions details
        objects_completion = next((c for c in completions if c.label == "objects()"), None)
        values_completion = next((c for c in completions if c.label == "values()"), None)
        update_completion = next((c for c in completions if c.label == "update()"), None)

        assert objects_completion is not None, "Should have completion for objects()"
        assert values_completion is not None, "Should have completion for values()"
        assert update_completion is not None, "Should have completion for update()"

        assert objects_completion.kind == CompletionItemKind.Method, "objects() should be a method"
        assert values_completion.kind == CompletionItemKind.Method, "values() should be a method"
        assert update_completion.kind == CompletionItemKind.Method, "update() should be a method"

        assert isinstance(objects_completion.documentation, str), (
            "Documentation should be a string"
        )
        assert isinstance(values_completion.documentation, str), "Documentation should be a string"
        assert isinstance(update_completion.documentation, str), "Documentation should be a string"

        assert (
            "dictionary of (parameter_name, parameter_object)" in objects_completion.documentation
        )
        assert "iterator of parameter values" in values_completion.documentation
        assert "Update multiple parameters at once" in update_completion.documentation

    def test_param_attribute_completion_method_filtering(self):
        """Test that method completions are filtered based on partial text."""
        server = ParamLanguageServer("test-server", "1.0.0")

        code_py = """\
import param

class P(param.Parameterized):
    x = param.Integer(default=1)

# Test partial method completion
P().param.o"""

        # Simulate document analysis
        server._analyze_document("file:///test.py", code_py)

        # Test completion after partial typing "o"
        position = Position(line=6, character=11)  # After "P().param.o"
        completions = server._get_param_attribute_completions(
            "file:///test.py", "P().param.o", position.character
        )

        # Should only suggest objects() method (starts with "o")
        assert len(completions) == 1, f"Expected 1 completion, got {len(completions)}"
        assert completions[0].label == "objects()", "Should suggest 'objects()' method"

    def test_param_attribute_completion_values_filtering(self):
        """Test that values() method completion is filtered based on partial text."""
        server = ParamLanguageServer("test-server", "1.0.0")

        code_py = """\
import param

class P(param.Parameterized):
    x = param.Integer(default=1)

# Test partial method completion
P().param.v"""

        # Simulate document analysis
        server._analyze_document("file:///test.py", code_py)

        # Test completion after partial typing "v"
        position = Position(line=6, character=11)  # After "P().param.v"
        completions = server._get_param_attribute_completions(
            "file:///test.py", "P().param.v", position.character
        )

        # Should only suggest values() method (starts with "v")
        assert len(completions) == 1, f"Expected 1 completion, got {len(completions)}"
        assert completions[0].label == "values()", "Should suggest 'values()' method"
