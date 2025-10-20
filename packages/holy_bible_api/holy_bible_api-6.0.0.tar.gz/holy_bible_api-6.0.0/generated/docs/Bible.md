# Bible


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**bible_id** | **int** |  | 
**language** | **str** |  | 
**version** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.bible import Bible

# TODO update the JSON string below
json = "{}"
# create an instance of Bible from a JSON string
bible_instance = Bible.from_json(json)
# print the JSON string representation of the object
print(Bible.to_json())

# convert the object into a dict
bible_dict = bible_instance.to_dict()
# create an instance of Bible from a dict
bible_from_dict = Bible.from_dict(bible_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


