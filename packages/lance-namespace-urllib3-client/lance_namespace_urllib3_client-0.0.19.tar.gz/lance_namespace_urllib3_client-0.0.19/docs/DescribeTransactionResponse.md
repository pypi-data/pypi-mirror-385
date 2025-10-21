# DescribeTransactionResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**TransactionStatus**](TransactionStatus.md) |  | 
**properties** | **Dict[str, str]** |  | [optional] 

## Example

```python
from lance_namespace_urllib3_client.models.describe_transaction_response import DescribeTransactionResponse

# TODO update the JSON string below
json = "{}"
# create an instance of DescribeTransactionResponse from a JSON string
describe_transaction_response_instance = DescribeTransactionResponse.from_json(json)
# print the JSON string representation of the object
print(DescribeTransactionResponse.to_json())

# convert the object into a dict
describe_transaction_response_dict = describe_transaction_response_instance.to_dict()
# create an instance of DescribeTransactionResponse from a dict
describe_transaction_response_from_dict = DescribeTransactionResponse.from_dict(describe_transaction_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


