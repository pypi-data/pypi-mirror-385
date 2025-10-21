## CommoRoad IDM Planner
A simple IDM-based planner implementation as a baseline for benchmarking new planners. 

The implemented planner uses the concept of path-velocity-decomposition: first a path is planned and, then, 
a velocity profile is generated to avoid (dynamic) obstacles

By default, the planner uses the reference path planning module 
implemented in [CommonRoad-Route-Planner](https://cps.pages.gitlab.lrz.de/commonroad-route-planner/) to generate the path
on which, subsequently, a modified version of the Intelligent Driver Model (IDM) [1] is used to perform velocity planning.

In standard configuration, the planner only avoids dynamic obstacles, as it would wait indefinitely for static obstacles.

## Installation
This tool is available as pypi package using:
```
pip install commonroad-idm-planner
```

If you want to build it from source, make sure that you use the correct g++ version, as this is one fixed version
for all CommonRoad C++ project (e.g. the CommonRoad Curvilinear Coordinate System and the CommonRoad Drivability Checker).

## Documentation and Examples
The documentation can be found [here](https://commonroad-idm-planner-ddfe71.pages.gitlab.lrz.de/). 

A [module for standard use cases](https://commonroad-idm-planner-ddfe71.pages.gitlab.lrz.de/easy_api/) enables effortless integration.

## Integrated Models
- Intelligent Driver Models (IDM) [1]

## Author
Tobias Mascetta: tobias.mascetta[at]tum.de

## Source Code and Contribution
The original source code lives in a private gitlab repo. The official branches are mirrored to the [CommonRoad github](https://github.com/CommonRoad).
You can still issue pull requests, though, if you wish to contribute

## References
[1] Treiber, M., Hennecke, A., & Helbing, D. (2000). Congested traffic states in empirical observations and microscopic simulations. Physical review E, 62(2), 1805.