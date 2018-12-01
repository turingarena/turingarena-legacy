from collections import namedtuple
from enum import Enum

ReferenceDirection = Enum("ReferenceDirection", names=["DOWNWARD", "UPWARD"])

ReferenceDefinition = namedtuple("ReferenceDefinition", ["reference", "dimensions"])
ReferenceResolution = namedtuple("ReferenceResolution", ["reference"])

VariableDeclaration = namedtuple("VariableDeclaration", ["variable", "dimensions"])
ReferenceAllocation = namedtuple("ReferenceAllocation", ["reference", "dimensions", "size"])
