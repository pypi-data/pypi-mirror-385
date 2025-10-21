"""
Integration tests for DMM floor API functionality.
"""

# pylint: disable=redefined-outer-name,import-outside-toplevel,too-many-statements,too-many-public-methods,duplicate-code
# mypy: disable-error-code=attr-defined

from typing import List
from unittest.mock import MagicMock, patch

import pytest

from py_dmmjp import DMMClient
from py_dmmjp.exceptions import DMMAPIError
from py_dmmjp.floor import Floor, Service, Site


@pytest.mark.integration
class TestDMMClientWithFloorIntegration:
    """Integration tests for DMM client with real API calls for floors."""

    def test_client_authentication(self, dmm_client: DMMClient) -> None:
        """Test that client can authenticate with valid credentials."""

        assert dmm_client.app_id is not None
        assert dmm_client.affiliate_id is not None

    def test_get_floors_basic_request(self, dmm_client: DMMClient) -> None:
        """Test basic floor list retrieval from DMM."""

        sites: List[Site] = dmm_client.get_floors()

        assert isinstance(sites, list)
        assert len(sites) > 0

        for site in sites:
            assert isinstance(site, Site)
            assert site.name is not None
            assert site.code is not None

    def test_get_floors_site_structure(self, dmm_client: DMMClient) -> None:
        """Test site data structure."""

        sites: List[Site] = dmm_client.get_floors()

        assert len(sites) >= 2

        dmm_site = next((s for s in sites if s.code == "DMM.com"), None)
        fanza_site = next((s for s in sites if s.code == "FANZA"), None)

        assert dmm_site is not None
        assert fanza_site is not None
        assert "DMM.com" in dmm_site.name
        assert "FANZA" in fanza_site.name

    def test_get_floors_services_list(self, dmm_client: DMMClient) -> None:
        """Test services list within sites."""

        sites: List[Site] = dmm_client.get_floors()

        for site in sites:
            assert isinstance(site.services, list)
            assert len(site.services) > 0

            for service in site.services:
                assert isinstance(service, Service)
                assert service.name is not None
                assert service.code is not None

    def test_get_floors_nested_structure(self, dmm_client: DMMClient) -> None:
        """Test complete nested structure of site-service-floor."""

        sites: List[Site] = dmm_client.get_floors()

        for site in sites:
            for service in site.services:
                assert isinstance(service.floors, list)
                assert len(service.floors) > 0

                for floor in service.floors:
                    assert isinstance(floor, Floor)
                    assert floor.id is not None
                    assert floor.name is not None
                    assert floor.code is not None

    def test_get_floors_specific_service(self, dmm_client: DMMClient) -> None:
        """Test retrieving specific service data."""

        sites: List[Site] = dmm_client.get_floors()

        fanza_site = next((s for s in sites if s.code == "FANZA"), None)
        assert fanza_site is not None

        digital_service = next(
            (svc for svc in fanza_site.services if svc.code == "digital"), None
        )
        assert digital_service is not None
        assert digital_service.name == "動画"

    def test_get_floors_specific_floor(self, dmm_client: DMMClient) -> None:
        """Test retrieving specific floor data."""

        sites: List[Site] = dmm_client.get_floors()

        fanza_site = next((s for s in sites if s.code == "FANZA"), None)
        assert fanza_site is not None

        digital_service = next(
            (svc for svc in fanza_site.services if svc.code == "digital"), None
        )
        assert digital_service is not None

        videoa_floor = next(
            (f for f in digital_service.floors if f.code == "videoa"), None
        )
        assert videoa_floor is not None
        assert videoa_floor.name == "ビデオ"
        assert videoa_floor.id == "43"

    def test_get_floors_data_types(self, dmm_client: DMMClient) -> None:
        """Test data types of floor list elements."""

        sites: List[Site] = dmm_client.get_floors()

        for site in sites:
            assert isinstance(site.name, str)
            assert isinstance(site.code, str)
            assert isinstance(site.services, list)

            for service in site.services:
                assert isinstance(service.name, str)
                assert isinstance(service.code, str)
                assert isinstance(service.floors, list)

                for floor in service.floors:
                    assert isinstance(floor.id, str)
                    assert isinstance(floor.name, str)
                    assert isinstance(floor.code, str)

    def test_get_floors_dmm_site_services(self, dmm_client: DMMClient) -> None:
        """Test DMM.com site services."""

        sites: List[Site] = dmm_client.get_floors()

        dmm_site = next((s for s in sites if s.code == "DMM.com"), None)
        assert dmm_site is not None

        assert len(dmm_site.services) > 0

        ebook_service = next(
            (svc for svc in dmm_site.services if svc.code == "ebook"), None
        )
        assert ebook_service is not None
        assert "ブックス" in ebook_service.name

    def test_get_floors_fanza_site_services(self, dmm_client: DMMClient) -> None:
        """Test FANZA site services."""

        sites: List[Site] = dmm_client.get_floors()

        fanza_site = next((s for s in sites if s.code == "FANZA"), None)
        assert fanza_site is not None

        assert len(fanza_site.services) > 0

        monthly_service = next(
            (svc for svc in fanza_site.services if svc.code == "monthly"), None
        )
        assert monthly_service is not None
        assert "月額動画" in monthly_service.name

    def test_get_floors_floor_count(self, dmm_client: DMMClient) -> None:
        """Test total floor count across all sites."""

        sites: List[Site] = dmm_client.get_floors()

        total_floors = sum(
            len(service.floors) for site in sites for service in site.services
        )

        assert total_floors > 0

    def test_get_floors_consistency(self, dmm_client: DMMClient) -> None:
        """Test consistency of multiple floor list calls."""

        first_call: List[Site] = dmm_client.get_floors()
        second_call: List[Site] = dmm_client.get_floors()

        assert len(first_call) == len(second_call)

        for first_site, second_site in zip(first_call, second_call):
            assert first_site.code == second_site.code
            assert first_site.name == second_site.name
            assert len(first_site.services) == len(second_site.services)

    def test_client_context_manager_floors(self, app_id: str, aff_id: str) -> None:
        """Test client as context manager with floor list retrieval."""

        with DMMClient(api_key=app_id, affiliate_id=aff_id) as client:
            sites: List[Site] = client.get_floors()
            assert isinstance(sites, list)
            assert len(sites) > 0

    def test_get_floors_ebook_floors(self, dmm_client: DMMClient) -> None:
        """Test ebook service floors."""

        sites: List[Site] = dmm_client.get_floors()

        dmm_site = next((s for s in sites if s.code == "DMM.com"), None)
        assert dmm_site is not None

        ebook_service = next(
            (svc for svc in dmm_site.services if svc.code == "ebook"), None
        )
        assert ebook_service is not None

        comic_floor = next((f for f in ebook_service.floors if f.code == "comic"), None)
        assert comic_floor is not None
        assert "コミック" in comic_floor.name

    def test_get_floors_mono_service(self, dmm_client: DMMClient) -> None:
        """Test mono (retail) service."""

        sites: List[Site] = dmm_client.get_floors()

        fanza_site = next((s for s in sites if s.code == "FANZA"), None)
        assert fanza_site is not None

        mono_service = next(
            (svc for svc in fanza_site.services if svc.code == "mono"), None
        )
        assert mono_service is not None
        assert "通販" in mono_service.name

        dvd_floor = next((f for f in mono_service.floors if f.code == "dvd"), None)
        assert dvd_floor is not None

    def test_get_floors_complete_hierarchy(self, dmm_client: DMMClient) -> None:
        """Test complete site-service-floor hierarchy."""

        sites: List[Site] = dmm_client.get_floors()

        assert len(sites) == 2

        for site in sites:
            assert site.code in ["DMM.com", "FANZA"]
            assert len(site.services) > 0

            for service in site.services:
                assert len(service.floors) > 0

                for floor in service.floors:
                    assert len(floor.id) > 0
                    assert len(floor.name) > 0
                    assert len(floor.code) > 0

    def test_error_missing_result_field(self, dmm_client: DMMClient) -> None:
        """Test error handling when API response is missing result field."""

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"sites": [], "services": []}'
        mock_response.raise_for_status = MagicMock()

        # pylint: disable=W0212
        with patch.object(dmm_client._session, "get", return_value=mock_response):
            with pytest.raises(DMMAPIError) as exc_info:
                dmm_client.get_floors()

            assert "missing 'result' field" in str(exc_info.value)

    def test_error_generic_exception_wrapped(self, dmm_client: DMMClient) -> None:
        """Test that generic exceptions are wrapped in DMMAPIError."""

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"result": {"site": []}}'
        mock_response.raise_for_status = MagicMock()

        # pylint: disable=W0212
        with patch.object(dmm_client._session, "get", return_value=mock_response):
            with patch(
                "py_dmmjp.client.FloorListResponse.from_dict",
                side_effect=AttributeError("Missing attribute"),
            ):
                with pytest.raises(DMMAPIError) as exc_info:
                    dmm_client.get_floors()

                assert "Failed to get floors" in str(exc_info.value)
                assert "Missing attribute" in str(exc_info.value)
