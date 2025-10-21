#
# (c) Copyright Ascensio System SIA 2025
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#



from setuptools import setup, find_packages  # noqa: H301

# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools
NAME = "docspace_api_sdk"
VERSION = "3.5.0"
PYTHON_REQUIRES = ">= 3.9"
REQUIRES = [
    "urllib3 >= 2.1.0, < 3.0.0",
    "python-dateutil >= 2.8.2",
    "pydantic >= 2",
    "typing-extensions >= 4.7.1",
]

setup(
    name=NAME,
    version=VERSION,
    description="A simple Python SDK for integrating with the ONLYOFFICE DocSpace API",
    author="Ascensio System SIA <integration@onlyoffice.com> (https://www.onlyoffice.com)",
    author_email="support@onlyoffice.com",
    url="https://github.com/ONLYOFFICE/docspace-api-sdk-python",
    keywords=["onlyoffice", 'docspace', "sdk"],
    install_requires=REQUIRES,
    packages=find_packages(exclude=["test", "tests"]),
    include_package_data=True,
    license="Apache-2.0",
    long_description_content_type='text/markdown',
    long_description="""\
    The ONLYOFFICE DocSpace SDK for Python is a library that provides tools for integrating and managing DocSpace features within your applications. It simplifies interaction with the DocSpace API by offering ready-to-use methods and models.
    """,  # noqa: E501
    package_data={"docspace_api_sdk": ["py.typed"]},
)