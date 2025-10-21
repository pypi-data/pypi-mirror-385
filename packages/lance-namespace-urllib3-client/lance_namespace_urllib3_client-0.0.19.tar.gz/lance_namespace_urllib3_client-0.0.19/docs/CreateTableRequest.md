# CreateTableRequest

Request for creating a table, excluding the Arrow IPC stream. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **List[str]** |  | [optional] 
**location** | **str** |  | [optional] 
**mode** | **str** | There are three modes when trying to create a table, to differentiate the behavior when a table of the same name already exists:   * create: the operation fails with 409.   * exist_ok: the operation succeeds and the existing table is kept.   * overwrite: the existing table is dropped and a new table with this name is created.  | [optional] 
**properties** | **Dict[str, str]** |  | [optional] 

## Example

```python
from lance_namespace_urllib3_client.models.create_table_request import CreateTableRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateTableRequest from a JSON string
create_table_request_instance = CreateTableRequest.from_json(json)
# print the JSON string representation of the object
print(CreateTableRequest.to_json())

# convert the object into a dict
create_table_request_dict = create_table_request_instance.to_dict()
# create an instance of CreateTableRequest from a dict
create_table_request_from_dict = CreateTableRequest.from_dict(create_table_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


