import os

from pytest_cases import cases_data, CaseDataGetter

from lambda_functions.v1.functions.lpa_codes.app.api.code_generator import get_codes
from lambda_functions.v1.tests.code_generator import cases_get_codes


@cases_data(module=cases_get_codes)
def test_get_codes(case_data: CaseDataGetter):
    test_data, code, key, expected_result, expected_result_count = case_data.get()

    print(f"session token: {os.environ['AWS_SESSION_TOKEN']}")
    print(f"AWS_SECURITY_TOKEN: {os.environ['AWS_SECURITY_TOKEN']}")

    # Set up test data
    # table = boto3.resource("dynamodb", endpoint_url="http://localhost:8000").Table(
    #     "lpa_codes")

    # data = table.scan()
    # print(f"table: {data}")
    # for row in test_data:
    #     table.put_item(Item=row)

    # Run test function
    result = get_codes(code=code, key=key)

    # lpa = key["lpa"]
    # actor = key["actor"]
    # return_fields = "lpa, actor, code, active, last_updated_date"
    # result = table.query(
    #     IndexName="key_index",
    #     KeyConditionExpression=Key("lpa").eq(lpa) & Key("actor").eq(actor),
    #     # FilterExpression=Attr("actor").eq(actor),
    #     ProjectionExpression=return_fields,
    # )
    print(f"result: {result}")

    for row in result:

        assert isinstance(row["active"], bool)

    assert len(result) == expected_result_count

    # Tidy up test data
    # for row in test_data:
    #     table.delete_item(Key=row)
