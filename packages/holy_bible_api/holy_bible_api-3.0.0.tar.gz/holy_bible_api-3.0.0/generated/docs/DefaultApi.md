# openapi_client.DefaultApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_audio_bible_books**](DefaultApi.md#get_audio_bible_books) | **GET** /audio_bibles/{audio_bible_id}/books | 
[**get_audio_bible_chapters**](DefaultApi.md#get_audio_bible_chapters) | **GET** /audio_bibles/{audio_bible_id}/books/{book_num}/chapters | 
[**get_audio_bibles**](DefaultApi.md#get_audio_bibles) | **GET** /audio_bibles | 
[**get_audio_chapter**](DefaultApi.md#get_audio_chapter) | **GET** /audio_bibles/{audio_bible_id}/books/{book_num}/chapters/{chapter_num} | 
[**get_bible_books**](DefaultApi.md#get_bible_books) | **GET** /bibles/{bible_id}/books | 
[**get_bible_chapters**](DefaultApi.md#get_bible_chapters) | **GET** /bibles/{bible_id}/books/{book_num}/chapters | 
[**get_bible_verse_by_number**](DefaultApi.md#get_bible_verse_by_number) | **GET** /bibles/{bible_id}/books/{book_num}/chapters/{chapter_num}/verses/{verse_num} | 
[**get_bible_verses**](DefaultApi.md#get_bible_verses) | **GET** /bibles/{bible_id}/books/{book_num}/chapters/{chapter_num}/verses | 
[**get_bibles**](DefaultApi.md#get_bibles) | **GET** /bibles | 
[**get_health**](DefaultApi.md#get_health) | **GET** /health | 


# **get_audio_bible_books**
> GetAudioBooksRes get_audio_bible_books(audio_bible_id)

### Example


```python
import openapi_client
from openapi_client.models.get_audio_books_res import GetAudioBooksRes
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)
    audio_bible_id = 56 # int | 

    try:
        api_response = api_instance.get_audio_bible_books(audio_bible_id)
        print("The response of DefaultApi->get_audio_bible_books:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_audio_bible_books: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **audio_bible_id** | **int**|  | 

### Return type

[**GetAudioBooksRes**](GetAudioBooksRes.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_audio_bible_chapters**
> GetAudioChaptersRes get_audio_bible_chapters(audio_bible_id, book_num)

### Example


```python
import openapi_client
from openapi_client.models.get_audio_chapters_res import GetAudioChaptersRes
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)
    audio_bible_id = 56 # int | 
    book_num = 56 # int | 

    try:
        api_response = api_instance.get_audio_bible_chapters(audio_bible_id, book_num)
        print("The response of DefaultApi->get_audio_bible_chapters:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_audio_bible_chapters: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **audio_bible_id** | **int**|  | 
 **book_num** | **int**|  | 

### Return type

[**GetAudioChaptersRes**](GetAudioChaptersRes.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_audio_bibles**
> GetAudioBiblesRes get_audio_bibles(language=language, version=version)

### Example


```python
import openapi_client
from openapi_client.models.get_audio_bibles_res import GetAudioBiblesRes
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)
    language = 'language_example' # str |  (optional)
    version = 'version_example' # str |  (optional)

    try:
        api_response = api_instance.get_audio_bibles(language=language, version=version)
        print("The response of DefaultApi->get_audio_bibles:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_audio_bibles: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **language** | **str**|  | [optional] 
 **version** | **str**|  | [optional] 

### Return type

[**GetAudioBiblesRes**](GetAudioBiblesRes.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_audio_chapter**
> get_audio_chapter(audio_bible_id, book_num, chapter_num)

### Example


```python
import openapi_client
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)
    audio_bible_id = 56 # int | 
    book_num = 56 # int | 
    chapter_num = 56 # int | 

    try:
        api_instance.get_audio_chapter(audio_bible_id, book_num, chapter_num)
    except Exception as e:
        print("Exception when calling DefaultApi->get_audio_chapter: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **audio_bible_id** | **int**|  | 
 **book_num** | **int**|  | 
 **chapter_num** | **int**|  | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: audio/mpeg, text/plain

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Returns the audio chapter file |  -  |
**404** | Audio Chapter not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_bible_books**
> GetBibleBooksRes get_bible_books(bible_id)

### Example


```python
import openapi_client
from openapi_client.models.get_bible_books_res import GetBibleBooksRes
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)
    bible_id = 56 # int | 

    try:
        api_response = api_instance.get_bible_books(bible_id)
        print("The response of DefaultApi->get_bible_books:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_bible_books: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **bible_id** | **int**|  | 

### Return type

[**GetBibleBooksRes**](GetBibleBooksRes.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_bible_chapters**
> GetBibleChaptersRes get_bible_chapters(bible_id, book_num)

### Example


```python
import openapi_client
from openapi_client.models.get_bible_chapters_res import GetBibleChaptersRes
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)
    bible_id = 56 # int | 
    book_num = 56 # int | 

    try:
        api_response = api_instance.get_bible_chapters(bible_id, book_num)
        print("The response of DefaultApi->get_bible_chapters:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_bible_chapters: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **bible_id** | **int**|  | 
 **book_num** | **int**|  | 

### Return type

[**GetBibleChaptersRes**](GetBibleChaptersRes.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_bible_verse_by_number**
> BibleVerse get_bible_verse_by_number(bible_id, book_num, chapter_num, verse_num)

### Example


```python
import openapi_client
from openapi_client.models.bible_verse import BibleVerse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)
    bible_id = 56 # int | 
    book_num = 56 # int | 
    chapter_num = 56 # int | 
    verse_num = 56 # int | 

    try:
        api_response = api_instance.get_bible_verse_by_number(bible_id, book_num, chapter_num, verse_num)
        print("The response of DefaultApi->get_bible_verse_by_number:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_bible_verse_by_number: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **bible_id** | **int**|  | 
 **book_num** | **int**|  | 
 **chapter_num** | **int**|  | 
 **verse_num** | **int**|  | 

### Return type

[**BibleVerse**](BibleVerse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_bible_verses**
> GetBibleVersesRes get_bible_verses(bible_id, book_num, chapter_num, start=start, end=end)

### Example


```python
import openapi_client
from openapi_client.models.get_bible_verses_res import GetBibleVersesRes
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)
    bible_id = 56 # int | 
    book_num = 56 # int | 
    chapter_num = 56 # int | 
    start = 56 # int |  (optional)
    end = 56 # int |  (optional)

    try:
        api_response = api_instance.get_bible_verses(bible_id, book_num, chapter_num, start=start, end=end)
        print("The response of DefaultApi->get_bible_verses:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_bible_verses: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **bible_id** | **int**|  | 
 **book_num** | **int**|  | 
 **chapter_num** | **int**|  | 
 **start** | **int**|  | [optional] 
 **end** | **int**|  | [optional] 

### Return type

[**GetBibleVersesRes**](GetBibleVersesRes.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_bibles**
> GetBiblesRes get_bibles(language=language, version=version)

### Example


```python
import openapi_client
from openapi_client.models.get_bibles_res import GetBiblesRes
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)
    language = 'language_example' # str |  (optional)
    version = 'version_example' # str |  (optional)

    try:
        api_response = api_instance.get_bibles(language=language, version=version)
        print("The response of DefaultApi->get_bibles:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_bibles: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **language** | **str**|  | [optional] 
 **version** | **str**|  | [optional] 

### Return type

[**GetBiblesRes**](GetBiblesRes.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_health**
> str get_health()

### Example


```python
import openapi_client
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)

    try:
        api_response = api_instance.get_health()
        print("The response of DefaultApi->get_health:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_health: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

**str**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/plain

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

