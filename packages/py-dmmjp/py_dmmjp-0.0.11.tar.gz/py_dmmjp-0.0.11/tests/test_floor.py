"""
Test floor, service, and site data models with actual implementation.
"""

from typing import Any, Dict

import pytest

from py_dmmjp.commons import ApiRequest, RequestParameters
from py_dmmjp.floor import Floor, FloorListResponse, FloorListResult, Service, Site
from tests.floor_test_base import (
    FloorListResponseTestBase,
    FloorTestBase,
    ServiceTestBase,
    SiteTestBase,
)


class TestFloorWithRealData(FloorTestBase):
    """Test floor with real API response data."""

    @pytest.fixture
    def floor_data(self) -> Dict[str, Any]:
        return {"id": "1", "name": "AKB48", "code": "akb48"}

    def test_floor_basic_fields(self, floor_data: Dict[str, Any]) -> None:
        floor = Floor.from_dict(floor_data)

        assert floor.id == "1"
        assert floor.name == "AKB48"
        assert floor.code == "akb48"

    def test_floor_from_dict(self, floor_data: Dict[str, Any]) -> None:
        floor = Floor.from_dict(floor_data)

        assert isinstance(floor, Floor)
        assert floor.id == floor_data["id"]
        assert floor.name == floor_data["name"]
        assert floor.code == floor_data["code"]

    def test_floor_id_type(self, floor_data: Dict[str, Any]) -> None:
        floor = Floor.from_dict(floor_data)

        assert isinstance(floor.id, str)

    def test_floor_name_validation(self, floor_data: Dict[str, Any]) -> None:
        floor = Floor.from_dict(floor_data)

        assert floor.name is not None
        assert len(floor.name) > 0
        assert isinstance(floor.name, str)

    def test_floor_code_validation(self, floor_data: Dict[str, Any]) -> None:
        floor = Floor.from_dict(floor_data)

        assert floor.code is not None
        assert len(floor.code) > 0
        assert isinstance(floor.code, str)

    def test_floor_empty_data_handling(self, floor_data: Dict[str, Any]) -> None:
        empty_data: Dict[str, Any] = {}
        floor = Floor.from_dict(empty_data)

        assert floor.id == ""
        assert floor.name == ""
        assert floor.code == ""

    def test_floor_default_values(self, floor_data: Dict[str, Any]) -> None:
        partial_data: Dict[str, Any] = {"id": "1"}
        floor = Floor.from_dict(partial_data)

        assert floor.id == "1"
        assert floor.name == ""
        assert floor.code == ""


class TestServiceWithRealData(ServiceTestBase):
    """Test service with real API response data."""

    @pytest.fixture
    def service_data(self) -> Dict[str, Any]:
        return {
            "name": "AKB48グループ",
            "code": "lod",
            "floor": [
                {"id": "1", "name": "AKB48", "code": "akb48"},
                {"id": "2", "name": "SKE48", "code": "ske48"},
                {"id": "3", "name": "NMB48", "code": "nmb48"},
            ],
        }

    def test_service_basic_fields(self, service_data: Dict[str, Any]) -> None:
        service = Service.from_dict(service_data)

        assert service.name == "AKB48グループ"
        assert service.code == "lod"

    def test_service_floors_list(self, service_data: Dict[str, Any]) -> None:
        service = Service.from_dict(service_data)

        assert isinstance(service.floors, list)
        assert len(service.floors) == 3

    def test_service_from_dict(self, service_data: Dict[str, Any]) -> None:
        service = Service.from_dict(service_data)

        assert isinstance(service, Service)
        assert service.name == service_data["name"]
        assert service.code == service_data["code"]
        assert len(service.floors) == len(service_data["floor"])

    def test_service_nested_floors(self, service_data: Dict[str, Any]) -> None:
        service = Service.from_dict(service_data)

        for floor in service.floors:
            assert isinstance(floor, Floor)
            assert floor.id is not None
            assert floor.name is not None
            assert floor.code is not None

    def test_service_empty_floors(self, service_data: Dict[str, Any]) -> None:
        empty_service_data: Dict[str, Any] = {
            "name": "Test",
            "code": "test",
            "floor": [],
        }
        service = Service.from_dict(empty_service_data)

        assert isinstance(service.floors, list)
        assert len(service.floors) == 0

    def test_service_multiple_floors(self, service_data: Dict[str, Any]) -> None:
        service = Service.from_dict(service_data)

        assert len(service.floors) == 3
        assert service.floors[0].code == "akb48"
        assert service.floors[1].code == "ske48"
        assert service.floors[2].code == "nmb48"

    def test_service_name_validation(self, service_data: Dict[str, Any]) -> None:
        service = Service.from_dict(service_data)

        assert service.name is not None
        assert len(service.name) > 0
        assert isinstance(service.name, str)

    def test_service_code_validation(self, service_data: Dict[str, Any]) -> None:
        service = Service.from_dict(service_data)

        assert service.code is not None
        assert len(service.code) > 0
        assert isinstance(service.code, str)

    def test_service_floors_type(self, service_data: Dict[str, Any]) -> None:
        service = Service.from_dict(service_data)

        assert isinstance(service.floors, list)
        for floor in service.floors:
            assert isinstance(floor, Floor)

    def test_service_default_values(self, service_data: Dict[str, Any]) -> None:
        partial_data: Dict[str, Any] = {"name": "Test"}
        service = Service.from_dict(partial_data)

        assert service.name == "Test"
        assert service.code == ""
        assert isinstance(service.floors, list)
        assert len(service.floors) == 0


