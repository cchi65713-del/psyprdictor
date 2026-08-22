class ActivationEngine:

    def __init__(self):
        self.connections = {}

    def connect(self, from_id, to_id):
        if from_id not in self.connections:
            self.connections[from_id] = []

        self.connections[from_id].append(to_id)

    def show_connections(self):
        print("\nActivation Paths\n")

        for source, targets in self.connections.items():
            print(f"{source} ---> {targets}")