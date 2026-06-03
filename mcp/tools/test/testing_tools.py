from models.testing_model import SumNumbersRequest, SumResponse
from register import register_tool


@register_tool(
    name="sum_numbers",
    description="Add two numbers together",
    input_schema=SumNumbersRequest.model_json_schema(),
    output_schema=SumResponse.model_json_schema(),
)
async def sum_numbers_tool(**kwargs):
    request = SumNumbersRequest(**kwargs)

    response = SumResponse(
        operation="sum",
        a=request.a,
        b=request.b,
        result=request.a + request.b,
    )

    return response.model_dump()
