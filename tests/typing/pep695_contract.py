class Box[T]:
    value: T

    def unwrap(self) -> T:
        return self.value
