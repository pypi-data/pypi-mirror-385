from dataclasses import dataclass

print("hello, world!")

a = 10

@dataclass
class Person:
    name: str
    age: int
    address: str

    def get_name(self) -> str:
        return self.name

    def get_age(self) -> int:
        return self.age

    def parse_address(self) -> str:
        ...


people = [
    Person("Alice", 25, "123 Main St"),
    Person("Bob", 30, "456 Elm St"),
    Person("Charlie", 35, "789 Oak St"),
    Person("David", 40, "1011 Pine St"),
    Person("Eve", 45, "1213 Cedar St"),
    Person("Emma", 47, "1314 Ash St"),
    Person("Gina", 49, "1516 Fir St"),
    Person("Frank", 50, "1415 Birch St"),
    Person("Grace", 55, "1617 Maple St"),
    Person("Heidi", 60, "1819 Walnut St"),
    Person("Ivan", 65, "2021 Spruce St"),
    Person("Judy", 70, "2223 Cedar St"),
]

numbers = [
    1,
    3
]


n_people = len(people)
person_name_lengths = [len(person.name) for person in people]

people_avg_age = sum(person_name_lengths) / n_people

print(f"{people_avg_age=}")


def hello_world():
    for i in range(4):
        try:
            print("hello world")
        except:
            pass


a = 2


match True:
    case False:
        ...
    case True:
        ...


def hello(): print("hello world!")
