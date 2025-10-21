from mpvis.mddrt.tree_node import TreeNode


def prune_tree_to_depth(node: TreeNode, max_depth: int) -> TreeNode:
    """
    Prunes the tree to the specified maximum depth.

    Args:
        node (TreeNode): The root node of the tree to prune.
        max_depth (int): The maximum depth to retain in the tree.

    Returns:
        TreeNode: The pruned tree.

    """
    node_copy = node.deep_copy()
    prune_tree_to_depth_impl(node_copy, max_depth)
    return node_copy


def prune_tree_to_depth_impl(node: TreeNode, max_depth: int) -> None:
    if node.depth >= max_depth - 1:
        node.children = []
    else:
        for child in node.children:
            prune_tree_to_depth_impl(child, max_depth)
