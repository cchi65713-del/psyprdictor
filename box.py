class Box:

    def __init__(self, id, name, options=None, box_type=""):
        self.id = id
        self.name = name
        self.children = []
        self.options = options if options else []
        self.box_type = box_type

    def add_child(self, name):
        if "." not in self.id and len(self.id) == 1:
            child_id = f"{self.id}{len(self.children) + 1}"
        else:
            child_id = f"{self.id}.{len(self.children) + 1}"

        child = Box(child_id, name, self.options, self.box_type)
        self.children.append(child)
        return child

    def expand(self, registry=None):
        # Only create one level of children
        for option in self.options:
            child = self.add_child(option)

            if registry is not None:
                registry.register(child)

    def show(self, level=0):
        print("  " * level + f"{self.id} - {self.name}")

        for child in self.children:
            child.show(level + 1)