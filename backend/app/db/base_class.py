
from typing import Any
from sqlalchemy.ext.declarative import as_declarative, declared_attr
import re

@as_declarative()
class Base:
    id: Any
    __name__: str
    
    # Generate tablename automatically from class name
    @declared_attr
    def __tablename__(cls) -> str:
        # Convert CamelCase to snake_case
        name = re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()
        return name