class TestSiteWithRealData(SiteTestBase):
    """Test site with real API response data."""

    @pytest.fixture
    def site_data(self) -> Dict[str, Any]:
        return {
            "name": "DMM.com（一般）",
            "code": "DMM.com",
            "service": [
                {
                    "name": "AKB48グループ",
                    "code": "lod",
                    "floor": [
                        {"id": "1", "name": "AKB48", "code": "akb48"},
                        {"id": "2", "name": "SKE48", "code": "ske48"},
                    ],
                },
                {
                    "name": "DMMブックス",
                    "code": "ebook",
                    "floor": [
                        {"id": "19", "name": "コミック", "code": "comic"},
                        {"id": "20", "name": "写真集", "code": "photo"},
                    ],
                },
            ],
        }

    def test_site_basic_fields(self, site_data: Dict[str, Any]) -> None:
        site = Site.from_dict(site_data)

        assert site.name == "DMM.com（一般）"
        assert site.code == "DMM.com"

    def test_site_services_list(self, site_data: Dict[str, Any]) -> None:
        site = Site.from_dict(site_data)

        assert isinstance(site.services, list)
        assert len(site.services) == 2

    def test_site_from_dict(self, site_data: Dict[str, Any]) -> None:
        site = Site.from_dict(site_data)

        assert isinstance(site, Site)
        assert site.name == site_data["name"]
        assert site.code == site_data["code"]
        assert len(site.services) == len(site_data["service"])

    def test_site_nested_services(self, site_data: Dict[str, Any]) -> None:
        site = Site.from_dict(site_data)

        for service in site.services:
            assert isinstance(service, Service)
            assert service.name is not None
            assert service.code is not None

    def test_site_nested_floors(self, site_data: Dict[str, Any]) -> None:
        site = Site.from_dict(site_data)

        for service in site.services:
            for floor in service.floors:
                assert isinstance(floor, Floor)
                assert floor.id is not None
                assert floor.name is not None
                assert floor.code is not None

    def test_site_empty_services(self, site_data: Dict[str, Any]) -> None:
        empty_site_data: Dict[str, Any] = {
            "name": "Test",
            "code": "test",
            "service": [],
        }
        site = Site.from_dict(empty_site_data)

        assert isinstance(site.services, list)
        assert len(site.services) == 0

    def test_site_multiple_services(self, site_data: Dict[str, Any]) -> None:
        site = Site.from_dict(site_data)

        assert len(site.services) == 2
        assert site.services[0].code == "lod"
        assert site.services[1].code == "ebook"

    def test_site_name_validation(self, site_data: Dict[str, Any]) -> None:
        site = Site.from_dict(site_data)

        assert site.name is not None
        assert len(site.name) > 0
        assert isinstance(site.name, str)

    def test_site_code_validation(self, site_data: Dict[str, Any]) -> None:
        site = Site.from_dict(site_data)

        assert site.code is not None
        assert len(site.code) > 0
        assert isinstance(site.code, str)

    def test_site_services_type(self, site_data: Dict[str, Any]) -> None:
        site = Site.from_dict(site_data)

        assert isinstance(site.services, list)
        for service in site.services:
            assert isinstance(service, Service)

    def test_site_default_values(self, site_data: Dict[str, Any]) -> None:
        partial_data: Dict[str, Any] = {"name": "Test"}
        site = Site.from_dict(partial_data)

        assert site.name == "Test"
        assert site.code == ""
        assert isinstance(site.services, list)
        assert len(site.services) == 0

    def test_site_hierarchy(self, site_data: Dict[str, Any]) -> None:
        site = Site.from_dict(site_data)

        assert isinstance(site, Site)
        assert len(site.services) == 2
        assert len(site.services[0].floors) == 2
        assert len(site.services[1].floors) == 2
        assert site.services[0].floors[0].code == "akb48"
        assert site.services[1].floors[0].code == "comic"


