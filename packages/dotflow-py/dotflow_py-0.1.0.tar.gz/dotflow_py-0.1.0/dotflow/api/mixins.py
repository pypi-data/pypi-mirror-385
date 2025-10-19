from .pythonic import PythonicAPI
from .dsl import TextualDSL
from ..core.interpreter import DotInterpreter


# Mixin for DotInterpreter
class PythonicAPIMixin:
    """Mixin to add Pythonic API methods to DotInterpreter."""

    @property
    def py(self) -> PythonicAPI:
        """Access Pythonic API methods."""
        return PythonicAPI(self)


# Mixin for DotInterpreter
class TextualDSLMixin:
    """Mixin to add textual DSL methods to DotInterpreter."""

    @property
    def dsl(self) -> TextualDSL:
        """Access textual DSL parser."""
        return TextualDSL(self)

    def parse_dsl(self, dsl_text: str) -> "DotInterpreter":
        """Parse DSL text (convenience method)."""
        return self.dsl.parse_dsl(dsl_text)
