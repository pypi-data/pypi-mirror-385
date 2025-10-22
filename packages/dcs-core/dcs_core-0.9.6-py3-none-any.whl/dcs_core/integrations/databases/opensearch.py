#  Copyright 2022-present, the Waterdip Labs Pvt. Ltd.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
from typing import Dict

from opensearchpy import OpenSearch

from dcs_core.core.common.errors import DataChecksDataSourcesConnectionError
from dcs_core.core.datasource.search_datasource import SearchIndexDataSource


class OpenSearchDataSource(SearchIndexDataSource):
    """
    OpenSearch data source
    """

    def __init__(self, data_source_name: str, data_connection: Dict):
        super().__init__(data_source_name, data_connection)

    def connect(self) -> OpenSearch:
        """
        Connect to the data source
        """
        try:
            auth = (
                self.data_connection.get("username"),
                self.data_connection.get("password"),
            )
            host = self.data_connection.get("host")
            port = int(self.data_connection.get("port"))
            self.client = OpenSearch(
                hosts=[{"host": host, "port": port}],
                http_auth=auth,
                use_ssl=True,
                verify_certs=False,
                ca_certs=False,
            )
            if not self.client.ping():
                raise Exception("Failed to connect to OpenSearch data source")
            return self.client
        except Exception as e:
            raise DataChecksDataSourcesConnectionError(
                f"Failed to connect to OpenSearch data source: [{str(e)}]"
            )

    def close(self):
        """
        Close the connection
        """
        self.client.close()

    def is_connected(self) -> bool:
        """
        Check if the data source is connected
        """
        return self.client.ping()
