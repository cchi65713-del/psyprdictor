class Registry:

    def __init__(self):
        self.by_id = {}
        self.by_name = {}

    def register(self, box):
        # Store by ID
        self.by_id[box.id] = box

        # Store by Name
        self.by_name[box.name.lower()] = box

    def get_by_id(self, id):
        return self.by_id.get(id)

    def get_by_name(self, name):
        return self.by_name.get(name.lower())

    def show(self):
        print("\n===== Registry =====")

        for id, box in self.by_id.items():
            print(f"{id} -> {box.name}")