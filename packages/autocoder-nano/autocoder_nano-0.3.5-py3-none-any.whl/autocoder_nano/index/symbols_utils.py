import re
from typing import List

from autocoder_nano.actypes import SymbolsInfo, SymbolType


def extract_symbols(text: str) -> SymbolsInfo:
    patterns = {
        "usage": r"用途：(.+)",
        "functions": r"函数：(.+)",
        "variables": r"变量：(.+)",
        "classes": r"类：(.+)",
        "import_statements": r"导入语句：(.+)",
    }

    info = SymbolsInfo()
    for field, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            value = match.group(1).strip()
            if field == "import_statements":
                value = [v.strip() for v in value.split("^^")]
            elif field == "functions" or field == "variables" or field == "classes":
                value = [v.strip() for v in value.split(",")]
            setattr(info, field, value)

    return info


def symbols_info_to_str(info: SymbolsInfo, symbol_types: List[SymbolType]) -> str:
    result = []
    for symbol_type in symbol_types:
        value = getattr(info, symbol_type.value)
        if value:
            if symbol_type == SymbolType.IMPORT_STATEMENTS:
                value_str = "^^".join(value)
            elif symbol_type in [SymbolType.FUNCTIONS, SymbolType.VARIABLES, SymbolType.CLASSES,]:
                value_str = ",".join(value)
            else:
                value_str = value
            result.append(f"{symbol_type.value}：{value_str}")

    return "\n".join(result)