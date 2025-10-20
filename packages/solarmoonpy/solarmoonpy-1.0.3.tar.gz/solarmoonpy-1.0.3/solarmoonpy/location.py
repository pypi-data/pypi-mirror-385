from dataclasses import dataclass
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo
from typing import Optional, Union

from .sun import sunrise_sunset, noon  # Importar funciones de sun.py

@dataclass
class LocationInfo:
    """Clase para almacenar información básica de una ubicación."""
    name: str
    region: str
    timezone: str
    latitude: float
    longitude: float
    elevation: float = 0.0

class Location:
    """Proporciona acceso a información y cálculos para una ubicación específica."""

    def __init__(self, info: Optional[LocationInfo] = None):
        """
        Inicializa la ubicación con un objeto LocationInfo.

        Args:
            info: Objeto LocationInfo con los datos de la ubicación. Si es None,
                  se usa una ubicación por defecto (Greenwich).
        """
        if not info:
            self._location_info = LocationInfo(
                name="Greenwich",
                region="England",
                timezone="Europe/London",
                latitude=51.4733,
                longitude=-0.0008333,
                elevation=0.0
            )
        else:
            self._location_info = info

    def __repr__(self) -> str:
        """Representación en string de la ubicación."""
        if self.region:
            _repr = f"{self.name}/{self.region}"
        else:
            _repr = self.name
        return (
            f"{_repr}, tz={self.timezone}, "
            f"lat={self.latitude:0.02f}, "
            f"lon={self.longitude:0.02f}, "
            f"elev={self.elevation:0.02f}"
        )

    @property
    def name(self) -> str:
        """Nombre de la ubicación."""
        return self._location_info.name

    @name.setter
    def name(self, name: str) -> None:
        self._location_info = LocationInfo(
            name=name,
            region=self.region,
            timezone=self.timezone,
            latitude=self.latitude,
            longitude=self.longitude,
            elevation=self.elevation
        )

    @property
    def region(self) -> str:
        """Región de la ubicación."""
        return self._location_info.region

    @region.setter
    def region(self, region: str) -> None:
        self._location_info = LocationInfo(
            name=self.name,
            region=region,
            timezone=self.timezone,
            latitude=self.latitude,
            longitude=self.longitude,
            elevation=self.elevation
        )

    @property
    def latitude(self) -> float:
        """Latitud de la ubicación (grados, positivo para Norte)."""
        return self._location_info.latitude

    @latitude.setter
    def latitude(self, latitude: Union[float, str]) -> None:
        if isinstance(latitude, str):
            latitude = float(latitude)  # Simplificado, asumir formato decimal
        self._location_info = LocationInfo(
            name=self.name,
            region=self.region,
            timezone=self.timezone,
            latitude=latitude,
            longitude=self.longitude,
            elevation=self.elevation
        )

    @property
    def longitude(self) -> float:
        """Longitud de la ubicación (grados, positivo para Este)."""
        return self._location_info.longitude

    @longitude.setter
    def longitude(self, longitude: Union[float, str]) -> None:
        if isinstance(longitude, str):
            longitude = float(longitude)  # Simplificado, asumir formato decimal
        self._location_info = LocationInfo(
            name=self.name,
            region=self.region,
            timezone=self.timezone,
            latitude=self.latitude,
            longitude=longitude,
            elevation=self.elevation
        )

    @property
    def elevation(self) -> float:
        """Elevación de la ubicación (metros sobre el nivel del mar)."""
        return self._location_info.elevation

    @elevation.setter
    def elevation(self, elevation: float) -> None:
        self._location_info = LocationInfo(
            name=self.name,
            region=self.region,
            timezone=self.timezone,
            latitude=self.latitude,
            longitude=self.longitude,
            elevation=float(elevation)
        )

    @property
    def timezone(self) -> str:
        """Nombre de la zona horaria."""
        return self._location_info.timezone

    @timezone.setter
    def timezone(self, name: str) -> None:
        try:
            ZoneInfo(name)  # Validar que la zona horaria existe
            self._location_info = LocationInfo(
                name=self.name,
                region=self.region,
                timezone=name,
                latitude=self.latitude,
                longitude=self.longitude,
                elevation=self.elevation
            )
        except Exception as exc:
            raise ValueError(f"Zona horaria desconocida: {name}") from exc

    @property
    def tzinfo(self) -> ZoneInfo:
        """Objeto ZoneInfo para la zona horaria."""
        try:
            return ZoneInfo(self.timezone)
        except Exception as exc:
            raise ValueError(f"Zona horaria desconocida: {self.timezone}") from exc

    def sunrise(
        self,
        date: Optional[date] = None,
        local: bool = True,
        elevation: Optional[float] = None
    ) -> datetime:
        """
        Calcula la hora del amanecer.

        Args:
            date: Fecha para la cual calcular el amanecer. Si es None, usa la fecha actual.
            local: True para devolver la hora en la zona horaria local, False para UTC.
            elevation: Elevación del observador en metros. Si es None, usa self.elevation.

        Returns:
            Objeto datetime con la hora del amanecer.
        """
        if local and self.timezone is None:
            raise ValueError("Se solicitó hora local pero no se definió una zona horaria.")

        if date is None:
            date = datetime.now(self.tzinfo if local else timezone.utc).date()

        elevation = elevation if elevation is not None else self.elevation
        sunrise, _ = sunrise_sunset(
            latitude=self.latitude,
            longitude=self.longitude,
            date=date,
            elevation=elevation,
            timezone=self.tzinfo if local else timezone.utc,
            with_refraction=True
        )
        return sunrise

    def sunset(
        self,
        date: Optional[date] = None,
        local: bool = True,
        elevation: Optional[float] = None
    ) -> datetime:
        """
        Calcula la hora del atardecer.

        Args:
            date: Fecha para la cual calcular el atardecer. Si es None, usa la fecha actual.
            local: True para devolver la hora en la zona horaria local, False para UTC.
            elevation: Elevación del observador en metros. Si es None, usa self.elevation.

        Returns:
            Objeto datetime con la hora del atardecer.
        """
        if local and self.timezone is None:
            raise ValueError("Se solicitó hora local pero no se definió una zona horaria.")

        if date is None:
            date = datetime.now(self.tzinfo if local else timezone.utc).date()

        elevation = elevation if elevation is not None else self.elevation
        _, sunset = sunrise_sunset(
            latitude=self.latitude,
            longitude=self.longitude,
            date=date,
            elevation=elevation,
            timezone=self.tzinfo if local else timezone.utc,
            with_refraction=True
        )
        return sunset

    def noon(
        self,
        date: Optional[date] = None,
        local: bool = True
    ) -> datetime:
        """
        Calcula la hora del mediodía solar.

        Args:
            date: Fecha para la cual calcular el mediodía. Si es None, usa la fecha actual.
            local: True para devolver la hora en la zona horaria local, False para UTC.

        Returns:
            Objeto datetime con la hora del mediodía solar.
        """
        if local and self.timezone is None:
            raise ValueError("Se solicitó hora local pero no se definió una zona horaria.")

        if date is None:
            date = datetime.now(self.tzinfo if local else timezone.utc).date()

        return noon(
            longitude=self.longitude,
            date=date,
            timezone=self.tzinfo if local else timezone.utc
        )

    def sun_events(
        self,
        date: Optional[date] = None,
        local: bool = True,
        elevation: Optional[float] = None
    ) -> dict:
        """
        Devuelve un diccionario con sunrise, noon y sunset para una fecha dada.

        Args:
            date: Fecha para la cual calcular los eventos solares. Si es None, usa la fecha actual.
            local: True para devolver las horas en la zona horaria local, False para UTC.
            elevation: Elevación del observador en metros. Si es None, usa self.elevation.

        Returns:
            dict: {
                "sunrise": datetime,
                "noon": datetime,
                "sunset": datetime
            }
        """
        if local and self.timezone is None:
            raise ValueError("Se solicitó hora local pero no se definió una zona horaria.")

        tz = self.tzinfo if local else timezone.utc
        date = date or datetime.now(tz).date()
        elevation = elevation if elevation is not None else self.elevation

        # Calcular amanecer y atardecer
        sunrise, sunset = sunrise_sunset(
            latitude=self.latitude,
            longitude=self.longitude,
            date=date,
            elevation=elevation,
            timezone=tz,
            with_refraction=True,
        )

        # Calcular mediodía solar
        noon_time = noon(
            longitude=self.longitude,
            date=date,
            timezone=tz,
        )

        return {
            "sunrise": sunrise,
            "noon": noon_time,
            "sunset": sunset,
        }
