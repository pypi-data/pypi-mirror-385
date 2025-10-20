import inspect
import json
from typing import Any

from aiohttp import ClientResponse
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import ValidationError
from pydantic.alias_generators import to_camel


class FregClientError(BaseModel):
    """Request model upstream errors in FREG."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    code: str
    message: str
    upstream_status: int | None = None
    upstream_body: str | None = None
    row_index: int | None = None

    @classmethod
    def maybe_model_validate_json(
        self,
        obj: Any,
        *,
        strict: bool | None = None,
        context: Any | None = None,
        by_alias: bool | None = None,
        by_name: bool | None = None,
    ) -> "FregClientError | None":
        """Wrapper method to return None instead of throwing error on validation failure."""
        try:
            return super().model_validate_json(
                obj,
                strict=strict,
                context=context,
                by_alias=by_alias,
                by_name=by_name,
            )
        except ValidationError:
            return None


async def handle_response_error(
    response: ClientResponse, indices_original_df: list[int] | None = None
) -> None:
    """Report error messages in response object."""
    match response.status:
        case status if status in range(200, 300):
            pass

        case 400 if (
            (
                freg_client_error := FregClientError.maybe_model_validate_json(
                    await response.text(), by_alias=True
                )
            )
            is not None
            and freg_client_error.upstream_status == 400
            and freg_client_error.row_index is not None
            and freg_client_error.upstream_body is not None
        ):

            message_freg = json.loads(freg_client_error.upstream_body).get(
                "message", ""
            )

            if indices_original_df is not None:
                row_index_original_df = indices_original_df[freg_client_error.row_index]
                row_message = f"The error was encountered in this row index in original dataframe: {row_index_original_df}"
            else:
                row_message = "No 'index' column was found in the DataFrame, row index for the error cannot be found."

            message = inspect.cleandoc(
                f"""
            FREG API returned an error.
            Message from FREG API: \"{message_freg}\"
            {row_message}
            """
            )

            raise ValueError(message)

        case _:
            print(response.headers)
            print(await response.text())
            response.raise_for_status()
