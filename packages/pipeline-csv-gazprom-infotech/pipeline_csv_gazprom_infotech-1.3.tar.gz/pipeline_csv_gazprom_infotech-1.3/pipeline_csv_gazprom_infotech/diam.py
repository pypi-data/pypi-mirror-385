"""Pipeline diameter change stuff."""


class InfotechDiam:
    """Diameter change Infotech codes."""

    D_1400_1200 = "6587149"
    D_1200_1000 = "6587146"
    D_1000_820 = "9708282"
    D_400_350 = "9097980"
    D_400_325 = "8566293"
    D_300_273 = "8541004"
    D_300_250 = "7636620"

    D_250_300 = "7636648"
    D_273_300 = "8541006"
    D_325_400 = "8566296"
    D_350_400 = "9097977"
    D_800_1000 = "9708285"
    D_1000_1200 = "6587147"
    D_1200_1400 = "6587148"


class DiamChange:
    """Diameter change class."""

    def __init__(self, code, name, start, end):
        """Set border parameters."""
        self.code = code
        self.name = name
        self.start_max, self.start_min = start
        self.end_max, self.end_min = end

    def get_code(self, start, end):
        """Return Infotech code for given diameter change parameters or None if not fit."""
        if (self.start_min <= start <= self.start_max) and (self.end_min <= end <= self.end_max):
            return (self.code, self.name)
        return None


D_1400 = (1500, 1300)
D_1200 = (1300, 1100)
D_1000 = (1100, 900)
D_800 = (900, 600)
D_400 = (600, 380)
D_350 = (380, 340)
D_325 = (340, 310)
D_300 = (310, 290)
D_273 = (290, 260)
D_250 = (260, 1)

DIAM_DECREASE = [
  DiamChange(InfotechDiam.D_1400_1200, "Переход с диаметра ДУ 1400 мм на ДУ 1200 мм", D_1400, D_1200),
  DiamChange(InfotechDiam.D_1200_1000, "Переход с диаметра ДУ 1200 мм на ДУ 1000 мм", D_1200, D_1000),
  DiamChange(InfotechDiam.D_1000_820, "Переход с диаметра ДУ1000 мм на ДУ820 мм", D_1000, D_800),
  DiamChange(InfotechDiam.D_400_350, "Переход с диаметра ДУ 400 мм на ДУ 350 мм", D_400, D_350),
  DiamChange(InfotechDiam.D_400_325, "Переход с диаметра ДУ 400 мм на ДУ 325 мм", D_400, D_325),
  DiamChange(InfotechDiam.D_300_273, "Переход с диаметра ДУ 300 мм на ДУ 273 мм", D_300, D_273),
  DiamChange(InfotechDiam.D_300_250, "Переход с диаметра ДУ 300 мм на ДУ 250 мм", D_300, D_250),
]
DIAM_INCREASE = [
  DiamChange(InfotechDiam.D_1200_1400, "Переход с диаметра ДУ 1200 мм на ДУ 1400 мм", D_1200, D_1400),
  DiamChange(InfotechDiam.D_1000_1200, "Переход с диаметра ДУ 1000 мм на ДУ 1200 мм", D_1000, D_1200),
  DiamChange(InfotechDiam.D_800_1000, "Переход с диаметра ДУ800 мм на ДУ1000 мм", D_800, D_1000),
  DiamChange(InfotechDiam.D_350_400, "Переход с диаметра ДУ 350 мм на ДУ 400 мм", D_350, D_400),
  DiamChange(InfotechDiam.D_325_400, "Переход с диаметра ДУ 325 мм на ДУ 400 мм", D_325, D_400),
  DiamChange(InfotechDiam.D_273_300, "Переход с диаметра ДУ 273 мм на ДУ 300 мм", D_273, D_300),
  DiamChange(InfotechDiam.D_250_300, "Переход с диаметра ДУ 250 мм на ДУ 300 мм", D_250, D_300),
]
