#!/usr/bin/env python3

"""Main."""

import sys
from cpu import *

cpu = CPU()

cpu.load(sys.argv[1])
# cpu.load('./examples/print8.ls8')

cpu.run()