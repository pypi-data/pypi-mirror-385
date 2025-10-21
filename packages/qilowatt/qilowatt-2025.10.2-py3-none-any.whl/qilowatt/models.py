from dataclasses import dataclass, field, fields
from typing import List, Optional
from datetime import datetime

@dataclass
class PingData:
    Reachable: bool = True

@dataclass
class ESP32Data:
    Temperature: float = 64.4  # Default value

@dataclass
class EnergyData:
    Power: List[float]
    Today: float
    Total: float
    Current: List[float]
    Voltage: List[float]
    Frequency: float

@dataclass
class MetricsData:
    PvPower: List[float]
    PvVoltage: List[float]
    PvCurrent: List[float]
    LoadPower: List[float]
    BatterySOC: int
    LoadCurrent: List[float]
    BatteryPower: List[float]
    BatteryCurrent: List[float]
    BatteryVoltage: List[float]
    GridExportLimit: float
    BatteryTemperature: List[float]
    InverterTemperature: float
    AlarmCodes: List[int] = field(default_factory=lambda: [0, 0, 0, 0, 0, 0])
    InverterStatus: int = 2  # Default value

@dataclass
class VersionData:
    API: str = "1.0"
    HA: str = "unknown"
    qilowatt_ha: str = "unknown"
    qilowatt_py: str = "unknown"

    def to_dict(self) -> dict:
        """Convert to dictionary with proper key names."""
        return {
            "API": self.API,
            "HA": self.HA,
            "qilowatt-ha": self.qilowatt_ha,
            "qilowatt-py": self.qilowatt_py,
        }

@dataclass
class WorkModeCommand:
    Mode: str = "normal"
    _source: Optional[str] = None
    BatterySoc: Optional[int] = None
    PowerLimit: Optional[int] = None
    PeakShaving: Optional[int] = None
    ChargeCurrent: Optional[int] = None
    DischargeCurrent: Optional[int] = None
    MaxPower: Optional[int] = None
    MxByPw: Optional[int] = None
    MxSlPw: Optional[int] = None
    # Container for any additional / unknown keys sent by device or API
    extras: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: dict) -> 'WorkModeCommand':
        if data is None:
            return cls()
        known = {f.name for f in fields(cls)} - {"extras"}
        kwargs = {k: v for k, v in data.items() if k in known}
        extras = {k: v for k, v in data.items() if k not in known}
        obj = cls(**kwargs)
        obj.extras = extras
        return obj

    def to_dict(self) -> dict:
        base = {k: getattr(self, k) for k in (
            "Mode", "_source", "BatterySoc", "PowerLimit", "PeakShaving",
            "ChargeCurrent", "DischargeCurrent", "MaxPower", "MxByPw", "MxSlPw"
        ) if getattr(self, k) is not None}
        # Merge extras without overwriting explicit attributes unless not set
        for k, v in self.extras.items():
            if k not in base:
                base[k] = v
        return base

    def __getattr__(self, item):
        # Allow attribute-style access to extras
        if item in self.extras:
            return self.extras[item]
        raise AttributeError(item)

    def __getitem__(self, item):
        return self.to_dict()[item]

@dataclass
class SensorData:
    ENERGY: EnergyData
    METRICS: MetricsData
    PING: PingData = field(default_factory=PingData)
    Time: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    ESP32: ESP32Data = field(default_factory=ESP32Data)
    VERSION: VersionData = field(default_factory=VersionData)
    TempUnit: str = "C"
    WORKMODE: Optional[WorkModeCommand] = None  # Will be set internally

    def to_dict(self) -> dict:
        """Convert the dataclass to a dictionary."""
        data = {
            "PING": self.PING.__dict__,
            "Time": self.Time,
            "ESP32": self.ESP32.__dict__,
            "ENERGY": self.ENERGY.__dict__,
            "METRICS": self.METRICS.__dict__,
            "VERSION": self.VERSION.to_dict(),
            "TempUnit": self.TempUnit,
            "WORKMODE": self.WORKMODE.to_dict() if self.WORKMODE else {},
        }
        return data

@dataclass
class StatusData:
    DeviceName: str
    FriendlyName: List[str]
    Topic: str

@dataclass
class StatusPRMData:
    StartupUTC: str
    BootCount: int

@dataclass
class StatusFWRData:
    Version: str
    Hardware: str

@dataclass
class StatusLOGData:
    TelePeriod: int

@dataclass
class StatusNETData:
    Hostname: str
    IPAddress: str
    Gateway: str
    Subnetmask: str
    Mac: str
    DNSServer1: Optional[str] = None
    DNSServer2: Optional[str] = None

@dataclass
class StatusMQTData:
    MqttHost: str
    MqttPort: int
    MqttClient: str
    MqttUser: str
    MqttCount: Optional[int] = None
    MqttClientMask: Optional[str] = None

@dataclass
class StatusTIMData:
    UTC: str
    Local: str
    StartDST: Optional[str] = None
    EndDST: Optional[str] = None
    Timezone: Optional[int] = None

@dataclass
class Status0Data:
    Status: StatusData
    StatusPRM: StatusPRMData
    StatusFWR: StatusFWRData
    StatusLOG: StatusLOGData
    StatusNET: StatusNETData
    StatusMQT: StatusMQTData
    StatusTIM: StatusTIMData

    def to_dict(self) -> dict:
        return {
            "Status": self.Status.__dict__,
            "StatusPRM": self.StatusPRM.__dict__,
            "StatusFWR": self.StatusFWR.__dict__,
            "StatusLOG": self.StatusLOG.__dict__,
            "StatusNET": self.StatusNET.__dict__,
            "StatusMQT": self.StatusMQT.__dict__,
            "StatusTIM": self.StatusTIM.__dict__,
        }