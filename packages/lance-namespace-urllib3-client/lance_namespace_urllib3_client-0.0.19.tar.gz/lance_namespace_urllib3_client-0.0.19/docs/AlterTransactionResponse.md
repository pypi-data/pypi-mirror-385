# AlterTransactionResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**TransactionStatus**](TransactionStatus.md) |  | 
**properties** | **Dict[str, str]** |  | [optional] 

## Example

```python
from lance_namespace_urllib3_client.models.alter_transaction_response import AlterTransactionResponse

# TODO update the JSON string below
json = "{}"
# create an instance of AlterTransactionResponse from a JSON string
alter_transaction_response_instance = AlterTransactionResponse.from_json(json)
# print the JSON string representation of the object
print(AlterTransactionResponse.to_json())

# convert the object into a dict
alter_transaction_response_dict = alter_transaction_response_instance.to_dict()
# create an instance of AlterTransactionResponse from a dict
alter_transaction_response_from_dict = AlterTransactionResponse.from_dict(alter_transaction_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


