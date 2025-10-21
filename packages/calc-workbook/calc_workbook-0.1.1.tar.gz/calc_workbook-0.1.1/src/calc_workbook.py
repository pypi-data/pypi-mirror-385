import re
from typing import Any, Dict, Union, List
import formulas


class CalcSheet:
    def __init__(self, name: str, cells: Dict[str, Any]):
        self.name = name
        self._cells = {self._norm_name_ref(k): v for k, v in cells.items()}
        self._rows = max((int(re.findall(r"\d+", k)[0]) for k in self._cells), default=0)
        self._cols = max((self._col_to_idx(re.findall(r"[A-Z]+", k)[0]) for k in self._cells),
                         default=0)

    def _col_to_idx(self, col: str) -> int:
        return sum((ord(c) - 64) * 26 ** i for i, c in enumerate(reversed(col.upper())))

    def _idx_to_col(self, idx: int) -> str:
        col = ""
        while idx > 0:
            idx, remainder = divmod(idx - 1, 26)
            col = chr(65 + remainder) + col
        return col

    def _norm_name_ref(self, ref: str) -> str:
        ref = ref.replace("$", "")
        m = re.fullmatch(r"([A-Za-z]+)(\d+)", ref)
        if not m:
            raise ValueError(f"Invalid cell ref: {ref}")
        return f"{m.group(1).upper()}{int(m.group(2))}"

    def rows(self) -> int:
        return self._rows

    def cols(self) -> int:
        return self._cols

    def cell(self, ref: Union[str, List[int], tuple]) -> Any:
        if isinstance(ref, (list, tuple)):
            col = self._idx_to_col(int(ref[0]))
            row = int(ref[1])
            ref = f"{col}{row}"
        else:
            ref = self._norm_name_ref(ref)
        return self._cells.get(ref)


class CalcWorkbook:
    def __init__(self):
        self._sheets: Dict[str, CalcSheet] = {}

    def _norm_name_ref(self, ref: str) -> str:
        ref = ref.replace("$", "")
        m = re.fullmatch(r"([A-Za-z]+)(\d+)", ref)
        if not m:
            raise ValueError(f"Invalid cell ref: {ref}")
        return f"{m.group(1).upper()}{int(m.group(2))}"

    @classmethod
    def load(cls, filename: str) -> "CalcWorkbook":
        self = cls()
        xl = formulas.ExcelModel().loads(filename).finish()
        solution = xl.calculate()
        sheets: Dict[str, Dict[str, Any]] = {}
        for k, cell in solution.items():
            m = re.match(r"^'\[(?P<file>.*?)\](?P<sheet>.*?)'!(?P<ref>\$?[A-Za-z]+\$?\d+)$", k)
            if not m:
                continue
            sheet = m.group("sheet").lower()
            ref = self._norm_name_ref(m.group("ref"))
            value = cell.value[0][0] if hasattr(cell, "value") else None
            sheets.setdefault(sheet, {})[ref] = value
        for sheet_name, sheet_cells in sheets.items():
            self._sheets[sheet_name] = CalcSheet(sheet_name, sheet_cells)
        return self

    def get_sheet_names(self) -> List[str]:
        return list(self._sheets.keys())

    def get_sheet(self, name: str = None) -> CalcSheet:
        if name is None:
            if not self._sheets:
                raise ValueError("No sheets available.")
            name = next(iter(self._sheets))
        return self._sheets[name.lower()]
