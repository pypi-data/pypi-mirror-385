from urllib.parse import urlencode
import requests
import pandas as pd
import json

GRAPHQL_API_URL = 'https://territorial.ec.europa.eu/ardeco-api-v2/graphql'
EXPORT_API_URL = 'https://territorial.ec.europa.eu/ardeco-api-v2/rest/export/'

def ardeco_get_dataset_list(var_code=None):
    """
    Retrieve the list of datasets related to a specific variable code.

    Parameters:
    var_code (str): The code of the variable for which to retrieve the datasets.

    Returns:
    pd.DataFrame: A DataFrame containing information about datasets, including variable code,
                  unit of measure, nuts version, and additional dimensions.
    """
    # Check if var_code is specified
    if not var_code:
        return "ERROR: You must specify var_code"

    # Retrieve the list of available variables
    variables_available = ardeco_get_variable_list()
    if var_code not in variables_available['code'].values:
        available_codes = ', '.join(variables_available['code'].unique())
        return f"Variable {var_code} does not exist. Variables permitted: [{available_codes}]"

    # Build the GraphQL query to retrieve the list of datasets for the requested variable
    query = f'''
    query {{
        variable (id: "{var_code}") {{
            nutsVersionList
            datasets {{
                datasetId
                dimensions {{ key value }}
            }}
        }}
    }}
    '''

    # Execute the GraphQL request
    try:
        response = requests.post(GRAPHQL_API_URL, json={'query': query})
        response.raise_for_status()
        result = response.json()
    except requests.exceptions.RequestException as e:
        return f"Error during execution: {str(e)}"

    # Check if the response contains the requested variable
    if 'data' not in result or result['data']['variable'] is None:
        return "Error during execution. Check variable value or API availability"

    # Extract datasets from the response
    variable_data = result['data']['variable']
    dataset_list = variable_data['datasets']
    nuts_version_list = [str(nv) for nv in variable_data['nutsVersionList']]  # Convert all items to string

    # Prepare data for the dataframe
    data = []
    for dataset in dataset_list:
        row = [var_code]
        row += [dim['value'] for dim in dataset['dimensions']]
        row.append(', '.join(nuts_version_list))
        data.append(row)

    # Create the dataframe
    if data:
        columns = ['var'] + [dim['key'] for dim in dataset_list[0]['dimensions']] + ['vers']
        dataset_dataframe = pd.DataFrame(data, columns=columns)
    else:
        dataset_dataframe = pd.DataFrame()

    return dataset_dataframe


def ardeco_get_variable_list():
    """
    Retrieve the list of available variables from the ARDECO GraphQL API.

    Returns:
    pd.DataFrame: A DataFrame containing the codes, descriptions, and related datasets of available variables.
    """
    # Build the GraphQL query to retrieve the list of available variables
    query = '''
    query {
        variableList(export: true) {
            code
            description
            allowedDimensions
            datasets {
                unit
                sector
            }
        }
    }
    '''

    # Execute the GraphQL request
    try:
        response = requests.post(GRAPHQL_API_URL, json={'query': query})
        response.raise_for_status()
        result = response.json()
    except requests.exceptions.RequestException as e:
        return f"Error during execution: {str(e)}"

    # Check if the response contains variables
    if 'data' not in result or result['data']['variableList'] is None:
        return "Error during execution. Check API availability"

    # Extract variables from the response
    variable_list = result['data']['variableList']

    # Prepare data for the dataframe
    data = []
    for variable in variable_list:
        #datasets_info = " | ".join([f"unit: {dataset['unit']}, sector: {dataset['sector']}" for dataset in variable['datasets']])
        row = [variable['code'], variable['description'], variable['allowedDimensions']]
        data.append(row)

    # Create the dataframe
    if data:
        columns = ['code', 'description', 'allowedDimensions']
        variable_dataframe = pd.DataFrame(data, columns=columns)
    else:
        variable_dataframe = pd.DataFrame()

    return variable_dataframe


