"""Module for Audi vehicle classes."""

from __future__ import annotations

from typing import TYPE_CHECKING

from carconnectivity.attributes import BooleanAttribute, GenericAttribute
from carconnectivity.objects import GenericObject
from carconnectivity.vehicle import CombustionVehicle, ElectricVehicle, GenericVehicle, HybridVehicle

from carconnectivity_connectors.audi.capability import Capabilities
from carconnectivity_connectors.audi.charging import AudiCharging
from carconnectivity_connectors.audi.climatization import AudiClimatization

SUPPORT_IMAGES = False
try:
    from PIL import Image

    SUPPORT_IMAGES = True
except ImportError:
    pass

if TYPE_CHECKING:
    from typing import Dict, Optional

    from carconnectivity.garage import Garage
    from carconnectivity_connectors.base.connector import BaseConnector


class GarageRawAPI(GenericObject):
    """
    Container for raw API responses from Audi Connect endpoints at garage level.

    This provides access to the raw JSON responses from different API endpoints
    through standardized paths like /garage/rawAPI/vehicles.
    """

    def __init__(self, garage) -> None:
        super().__init__(object_id="rawAPI", parent=garage)

        # Raw API response storage for garage-level endpoints
        self.vehicles = GenericAttribute("vehicles", self, value=None, tags={"connector_custom", "rawapi"})


class RawAPI(GenericObject):
    """
    Container for raw API responses from Audi Connect endpoints.

    This provides access to the raw JSON responses from different API endpoints
    through standardized paths like /rawAPI/selectivestatus or /rawAPI/parkingposition.
    """

    def __init__(self, vehicle: AudiVehicle) -> None:
        super().__init__(object_id="rawAPI", parent=vehicle)

        # Raw API response storage - vehicle-specific endpoints only
        self.selectivestatus = GenericAttribute("selectivestatus", self, value=None, tags={"connector_custom", "rawapi"})
        self.parkingposition = GenericAttribute("parkingposition", self, value=None, tags={"connector_custom", "rawapi"})
        self.vehicle_images = GenericAttribute("vehicle_images", self, value=None, tags={"connector_custom", "rawapi"})


class AudiVehicle(GenericVehicle):  # pylint: disable=too-many-instance-attributes
    """
    A class to represent a generic Audi vehicle.

    Attributes:
    -----------
    vin : StringAttribute
        The vehicle identification number (VIN) of the vehicle.
    license_plate : StringAttribute
        The license plate of the vehicle.
    """

    def __init__(
        self,
        vin: Optional[str] = None,
        garage: Optional[Garage] = None,
        managing_connector: Optional[BaseConnector] = None,
        origin: Optional[AudiVehicle] = None,
    ) -> None:
        if origin is not None:
            super().__init__(garage=garage, origin=origin)
            self.capabilities: Capabilities = origin.capabilities
            self.capabilities.parent = self
            self.is_active: BooleanAttribute = origin.is_active
            self.is_active.parent = self
            self.rawAPI: RawAPI = origin.rawAPI
            self.rawAPI.parent = self
            if SUPPORT_IMAGES:
                self._car_images = origin._car_images
        else:
            super().__init__(vin=vin, garage=garage, managing_connector=managing_connector)
            self.capabilities: Capabilities = Capabilities(vehicle=self)
            self.climatization = AudiClimatization(vehicle=self, origin=self.climatization)
            self.is_active = BooleanAttribute(name="is_active", parent=self, tags={"connector_custom"})
            self.rawAPI: RawAPI = RawAPI(vehicle=self)
            if SUPPORT_IMAGES:
                self._car_images: Dict[str, Image.Image] = {}
        self.manufacturer._set_value(value="Audi")  # pylint: disable=protected-access


