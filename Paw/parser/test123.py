from PrettyPrint import PrettyPrintTree


class Tree:
    def __init__(self, value):
        self.val = value
        self.children = []

    def add_child(self, child):
        self.children.append(child)
        return child

    def __str__(self):
        return f'{self.val} {self.children}'

    def __repr__(self):
        return f'{self.val} {self.children}'


pt = PrettyPrintTree(lambda x: x.children, lambda x: x.val)
tree = Tree(1)
child1 = tree.add_child(Tree(2))
child2 = tree.add_child(Tree(3))
child1.add_child(Tree(4))
child1.add_child(Tree(5))
child1.add_child(Tree(6))
child2.add_child(Tree(7))
print(str(tree.children))
pt(tree)