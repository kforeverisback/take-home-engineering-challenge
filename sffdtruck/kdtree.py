# -*- coding: utf-8 -*-
import heapq
import itertools
import math
from functools import wraps

dim = 2  # Constant for our case


def dist_sq(p1, p2):
    from math import pow

    """
    Euclidean distance of two points
    """
    return sum([pow(p2[i] - p1[i], 2) for i in range(dim)])


class FTData:
    """
    Generic representation of
    """

    def __init__(self, csv_dict):
        self.latlon = (float(csv_dict["Latitude"]), float(csv_dict["Longitude"]))
        self.data = csv_dict

    def __getitem__(self, i):
        return self.latlon[i]

    def __len__(self):
        return len(self.latlon)

    def __repr__(self):
        # return f"{self.latlon}"
        return f'ft <{self.latlon},{self.data["Applicant"]}, {self.data["Address"]}>'


class FTNode:
    def __repr__(self):
        return f"Node<{self.ft_data}>"

    def __init__(self, ft_data, axis, left, right, dist_fn=None):
        self.data = ft_data
        self.ft_data = ft_data
        self.cur_axis = axis
        self.left = left
        self.right = right
        if dist_fn is None:
            self.dist_fn = dist_sq
        else:
            self.dist_fn = dist_fn

    from itertools import count

    global_counter = count()
    """
    Very important to have counter variable!!
    Otherwise, the priority sort/push will if similar priorities are found
    """

    def search(self, point, k=1):
        results = []
        _ = self.search_knn(point, results=results, k=k)
        """
        We reverse sort them, coz, we pused negative distance
        Python uses MIN heap, hence we have to reverse it to get the
        closest one first
        """
        return [ftn for _, _, ftn in sorted(results, reverse=True)]

    def search_knn(self, point, results, k):
        def closest_of_point(n1, n2):
            if n1 is None:
                return n2
            if n2 is None:
                return n1
            # The target point is always the pivot
            d1 = self.dist_fn(point, n1.ft_data)
            d2 = self.dist_fn(point, n2.ft_data)

            return n1 if d1 < d2 else n2

        if k < 1:
            raise ValueError("k must be greater than 0.")
        # print(f'Processing: {self.ft_data}')
        cur_node_dist = self.dist_fn(self.ft_data, point)
        q_item = (-cur_node_dist, next(FTNode.global_counter), self)
        if len(results) >= k:
            if -cur_node_dist > results[0][0]:
                heapq.heapreplace(results, q_item)
        else:
            heapq.heappush(results, q_item)

        if point[self.cur_axis] < self.ft_data[self.cur_axis]:
            best_branch, opposite_branch = (self.left, self.right)
        else:
            best_branch, opposite_branch = (self.right, self.left)

        best = closest_of_point(
            best_branch.search_knn(point, results, k) if best_branch else None, self
        )

        # Even if we found a best branch, the nearest neighbor could be lurking in the opposite one!
        if (
            -((point[self.cur_axis] - self.ft_data[self.cur_axis]) ** 2) > results[0][0]
            or len(results) < k
        ):  # > math.pow(point[self.cur_axis] - self.ft_data[self.cur_axis], 2):
            best = closest_of_point(
                opposite_branch.search_knn(point, results, k)
                if opposite_branch
                else None,
                best,
            )
        return best

    def build_tree(ftdata_list, depth=0, dist_fn=dist_sq):

        if ftdata_list is None or len(ftdata_list) <= 0:
            return None

        cur_axis = depth % dim
        ftdata_list.sort(key=lambda point: point[cur_axis])
        median_idx = len(ftdata_list) // 2
        median_data = ftdata_list[median_idx]

        # next_axis = (cur_axis + 1) % dim
        # Return the root Node of the tree
        return FTNode(
            median_data,
            cur_axis,
            FTNode.build_tree(ftdata_list[:median_idx], depth + 1, dist_fn),
            FTNode.build_tree(ftdata_list[median_idx + 1 :], depth + 1, dist_fn),
            dist_fn=dist_fn,
        )
        # self.root = build_tree(list(ftdata_list))
