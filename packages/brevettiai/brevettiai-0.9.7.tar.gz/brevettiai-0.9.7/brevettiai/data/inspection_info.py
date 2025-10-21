from enum import Enum
from typing import Dict


class CameraView(Enum):
    side = "side"
    low_angle = "low_angle"
    high_angle = "high_angle"
    top = "top"
    bottom = "bottom"


class InspectionType(Enum):
    particle_light = "particle_light"
    particle_dark = "particle_dark"
    discoloration = "discoloration"
    glass = "glass"
    plunger = "plunger"
    flange = "flange"
    aluseal = "aluseal"
    needleshield = "needleshield"
    stopper_neck = "stopper_neck"
    plunger_top = "plunger_top"
    glass_heel = "glass_heel"
    flipoff = "flipoff"
    glass_bottom = "glass_bottom"
    cake_top = "cake_top"
    NA = "NA"


inspection_view_map: Dict[InspectionType, CameraView] = {
    InspectionType.particle_light: CameraView.side,
    InspectionType.particle_dark: CameraView.side,
    InspectionType.discoloration: CameraView.side,
    InspectionType.glass: CameraView.side,
    InspectionType.plunger: CameraView.side,
    InspectionType.flange: CameraView.bottom,
    InspectionType.aluseal: CameraView.side,
    InspectionType.needleshield: CameraView.side,
    InspectionType.stopper_neck: CameraView.low_angle,
    InspectionType.plunger_top: CameraView.high_angle,
    InspectionType.glass_heel: CameraView.high_angle,
    InspectionType.flipoff: CameraView.top,
    InspectionType.glass_bottom: CameraView.bottom,
    InspectionType.cake_top: CameraView.high_angle
}
inspection_view_map = {k.value: v.value for k, v in inspection_view_map.items()}
