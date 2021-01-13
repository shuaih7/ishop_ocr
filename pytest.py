import os, sys
import numpy as np

params = {
    "hobby": "soccer",
    "name": "Shuai",
    "age": 27,
}


def build_person(id, name, age, hobby):
    print("Person's ID:   ", id)
    print("Person's name: ", name)
    print("Person's age:  ", age)
    print("Person's hobby:", hobby)
    
    
if __name__ == "__main__":
    #build_person("212780558", **params)
    number = "12345679"
    number = number[:-4]+"Z"+number[-2:]
    print(number)