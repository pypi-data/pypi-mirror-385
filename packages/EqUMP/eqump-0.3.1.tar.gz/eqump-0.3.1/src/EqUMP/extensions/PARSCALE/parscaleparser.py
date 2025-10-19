import os
import re
import numpy as np
import pandas as pd

class PARSCALEParser:
    """Parser for PARSCALE output files (e.g. `.PH2`)
    """
    ALLOWED_EXTENSIONS = [
        "PAR", "PH0", "PH1", "PH2"
    ]
    def __init__(self, filepath: str):
        self.filepath = filepath
        if not any(filepath.endswith(ext) for ext in self.ALLOWED_EXTENSIONS):
            raise TypeError(f"unsupport file type: {filepath}")
        self.lines = self._load_file()

    def _load_file(self) -> list:
        with open(self.filepath, "r") as f:
            lines = f.readlines()
        if len(lines) == 0:
            raise ValueError(f"empty file: {self.filepath}")
        return lines

    def summarize_estimation_result(self):
        pass

class PARHandler:
    """Handler for PARSCALE output files (e.g. `.PH2`)
    
    Notes
    -----
    only 2PL, 3PL, GPCM are supported
    """
    def __init__(self, lines: list):
        if not self._validate_lines(lines):
            raise ValueError("lines must not be empty")
        self.lines = [line for line in lines if line.strip()]
    
    @staticmethod
    def _validate_lines(lines: list):
        if not isinstance(lines, list):
            raise TypeError(f"lines must be a list, not {type(lines)}")
        if len(lines) == 0:
            raise ValueError("lines must not be empty")

        return True
    
    def parse_itemblock(self):
        start_loc = self._find_itemblock_startloc()
        itemblock_lines = self.lines[start_loc:]

        itemblocks = list()
        for idx in range(len(itemblock_lines)/3):
            itemblocks.append(itemblock_lines[idx*3:(idx+1)*3])

        itemblocks_parsed = dict()
        for itemblock in itemblocks:
            k, params = self._parse_itemparam(itemblock)
            itemblocks_parsed[k] = params
        return itemblocks_parsed

    def _find_itemblock_startloc(self):
        start_loc = None
        for i, line in enumerate(self.lines):
            if line.startswith("GROUP 01"):
                start_loc = i + 1
                break
        
        # verification
        residual_lines = self.lines[start_loc:]
        if len(residual_lines) % 3 != 0:
            raise ValueError("residual lines must be multiple of 3")
        return start_loc

    def _parse_itemparam(self, itemblocks: list) -> tuple:
        if not len(itemblocks) == 3:
            raise ValueError("itemblocks must be multiple of 3")
        
        import re
        item_param = dict()
        # parse first line
        param_order = "a a.se b b.se c c.se".split()
        line1 = itemblocks[0]
        chunks = re.sub("\s+", " ", line1.strip()).split(" ")
        for param, chk in zip(param_order, chunks[2:]):
            if chk != "0.00000":
                item_param[param] = float(chk)
        item_id = chunks[0]
        
        # parse other lines
        line2 = itemblocks[1]
        line3 = itemblocks[2]
        chunks2 = re.sub("\s+", " ", line2.strip()).split(" ")
        chunks3 = re.sub("\s+", " ", line3.strip()).split(" ")
        if len(chunks2) != len(chunks3):
            raise ValueError("line2 and line3 must have the same length")
        if len(chunks2) > 7:
            raise ValueError("chunks more than 7 cannot be handled")
        
        if len(chunks2) == 2: # no step parameter
            return item_param
        
        for idx, (chk2, chk3) in enumerate(zip(chunks2, chunks3)):
            k2 = f"s{idx}"
            k3 = f"s{idx}.se"

            item_param[k2] = float(chk2)
            item_param[k3] = float(chk3)

        return item_id, item_param

