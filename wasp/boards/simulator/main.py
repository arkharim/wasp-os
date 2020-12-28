# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

import wasp

#Add here your apps

from apps.configurable_clock import ConfigurableClockApp
wasp.system.register(ConfigurableClockApp())

from apps.analog import AnalogueClockApp
wasp.system.register(AnalogueClockApp())
#
from apps.chrono24 import Chrono24App
wasp.system.register(Chrono24App())

from apps.configurable_clock_slow import ConfigurableClockAppSlow
wasp.system.register(ConfigurableClockAppSlow())

# no va
# from apps.chrono import Chrono3App
# wasp.system.register(Chrono3App())

# from apps.chrono20 import Chrono20App
# wasp.system.register(Chrono20App())



wasp.system.run()