class AudiElectricVehicle(ElectricVehicle, AudiVehicle):
    """
    Represents an Audi electric vehicle.

    This class uses multiple inheritance from ElectricVehicle and AudiVehicle.
    The super().__init__() call properly initializes all parent classes through
    Python's Method Resolution Order (MRO).

    MRO for AudiElectricVehicle:
    1. AudiElectricVehicle
    2. ElectricVehicle
    3. AudiVehicle
    4. GenericVehicle
    5. GenericObject
    6. object

    The super().__init__() call ensures proper initialization of all parent classes.
    """

    def __init__(
        self,
        vin: Optional[str] = None,
        garage: Optional[Garage] = None,
        managing_connector: Optional[BaseConnector] = None,
        origin: Optional[AudiVehicle] = None,
    ) -> None:
        # Initialize parent classes through MRO - always call super().__init__()
        # CodeQL requires this call to be made in all code paths
        if origin is not None:
            # Initialize with origin-based parameters
            super().__init__(garage=garage, origin=origin)
            # Set up Audi-specific charging with origin
            if isinstance(origin, ElectricVehicle):
                self.charging = AudiCharging(vehicle=self, origin=origin.charging)
            else:
                self.charging = AudiCharging(vehicle=self, origin=self.charging)
        else:
            # Initialize with direct parameters
            super().__init__(vin=vin, garage=garage, managing_connector=managing_connector)
            # Set up Audi-specific charging without origin
            self.charging = AudiCharging(vehicle=self, origin=self.charging)


class AudiCombustionVehicle(CombustionVehicle, AudiVehicle):
    """
    Represents an Audi combustion vehicle.

    This class uses multiple inheritance from CombustionVehicle and AudiVehicle.
    The super().__init__() call properly initializes all parent classes through
    Python's Method Resolution Order (MRO).

    MRO for AudiCombustionVehicle:
    1. AudiCombustionVehicle
    2. CombustionVehicle
    3. AudiVehicle
    4. GenericVehicle
    5. GenericObject
    6. object

    The super().__init__() call ensures proper initialization of all parent classes.
    """

    def __init__(
        self,
        vin: Optional[str] = None,
        garage: Optional[Garage] = None,
        managing_connector: Optional[BaseConnector] = None,
        origin: Optional[AudiVehicle] = None,
    ) -> None:
        # Initialize parent classes through MRO - always call super().__init__()
        # CodeQL requires this call to be made in all code paths
        if origin is not None:
            # Initialize with origin-based parameters
            super().__init__(garage=garage, origin=origin)
        else:
            # Initialize with direct parameters
            super().__init__(vin=vin, garage=garage, managing_connector=managing_connector)


class AudiHybridVehicle(HybridVehicle, AudiElectricVehicle, AudiCombustionVehicle):
    """
    Represents an Audi hybrid vehicle.

    This class uses multiple inheritance from HybridVehicle, AudiElectricVehicle, and AudiCombustionVehicle.
    The super().__init__() call properly initializes all parent classes through
    Python's Method Resolution Order (MRO).

    MRO for AudiHybridVehicle:
    1. AudiHybridVehicle
    2. HybridVehicle
    3. AudiElectricVehicle
    4. ElectricVehicle
    5. AudiCombustionVehicle
    6. CombustionVehicle
    7. AudiVehicle
    8. GenericVehicle
    9. GenericObject
    10. object

    The super().__init__() call ensures proper initialization of all parent classes.
    """

    def __init__(
        self,
        vin: Optional[str] = None,
        garage: Optional[Garage] = None,
        managing_connector: Optional[BaseConnector] = None,
        origin: Optional[AudiVehicle] = None,
    ) -> None:
        # Initialize parent classes through MRO - always call super().__init__()
        # CodeQL requires this call to be made in all code paths
        if origin is not None:
            # Initialize with origin-based parameters
            super().__init__(garage=garage, origin=origin)
        else:
            # Initialize with direct parameters
            super().__init__(vin=vin, garage=garage, managing_connector=managing_connector)
