import os

from square_commons import get_api_output_in_standard_format
from square_commons.api_utils import make_request_json_output, make_request

"""
get_api_output_in_standard_format
"""
output = get_api_output_in_standard_format(
    data=[1, 2, 3], message="Data fetched successfully!", log={"time_taken": 23.563}
)
print(output)

"""
make_request_json_output
"""

file_content = b"Sample file content"
file_name = "example.txt"

with open(file_name, "wb") as file:
    file.write(file_content)

try:
    with open(file_name, "rb") as file:
        files = {"file": file}
        result = make_request_json_output(
            method="POST", base_url="https://httpbin.org", endpoint="post", files=files
        )
        print("API response:", result)
except Exception as e:
    print("Error occurred:", e)
finally:
    if os.path.exists(file_name):
        os.remove(file_name)

"""
make_request
"""

file_content = b"Sample file content"
file_name = "example.txt"

with open(file_name, "wb") as file:
    file.write(file_content)

try:
    with open(file_name, "rb") as file:
        files = {"file": file}
        result = make_request(
            method="POST",
            url="https://httpbin.org",
            endpoint="post",
            files=files,
            return_type="json",
        )
        print("API response:", result)
except Exception as e:
    print("Error occurred:", e)
finally:
    if os.path.exists(file_name):
        os.remove(file_name)