def ardeco_get_tercet_list(var_code=None):
    """
    Retrieve the list of tercets available, optionally filtered by a specific variable code.

    Parameters:
    var_code (str, optional): The code of the variable for which to retrieve tercet classes.

    Returns:
    pd.DataFrame: A DataFrame containing tercet information, including tercet code, tercet name,
                  tercet class code, and tercet class name.
    """
    # Check if var_code is specified and validate it
    if var_code:
        # Retrieve the list of available variables
        variables_available = ardeco_get_variable_list()
        if var_code not in variables_available['code'].values:
            available_codes = ', '.join(variables_available['code'].unique())
            return f"Variable {var_code} does not exist. Variables permitted: [{available_codes}]"

        # Check if the variable has data at nuts level 3
        variable_props = ardeco_get_variable_props(var_code)
        if 'nutsLevel' not in variable_props or not isinstance(variable_props['nutsLevel'], int):
            return f"The variable {var_code} has no nutsLevel information available."
        nuts_level = variable_props['nutsLevel']
        if str(nuts_level) != "3":
            return f"The variable {var_code} has no data at level 3 and it's not possible to aggregate data at tercet classes"

    # Build the GraphQL query to recover the tercet class list
    query = '''{
        territorialTercetList(territorialLevelId: 3) {
            id
            name
            territorialTercetClassList {
                id
                name
            }
        }
    }'''

    # Execute the GraphQL request
    try:
        response = requests.post(GRAPHQL_API_URL, headers={"Content-Type": "application/json"}, json={'query': query})
        response.raise_for_status()
        result = response.json()
    except requests.exceptions.RequestException as e:
        return f"Error during execution: {str(e)}"

    # Check if the response contains tercet data
    if 'data' not in result or result['data']['territorialTercetList'] is None:
        return "Error during execution. Check API availability"

    # Extract tercet data from the response
    tercet_list = result['data']['territorialTercetList']

    # Prepare data for the dataframe
    data = []
    for tercet in tercet_list:
        for tercet_class in tercet['territorialTercetClassList']:
            row = [
                tercet['id'],
                requests.utils.unquote(tercet['name']),
                tercet_class['id'],
                requests.utils.unquote(tercet_class['name'])
            ]
            data.append(row)

    # Create the dataframe
    if data:
        columns = ['tercet_code', 'tercet_name', 'tercet_class_code', 'tercet_class_name']
        tercet_dataframe = pd.DataFrame(data, columns=columns)
    else:
        tercet_dataframe = pd.DataFrame()

    return tercet_dataframe


def ardeco_get_variable_props(var_code):
    """
    Retrieve the properties of a specific variable, including nutsLevel and description.

    Parameters:
    var_code (str): The code of the variable to retrieve details for.

    Returns:
    dict: A dictionary containing details about the variable, including nutsLevel and description.
    """
    # Build the GraphQL query to retrieve the properties of the requested variable
    query = f'''
    query {{
        variable (id: "{var_code}") {{
            nutsLevel
            description
        }}
    }}
    '''

    # Execute the GraphQL request
    try:
        response = requests.post(GRAPHQL_API_URL, json={'query': query})
        response.raise_for_status()
        result = response.json()
    except requests.exceptions.RequestException as e:
        return f"Error during execution: {str(e)}"

    # Check if the response contains the requested variable
    if 'data' not in result or result['data']['variable'] is None:
        return "Error during execution. Check variable value or API availability"

    # Extract details of the variable from the response
    variable_props = result['data']['variable']

    return variable_props