class PH2Handler:
    """Handler for PARSCALE output files (e.g. `.PH2`)
    
    Notes
    -----
    only 2PL, 3PL, GPCM are supported
    """
    def __init__(self, lines: list):
        if not self._validate_lines(lines):
            raise ValueError("lines must not be empty")
        self.lines = [line for line in lines if line.strip()]

    @staticmethod
    def _validate_lines(lines: list):
        if not isinstance(lines, list):
            raise TypeError(f"lines must be a list, not {type(lines)}")
        if len(lines) == 0:
            raise ValueError("lines must not be empty")
        return True

    def parse_itemfit(self) -> dict():
        start_idx = 0
        for idx, line in enumerate(self.lines):
            if line.startswith(" |  BLOCK   | ITEM | "):
                start_idx = idx
                break

        end_idx = 0
        for idx, line in enumerate(self.lines[start_idx:]):
            if line.startswith(" |  TOTAL   |  "):
                end_idx = start_idx + idx
                break
        if start_idx == 0:
            raise ValueError(
                "Could not find item fit table start marker ' |  BLOCK   | ITEM | ' in PH2 file. "
                f"File may be malformed or incomplete. Total lines: {len(self.lines)}"
            )
        if end_idx == 0:
            raise ValueError(
                "Could not find item fit table end marker ' |  TOTAL   |  ' in PH2 file. "
                f"File may be malformed or incomplete. Start index found at: {start_idx}"
            )

        itemfit_blocks = self.lines[start_idx + 2 : end_idx - 1]
        itemfit_dict = dict()
        for block in itemfit_blocks:
            cleaned_block = [re.sub("\s+", "", val) for val in block.split("|")]
            cleaned_block = [
                val for val in cleaned_block if val != ""
            ] # remove empty space in list

            itemfit_dict[cleaned_block[0]] = {
                "chi.sq": float(cleaned_block[2]),
                "dof": float(cleaned_block[3]),
                "prob": float(cleaned_block[4])
            }
        return itemfit_dict

    def parse_quadrature(self) -> list:
        start_loc = 0
        for idx, line in enumerate(self.lines):
            if line.startswith(
                "                1           2           3           4           5"
            ):
                start_loc = idx + 1
                break

        end_loc = 0
        for idx, line in enumerate(self.lines[start_loc:]):
            if line.startswith(" TOTAL WEIGHT: 1.00000"):
                end_loc = start_loc + idx
                break
        assert end_loc > start_loc, f"{start_loc}, {end_loc}"
        assert self.lines[end_loc - 1] == "\n", f"{self.lines[end_loc - 1]}"
        assert self.lines[end_loc - 2] == "\n", f"{self.lines[end_loc - 2]}"
        quadrature_lines = self.lines[start_loc : end_loc - 2]
        assert (
            len(quadrature_lines) % 3 == 1
        ), f"it seems like lines are not well parsed, {len(quadrature_lines)}: {quadrature_lines}"

        """
        The section is divided by POINT & WEIGHT
        
        Example
        -------
        POINT    -0.xxxxE+xx -0.xxxxE+xx -0.xxxxE+xx -0.xxxxE+xx -0.xxxxE+xx
        WEIGHT    0.xxxxE-xx  0.xxxxE-xx  0.xxxxE-xx  0.xxxxE-xx  0.xxxxE-xx
        """
        flatted_lines = list()
        for idx, line in enumerate(quadrature_lines):
            if line.startswith(" POINT"):
                assert quadrature_lines[idx + 1].startswith(
                    " WEIGHT"
                ), f"{quadrature_lines[idx + 1]}"
                quadrature_section = line + quadrature_lines[idx + 1]
                flatted_lines.append(quadrature_section)
            else:
                continue

        qps = list()
        for section in flatted_lines:
            # for each section, maximum 5 quadrature points are available
            assert type(section) == str, f"{section}, {type(section)}"
            section_ls = [tkn for tkn in section.split("\n") if tkn != ""]
            assert len(section_ls) == 2, f"{section_ls}"
            point_line = section_ls[0].split()
            weight_line = section_ls[1].split()
            assert len(point_line) == len(weight_line), f"{point_line}, {weight_line}"

            for idx, (point, weight) in enumerate(zip(point_line, weight_line)):
                if idx == 0:
                    assert point == "POINT", f"{point}"
                    assert weight == "WEIGHT", f"{weight}"
                    continue
                qps.append((point, weight))
        
        return qps