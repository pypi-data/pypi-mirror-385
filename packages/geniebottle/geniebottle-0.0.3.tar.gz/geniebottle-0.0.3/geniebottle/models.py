
class Bytes(bytes):
    def __repr__(self):
        return f"Bytes({super().__repr__()[:10]}...)"

    def __str__(self):
        return f"Bytes({super().__str__()[:10]}...)"
