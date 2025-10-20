
# Survivor Optimizer

**Author:** Arif Yelği  
**Journal:** Ain Shams Engineering Journal, 2025  
**DOI:** [https://doi.org/10.1016/j.asej.2025.103561](https://doi.org/10.1016/j.asej.2025.103561)

## Description
The Survivor Optimizer is a competitive, survival-based metaheuristic algorithm that balances exploration and exploitation to achieve high search efficiency.

## Installation
```
pip install survivor-optimizer
```

## Example Usage
```python
from survivor_optimizer import Survivor
import numpy as np

def sphere(x):
    return np.sum(x**2)

params = {'npop':50, 'itermax':200, 'wdamp':0.99}
optimizer = Survivor(problem=sphere, nvar=5, xmin=-100, xmax=100, params=params, SF=1, LF=5)
EFN, mincost, minlocation, Curv_best_local, Curv_best_global = optimizer.update_swarm()

print("Best cost:", mincost)
print("Best location:", minlocation)
```
