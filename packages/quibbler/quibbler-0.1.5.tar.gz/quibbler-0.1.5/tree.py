class TreeNode:
    """A node in a binary tree."""

    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None


class BinaryTree:
    """A simple binary search tree implementation."""

    def __init__(self):
        self.root = None

    def insert(self, value):
        """Insert a value into the tree."""
        if self.root is None:
            self.root = TreeNode(value)
        else:
            self._insert_recursive(self.root, value)

    def _insert_recursive(self, node, value):
        """Helper method to recursively insert a value."""
        if value < node.value:
            if node.left is None:
                node.left = TreeNode(value)
            else:
                self._insert_recursive(node.left, value)
        else:
            if node.right is None:
                node.right = TreeNode(value)
            else:
                self._insert_recursive(node.right, value)

    def search(self, value):
        """Search for a value in the tree."""
        return self._search_recursive(self.root, value)

    def _search_recursive(self, node, value):
        """Helper method to recursively search for a value."""
        if node is None:
            return False

        if value == node.value:
            return True
        elif value < node.value:
            return self._search_recursive(node.left, value)
        else:
            return self._search_recursive(node.right, value)

    def inorder_traversal(self):
        """Return list of values in inorder (left, root, right)."""
        result = []
        self._inorder_recursive(self.root, result)
        return result

    def _inorder_recursive(self, node, result):
        """Helper method for inorder traversal."""
        if node is not None:
            self._inorder_recursive(node.left, result)
            result.append(node.value)
            self._inorder_recursive(node.right, result)

    def preorder_traversal(self):
        """Return list of values in preorder (root, left, right)."""
        result = []
        self._preorder_recursive(self.root, result)
        return result

    def _preorder_recursive(self, node, result):
        """Helper method for preorder traversal."""
        if node is not None:
            result.append(node.value)
            self._preorder_recursive(node.left, result)
            self._preorder_recursive(node.right, result)

    def postorder_traversal(self):
        """Return list of values in postorder (left, right, root)."""
        result = []
        self._postorder_recursive(self.root, result)
        return result

    def _postorder_recursive(self, node, result):
        """Helper method for postorder traversal."""
        if node is not None:
            self._postorder_recursive(node.left, result)
            self._postorder_recursive(node.right, result)
            result.append(node.value)

    def find_min(self):
        """Find the minimum value in the tree."""
        if self.root is None:
            return None
        return self._find_min_recursive(self.root)

    def _find_min_recursive(self, node):
        """Helper method to find minimum value."""
        if node.left is None:
            return node.value
        return self._find_min_recursive(node.left)

    def find_max(self):
        """Find the maximum value in the tree."""
        if self.root is None:
            return None
        return self._find_max_recursive(self.root)

    def _find_max_recursive(self, node):
        """Helper method to find maximum value."""
        if node.right is None:
            return node.value
        return self._find_max_recursive(node.right)

    def height(self):
        """Get the height of the tree."""
        return self._height_recursive(self.root)

    def _height_recursive(self, node):
        """Helper method to calculate height."""
        if node is None:
            return -1
        return 1 + max(self._height_recursive(node.left),
                       self._height_recursive(node.right))
