from httpx import AsyncClient
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

# Create a single async client instance for use across
# the SDK.
# Each instance creates its own connection pool, so it's best
# to re-use them if possible.
# See: https://www.python-httpx.org/async/#opening-and-closing-clients
async_client = AsyncClient()

# We manually instrument this specific client, so traces
# get propagated for our client, but not any the user may create.
HTTPXClientInstrumentor.instrument_client(async_client)