def ardeco_get_dataset_data(variable=None, **kwargs):
    """
    Retrieve data for a specific dataset defined by variable code, unit, version, nutscode, year, level, and other dimensions.

    Parameters:
    variable (str): The code of the variable to retrieve the dataset for.
    **kwargs: Optional parameters including unit, version, nutscode, year, level, and dimensions.

    Returns:
    pd.DataFrame: A DataFrame containing the dataset information including variable, version, level, nutscode,
                  year, dimensions, unit, tercet class name (if applicable), and value.
    """
    # Check if variable is specified
    if not variable:
        return "Variable is mandatory"

    # Retrieve the list of available variables
    variables_available = ardeco_get_variable_list()
    if variable not in variables_available['code'].values:
        return f"Variable {variable} does not exist"

    # Retrieve the list of available datasets for the given variable
    datasets_available = ardeco_get_dataset_list(variable)

    variable_entry = variables_available[variables_available['code'] == variable]
    
    kwargs_keys = list(kwargs.keys())
    for dim in variable_entry['allowedDimensions'].values[0]:
        if dim not in kwargs_keys and dim != 'tercet':
            return f"Dimension '{dim}' is mandatory for variable '{variable}'"
    
    # Define the base URL for the REST API
    url = f"{EXPORT_API_URL}{variable}?"
    
    

    # Process optional parameters
    unit = kwargs.get('unit', None)
    version = kwargs.get('version', None)
    nutscode = kwargs.get('nutscode', None)
    year = kwargs.get('year', None)
    level = kwargs.get('level', None)
    tercet = kwargs.get('tercet', None)

    url += urlencode(kwargs)
    
    # # Check if unit is valid
    # if unit and unit not in datasets_available['unit'].values:
    #     return f"Unit {unit} is not valid. Units permitted: [{', '.join(datasets_available['unit'].unique())}]"
    # if unit:
    #     url += f"&unit={unit}"

    # # Check if version is valid
    # if version and not any(version in v for v in datasets_available['vers'].values):
    #     return f"Version {version} is not valid. Versions permitted: [{', '.join(datasets_available['vers'].unique())}]"
    # if version:
    #     url += f"&version={version}"

    # # Check if nutscode is valid and add to URL
    # if nutscode:
    #     nutscode_list = nutscode.split(',')
    #     for ns in nutscode_list:
    #         url += f"&territory_id={ns}"

    # # Check if year is valid and add to URL
    # if year:
    #     year_list = str(year).split(',')
    #     for yr in year_list:
    #         url += f"&year={yr}"

    # # Check if level is valid and add to URL
    # if level:
    #     level_list = str(level).split(',')
    #     for lv in level_list:
    #         url += f"&level_id={lv}"

    # # Check if tercet is valid and add to URL
    # if tercet is not None:
    #     valid_tercets = ardeco_get_tercet_list()
    #     if tercet not in valid_tercets['tercet_class_code'].values:
    #         return f"Tercet {tercet} is not valid. Tercet values permitted: [{', '.join(valid_tercets['tercet_class_code'].unique())}]"
    #     url += f"&tercet_class={tercet}"

    print(url)
    
    # Execute the request to retrieve the dataset
    try:
        response = requests.get(url)
        response.raise_for_status()
        dataset = pd.read_csv(url)
    except requests.exceptions.RequestException as e:
        return f"Error during execution: {str(e)}"
    except Exception as e:
        return f"Error reading dataset: {str(e)}"

    # Rename columns as requested
    dataset.rename(columns={'LEVEL_ID': 'LEVEL', 'TERRITORY_ID': 'NUTS'}, inplace=True)
    if 'NAME_HTML' in dataset.columns:
        dataset.drop(columns=['NAME_HTML'], inplace=True)
    if 'DATE' in dataset.columns:
        dataset.drop(columns=['DATE'], inplace=True)

    # Add VARIABLE column as the first column
    dataset.insert(0, 'VARIABLE', variable)

    # If tercet is specified, add TERCET_CLASS_NAME before VALUE column
    if tercet is not None:
        valid_tercets = ardeco_get_tercet_list()
        tercet_name = valid_tercets.loc[valid_tercets['tercet_class_code'] == tercet, 'tercet_class_name'].values[0]
        dataset['TERCET_CLASS_NAME'] = tercet_name
        if 'VALUE' in dataset.columns:
            value_index = dataset.columns.get_loc('VALUE')
            dataset.insert(value_index, 'TERCET_CLASS_NAME', dataset.pop('TERCET_CLASS_NAME'))

    # Return the dataset as a DataFrame
    if dataset.empty:
        return "*** NO DATA ***"
    return dataset


#print(ardeco_get_variable_list())
#print(ardeco_get_tercet_list("SUVGE"))
#print(ardeco_get_tercet_list("PPP"))
#print(ardeco_get_dataset_list("SUVGE"))
#print(ardeco_get_dataset_data("SNPTN", year="2020", nutscode="AT", version="2016"))
#print(ardeco_get_dataset_data("SNPTN", year="2018", nutscode="IT", version="2016", tercet=6))

