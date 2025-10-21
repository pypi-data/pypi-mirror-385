class math:
    @staticmethod
    def add(a, b):
        return a + b

    @staticmethod
    def subtract(a, b):
        return a - b

    @staticmethod
    def divide(a, b):
        # Add error handling for division by zero
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b

    @staticmethod
    def multiply(a, b):
        return a * b