# EqUMP
IRT Equating for Unidimensional Mixed Format Test with Python

## Motivation
Item Respone Theory (IRT) test equating is a critical process for maintaining score comparability across different test forms. However, current implementations often rely on limited software or complex scripting environments. We introduce EqUMP, a Python package designed to streamline and democratize IRT equating for unidimensional mixed format test. Built upon the robust ecosystem of scientific computing in Python (Numpy, Scipy), it provides a flexible framework for various IRT equating methods (e.g., scale transformation, true score equating). The package is openly licensed, pip-installable, and includes comprehensive documentation and test suites, enabling researchers and practitioners to readily reproduce analysis pipelines. By leveraging Python’s accessibility and extensibility, EqUMP facilitates rigorous and reproducible test equating for a wider educational data analysists and psychometricians.

## Core Principles
- **Academically faithful code and documentation**  
  EqUMP is designed for researchers and practitioners familiar with standard test equating literature. We follow textbook-style notation and structure—even at the cost of computational speed—to ensure clarity and pedagogical value.

- **Practical focus**  
  While many equating methods exist in the literature, some are infeasible in operational testing. EqUMP prioritizes features that reflect real-world usage and operational constraints. Users can request or contribute less common methods.

- **Symmetric linking constant support**  
  Symmetry property of equating function is a critical but often neglected aspect of Haebara or Stocking-Lord linking method. EqUMP handles this through carefully implemented two-sided(symmtric) or one-sided loss function.

## Installation
```bash
pip install EqUMP
```

## Compared to other related packages
- Before we create this package, we analyze the packages below
- As far as we know, there are no Python-based IRT Test Equating packages.
- We found some R packages and commercial programs below. And summarize their features in the table below.