class TestFloorListResponse(FloorListResponseTestBase):
    """Test FloorListResponse class properties and attributes."""

    @pytest.fixture
    def full_api_response(self) -> Dict[str, Any]:
        return {
            "request": {
                "parameters": {
                    "api_id": "***REDACTED_APP_ID***",
                    "affiliate_id": "***REDACTED_AFF_ID***",
                }
            },
            "result": {
                "site": [
                    {
                        "name": "DMM.com（一般）",
                        "code": "DMM.com",
                        "service": [
                            {
                                "name": "AKB48グループ",
                                "code": "lod",
                                "floor": [
                                    {"id": "1", "name": "AKB48", "code": "akb48"},
                                    {"id": "2", "name": "SKE48", "code": "ske48"},
                                    {"id": "3", "name": "NMB48", "code": "nmb48"},
                                ],
                            },
                            {
                                "name": "DMMブックス",
                                "code": "ebook",
                                "floor": [
                                    {"id": "19", "name": "コミック", "code": "comic"},
                                    {"id": "20", "name": "写真集", "code": "photo"},
                                ],
                            },
                        ],
                    },
                    {
                        "name": "FANZA（アダルト）",
                        "code": "FANZA",
                        "service": [
                            {
                                "name": "動画",
                                "code": "digital",
                                "floor": [
                                    {"id": "43", "name": "ビデオ", "code": "videoa"},
                                    {"id": "44", "name": "素人", "code": "videoc"},
                                ],
                            }
                        ],
                    },
                ]
            },
        }

    def test_response_basic_structure(self, full_api_response: Dict[str, Any]) -> None:
        response = FloorListResponse.from_dict(full_api_response)

        assert isinstance(response, FloorListResponse)
        assert isinstance(response.request, ApiRequest)
        assert isinstance(response.result, FloorListResult)

    def test_response_request_property(self, full_api_response: Dict[str, Any]) -> None:
        response = FloorListResponse.from_dict(full_api_response)

        assert response.request is not None
        assert isinstance(response.request, ApiRequest)
        assert isinstance(response.request.parameters, RequestParameters)

    def test_response_request_parameters(
        self, full_api_response: Dict[str, Any]
    ) -> None:
        response = FloorListResponse.from_dict(full_api_response)

        params = response.request.parameters
        assert params.api_id == "***REDACTED_APP_ID***"
        assert params.affiliate_id == "***REDACTED_AFF_ID***"

    def test_response_result_property(self, full_api_response: Dict[str, Any]) -> None:
        response = FloorListResponse.from_dict(full_api_response)

        assert response.result is not None
        assert isinstance(response.result, FloorListResult)
        assert isinstance(response.result.sites, list)

    def test_response_sites_property(self, full_api_response: Dict[str, Any]) -> None:
        response = FloorListResponse.from_dict(full_api_response)

        sites = response.sites
        assert isinstance(sites, list)
        assert len(sites) == 2
        assert all(isinstance(site, Site) for site in sites)

    def test_response_raw_response_property(
        self, full_api_response: Dict[str, Any]
    ) -> None:
        response = FloorListResponse.from_dict(full_api_response)

        raw = response.raw_response
        assert raw is not None
        assert isinstance(raw, dict)
        assert "request" in raw
        assert "result" in raw

    def test_response_raw_response_immutability(
        self, full_api_response: Dict[str, Any]
    ) -> None:
        response = FloorListResponse.from_dict(full_api_response)

        raw = response.raw_response
        assert raw is not None
        assert raw is not full_api_response
        assert raw == full_api_response

    def test_response_sites_access_through_result(
        self, full_api_response: Dict[str, Any]
    ) -> None:
        response = FloorListResponse.from_dict(full_api_response)

        assert response.sites == response.result.sites
        assert len(response.sites) == len(response.result.sites)

    def test_response_nested_structure_integrity(
        self, full_api_response: Dict[str, Any]
    ) -> None:
        response = FloorListResponse.from_dict(full_api_response)

        assert len(response.sites) == 2
        assert len(response.sites[0].services) == 2
        assert len(response.sites[1].services) == 1
        assert len(response.sites[0].services[0].floors) == 3
        assert len(response.sites[0].services[1].floors) == 2

    def test_response_site_names(self, full_api_response: Dict[str, Any]) -> None:
        response = FloorListResponse.from_dict(full_api_response)

        assert response.sites[0].name == "DMM.com（一般）"
        assert response.sites[0].code == "DMM.com"
        assert response.sites[1].name == "FANZA（アダルト）"
        assert response.sites[1].code == "FANZA"

    def test_response_service_names(self, full_api_response: Dict[str, Any]) -> None:
        response = FloorListResponse.from_dict(full_api_response)

        dmm_services = response.sites[0].services
        assert dmm_services[0].name == "AKB48グループ"
        assert dmm_services[0].code == "lod"
        assert dmm_services[1].name == "DMMブックス"
        assert dmm_services[1].code == "ebook"

    def test_response_floor_details(self, full_api_response: Dict[str, Any]) -> None:
        response = FloorListResponse.from_dict(full_api_response)

        first_service = response.sites[0].services[0]
        assert first_service.floors[0].id == "1"
        assert first_service.floors[0].name == "AKB48"
        assert first_service.floors[0].code == "akb48"

    def test_response_with_empty_result(self) -> None:
        empty_response = {
            "request": {"parameters": {"api_id": "test", "affiliate_id": "test"}},
            "result": {"site": []},
        }
        response = FloorListResponse.from_dict(empty_response)

        assert isinstance(response, FloorListResponse)
        assert len(response.sites) == 0
        assert isinstance(response.result.sites, list)

    def test_response_from_dict_creates_deep_copy(
        self, full_api_response: Dict[str, Any]
    ) -> None:
        response = FloorListResponse.from_dict(full_api_response)

        full_api_response["request"]["parameters"]["api_id"] = "modified"
        assert response.request.parameters.api_id == "***REDACTED_APP_ID***"

    def test_response_result_sites_type_consistency(
        self, full_api_response: Dict[str, Any]
    ) -> None:
        response = FloorListResponse.from_dict(full_api_response)

        for site in response.result.sites:
            assert isinstance(site, Site)
            for service in site.services:
                assert isinstance(service, Service)
                for floor in service.floors:
                    assert isinstance(floor, Floor)

    def test_response_raw_response_contains_all_data(
        self, full_api_response: Dict[str, Any]
    ) -> None:
        response = FloorListResponse.from_dict(full_api_response)

        raw = response.raw_response
        assert raw is not None
        assert raw["request"]["parameters"]["api_id"] == "***REDACTED_APP_ID***"
        assert len(raw["result"]["site"]) == 2

    def test_response_private_raw_response_not_in_repr(
        self, full_api_response: Dict[str, Any]
    ) -> None:
        response = FloorListResponse.from_dict(full_api_response)

        repr_str = repr(response)
        assert "_raw_response" not in repr_str

    def test_response_multiple_floors_per_service(
        self, full_api_response: Dict[str, Any]
    ) -> None:
        response = FloorListResponse.from_dict(full_api_response)

        akb_service = response.sites[0].services[0]
        assert len(akb_service.floors) == 3
        assert akb_service.floors[1].name == "SKE48"
        assert akb_service.floors[2].name == "NMB48"

    def test_response_fanza_site_structure(
        self, full_api_response: Dict[str, Any]
    ) -> None:
        response = FloorListResponse.from_dict(full_api_response)

        fanza_site = response.sites[1]
        assert fanza_site.code == "FANZA"
        assert len(fanza_site.services) == 1
        assert fanza_site.services[0].code == "digital"
        assert len(fanza_site.services[0].floors) == 2
