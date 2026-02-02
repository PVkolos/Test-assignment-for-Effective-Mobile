from enum import Enum
from .config import Roles

Role = Enum('Role', Roles().dict())
