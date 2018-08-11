# Copyright 2014-present PlatformIO <contact@platformio.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Arduino

Arduino Wiring-based Framework allows writing cross-platform software to
control devices attached to a wide range of Arduino boards to create all
kinds of creative coding, interactive objects, spaces or physical experiences.

http://www.stm32duino.com
"""

from os.path import isdir, join
from platformio import util

env = DefaultEnvironment()
platform = env.PioPlatform()
board = env.BoardConfig()

FRAMEWORK_DIR = platform.get_package_dir("framework-arduinostm32l0")
assert isdir(FRAMEWORK_DIR)

mcu_type = board.get("build.mcu")[:-2]
variant = board.get("build.variant")
f_cpu = board.get("build.f_cpu")
ldscript = board.get("build.mcu").upper() + "_FLASH.ld"
startup_file = "startup_" + mcu_type + "xx.S"

# support a custom variants directory named in the platformio.ini's [platformio] section
print("VARIANT: " + variant)
avd = util.get_project_optional_dir("arduino_variants_dir")
variant_dir = join(FRAMEWORK_DIR, "variants", variant)
if avd and isdir(join(avd, variant)):
    variant_dir = join(avd, variant)
    print("VARIANT_DIR: " + variant_dir)

env.Append(
    CFLAGS=["-std=gnu11"],

    CXXFLAGS=["-std=gnu++11"],

    CCFLAGS=[
        "-MMD",
        "--param", "max-inline-insns-single=500",
        "-march=armv6-m", "-mabi=aapcs",
        "-mfloat-abi=soft", "-fsingle-precision-constant", ],

    CPPDEFINES=[
        ("_SYSTEM_CORE_CLOCK_", f_cpu),
        ("ARDUINO", 10610),
        ("ARDUINO_%s" % variant.upper().replace("-","_")),
        ("ARDUINO_ARCH_STM32L0"),
        ("__STM32L0__"),
        ("MCU_%s" % mcu_type.upper())
    ],

    CPPPATH=[
        join(FRAMEWORK_DIR, "system", "CMSIS", "Include"),
        join(FRAMEWORK_DIR, "system", "CMSIS", "Device", "ST", "STM32L0xx", "Include"),
        join(FRAMEWORK_DIR, "system", "STM32L0xx", "Include"),
        join(FRAMEWORK_DIR, "cores", "arduino"),
    ],

    LIBPATH=[
        join(FRAMEWORK_DIR, "system/STM32L0xx/Lib"),
        join(FRAMEWORK_DIR, "system/CMSIS/Lib"),
        join(variant_dir, "linker_scripts"),
    ],

    LIBS=["c", "stm32l082xx", "arm_cortexM0l_math"]
)

# remap ldscript
env.Replace(LDSCRIPT_PATH=ldscript)

# remove unused linker flags
for item in ("-nostartfiles", "-nostdlib"):
    if item in env['LINKFLAGS']:
        env['LINKFLAGS'].remove(item)

# remove unused libraries
for item in ("stdc++", "nosys"):
    if item in env['LIBS']:
        env['LIBS'].remove(item)

#
# Lookup for specific core's libraries
#

env.Append(
    LIBSOURCE_DIRS=[
        join(FRAMEWORK_DIR, "libraries")
    ]
)

#
# Target: Build Core Library
#

libs = []

if "build.variant" in board:
    env.Append(
        CPPPATH=[variant_dir],
        #PIOBUILDFILES=join(FRAMEWORK_DIR, "system", "STM32L0xx", "Source", startup_file)
    )
    libs.append(env.BuildLibrary(
        join("$BUILD_DIR", "FrameworkArduinoVariant"),
        variant_dir
    ))

libs.append(env.BuildLibrary(
    join("$BUILD_DIR", "FrameworkArduino"),
    join(FRAMEWORK_DIR, "cores", "arduino")
))

env.Prepend(LIBS=libs)
