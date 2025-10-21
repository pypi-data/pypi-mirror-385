from ardeco_py_package.models import Variable
import pytest
import pandas as pd
import requests_mock
from ardeco_py_package import Ardeco
from ardeco_py_package.exceptions import ArdecoAPIError


def test_get_variable_list_success(ardeco_client):
    mock_response = {
        "data": {
            "variableList": [
                {
                    "code": "SNMTN",
                    "description": "Net migration by broad age group",
                    "allowedDimensions": [
                        "unit",
                        "age",
                        "sex"
                    ]
                },
                {
                    "code": "PVGD",
                    "description": "GDP price index (implicit deflator, national, euro)",
                    "allowedDimensions": [
                        "unit"
                    ]
                },
                {
                    "code": "PVGE",
                    "description": "GVA price index (implicit deflator, national, euro)",
                    "allowedDimensions": [
                        "unit"
                    ]
                },
                {
                    "code": "SNPDZ",
                    "description": "Deaths by 5-year age group",
                    "allowedDimensions": [
                        "unit",
                        "age",
                        "sex"
                    ]
                },
                {
                    "code": "SNPTZ",
                    "description": "Population on 1st January by 5-year age group and sex",
                    "allowedDimensions": [
                        "unit",
                        "age",
                        "sex"
                    ]
                }
            ]
        }
    }

    with requests_mock.Mocker() as m:
        m.post("https://territorial.ec.europa.eu/ardeco-api-v2/graphql", json=mock_response)
        df = ardeco_client.get_variable_list()

    assert isinstance(df, pd.DataFrame)
    assert "code" in df.columns
    assert "SNPTZ" in df["code"].values


def test_get_variable_success(ardeco_client):
    mock_response = {
        "data": {
            "variable": {
                "code": "SNPTN",
                "description": "Population on 1st January by broad age group and sex",
                "nutsLevel": 3,
                "allowedDimensions": [
                    "sex",
                    "age",
                    "unit"
                ]
            }
        }
    }

    with requests_mock.Mocker() as m:
        m.post("https://territorial.ec.europa.eu/ardeco-api-v2/graphql", json=mock_response)
        variable = ardeco_client.get_variable("SNPTZ")
        
        assert isinstance(variable, Variable)
        assert variable.code == "SNPTN"


def test_get_dataset_list_success(ardeco_client):
    mock_response = {
        "data": {
            "variable": {
                "nutsVersionList": [
                    2016,
                    2021,
                    2024
                ],
                "code": "SNPTN",
                "description": "Population on 1st January by broad age group and sex",
                "nutsLevel": 3,
                "allowedDimensions": [
                    "sex",
                    "age",
                    "unit"
                ],
                "datasets": [
                    {
                        "datasetId": 297,
                        "dimensions": [
                            {
                                "key": "age",
                                "value": "TOTAL"
                            },
                            {
                                "key": "sex",
                                "value": "F"
                            },
                            {
                                "key": "unit",
                                "value": "NR"
                            }
                        ]
                    },
                    {
                        "datasetId": 298,
                        "dimensions": [
                            {
                                "key": "age",
                                "value": "TOTAL"
                            },
                            {
                                "key": "sex",
                                "value": "M"
                            },
                            {
                                "key": "unit",
                                "value": "NR"
                            }
                        ]
                    },
                    {
                        "datasetId": 62,
                        "dimensions": [
                            {
                                "key": "age",
                                "value": "TOTAL"
                            },
                            {
                                "key": "sex",
                                "value": "TOTAL"
                            },
                            {
                                "key": "unit",
                                "value": "NR"
                            }
                        ]
                    }
                ]
            }
        }
    }

    with requests_mock.Mocker() as m:
        m.post("https://territorial.ec.europa.eu/ardeco-api-v2/graphql", json=mock_response)
        df = ardeco_client.get_dataset_list("SNPTN")

    assert isinstance(df, pd.DataFrame)
    assert "nuts_versions" in df.columns
    assert df.iloc[0]["unit"] == "NR"
    assert df.iloc[0]["age"] == "TOTAL"
    assert df.iloc[0]["sex"] == "F"


# def test_get_data_with_filters(ardeco_client):
#     variable_mock = {
#         "data": {"variable": {"code": "SUVGD", "description": "GDP", "allowedDimensions": ["unit"], "nutsLevel": 3}}
#     }
#     dataset_mock = {
#         "data": {
#             "variable": {
#                 "allowedDimensions": ["unit"],
#                 "nutsVersionList": ["2021"],
#                 "datasets": [
#                     {"datasetId": "1", "dimensions": [{"key": "unit", "value": "MIO_EUR"}]}
#                 ],
#             }
#         }
#     }

#     csv_mock = "territory_id,date,value\nITC4,2021,23000\nITC2,2021,18000"

#     with requests_mock.Mocker() as m:
#         m.post("https://territorial.ec.europa.eu/ardeco-api-v2/graphql", json=variable_mock)
#         m.post("https://territorial.ec.europa.eu/ardeco-api-v2/graphql", json=dataset_mock)
#         m.get("https://territorial.ec.europa.eu/ardeco-api-v2/rest/export/SNPTN", text=csv_mock)

#         df = ardeco_client.get_data("SNPTN", unit="NR", age="TOTAL", nuts_versions="2021")

#     assert isinstance(df, pd.DataFrame)
#     assert "territory_id" in df.columns
#     assert len(df) == 2