| Package/Program | Author | Category | scale-linking | true-score | observed-score | kernel | link |
|-----------------|--------|----------|---------------|------------|----------------|--------|--------|
| STUIRT | Kim & Kolen, 2004 | Standalone | O | X | X | X | [download](https://education.uiowa.edu/casma/computer-programs) |
| POLYEQUATE | Kolen, 2004 | Standalone | X | O | O | X |  [download](https://education.uiowa.edu/casma/computer-programs)  |
| IRTEQ | Han, 2009 | Standalone | O | O | X | X | [homepage](http://www.hantest.net/irteq/) |
| kequate | Andersson et al., 2013 | R | O | X | O | O | [cran](https://cran.r-project.org/web/packages/kequate/index.html) |
| equateIRT | Battauz, 2015 | R | O | O | O | X | [cran](https://cran.r-project.org/web/packages/equateIRT/index.html) |
| SNSequate | Jorge Gonzalez, 2024 | R | O | O | O | O |  [download](https://cran.r-project.org/web/packages/SNSequate/index.html)  

## Core API
### Item Response Model
```python
from EqUMP.base import IRF
# Dichotomous item
item_2pl = IRF(params={"a": 1.2, "b": 0.5}, model="2PL")
probs = item_2pl.prob(theta=0.0)
print(probs)
    
# Polytomous item with custom scores
item_gpcm = IRF(
    params={"a": 1.0, "b": [-0.5, 0.0, 0.5]},
    model="GPCM",
    scores=[0, 2, 5, 10]
)
expected = item_gpcm.expected_score(theta=0.0)
```

### Scale Transformation
#### Mean-Mean
```python
from EqUMP.base import IRF
from EqUMP.linking import mean_mean

# Create IRF objects for new and old forms
items_new = {
    1: IRF({"a": 1.2, "b": 0.5}, "2PL"),
    2: IRF({"a": 1.0, "b": -0.3}, "2PL"),
    3: IRF({"a": 1.5, "b": 0.8}, "2PL"),
}
items_old = {
    1: IRF({"a": 1.15, "b": 0.48}, "2PL"),
    2: IRF({"a": 0.95, "b": -0.28}, "2PL"),
    3: IRF({"a": 1.45, "b": 0.85}, "2PL"),
}

A, B = mean_mean(
    items_new=items_new,
    items_old=items_old,
    common_new=[1, 2, 3],
    common_old=[1, 2, 3],
)
print(f"Linking constants: A={A:.4f}, B={B:.4f}")
```

#### Mean-Sigma
```python
from EqUMP.base import IRF
from EqUMP.linking import mean_sigma

# Create IRF objects for new and old forms
items_new = {
    1: IRF({"a": 1.2, "b": 0.5}, "2PL"),
    2: IRF({"a": 1.0, "b": -0.3}, "2PL"),
    3: IRF({"a": 1.5, "b": 0.8}, "2PL"),
}
items_old = {
    1: IRF({"a": 1.15, "b": 0.48}, "2PL"),
    2: IRF({"a": 0.95, "b": -0.28}, "2PL"),
    3: IRF({"a": 1.45, "b": 0.85}, "2PL"),
}

A, B = mean_sigma(
    items_new=items_new,
    items_old=items_old,
    common_new=[1, 2, 3],
    common_old=[1, 2, 3],
)
print(f"Linking constants: A={A:.4f}, B={B:.4f}")
```

#### Haebara
```python
import numpy as np
from EqUMP.base import IRF
from EqUMP.linking import haebara

# Create IRF objects with mixed item types
items_new = {
    1: IRF({"a": 1.2, "b": 0.5, "c": 0.2}, "3PL", D=1.7),
    2: IRF({"a": 1.0, "b": -0.3, "c": 0.15}, "3PL", D=1.7),
    3: IRF({"a": 1.0, "b": [-0.5, 0.0, 0.5]}, "GPCM", D=1.7),
}
items_old = {
    1: IRF({"a": 1.15, "b": 0.48, "c": 0.18}, "3PL", D=1.7),
    2: IRF({"a": 0.95, "b": -0.28, "c": 0.14}, "3PL", D=1.7),
    3: IRF({"a": 0.95, "b": [-0.48, 0.02, 0.52]}, "GPCM", D=1.7),
}

A, B = haebara(
    items_new=items_new,
    items_old=items_old,
    common_new=[1, 2, 3],
    common_old=[1, 2, 3],
    quadrature="gauss_hermite",
    nq=30,
    symmetry=True,
)
print(f"Linking constants: A={A:.4f}, B={B:.4f}")
```

#### Stocking-Lord
```python
import numpy as np
from EqUMP.base import IRF
from EqUMP.linking import stocking_lord

# Create IRF objects with mixed item types
items_new = {
    1: IRF({"a": 1.2, "b": 0.5, "c": 0.2}, "3PL", D=1.7),
    2: IRF({"a": 1.0, "b": -0.3, "c": 0.15}, "3PL", D=1.7),
    3: IRF({"a": 1.0, "b": [-0.5, 0.0, 0.5]}, "GPCM", D=1.7),
}
items_old = {
    1: IRF({"a": 1.15, "b": 0.48, "c": 0.18}, "3PL", D=1.7),
    2: IRF({"a": 0.95, "b": -0.28, "c": 0.14}, "3PL", D=1.7),
    3: IRF({"a": 0.95, "b": [-0.48, 0.02, 0.52]}, "GPCM", D=1.7),
}

A, B = stocking_lord(
    items_new=items_new,
    items_old=items_old,
    common_new=[1, 2, 3],
    common_old=[1, 2, 3],
    quadrature="gauss_hermite",
    nq=30,
    symmetry=True,
)
print(f"Linking constants: A={A:.4f}, B={B:.4f}")
```

### True Score Equating
```python
from EqUMP.base import IRF
from EqUMP.equating.TSE import tse

# Create IRF objects for new and old forms
items_new = {
    0: IRF({"a": 1.2, "b": -0.5}, "2PL"),
    1: IRF({"a": 1.0, "b": 0.0}, "2PL"),
    2: IRF({"a": 1.5, "b": 0.8}, "2PL"),
    3: IRF({"a": 0.9, "b": -1.2}, "2PL"),
}
items_old = {
    0: IRF({"a": 1.15, "b": -0.47}, "2PL"),
    1: IRF({"a": 0.95, "b": 0.05}, "2PL"),
    2: IRF({"a": 1.45, "b": 0.85}, "2PL"),
    3: IRF({"a": 0.85, "b": -1.15}, "2PL"),
}

# Equate a test score of 2.5 on the new form
ts = 2.5
theta_eq, score_old = tse(
    ts=ts,
    items_new=items_new,
    items_old=items_old,
    common_new=[0, 1, 2],
    common_old=[0, 1, 2],
    anchor="internal"
)
print(f"Theta estimate: {theta_eq:.4f}")
print(f"Equivalent score on old form: {score_old:.4f}")
```

### Observed Score Equating
```python
# in developing
```

### Kernel Methods
```python
# in developing
```

## How to contribute
`EqUMP` is actively being developed, and upcoming releases will include additional item response models and equating methods.
We welcome contributions of any kind—if you’d like to get involved, please check out our contribution [guidelines](https://github.com/huni1023/EqUMP/blob/main/CONTRIBUTE.md).

## How to cite
<pre>
  ```
  this section will be filled after publishing this package in a peer reviewed journal
  ```
</pre>

## Used by
following contents are not real at all. It's just our hope and vision
<table>
  <tr align="center">
    <td>
      <img src="" height="60"/><br/>
      <strong>fictitious company</strong><br/>
      scale linking, true score equating
    </td>
    <td>
      <img src="" height="60"/><br/>
      <strong>fictitious high school</strong><br/>
      item paramter estimation
    </td>
    <td>
      <img src="" height="60"/><br/>
      <strong>CBTManager</strong><br/>
      emulate scale linking, ploting
    </td>
  </tr>
</table>

> 💡 Want your organization featured? Open an [Issue](https://github.com/huni1023/eqump/issues/new) or [Pull Request](https://github.com/huni1023/eqump/pulls) to be listed.

## References
- [1] Kolen, M. J., & Brennan, R. L. (2014). Test equating, scaling, and linking: Methods and practices (3rd ed.). Springer Science + Business Media. [https://doi.org/10.1007/978-1-4939-0317-7.](https://doi.org/10.1007/978-1-4939-0317-7.)
- [2] 김성훈. (2022). 문항반응이론 검사 동등화. 공동체.
- [3] Andersson, B., Bränberg, K., & Wiberg, M. (2013). Performing the Kernel Method of Test Equating with the Package kequate. Journal of Statistical Software, 55(6), 1–25. https://doi.org/10.18637/jss.v055.i06
- [4] Battauz, M. (2015). equateIRT: An R Package for IRT Test Equating. Journal of Statistical Software, 68(7), 1–22. https://doi.org/10.18637/jss.v068.i0
