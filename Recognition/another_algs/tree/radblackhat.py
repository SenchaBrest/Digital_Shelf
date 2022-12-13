import os

import numpy as np

from koef import compare, extract
from PIL import Image

from treeart import *

BASIS = np.ones(1280) / 2


class Vector:
    def __init__(self, val):
        self.val = val

    def __lt__(self, other):
        return compare(self.val, BASIS)[0][0] < 0.5

    def __gt__(self, other):
        return compare(self.val, BASIS)[0][0] > 0.5
    def __eq__(self, other):
        return compare(self.val, BASIS)[0][0] == 0.5

class RBNode:
    def __init__(self, key, val):
        self.red = False
        self.parent = None
        self.key = key
        self.val = val
        self.left = None
        self.right = None


class RBTree:
    def __init__(self):
        self.nil = RBNode(0, 0)
        self.nil.red = False
        self.nil.left = None
        self.nil.right = None
        self.root = self.nil

    def insert(self, key, val):
        # Ordinary Binary Search Insertion
        new_node = RBNode(key, val)
        new_node.parent = None
        new_node.left = self.nil
        new_node.right = self.nil
        new_node.red = True  # new node must be red

        parent = None
        current = self.root
        while current != self.nil:
            parent = current
            if new_node.key < current.key:
                current = current.left
            elif new_node.key > current.key:
                current = current.right
            else:
                return

        # Set the parent and insert the new node
        new_node.parent = parent
        if parent is None:
            self.root = new_node
        elif new_node.key < parent.key:
            parent.left = new_node
        else:
            parent.right = new_node

        # Fix the tree
        self.fix_insert(new_node)

    def fix_insert(self, new_node):
        while new_node != self.root and new_node.parent.red:
            if new_node.parent == new_node.parent.parent.right:
                u = new_node.parent.parent.left  # uncle
                if u.red:
                    u.red = False
                    new_node.parent.red = False
                    new_node.parent.parent.red = True
                    new_node = new_node.parent.parent
                else:
                    if new_node == new_node.parent.left:
                        new_node = new_node.parent
                        self.rotate_right(new_node)
                    new_node.parent.red = False
                    new_node.parent.parent.red = True
                    self.rotate_left(new_node.parent.parent)
            else:
                u = new_node.parent.parent.right  # uncle

                if u.red:
                    u.red = False
                    new_node.parent.red = False
                    new_node.parent.parent.red = True
                    new_node = new_node.parent.parent
                else:
                    if new_node == new_node.parent.right:
                        new_node = new_node.parent
                        self.rotate_left(new_node)
                    new_node.parent.red = False
                    new_node.parent.parent.red = True
                    self.rotate_right(new_node.parent.parent)
        self.root.red = False

    def exists(self, key):
        curr = self.root
        while curr != self.nil and key != curr.key:
            if key < curr.key:
                curr = curr.left
            else:
                curr = curr.right
        return curr

    def search_nearest(self, key):
        curr = self.root
        nearest = None
        while curr != self.nil:
            nearest = curr
            if curr.left.key < curr.right.key:
                curr = curr.left
            elif key > curr.key:
                curr = curr.right
            else:
                return curr
        return nearest

    # rotate left at node x
    def rotate_left(self, x):
        y = x.right
        x.right = y.left
        if y.left != self.nil:
            y.left.parent = x

        y.parent = x.parent
        if x.parent is None:
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.left = x
        x.parent = y

    # rotate right at node x
    def rotate_right(self, x):
        y = x.left
        x.left = y.right
        if y.right != self.nil:
            y.right.parent = x

        y.parent = x.parent
        if x.parent is None:
            self.root = y
        elif x == x.parent.right:
            x.parent.right = y
        else:
            x.parent.left = y
        y.right = x
        x.parent = y

    def __repr__(self):
        draw_tree(self.root)


def print_tree(node, lines, level=0):
    if node.val != 0:
        print_tree(node.left, lines, level + 1)
        lines.append(f"[{str(node.val)}, '{node.key}']")
        print_tree(node.right, lines, level + 1)


def draw_tree(node):
    if node.val != 0:
        return binary_edge(node.val, draw_tree(node.left), draw_tree(node.right), align='center')
    else:
        return "N"


def export_to_txt_val(tree, filename):
    with open(filename, 'w') as f:
        f.write(tree.__repr__())


def export_from_txt_val(tree, filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    for line in lines:
        line = line.replace('[', '').replace(']', '').replace(',', '')
        val = line.split(' ')[0], line.split(' ')[1]
        tree.insert([float(val[0]), val[1]])


def main():
    tree = RBTree()
    directory = "products"
    for dirname in os.listdir(directory):
        path = f"{directory}/{dirname}"
        for filename in os.listdir(path):
            path = f"{directory}/{dirname}/{filename}"

            Image.open(path).resize((224, 224)).save(path)

            tree.insert(Vector(extract(path)), dirname)

    print(draw_tree(tree.root))

    directory = "1"
    for filename in os.listdir(directory):
        path = f"{directory}/{filename}"
        Image.open(path).resize((224, 224)).save(path)
        print(tree.search_nearest(Vector(extract(path))).val)

    # draw tree by asciitree


main()
