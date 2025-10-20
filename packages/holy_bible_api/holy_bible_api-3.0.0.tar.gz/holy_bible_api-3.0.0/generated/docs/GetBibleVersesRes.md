# GetBibleVersesRes


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**verses** | [**List[BibleVerse]**](BibleVerse.md) |  | 

## Example

```python
from openapi_client.models.get_bible_verses_res import GetBibleVersesRes

# TODO update the JSON string below
json = "{}"
# create an instance of GetBibleVersesRes from a JSON string
get_bible_verses_res_instance = GetBibleVersesRes.from_json(json)
# print the JSON string representation of the object
print(GetBibleVersesRes.to_json())

# convert the object into a dict
get_bible_verses_res_dict = get_bible_verses_res_instance.to_dict()
# create an instance of GetBibleVersesRes from a dict
get_bible_verses_res_from_dict = GetBibleVersesRes.from_dict(get_bible_verses_res_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


