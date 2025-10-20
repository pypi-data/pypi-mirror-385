import copy
import math

def find_xy_container(obj):
    """Find the first object that has X/x and Y/y attributes (case-insensitive)."""
    attrs = {name.lower(): name for name in dir(obj)}

    # Direct match
    if "x" in attrs and "y" in attrs:
        return obj

    # Look one level down into attributes
    for name in attrs.values():
        if name.startswith("__") and name.endswith("__"):
            continue  # skip dunders
        try:
            nested = getattr(obj, name)
        except Exception:
            continue
        if not hasattr(nested, "__dict__"):
            continue
        nested_attrs = {n.lower(): n for n in dir(nested)}
        if "x" in nested_attrs and "y" in nested_attrs:
            return nested

    return None

def get_xy(obj):
    container = find_xy_container(obj)
    if container is None:
        raise AttributeError(f"{type(obj).__name__} has no X/x and Y/y attributes")
    attrs = {name.lower(): name for name in dir(container)}
    return getattr(container, attrs["x"]), getattr(container, attrs["y"])


def set_xy(obj, x, y):
    container = find_xy_container(obj)
    if container is None:
        raise AttributeError(f"{type(obj).__name__} has no X/x and Y/y attributes")
    attrs = {name.lower(): name for name in dir(container)}
    setattr(container, attrs["x"], x)
    setattr(container, attrs["y"], y)

def point_line_distance(x1, y1, x2, y2, x0, y0):
    A = y2 - y1
    B = x1 - x2
    C = x2*y1 - x1*y2
    denom = math.hypot(A, B)
    if denom == 0:
        # endpoints are the same point; return distance to that point
        return math.hypot(x0 - x1, y0 - y1)
    return abs(A*x0 + B*y0 + C) / denom

def sort_by_xy(objs, threshold):
    """Sort a list of objects that have X/x and Y/y attributes.

    Algorithm (iterative):
    - Work on a deep copy of the list so callers' objects aren't mutated.
    - While there are points remaining:
      - If <= 2 points remain, append them sorted by (x, y) and finish.
      - Find the top-left and top-right candidates using Y-X and X+Y heuristics.
      - Build a row: include the endpoints and any points whose orthogonal distance
        to the line between endpoints is < threshold.
      - Sort that row left-to-right (by x then y), append to the result, and remove
        those points from the remaining list.
    - If a row can't be found, fall back to a simple (x, y) sort for the rest.
    """

    objs = copy.deepcopy(objs)
    sorted_list = []

    while objs:
        # Small remainder -> just append sorted by x then y
        if len(objs) <= 2:
            remainder_sorted = sorted(objs, key=lambda o: (get_xy(o)[0], get_xy(o)[1]))
            sorted_list.extend(remainder_sorted)
            break

        xy_values = [get_xy(o) for o in objs]

        # Prefer endpoints from the topmost row (smallest y) when possible.
        try:
            y_min = min(y for x, y in xy_values)
            top_candidates = [i for i, (x, y) in enumerate(xy_values) if y == y_min]
            if len(top_candidates) >= 2:
                top_left_idx = min(top_candidates, key=lambda i: xy_values[i][0])
                top_right_idx = max(top_candidates, key=lambda i: xy_values[i][0])
            else:
                # fallback heuristics for rotated rows or single-top-point cases
                top_left_idx = max(range(len(xy_values)), key=lambda i: xy_values[i][1] - xy_values[i][0]) # Computer Max(y - x) (Maximize y, minimize x)
                top_right_idx = max(range(len(xy_values)), key=lambda i: xy_values[i][0] + xy_values[i][1]) # computer Max(x + y) (Maximize x, maximize y)
        except ValueError:
            # no points
            break

        x1, y1 = xy_values[top_left_idx]
        x2, y2 = xy_values[top_right_idx]

        print(f"Top-left idx: {top_left_idx}, point: ({x1}, {y1})")
        print(f"Top-right idx: {top_right_idx}, point: ({x2}, {y2})")

        close_points = []

        # Always include the endpoints
        close_points.append(objs[top_left_idx])
        if top_right_idx != top_left_idx:
            close_points.append(objs[top_right_idx])

        # Collect other points close to the line
        for i, (x0, y0) in enumerate(xy_values):
            if i == top_left_idx or i == top_right_idx:
                continue
            dist = point_line_distance(x1, y1, x2, y2, x0, y0)
            if dist <= threshold:
                close_points.append(objs[i])

        # If we didn't collect any non-endpoint points and only have endpoints,
        # fall back to a simple sort to avoid infinite loops or bad grouping.
        if not close_points:
            remainder_sorted = sorted(objs, key=lambda o: (get_xy(o)[0], get_xy(o)[1]))
            sorted_list.extend(remainder_sorted)
            break

        # Sort the row left-to-right (x then y) and append to output
        close_points.sort(key=lambda o: (get_xy(o)[0], get_xy(o)[1]))
        sorted_list.extend(close_points)

        # Remove those points from objs (compare by identity of the deepcopy)
        remove_ids = {id(p) for p in close_points}
        objs = [p for p in objs if id(p) not in remove_ids]

    return sorted_list
