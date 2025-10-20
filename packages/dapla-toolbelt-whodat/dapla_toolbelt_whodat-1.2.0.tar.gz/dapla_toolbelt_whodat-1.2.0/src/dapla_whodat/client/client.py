"""Module that implements a client abstraction that makes it easy to communicate with the Dapla Pseudo Service REST API."""

import asyncio
import os
import typing as t
import zlib

import google.auth.transport.requests
import google.oauth2.id_token
from aiohttp import ClientPayloadError
from aiohttp import ClientSession
from aiohttp import ClientTimeout
from aiohttp import ServerDisconnectedError
from aiohttp import TCPConnector
from aiohttp_retry import ExponentialRetry
from aiohttp_retry import RetryClient
from dapla_auth_client import AuthClient
from ulid import ULID

from dapla_whodat.client.response_errors import handle_response_error
from dapla_whodat.constants import Env
from dapla_whodat.model import WhodatRequest
from dapla_whodat.model import WhodatResponse


class WhodatClient:
    """Client for interacting with the Dapla Pseudo Service REST API."""

    def __init__(
        self,
        whodat_service_url: str | None = None,
        auth_token: str | None = None,
    ) -> None:
        """Constructor for WhodatClient.

        Args:
            whodat_service_url (str | None, optional): Base URL for Whodat Service
            auth_token (str | None, optional): Static auth token
        """
        self.whodat_service_url = whodat_service_url
        self.static_auth_token = auth_token

    def __auth_token(self) -> str:
        if os.environ.get("DAPLA_REGION") == "CLOUD_RUN":
            audience = os.environ["WHODAT_SERVICE_URL"]
            auth_req = google.auth.transport.requests.Request()  # type: ignore[no-untyped-call]
            token = t.cast(
                str,
                google.oauth2.id_token.fetch_id_token(auth_req, audience),  # type: ignore[no-untyped-call]
            )
            return token
        else:
            return (
                str(AuthClient.fetch_personal_token())
                if self.static_auth_token is None
                else str(self.static_auth_token)
            )

    async def post_to_field_endpoint(
        self,
        path: str,
        timeout: float,
        whodat_requests: list[WhodatRequest],
        indices_original_df: list[int] | None = None,
    ) -> list[WhodatResponse]:
        """Post a request to the Pseudo Service field endpoint.

        Args:
            path (str): Full URL to the endpoint
            timeout (float): Request timeout
            whodat_requests: list[list[WhodatRequest]] Whodat requests, with each inner list representing the requests for a single row.
            indices_original_df: list[int] | None = None: Indices from the original DataFrame, if available.

        Returns:
            list[tuple[WhodatResponse, int]]: A list of tuple of (field_name, data, metadata)
        """

        async def _post(
            client: RetryClient,
            path: str,
            timeout: ClientTimeout,
            request: WhodatRequest,
            correlation_id: str,
            indices_original_df: list[int] | None = None,
        ) -> WhodatResponse:
            data = zlib.compress(request.model_dump_json(by_alias=True).encode("utf-8"))
            async with client.post(
                url=f"{self.whodat_service_url}/{path}",
                headers={
                    "Authorization": f"Bearer {self.__auth_token()}",
                    "Content-Type": "application/json",
                    "Content-Encoding": "deflate",
                    "X-Correlation-Id": correlation_id,
                },
                data=data,
                timeout=timeout,
            ) as response:
                await handle_response_error(response, indices_original_df)
                response_json = await response.json()
                responses = [r.get("foedselsEllerDNummer", []) for r in response_json]

            return WhodatResponse.model_validate({"found_personal_ids": responses})

        total_timeout = ClientTimeout(
            total=None,
            connect=3.0,
            sock_read=timeout,
            sock_connect=3.0,
        )

        per_request_timeout = ClientTimeout(
            total=None,
            connect=3.0,
            sock_read=timeout * 0.95,
            sock_connect=3.0,
        )

        aio_session = ClientSession(
            connector=TCPConnector(limit=50),
            timeout=total_timeout,
        )

        async with RetryClient(
            client_session=aio_session,
            retry_options=ExponentialRetry(
                attempts=3,
                start_timeout=0.1,
                max_timeout=30,
                factor=3,
                statuses={429}.union(
                    set(range(500, 600))
                ),  # Retry all 5xx errors and 429 Too Many Requests
                exceptions={
                    ClientPayloadError,
                    ServerDisconnectedError,
                    asyncio.TimeoutError,
                    OSError,
                },
            ),
        ) as client:
            results = await asyncio.gather(
                *[
                    _post(
                        client=client,
                        path=path,
                        timeout=per_request_timeout,
                        request=reqs,
                        correlation_id=WhodatClient._generate_new_correlation_id(),
                        indices_original_df=indices_original_df,
                    )
                    for reqs in whodat_requests
                ]
            )

        await asyncio.sleep(0.5)  # Allow time for sockets to close
        await aio_session.close()

        return results

    @staticmethod
    def _generate_new_correlation_id() -> str:
        return str(ULID())


def _client() -> WhodatClient:
    return WhodatClient(
        whodat_service_url=os.getenv(Env.WHODAT_SERVICE_URL),
        auth_token=os.getenv(Env.WHODAT_SERVICE_AUTH_TOKEN),
    )
