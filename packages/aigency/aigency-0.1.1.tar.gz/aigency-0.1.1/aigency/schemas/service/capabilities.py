"""Service capability configuration schema.

This module defines the Capabilities Pydantic model for configuring service
capabilities within the Aigency framework. It provides structured configuration
for defining what capabilities a service or agent can provide to other components
in the system.

The capabilities configuration helps establish service contracts and enables
proper service discovery and integration within the distributed agent ecosystem.

Example:
    Configuring service capabilities:

    >>> capabilities = Capabilities(
    ...     streaming=True
    ... )

Attributes:
    None: This module contains only Pydantic model definitions.
"""

from pydantic import BaseModel


class Capabilities(BaseModel):
    """Technical capabilities of the agent service.

    Attributes:
        streaming (bool): Whether the agent supports streaming responses.
    """

    streaming: bool
