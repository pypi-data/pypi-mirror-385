import re
import numpy as np


class STUIRTParser:
    """Parser for STUIRT output files (e.g. `.cc`, `.cc01`, `.cc.out`)

    References
    ----------
    Kim S, Kolen MJ (2004). STUIRT: A Computer Program for Scale Transformation under Unidimensional Item Response Theory Models. University of Iowa. Version 1.0, http://www.education.uiowa.edu/casma/computer_programs.htm#irt.
    """

    def __init__(self, filepath: str):
        self.filepath = filepath
        if filepath.endswith(".cc") or filepath.endswith(".cc01"):
            self.lines = self._load_cc()
            self.filetype = "cc"
        elif filepath.endswith(".out"):
            self.lines = self._load_cc()
            self.filetype = "ccout"
        else:
            raise TypeError(f"unsupport file type: {filepath}")

    def _load_cc(self) -> list:
        with open(self.filepath, "r") as f:
            lines = f.readlines()
        if len(lines) == 0:
            raise ValueError(f"empty file: {self.filepath}")
        return lines

    def get_quadrature(self) -> tuple:
        """get nodes and weights from cc file"""
        assert self.filetype == "cc"
        old_idx = next(i for i, line in enumerate(self.lines) if "OD 41 SE DI" in line)
        new_idx = next(i for i, line in enumerate(self.lines) if "ND 41 SE DI" in line)
        end_idx = next(i for i, line in enumerate(self.lines) if "SY NO NO" in line)

        old_quadrature = self.lines[old_idx + 1 : new_idx - 2]
        new_quadrature = self.lines[new_idx + 1 : end_idx - 2]

        def clean_txt(txt: str):
            txt = txt.replace("\n", "").strip()
            txt_ls = txt.split("       ")
            assert len(txt_ls) == 2
            return txt_ls

        old_nodes = list()
        old_weights = list()
        for line in old_quadrature:
            node, weight = clean_txt(line)
            old_nodes.append(float(node))
            old_weights.append(float(weight))
        assert len(old_nodes) == len(old_weights)

        new_nodes = list()
        new_weights = list()
        for line in new_quadrature:
            node, weight = clean_txt(line)
            new_nodes.append(float(node))
            new_weights.append(float(weight))
        assert len(new_nodes) == len(new_weights)

        return old_nodes, old_weights, new_nodes, new_weights

    def get_itemparameter(self, startkey_new="NE ", startkey_old="OL ") -> tuple:
        """get item parameters from cc file"""
        assert self.filetype == "cc"

        # find start idx and extract lines
        new_lines = self._extract_item_lines(startkey_new)
        old_lines = self._extract_item_lines(startkey_old)

        new_items = dict()
        for idx in range(len(new_lines)):
            new_items[idx] = self._parse_itemparam(new_lines[idx])

        old_items = dict()
        for idx in range(len(old_lines)):
            old_items[idx] = self._parse_itemparam(old_lines[idx])

        return old_items, new_items

    def get_scalingconst(self, startkey="===[Final") -> dict:
        """get scaling constants from cc.out file"""
        assert self.filetype == "ccout"
        start_idx = next(i for i, line in enumerate(self.lines) if startkey in line)

        result = dict()
        for i in range(0, 4):
            line = self.lines[start_idx + 3 + i]
            assert line[0] != " ", f"suspicious line: {line}"
            line = re.sub("\s+", " ", line.strip())
            line_ls = line.split(" ")
            assert len(line_ls) == 3, f"invalid line: {line_ls}"
            result[line_ls[0]] = (float(line_ls[1]), float(line_ls[2]))

        return result

    def _extract_item_lines(self, start_key: str) -> list:
        """Extract item parameter lines starting from a given key"""
        start_idx = next(i for i, line in enumerate(self.lines) if start_key in line)

        lines = list()
        for idx in range(start_idx + 1, len(self.lines)):
            if self.lines[idx].startswith("# "):
                lines.append(self.lines[idx])
            elif self.lines[idx].startswith("\n"):
                break
            else:
                raise ValueError(f"unsupport line, {idx}: {self.lines[idx]}")
        assert len(lines) > 0
        return lines

    def get_commonitemloc(self, startkey="CO ", endkey="OP") -> tuple:
        start_idx = next(i for i, line in enumerate(self.lines) if startkey in line)
        end_idx = next(i for i, line in enumerate(self.lines) if endkey in line)
        new_item_locs = list()
        old_item_locs = list()
        for line in self.lines[start_idx + 1 : end_idx]:
            if line == "\n":
                continue
            else:
                nums = line.split()
                assert len(nums) == 2, f"invalid nums: {line}"
                new_item_locs.append(int(nums[0]) - 1)  # due to 0-index
                old_item_locs.append(int(nums[1]) - 1)

        return new_item_locs, old_item_locs

    def _parse_itemparam(self, item_line: str) -> dict:
        """parse item parameter line

        Parameters
        ----------
        item_line : str
            item parameter line

        Returns
        -------
        dict
            item parameter dictionary

        Notes
        -----
        - only 3PL and GPCM are supported
        """
        assert type(item_line) == str
        item_line = re.sub("\s+", " ", item_line.strip())

        item_line_ls = item_line.split(" ")
        if "L3" in item_line_ls:
            model = "3PL"
        elif "MU" in item_line_ls:
            mu_loc = item_line_ls.index("MU")
            if item_line_ls[mu_loc + 1] == "2":  # two category
                model = "3PL"
            else:
                model = "GPCM"
        else:
            raise ValueError(f"invalid item line: {item_line_ls}")

        param_start_loc = item_line_ls.index("1.7")
        params = item_line_ls[param_start_loc + 1 :]

        if model == "3PL":
            if len(params) == 2:
                return {"model": model, "a": float(params[0]), "b": float(params[1])}
            elif len(params) == 3:
                return {
                    "model": model,
                    "a": float(params[0]),
                    "b": float(params[1]),
                    "c": float(params[2]),
                }
            else:
                raise ValueError(f"invalid item line: {item_line_ls}")
        elif model == "GPCM":
            assert len(params) > 3, f"invalid item line: {item_line_ls}"
            #!# Todo. NAEA2024, G09, MAT, 일부 가교에서 MU인데 이분처럼 처리된 경우 있었음
            b_i = float(params[1])
            c_ls = [float(c) for c in params[2:]]
            b_ls = b_i - np.array(c_ls)
            return {"model": model, "a": float(params[0]), "b": b_ls}
