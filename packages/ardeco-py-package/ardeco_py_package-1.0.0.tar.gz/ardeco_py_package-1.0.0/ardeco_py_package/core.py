from functools import wraps
import logging
import pandas as pd
import requests

from typing import Dict, Any, List
from urllib.parse import unquote

from ardeco_py_package.exceptions import ArdecoAPIError
from .models import Tercet, Variable, Dataset, DataTable


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

GLOBAL_FILTERS = ["territory_id", "date", "level_id", "tercet_class", "tercet"]


def _require_var_code(func):
    """Decorator that ensures a variable code is provided to the decorated method.

    Args:
        func (Callable): The method being decorated.

    Raises:
        ArdecoAPIError: If the variable code is missing.

    Returns:
        Callable: The wrapped method.
    """
    @wraps(func)
    def wrapper(self, var_code: str, *args, **kwargs):
        if not var_code:
            raise ArdecoAPIError("A variable code must be specified.")
        return func(self, var_code, *args, **kwargs)
    return wrapper


class Ardeco:
    """Main client for interacting with the ARDECO API.

    This class provides methods to retrieve variables, datasets, and statistical data
    from the ARDECO API, as well as helper methods for handling GraphQL and REST requests.
    """
    
    def __init__(self):
        """Initialize the ARDECO API client with default endpoints."""
        self.graphql_api_url = "https://territorial.ec.europa.eu/ardeco-api-v2/graphql"
        self.graphql_udp_url = "https://territorial.ec.europa.eu/api/graphql"
        self.data_source = "https://territorial.ec.europa.eu/ardeco-api-v2/rest/export"

    def _extract_params(self, row, allowed_dims, kwargs):
        """Extract and combine query parameters from dataset rows and user filters.

        Args:
            row (pd.Series): A row from the dataset DataFrame.
            allowed_dims (list): List of allowed dimension names.
            kwargs (dict): User-specified filter arguments.

        Returns:
            dict: A dictionary of query parameters to send to the REST API.
        """
        params = {}

        for dim in allowed_dims:
            if dim in kwargs and kwargs[dim]:
                params[dim] = kwargs[dim]
            elif pd.notna(row.get(dim)):
                params[dim] = row.get(dim)

        if "nuts_versions" in kwargs and kwargs["nuts_versions"]:
            params["versions"] = str(kwargs["nuts_versions"])
        elif row.get("nuts_versions"):
            versions = [v.strip() for v in str(row["nuts_versions"]).split(",")]
            params["versions"] = versions[-1]

        for key, value in kwargs.items():
            if key.lower() in GLOBAL_FILTERS and value is not None:
                params[key.lower()] = value

        return params

    def _execute_graphql_query(self, query: str, source: str | None = None) -> Dict[str, Any]:
        """Execute a GraphQL query against the ARDECO API.

        Args:
            query (str): The GraphQL query string.
            source (str, optional): Selects between default (`None`) and UDP endpoint (`"udp"`).

        Raises:
            ArdecoAPIError: If the API request fails or returns errors.

        Returns:
            dict: The parsed JSON response from the API.
        """
        try:
            url = self.graphql_api_url
            if source == "udp":
                url = self.graphql_udp_url
            response = requests.post(url, json={"query": query})
            response.raise_for_status()
            result = response.json()
        except requests.exceptions.RequestException as e:
            raise ArdecoAPIError(f"API connection error: {e}")

        if "errors" in result:
            logger.error("GraphQL error: %s", result["errors"])
            raise ArdecoAPIError(f"GraphQL error: {result['errors']}")

        data = result.get("data")
        if not data:
            return {}

        return data

    def _match_dimension(self, row_value, filter_value, dim):
        """Compare dataset dimension values to user filters, case-insensitive.

        Args:
            row_value (Any): The value from the dataset row.
            filter_value (Any): The user-provided filter value.
            dim (str): The name of the dimension being compared.

        Returns:
            bool: True if the values match, False otherwise.
        """
        if dim == "nuts_versions":
            row_versions = [str(v).strip().lower() for v in str(row_value).split(",")] if row_value else []
            return str(filter_value).strip().lower() in row_versions
        return str(row_value).strip().lower() == str(filter_value).strip().lower()

    def get_variable_list(self) -> pd.DataFrame:
        """Retrieve the list of all available variables from the ARDECO API.

        Returns:
            pd.DataFrame: A DataFrame containing each variable’s code, description,
                and allowed dimensions.
        """
        query = """
            query {
                variableList(export: true) {
                    code
                    description
                    allowed_dimensions: allowedDimensions
                }
            }
        """
        data = self._execute_graphql_query(query)
        variable_list = data["variableList"]


        logger.info("[ARDECO] Retrieved %d variables from ARDECO API.", len(variable_list))
        
        return DataTable(variable_list).to_pandas()

    @_require_var_code
    def get_variable(self, var_code: str) -> Variable:
        """Retrieve detailed information about a specific variable.

        Args:
            var_code (str): The variable code.

        Raises:
            ArdecoAPIError: If the variable is not found or data is missing.

        Returns:
            Variable: A `Variable` object containing metadata about the variable.
        """
        query = f'''
            query {{
                variable(id: "{var_code}") {{
                    code
                    description
                    nutsLevel
                    allowedDimensions
                    usedDimensionsList {{
                        dimensionGroupName
                        dimensionValueList {{
                            dimensionValueName
                        }}
                    }}
                }}
            }}
        '''
        data = self._execute_graphql_query(query)

        variable_data = data["variable"]
        if not variable_data:
            raise ArdecoAPIError(f"Variable '{var_code}' not found or missing data.")

        logger.debug("Fetched variable details: %s", variable_data)

        variable_obj = Variable(
            code=variable_data.get("code", var_code),
            description=variable_data.get("description", ""),
            allowed_dimensions=variable_data.get("allowedDimensions", []),
            nuts_level=variable_data.get("nutsLevel", None),
            _dimensions_raw=variable_data.get("usedDimensionsList", [])
        )

        return variable_obj

    @_require_var_code
    def get_dataset_list(self, var_code: str) -> pd.DataFrame:
        """Retrieve the list of datasets associated with a variable.

        Args:
            var_code (str): The variable code.

        Raises:
            ArdecoAPIError: If no dataset information is available.

        Returns:
            pd.DataFrame: A DataFrame listing available datasets, including
                dimension values and available NUTS versions.
        """
        query = f"""
        query {{
            variable(id: "{var_code}") {{
                nutsVersionList
                code
                description
                nutsLevel
                allowedDimensions
                datasets {{
                    datasetId
                    dimensions {{
                        key
                        value
                    }}
                }}
            }}
        }}
        """

        data = self._execute_graphql_query(query)
        variable_data = data.get("variable")

        if not variable_data:
            raise ArdecoAPIError(f"No data found for variable '{var_code}'.")

        allowed_dims = variable_data.get("allowedDimensions", [])
        dataset_list = variable_data.get("datasets", [])
        nuts_versions = variable_data.get("nutsVersionList", [])

        if not dataset_list:
            logger.warning("No datasets found for variable %s", var_code)
            return pd.DataFrame(columns=['variable_code'] + allowed_dims + ['nuts_versions'])

        datasets: List[Dataset] = []
        for ds in dataset_list:
            dimensions = {dim["key"]: dim["value"] for dim in ds["dimensions"]}
            dataset_obj = Dataset(
                variable_code=var_code,
                dimensions=dimensions,
                nuts_versions=nuts_versions,
            )
            datasets.append(dataset_obj)

        logger.info("[ARDECO] Retrieved %d datasets for variable %s.", len(datasets), var_code)

        columns = ['variable_code'] + allowed_dims + ['nuts_versions']
        return DataTable([x.to_dict() for x in datasets], columns).to_pandas()

    @_require_var_code
    def get_data(self, variable_code: str, **kwargs) -> pd.DataFrame:
        """Retrieve actual statistical data for a given variable and filters.

        Args:
            variable_code (str): The variable code to query.
            **kwargs: Optional filters such as:
                - Dimensions (e.g., `sex="M"`, `age="TOTAL"`, `unit="NR"`)
                - Global filters (e.g., `territory_id`, `date`, `level_id`)
                - NUTS version (via `nuts_versions`)

        Raises:
            ArdecoAPIError: If no datasets match the filters or if no data is returned.

        Returns:
            pd.DataFrame: The requested dataset as a Pandas DataFrame.
        """
        variable = self.get_variable(variable_code)
        allowed_dims = variable.allowed_dimensions or []
        all_datasets = self.get_dataset_list(variable_code)

        filtered = []
        for _, row in all_datasets.iterrows():
            match = True
            for dim, value in kwargs.items():
                if dim.lower() in GLOBAL_FILTERS or dim == "nuts_versions":
                    continue
                if dim not in allowed_dims:
                    raise ArdecoAPIError(f"Invalid dimension '{dim}' for variable '{variable_code}'.")
                if value and not self._match_dimension(row.get(dim), value, dim):
                    match = False
                    break
            if match:
                filtered.append(row)

        if not filtered:
            raise ArdecoAPIError(f"No dataset found for variable '{variable_code}' with filters {kwargs}.")

        filtered_df = pd.DataFrame(filtered)
        filtered_df = (
            filtered_df.assign(nuts_versions=filtered_df["nuts_versions"])
            .explode("nuts_versions")
            .assign(nuts_versions=lambda df: df["nuts_versions"])
            .reset_index(drop=True)
        )

        logger.info("[ARDECO] Found %d matching dataset(s) for %s", len(filtered_df), variable_code)

        if "nuts_versions" in kwargs and kwargs["nuts_versions"]:
            filter_value = kwargs["nuts_versions"]
            available_versions = filtered_df["nuts_versions"].unique().tolist()

            if filter_value not in available_versions:
                raise ArdecoAPIError(
                    f"nuts_versions '{filter_value}' not available for variable '{variable_code}'. "
                    f"Available versions: {available_versions}"
                )

            filtered_df = filtered_df[filtered_df["nuts_versions"] == filter_value]
            logger.info("[ARDECO] Applied nuts_versions filter: %s (remaining %d datasets)", filter_value, len(filtered_df))

        logger.info("[ARDECO] Found %d matching dataset(s) for %s", len(filtered_df), variable_code)

        base_url = self.data_source
        all_results = []

        for _, row in filtered_df.iterrows():
            params = self._extract_params(row, allowed_dims, kwargs)
            url = f"{base_url}/{variable_code}"
            logger.debug("Fetching data from: %s with params %s", url, params)

            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                from io import StringIO
                data = pd.read_csv(StringIO(response.text)).to_dict(orient="records")
            except requests.exceptions.RequestException as e:
                logger.error("Error fetching dataset: %s", e)
                continue
            # TODO: try to extend the dataframe and not append to the list
            all_results.extend(data)

        if not all_results:
            raise ArdecoAPIError(f"No data returned from REST API for '{variable_code}'.")

        logger.info("[ARDECO] Retrieved %d records for %s", len(all_results), variable_code)
        
        return DataTable(all_results).to_pandas()

    def get_tercet_list(self, territorial_level_id: int = 3) -> pd.DataFrame:
        """Retrieve the list of territorial tercets and their classification.

        Args:
            territorial_level_id (int, optional): The territorial level to query.
                Defaults to 3.

        Returns:
            pd.DataFrame: A DataFrame containing tercet codes, names, and class details.
        """
        query = f"""
            query {{
                territorialTercetList(territorialLevelId: {territorial_level_id}) {{
                    id
                    name
                    territorialTercetClassList {{
                        id
                        name
                    }}
                }}
            }}
        """
        data = self._execute_graphql_query(query, source="udp")
        tercet_list = data.get("territorialTercetList", [])

        output = []
        for tercet in tercet_list:
            for tercet_class in tercet['territorialTercetClassList']:
                row = Tercet(
                    code=tercet['id'],
                    name=unquote(tercet['name']),
                    tercet_class_code=tercet_class['id'],
                    tercet_class_name=unquote(tercet_class['name'])
                )
                output.append(row)

        return DataTable([x.to_dict() for x in output]).to_pandas()
