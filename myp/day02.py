class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    def greet(self):
        return f"Hello, my name is {self.name} and I am {self.age} years old."
    def celebrate_birthday(self):
        self.age += 1
        return f"Happy Birthday! Now I am {self.age} years old."

lst = []
lst2 = [1,2,3,4,5]

if __name__ == "__main__":
    if not lst:
        print("lst is empty")
    if not lst2:
        print("lst2 is empty")
    person1 = Person("Alice", 30);
    print(person1.greet())
    print(person1.celebrate_birthday())
  # Main execution block
