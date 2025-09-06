from typing import Optional, List
import math

class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

class Cab:
    def __init__(self, name: str):
        self.name = name

class QuadStatus:
    EMPTY_LEAF = 'EmptyLeaf'
    FILLED_LEAF = 'FilledLeaf'
    DIVIDED = 'Divided'

#================
#  QUAD NODE
#===============
class Quad:
    quad_id_counter = 1  # static for unique id

    def __init__(self, center: Point, half_width: float, half_height: float, parent=None):
        self.center = center
        self.half_width = half_width
        self.half_height = half_height
        self.status = QuadStatus.EMPTY_LEAF
        self.parent = parent

        self.nw = None
        self.ne = None
        self.sw = None
        self.se = None

        self.cab = None
        self.cab_location = None

        self.quad_id = Quad.quad_id_counter
        Quad.quad_id_counter += 1

    def contains(self, p: Point):
        left = self.center.x - self.half_width
        right = self.center.x + self.half_width
        top = self.center.y - self.half_height
        bottom = self.center.y + self.half_height
        return (left <= p.x < right) and (top <= p.y < bottom)

    def locate_sub_quad(self, p: Point):
        east = p.x >= self.center.x
        south = p.y >= self.center.y
        if not east and not south:
            return 'NW'
        if east and not south:
            return 'NE'
        if not east and south:
            return 'SW'
        return 'SE'

    def create_children(self):
        chw = self.half_width / 2.0
        chh = self.half_height / 2.0
        self.nw = Quad(Point(self.center.x - chw, self.center.y - chh), chw, chh, parent=self)
        self.ne = Quad(Point(self.center.x + chw, self.center.y - chh), chw, chh, parent=self)
        self.sw = Quad(Point(self.center.x - chw, self.center.y + chh), chw, chh, parent=self)
        self.se = Quad(Point(self.center.x + chw, self.center.y + chh), chw, chh, parent=self)

    def child_for_key(self, key):
        if key == 'NW':
            return self.nw
        if key == 'NE':
            return self.ne
        if key == 'SW':
            return self.sw
        return self.se

    def insert(self, cab: Cab, loc: Point):
        if not self.contains(loc):
            print(f"Location ({loc.x}, {loc.y}) out of bounds for quad_id {self.quad_id}")
            return

        if self.status == QuadStatus.EMPTY_LEAF:
            self.cab = cab
            self.cab_location = loc
            self.status = QuadStatus.FILLED_LEAF
            print(f"Inserted cab at ({loc.x}, {loc.y}) into quad_id {self.quad_id}")
            return
        elif self.status == QuadStatus.DIVIDED:
            key = self.locate_sub_quad(loc)
            child = self.child_for_key(key)
            child.insert(cab, loc)
            return
        elif self.status == QuadStatus.FILLED_LEAF:
            existing_cab = self.cab
            existing_loc = self.cab_location
            self.status = QuadStatus.DIVIDED
            self.cab = None
            self.create_children()
            key_a = self.locate_sub_quad(existing_loc)
            key_b = self.locate_sub_quad(loc)
            a_node = self.child_for_key(key_a)
            b_node = self.child_for_key(key_b)

            # subdivide until both cabs are separated
            while a_node == b_node:
                a_node.status = QuadStatus.DIVIDED
                a_node.create_children()
                key_a_2 = a_node.locate_sub_quad(existing_loc)
                key_b_2 = a_node.locate_sub_quad(loc)
                a_node = a_node.child_for_key(key_a_2)
                b_node = a_node.parent.child_for_key(key_b_2)
                # For clarity, reset both from subdivided parent:
                common = a_node.parent
                key_ra = common.locate_sub_quad(existing_loc)
                key_rb = common.locate_sub_quad(loc)
                a_node = common.child_for_key(key_ra)
                b_node = common.child_for_key(key_rb)
            a_node.insert(existing_cab, existing_loc)
            b_node.insert(cab, loc)
            return

    # --- Search methods, names kept per video style ---

    def descend_to_leaf(self, p: Point):
        cur = self
        while cur and cur.status == QuadStatus.DIVIDED:
            key = cur.locate_sub_quad(p)
            cur = cur.child_for_key(key)
        return cur

    def collect_leaf_cabs(self, out: List, p: Point):
        if self.status == QuadStatus.FILLED_LEAF and self.cab:
            dx = self.cab_location.x - p.x
            dy = self.cab_location.y - p.y
            out.append({'cab': self.cab, 'loc': self.cab_location, 'dist2': dx*dx + dy*dy})
        elif self.status == QuadStatus.DIVIDED:
            for child in [self.nw, self.ne, self.sw, self.se]:
                child.collect_leaf_cabs(out, p)

    def collect_siblings(self, skip_child, out: List, p: Point):
        if self.status != QuadStatus.DIVIDED:
            return
        for child in [self.nw, self.ne, self.sw, self.se]:
            if child is not skip_child:
                child.collect_leaf_cabs(out, p)

    def find_nearest_cabs(self, p: Point, k=1, max_levels_up=8):
        candidates = []
        leaf = self.descend_to_leaf(p)
        if leaf:
            leaf.collect_leaf_cabs(candidates, p)
            child = leaf
            parent = leaf.parent
            level = 0
            while len(candidates) < k and parent and level < max_levels_up:
                parent.collect_siblings(child, candidates, p)
                child = parent
                parent = parent.parent
                level += 1
            if len(candidates) < k and child and child.status == QuadStatus.DIVIDED:
                child.collect_leaf_cabs(candidates, p)
            candidates.sort(key=lambda c: c['dist2'])
            return candidates[:k]
        return []
