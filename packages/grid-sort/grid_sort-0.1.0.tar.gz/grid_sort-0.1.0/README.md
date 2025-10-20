# Grid-Sort

Ever wondered how to sort points from top left to top right? This repository contains the code required to just that!

## Testing

Run the unit tests with the Python interpreter used in this environment. For many macOS setups use:

```
/usr/local/bin/python3 -m unittest tests.test_sort -v
```

Or discover all tests:

```
/usr/local/bin/python3 -m unittest discover -v
```

The repo includes `tests/test_sort.py` which covers the core behaviors of `sort.py`.

### Installation

To install the package in editable mode, run the following command in your terminal:

```
pip install -e .
```

### Example Usage

```python
from grid_sort import sort_by_xy, get_xy, set_xy
# Example usage
points = [...]  # your points here
sorted_points = sort_by_xy(points)
```

## Code Overview

The main functionality is in `sort.py`, which provides functions to sort objects based on their X and Y coordinates. The sorting logic considers a threshold to determine when to switch from sorting by Y to sorting by X.
Key functions include:

- `get_xy(obj)`: Retrieves the X and Y coordinates from an object.
- `set_xy(obj, x, y)`: Sets the X and Y coordinates on an
  object.
- `sort_by_xy(objs, threshold=2.0)`: Sorts a list of objects based on their coordinates, using a specified threshold to determine sorting behavior.
- `point_line_distance(x0, y0, x1, y1, x2, y2)`: Calculates the perpendicular distance from a point to a line segment.

## How it works

This algorithm is based off the research paper found [here](https://www.researchgate.net/publication/282446068_Automatic_chessboard_corner_detection_method). The algorithm works by performing the following computations in order

1. Find the top left most point (min (y - x))
2. Find the top right most point (max (x+y)). These points are allowed to be the same. 
3. Compute the line between these two points. 
4. For each point, compute the orthogonal distance to the line; [$ dist = \frac{ | a x_0 + b y_0 + c | }{\sqrt{a^2 + b^2}} $](https://en.wikipedia.org/wiki/Distance_from_a_point_to_a_line).

    If the distance is less than the specified threshold, sort by x coordinate.
5. Remove sorted points from the list and repeat until all points are sorted.

This results in a grid like sorting of points from top left to top right, then next row down, and so on. This process could easily be extrapolated to work for 3D points as well.

## Example Visualization

In this example you see we will have 3 seperate rows, each with a unique y value. The points are sorted from left to right within each row, and the rows are sorted from top to bottom.

![alt text](images/image.png)

### Notes

A few things to note: 
- The threshold value is crucial for determining how strictly the points are sorted into rows. A smaller threshold means points need to be closer to the line to be considered in the same row. 
- The algorithm assumes that the input points are roughly aligned in a grid-like structure. If the points are scattered randomly, the sorting may not yield meaningful results.
- The performance of the algorithm can vary based on the number of points and their distribution. For large datasets, optimizations may be necessary.
- This algorithm is designed for a standard cartesian coordinate system where the origin (0,0) is at the top left corner, x increases to the right, and y increases updward. Adjusting it to work for other coordinate systems (e.g. images, 3D spaces, etc.) can be done with relative ease. 

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## Acknowledgements

I'd like to acknowledge [this Stack Overflow thread](https://stackoverflow.com/questions/29630052/ordering-coordinates-from-top-left-to-bottom-right) for the inspiration and helpful discussions that lead to me creating this library. Special thanks to all contributors and users who have provided feedback and improvements.

## Contact

For questions or suggestions, please open an issue on GitHub or contact the maintainer directly.
