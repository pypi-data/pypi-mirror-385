"""Flow-specific document base class for persistent pipeline data.

@public

This module provides the FlowDocument abstract base class for documents
that need to persist across Prefect flow runs and between pipeline steps.
"""

from typing import Literal, final

from .document import Document


class FlowDocument(Document):
    """Abstract base class for documents that persist across flow runs.

    @public

    FlowDocument is used for data that needs to be saved between pipeline
    steps and across multiple flow executions. These documents are typically
    written to the file system using the simple_runner utilities.

    Key characteristics:
    - Persisted to file system between pipeline steps
    - Survives across multiple flow runs
    - Used for flow inputs and outputs
    - Saved in directories organized by the document's type/name

    Creating FlowDocuments:
        Same as Document - use `create()` for automatic conversion, `__init__` for bytes.
        See Document.create() for detailed usage examples.

    Persistence:
        Documents are saved under an output directory path associated with the document's type/name.
        For example: output/my_doc/data.json

    Note:
        - Cannot instantiate FlowDocument directly - must subclass
        - Used with FlowConfig to define flow input/output types
        - No additional abstract methods to implement
    """

    def __init__(
        self,
        *,
        name: str,
        content: bytes,
        description: str | None = None,
        sources: list[str] | None = None,
    ) -> None:
        """Initialize a FlowDocument with raw bytes content.

        See Document.__init__() for parameter details and usage notes.

        Prevents direct instantiation of the abstract FlowDocument class.
        FlowDocument must be subclassed for specific document types.

        Args:
            name: Document filename (required, keyword-only)
            content: Document content as raw bytes (required, keyword-only)
            description: Optional human-readable description (keyword-only)
            sources: Optional list of strings for provenance tracking

        Raises:
            TypeError: If attempting to instantiate FlowDocument directly
                      instead of using a concrete subclass.

        Example:
            >>> from enum import StrEnum
            >>>
            >>> # Simple subclass:
            >>> class MyFlowDoc(FlowDocument):
            ...     pass
            >>>
            >>> # With FILES restriction:
            >>> class RestrictedDoc(FlowDocument):
            ...     class FILES(StrEnum):
            ...         DATA = "data.json"
            ...         METADATA = "metadata.yaml"
            >>>
            >>> # Direct constructor - only for bytes:
            >>> doc = MyFlowDoc(name="test.bin", content=b"raw data")
            >>>
            >>> # RECOMMENDED - use create for automatic conversion:
            >>> doc = RestrictedDoc.create(name="data.json", content={"key": "value"})
            >>> # This would raise DocumentNameError:
            >>> # doc = RestrictedDoc.create(name="other.json", content={})
        """
        if type(self) is FlowDocument:
            raise TypeError("Cannot instantiate abstract FlowDocument class directly")

        # Only pass sources if not None to let Pydantic's default_factory handle it
        if sources is not None:
            super().__init__(name=name, content=content, description=description, sources=sources)
        else:
            super().__init__(name=name, content=content, description=description)

    @final
    def get_base_type(self) -> Literal["flow"]:
        """Return the base type identifier for flow documents.

        This method is final and cannot be overridden by subclasses.
        It identifies this document as a flow-persistent document.

        Returns:
            "flow" - Indicates this document persists across flow runs.

        Note:
            This determines the document's lifecycle and persistence behavior
            in the pipeline system.
        """
        return "flow"
