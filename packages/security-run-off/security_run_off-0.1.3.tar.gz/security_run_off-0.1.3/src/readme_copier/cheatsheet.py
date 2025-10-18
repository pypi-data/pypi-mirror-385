"""
Embedded full cheatsheet content for the security-run-off package.

This module contains the full Ultimate Python 3.12+ Cheatsheet embedded from
`fREADME.mdf`.
"""

__readme_full__ = r"""# Ultimate Python 3.12+ Cheatsheet

> **Comprehensive Python Reference for Data Science, AI, and Software Development**  
> Compatible with Python 3.12 and above | Last Updated: 2025-10-15

---

## Table of Contents
1. [Basic Syntax & Data Types](#1-basic-syntax--data-types)
2. [Data Structures](#2-data-structures)
3. [Control Flow](#3-control-flow)
4. [Functions](#4-functions)
5. [String Manipulation](#5-string-manipulation)
6. [File I/O](#6-file-io)
7. [Data Processing with Pandas](#7-data-processing-with-pandas)
8. [Comprehensions](#8-comprehensions)
9. [Generators](#9-generators)
10. [Object-Oriented Programming](#10-object-oriented-programming)
11. [Error Handling](#11-error-handling)
12. [Logging](#12-logging)
13. [Modules & Packages](#13-modules--packages)
14. [Testing](#14-testing)
15. [Parallel & Distributed Computing](#15-parallel--distributed-computing)
16. [Type Hints](#16-type-hints)
17. [Real-World Examples from Course Labs](#17-real-world-examples-from-course-labs)
18. [Lecture Coverage Summary](#18-lecture-coverage-summary)
19. [Best Practices](#19-best-practices)

---

## 1. Basic Syntax & Data Types

### Variables and Assignment
```python
# Variable assignment (no declaration needed)
x = 10              # Integer
y = 3.14            # Float
name = "Python"     # String
is_active = True    # Boolean
nothing = None      # None type

# Multiple assignment
a, b, c = 1, 2, 3
x = y = z = 0

# Swap variables
a, b = b, a
```

### Numeric Types
```python
# Integers
age = 25
big_num = 1_000_000  # Underscores for readability (Python 3.6+)

# Floats
pi = 3.14159
scientific = 2.5e-3  # 0.0025

# Complex numbers
z = 3 + 4j

# Type conversion
int("123")      # 123
float("3.14")   # 3.14
str(42)         # "42"

# Arithmetic operators
+ - * / // % **  # Addition, Subtraction, Multiplication, Division, Floor division, Modulo, Power

# Comparison operators
== != < > <= >=

# Logical operators
and or not
```

### Strings
```python
# String creation
single = 'Hello'
double = "World"
triple = '''Multi
line
string'''

# f-strings (Python 3.6+)
name = "Alice"
age = 30
message = f"My name is {name} and I'm {age} years old"
formatted = f"{pi:.2f}"  # 3.14

# String methods
text = "  Hello World  "
text.lower()          # "  hello world  "
text.upper()          # "  HELLO WORLD  "
text.strip()          # "Hello World"
text.replace("World", "Python")  # "  Hello Python  "
text.split()          # ["Hello", "World"]
"_".join(["a", "b"]) # "a_b"

# String indexing and slicing
s = "Python"
s[0]        # 'P'
s[-1]       # 'n'
s[0:3]      # 'Pyt'
s[::-1]     # 'nohtyP' (reverse)
```

---

## 2. Data Structures

### Lists (Mutable, Ordered)
```python
# Creation
fruits = ["apple", "banana", "cherry"]
numbers = [1, 2, 3, 4, 5]
mixed = [1, "two", 3.0, True]
empty = []

# Accessing elements
fruits[0]      # "apple"
fruits[-1]     # "cherry"
fruits[1:3]    # ["banana", "cherry"]

# Modifying lists
fruits.append("orange")          # Add to end
fruits.insert(1, "mango")        # Insert at index
fruits.remove("banana")          # Remove by value
popped = fruits.pop()            # Remove and return last item
fruits.extend([1, 2, 3])         # Add multiple items
fruits.clear()                   # Remove all items

# List operations
len(fruits)                      # Length
fruits.count("apple")            # Count occurrences
fruits.index("cherry")           # Find index
fruits.sort()                    # Sort in place
fruits.reverse()                 # Reverse in place
sorted(fruits)                   # Return sorted copy
fruits.copy()                    # Shallow copy

# List unpacking (Python 3.5+)
first, *rest = [1, 2, 3, 4]     # first=1, rest=[2,3,4]
first, *middle, last = [1, 2, 3, 4]  # first=1, middle=[2,3], last=4
```

### Tuples (Immutable, Ordered)
```python
# Creation
point = (10, 20)
single = (42,)      # Comma needed for single element
coordinates = 10, 20, 30  # Parentheses optional

# Accessing
point[0]            # 10
x, y = point        # Unpacking

# Tuple methods
point.count(10)     # Count occurrences
point.index(20)     # Find index

# Named tuples
from collections import namedtuple
Point = namedtuple('Point', ['x', 'y'])
p = Point(10, 20)
p.x                 # 10
```

### Dictionaries (Mutable, Unordered Key-Value Pairs)
```python
# Creation
person = {"name": "Alice", "age": 30, "city": "NYC"}
empty = {}
dict_from_list = dict([("a", 1), ("b", 2)])

# Accessing
person["name"]              # "Alice"
person.get("age")           # 30
person.get("salary", 0)     # 0 (default if key not found)

# Modifying
person["age"] = 31          # Update value
person["job"] = "Engineer"  # Add new key-value
del person["city"]          # Remove key
person.pop("age")           # Remove and return value
person.clear()              # Remove all items

# Dictionary methods
person.keys()               # dict_keys(['name', 'age'])
person.values()             # dict_values(['Alice', 30])
person.items()              # dict_items([('name', 'Alice'), ('age', 30)])
person.update({"age": 32})  # Update multiple items

# Dictionary merging (Python 3.9+)
dict1 = {"a": 1, "b": 2}
dict2 = {"b": 3, "c": 4}
merged = dict1 | dict2      # {"a": 1, "b": 3, "c": 4}
```

### Sets (Mutable, Unordered, Unique Elements)
```python
# Creation
fruits = {"apple", "banana", "cherry"}
numbers = set([1, 2, 2, 3, 3, 3])  # {1, 2, 3}
empty = set()  # NOT {} (that's a dict)

# Set operations
fruits.add("orange")        # Add element
fruits.remove("banana")     # Remove (raises error if not found)
fruits.discard("mango")     # Remove (no error if not found)
fruits.pop()                # Remove and return arbitrary element
fruits.clear()              # Remove all elements

# Set mathematics
a = {1, 2, 3}
b = {3, 4, 5}
a | b           # Union: {1, 2, 3, 4, 5}
a & b           # Intersection: {3}
a - b           # Difference: {1, 2}
a ^ b           # Symmetric difference: {1, 2, 4, 5}

# Set methods
a.union(b)
a.intersection(b)
a.difference(b)
a.symmetric_difference(b)
a.issubset(b)
a.issuperset(b)
```

---

## 3. Control Flow

### Conditional Statements
```python
# if/elif/else
age = 18
if age < 13:
    print("Child")
elif age < 20:
    print("Teenager")
else:
    print("Adult")

# Ternary operator
status = "Adult" if age >= 18 else "Minor"

# Multiple conditions
if 18 <= age < 65:
    print("Working age")

# Truthy and Falsy values
# Falsy: False, None, 0, 0.0, "", [], {}, set()
# Everything else is Truthy
```

### Loops

#### For Loop
```python
# Iterate over sequence
for fruit in ["apple", "banana", "cherry"]:
    print(fruit)

# Range
for i in range(5):          # 0, 1, 2, 3, 4
    print(i)

for i in range(2, 10, 2):   # 2, 4, 6, 8 (start, stop, step)
    print(i)

# Enumerate (get index and value)
for index, fruit in enumerate(["apple", "banana"]):
    print(f"{index}: {fruit}")

# Iterate over dictionary
person = {"name": "Alice", "age": 30}
for key in person:
    print(key, person[key])

for key, value in person.items():
    print(f"{key}: {value}")

# Zip (iterate over multiple sequences)
names = ["Alice", "Bob"]
ages = [25, 30]
for name, age in zip(names, ages):
    print(f"{name} is {age}")
```

#### While Loop
```python
# Basic while loop
count = 0
while count < 5:
    print(count)
    count += 1

# Infinite loop with break
while True:
    response = input("Enter 'quit' to exit: ")
    if response == 'quit':
        break
```

#### Loop Control
```python
# break: exit loop
for i in range(10):
    if i == 5:
        break
    print(i)  # 0, 1, 2, 3, 4

# continue: skip to next iteration
for i in range(5):
    if i == 2:
        continue
    print(i)  # 0, 1, 3, 4

# else clause (executes if loop completes without break)
for i in range(5):
    if i == 10:
        break
else:
    print("Loop completed normally")
```

---

## 4. Functions

### Function Definition
```python
# Basic function
def greet(name):
    \"\"\"Function docstring\"\"\"
    return f"Hello, {name}!"

result = greet("Alice")

# Multiple return values
def get_stats(numbers):
    return sum(numbers), len(numbers), sum(numbers) / len(numbers)

total, count, average = get_stats([1, 2, 3, 4, 5])

# Default arguments
def power(base, exponent=2):
    return base ** exponent

power(3)        # 9
power(3, 3)     # 27

# Keyword arguments
def describe_person(name, age, city="Unknown"):
    return f"{name}, {age}, from {city}"

describe_person(name="Alice", age=30, city="NYC")
describe_person("Bob", 25)  # Positional

# *args and **kwargs
def sum_all(*args):
    \"\"\"Accept any number of positional arguments\"\"\"
    return sum(args)

sum_all(1, 2, 3, 4)  # 10

def print_info(**kwargs):
    \"\"\"Accept any number of keyword arguments\"\"\"
    for key, value in kwargs.items():
        print(f"{key}: {value}")

print_info(name="Alice", age=30)
```

### Lambda Functions
```python
# Anonymous function
square = lambda x: x ** 2
square(5)  # 25

add = lambda x, y: x + y
add(3, 4)  # 7

# Common use with built-in functions
numbers = [1, 2, 3, 4, 5]
squared = list(map(lambda x: x**2, numbers))  # [1, 4, 9, 16, 25]
evens = list(filter(lambda x: x % 2 == 0, numbers))  # [2, 4]

# Sorting with lambda
students = [("Alice", 25), ("Bob", 20), ("Charlie", 23)]
sorted_by_age = sorted(students, key=lambda x: x[1])
```

### Higher-Order Functions
```python
# Functions as arguments
def apply_operation(x, y, operation):
    return operation(x, y)

apply_operation(5, 3, lambda a, b: a + b)  # 8

# Functions returning functions
def multiplier(n):
    def multiply(x):
        return x * n
    return multiply

times_three = multiplier(3)
times_three(10)  # 30

# Decorators (functions that modify other functions)
def log_call(func):
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@log_call
def add(a, b):
    return a + b

add(3, 4)  # Prints: Calling add, Returns: 7
```

### Built-in Functions
```python
# Common built-in functions
len([1, 2, 3])              # 3
max([1, 5, 3])              # 5
min([1, 5, 3])              # 1
sum([1, 2, 3])              # 6
abs(-5)                     # 5
round(3.7)                  # 4
sorted([3, 1, 2])           # [1, 2, 3]
reversed([1, 2, 3])         # Reverse iterator
any([False, True, False])  # True (at least one True)
all([True, True, False])   # False (not all True)
```

---

## 5. String Manipulation

### String Methods
```python
s = "Hello World"

# Case conversion
s.lower()           # "hello world"
s.upper()           # "HELLO WORLD"
s.capitalize()      # "Hello world"
s.title()           # "Hello World"
s.swapcase()        # "hELLO wORLD"

# Searching and checking
s.startswith("Hello")   # True
s.endswith("World")     # True
s.find("World")         # 6 (index, -1 if not found)
s.index("World")        # 6 (raises error if not found)
s.count("l")            # 3
"World" in s            # True

# Cleaning
s.strip()           # Remove leading/trailing whitespace
s.lstrip()          # Remove leading whitespace
s.rstrip()          # Remove trailing whitespace
s.replace("World", "Python")  # "Hello Python"

# Splitting and joining
s.split()           # ["Hello", "World"]
s.split("o")        # ["Hell", " W", "rld"]
" ".join(["a", "b", "c"])  # "a b c"

# Checking
s.isalpha()         # False (has space)
s.isdigit()         # False
s.isalnum()         # False
s.isspace()         # False
"123".isdigit()     # True
```

### String Formatting
```python
# f-strings (Python 3.6+, RECOMMENDED)
name = "Alice"
age = 30
f"Name: {name}, Age: {age}"

# Format with expressions
f"Next year: {age + 1}"
f"Uppercase: {name.upper()}"

# Formatting numbers
pi = 3.14159
f"{pi:.2f}"         # "3.14"
f"{pi:10.2f}"       # "      3.14" (width 10)
f"{1000000:,}"      # "1,000,000"

# .format() method (older)
"Name: {}, Age: {}".format(name, age)
"Name: {0}, Age: {1}".format(name, age)
"Name: {n}, Age: {a}".format(n=name, a=age)

# % formatting (legacy, avoid)
"Name: %s, Age: %d" % (name, age)
```

### Regular Expressions
```python
import re

# Pattern matching
text = "The price is 100 dollars"
pattern = r'\\d+'
match = re.search(pattern, text)  # Finds first match
if match:
    print(match.group())  # "100"

# Find all matches
numbers = re.findall(r'\\d+', text)  # ["100"]

# Replace
new_text = re.sub(r'\\d+', 'XX', text)  # "The price is XX dollars"

# Split
parts = re.split(r'\\s+', text)

# Common patterns
r'\\d'       # Digit
r'\\w'       # Word character (letter, digit, underscore)
r'\\s'       # Whitespace
r'.'        # Any character
r'^'        # Start of string
r'$'        # End of string
r'*'        # 0 or more
r'+'        # 1 or more
r'?'        # 0 or 1
r'{n}'      # Exactly n
r'{n,m}'    # Between n and m
```

---

## 6. File I/O

### Reading Files
```python
# Read entire file
with open('file.txt', 'r') as f:
    content = f.read()

# Read line by line
with open('file.txt', 'r') as f:
    for line in f:
        print(line.strip())

# Read all lines into list
with open('file.txt', 'r') as f:
    lines = f.readlines()  # List of strings

# Read specific number of lines
with open('file.txt', 'r') as f:
    line1 = f.readline()
    line2 = f.readline()
```

### Writing Files
```python
# Write (overwrites existing file)
with open('output.txt', 'w') as f:
    f.write("Hello World\\n")
    f.write("Second line\\n")

# Append
with open('output.txt', 'a') as f:
    f.write("Appended line\\n")

# Write multiple lines
lines = ["Line 1\\n", "Line 2\\n", "Line 3\\n"]
with open('output.txt', 'w') as f:
    f.writelines(lines)
```

### CSV Files
```python
import csv

# Reading CSV
with open('data.csv', 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        print(row)  # row is a list

# Reading CSV with headers
with open('data.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row)  # row is a dictionary

# Writing CSV
data = [
    ['Name', 'Age', 'City'],
    ['Alice', 30, 'NYC'],
    ['Bob', 25, 'LA']
]
with open('output.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(data)

# Writing CSV with headers
with open('output.csv', 'w', newline='') as f:
    fieldnames = ['Name', 'Age', 'City']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerow({'Name': 'Alice', 'Age': 30, 'City': 'NYC'})
```

### JSON Files
```python
import json

# Reading JSON
with open('data.json', 'r') as f:
    data = json.load(f)

# Writing JSON
data = {'name': 'Alice', 'age': 30, 'city': 'NYC'}
with open('output.json', 'w') as f:
    json.dump(data, f, indent=4)

# Convert to/from JSON string
json_string = json.dumps(data)
data = json.loads(json_string)
```

### File and Directory Operations
```python
import os
from pathlib import Path

# Check if file exists
os.path.exists('file.txt')
Path('file.txt').exists()

# Create directory
os.makedirs('new_folder', exist_ok=True)
Path('new_folder').mkdir(exist_ok=True)

# List files in directory
os.listdir('.')
list(Path('.').iterdir())

# Get file info
os.path.getsize('file.txt')
os.path.isfile('file.txt')
os.path.isdir('folder')

# Path operations (pathlib - RECOMMENDED)
path = Path('folder/subfolder/file.txt')
path.parent         # Path('folder/subfolder')
path.name           # 'file.txt'
path.stem           # 'file'
path.suffix         # '.txt'
path.exists()       # True/False
```

---

## 7. Data Processing with Pandas

### DataFrame Basics
```python
import pandas as pd
import numpy as np

# Creating DataFrames
df = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35],
    'city': ['NYC', 'LA', 'Chicago']
})

# From CSV
df = pd.read_csv('data.csv')
df = pd.read_csv('data.csv', sep=';')  # Custom delimiter

# Basic info
df.head()           # First 5 rows
df.tail(10)         # Last 10 rows
df.info()           # Data types and memory usage
df.describe()       # Statistical summary
df.shape            # (rows, columns)
df.columns          # Column names
df.dtypes           # Data types
```

### Data Selection
```python
# Select column
df['name']          # Series
df[['name', 'age']] # DataFrame

# Select rows by index
df.iloc[0]          # First row
df.iloc[0:3]        # First 3 rows
df.iloc[:, 0]       # First column

# Select rows by label
df.loc[0]           # Row with index 0
df.loc[0:2]         # Rows 0-2 (inclusive)
df.loc[:, 'name']   # Column 'name'

# Boolean indexing
df[df['age'] > 25]
df[(df['age'] > 25) & (df['city'] == 'NYC')]
df[df['name'].isin(['Alice', 'Bob'])]
```

### Data Manipulation
```python
# Add column
df['salary'] = [50000, 60000, 70000]
df['age_next_year'] = df['age'] + 1

# Modify column
df['age'] = df['age'] + 1

# Remove column
df.drop('salary', axis=1, inplace=True)
df = df.drop(['col1', 'col2'], axis=1)

# Remove rows
df.drop(0, inplace=True)  # Remove row with index 0
df = df.drop([0, 1, 2])   # Remove multiple rows

# Rename columns
df.rename(columns={'name': 'full_name'}, inplace=True)

# Sort
df.sort_values('age', ascending=False)
df.sort_values(['city', 'age'])

# Reset index
df.reset_index(drop=True, inplace=True)
```

### Data Cleaning
```python
# Handle missing values
df.isnull()              # Boolean DataFrame
df.isnull().sum()        # Count nulls per column
df.dropna()              # Remove rows with any null
df.dropna(how='all')     # Remove rows where all values are null
df.fillna(0)             # Fill nulls with 0
df.fillna(df.mean())     # Fill with column mean

# Remove duplicates
df.drop_duplicates()
df.drop_duplicates(subset=['name'])

# Replace values
df.replace('NYC', 'New York')
df.replace({'NYC': 'New York', 'LA': 'Los Angeles'})

# Convert data types
df['age'] = df['age'].astype(int)
df['date'] = pd.to_datetime(df['date'])
```

### Aggregation and Grouping
```python
# Basic statistics
df['age'].mean()
df['age'].median()
df['age'].std()
df['age'].min()
df['age'].max()
df['age'].sum()
df['age'].count()
df['age'].value_counts()

# Group by
df.groupby('city')['age'].mean()
df.groupby('city').agg({
    'age': ['mean', 'min', 'max'],
    'salary': 'sum'
})

# Multiple grouping
df.groupby(['city', 'department'])['salary'].mean()

# Apply custom function
df.groupby('city')['age'].apply(lambda x: x.max() - x.min())
```

### Merging and Joining
```python
# Concatenate
df1 = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
df2 = pd.DataFrame({'A': [5, 6], 'B': [7, 8]})
pd.concat([df1, df2])  # Vertical
pd.concat([df1, df2], axis=1)  # Horizontal

# Merge (SQL-style joins)
left = pd.DataFrame({'key': ['A', 'B', 'C'], 'value': [1, 2, 3]})
right = pd.DataFrame({'key': ['A', 'B', 'D'], 'value': [4, 5, 6]})

pd.merge(left, right, on='key', how='inner')  # Inner join
pd.merge(left, right, on='key', how='left')   # Left join
pd.merge(left, right, on='key', how='right')  # Right join
pd.merge(left, right, on='key', how='outer')  # Outer join
```

### Data Analysis
```python
# Correlation
df.corr()  # Correlation matrix
df['col1'].corr(df['col2'])  # Correlation between two columns

# Pivot tables
df.pivot_table(values='salary', index='city', columns='department', aggfunc='mean')

# Cross-tabulation
pd.crosstab(df['city'], df['department'])

# Rolling window
df['rolling_mean'] = df['value'].rolling(window=3).mean()

# Cumulative operations
df['cumsum'] = df['value'].cumsum()
df['cumprod'] = df['value'].cumprod()
```

---

## 8. Comprehensions

### List Comprehensions
```python
# Basic syntax: [expression for item in iterable]
squares = [x**2 for x in range(10)]
# [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

# With condition
evens = [x for x in range(10) if x % 2 == 0]
# [0, 2, 4, 6, 8]

# With if-else
labels = ["even" if x % 2 == 0 else "odd" for x in range(5)]
# ["even", "odd", "even", "odd", "even"]

# Nested comprehensions
matrix = [[i*j for j in range(3)] for i in range(3)]
# [[0, 0, 0], [0, 1, 2], [0, 2, 4]]

# Flatten nested list
nested = [[1, 2], [3, 4], [5, 6]]
flat = [item for sublist in nested for item in sublist]
# [1, 2, 3, 4, 5, 6]

# Multiple conditions
result = [x for x in range(100) if x % 3 == 0 if x % 5 == 0]
# [0, 15, 30, 45, 60, 75, 90]
```

### Dictionary Comprehensions
```python
# Basic syntax: {key: value for item in iterable}
squares = {x: x**2 for x in range(5)}
# {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}

# From two lists
keys = ['a', 'b', 'c']
values = [1, 2, 3]
mapping = {k: v for k, v in zip(keys, values)}
# {'a': 1, 'b': 2, 'c': 3}

# With condition
even_squares = {x: x**2 for x in range(10) if x % 2 == 0}
# {0: 0, 2: 4, 4: 16, 6: 36, 8: 64}

# Swap keys and values
original = {'a': 1, 'b': 2, 'c': 3}
swapped = {v: k for k, v in original.items()}
# {1: 'a', 2: 'b', 3: 'c'}

# From DataFrame
df = pd.DataFrame({'name': ['Alice', 'Bob'], 'age': [25, 30]})
name_to_age = {row['name']: row['age'] for _, row in df.iterrows()}
```

### Set Comprehensions
```python
# Basic syntax: {expression for item in iterable}
unique_lengths = {len(word) for word in ['hello', 'world', 'python']}
# {5, 6}

# With condition
vowels = {char for char in 'hello world' if char in 'aeiou'}
# {'e', 'o'}
```

### Generator Expressions
```python
# Like list comprehension but with () instead of []
# Returns a generator (lazy evaluation)
gen = (x**2 for x in range(1000000))

# Memory efficient - elements generated on-demand
sum(x**2 for x in range(1000000))

# Can be consumed only once
g = (x for x in range(3))
list(g)  # [0, 1, 2]
list(g)  # [] (already consumed)
```

---

## 9. Generators

### Generator Functions
```python
# Function with yield instead of return
def countdown(n):
    while n > 0:
        yield n
        n -= 1

# Use generator
for i in countdown(5):
    print(i)  # 5, 4, 3, 2, 1

# Generators are iterators
gen = countdown(3)
next(gen)  # 3
next(gen)  # 2
next(gen)  # 1
next(gen)  # StopIteration error
```

### Generator Examples
```python
# Infinite generator
def infinite_sequence():
    num = 0
    while True:
        yield num
        num += 1

# Read large file line by line
def read_large_file(file_path):
    with open(file_path, 'r') as f:
        for line in f:
            yield line.strip()

# Fibonacci generator
def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

# Take first n elements
fib = fibonacci()
first_10 = [next(fib) for _ in range(10)]
# [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]

# Generator pipeline
def numbers():
    for i in range(10):
        yield i

def squares(nums):
    for n in nums:
        yield n ** 2

def evens(nums):
    for n in nums:
        if n % 2 == 0:
            yield n

# Chain generators
result = list(evens(squares(numbers())))
# [0, 4, 16, 36, 64]
```

### Memory Efficiency
```python
import sys

# List comprehension (eager evaluation)
list_comp = [x**2 for x in range(1000000)]
print(sys.getsizeof(list_comp))  # ~8,000,000 bytes

# Generator expression (lazy evaluation)
gen_exp = (x**2 for x in range(1000000))
print(sys.getsizeof(gen_exp))    # ~120 bytes

# Use generators for large datasets
# BAD: Load everything into memory
def process_all(data):
    return [process(item) for item in data]

# GOOD: Process one at a time
def process_stream(data):
    for item in data:
        yield process(item)
```

---

## 10. Object-Oriented Programming

### Classes and Objects
```python
# Class definition
class Person:
    # Class variable (shared by all instances)
    species = "Homo sapiens"
    
    # Constructor
    def __init__(self, name, age):
        # Instance variables
        self.name = name
        self.age = age
    
    # Instance method
    def greet(self):
        return f"Hello, I'm {self.name}"
    
    # Method with parameters
    def birthday(self):
        self.age += 1
    
    # String representation
    def __str__(self):
        return f"Person({self.name}, {self.age})"

# Create instances
person1 = Person("Alice", 30)
person2 = Person("Bob", 25)

# Access attributes and methods
print(person1.name)     # "Alice"
print(person1.greet())  # "Hello, I'm Alice"
person1.birthday()
print(person1.age)      # 31
```

### Encapsulation (Data Hiding)
```python
class BankAccount:
    def __init__(self, balance):
        # Private attribute (name mangling)
        self.__balance = balance
    
    # Public method to access private attribute
    def get_balance(self):
        return self.__balance
    
    # Public method to modify private attribute
    def deposit(self, amount):
        if amount > 0:
            self.__balance += amount
        else:
            raise ValueError("Amount must be positive")
    
    def withdraw(self, amount):
        if 0 < amount <= self.__balance:
            self.__balance -= amount
        else:
            raise ValueError("Invalid amount")

account = BankAccount(1000)
# account.__balance  # AttributeError (private)
print(account.get_balance())  # 1000 (public getter)
account.deposit(500)
print(account.get_balance())  # 1500
```

### Inheritance
```python
# Parent class
class Animal:
    def __init__(self, name):
        self.name = name
    
    def speak(self):
        raise NotImplementedError("Subclass must implement")

# Child class
class Dog(Animal):
    def __init__(self, name, breed):
        # Call parent constructor
        super().__init__(name)
        self.breed = breed
    
    def speak(self):
        return f"{self.name} says Woof!"

class Cat(Animal):
    def speak(self):
        return f"{self.name} says Meow!"

# Multiple inheritance
class FlyingMixin:
    def fly(self):
        return f"{self.name} is flying"

class Bird(Animal, FlyingMixin):
    def speak(self):
        return f"{self.name} says Tweet!"

# Usage
dog = Dog("Buddy", "Golden Retriever")
print(dog.speak())  # "Buddy says Woof!"

bird = Bird("Tweety")
print(bird.speak())  # "Tweety says Tweet!"
print(bird.fly())    # "Tweety is flying"
```

### Properties and Decorators
```python
class Temperature:
    def __init__(self, celsius):
        self._celsius = celsius
    
    # Getter (property)
    @property
    def celsius(self):
        return self._celsius
    
    # Setter
    @celsius.setter
    def celsius(self, value):
        if value < -273.15:
            raise ValueError("Temperature below absolute zero")
        self._celsius = value
    
    # Computed property
    @property
    def fahrenheit(self):
        return (self._celsius * 9/5) + 32
    
    @fahrenheit.setter
    def fahrenheit(self, value):
        self.celsius = (value - 32) * 5/9

# Usage
temp = Temperature(25)
print(temp.celsius)      # 25
print(temp.fahrenheit)   # 77.0
temp.celsius = 30
print(temp.fahrenheit)   # 86.0
```

### Class Methods and Static Methods
```python
class MathOperations:
    pi = 3.14159
    
    # Regular instance method (needs self)
    def instance_method(self, x):
        return x * 2
    
    # Class method (receives class as first argument)
    @classmethod
    def from_string(cls, config_string):
        # Alternative constructor
        values = config_string.split(',')
        return cls(*values)
    
    # Static method (no self or cls)
    @staticmethod
    def add(x, y):
        return x + y

# Usage
obj = MathOperations()
obj.instance_method(5)           # 10
MathOperations.add(3, 4)         # 7 (no instance needed)
obj2 = MathOperations.from_string("param1,param2")
```

### Special Methods (Magic Methods)
```python
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    # String representation
    def __str__(self):
        return f"Vector({self.x}, {self.y})"
    
    def __repr__(self):
        return f"Vector(x={self.x}, y={self.y})"
    
    # Arithmetic operations
    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)
    
    # Comparison
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    # Length
    def __len__(self):
        return int((self.x**2 + self.y**2)**0.5)
    
    # Indexing
    def __getitem__(self, index):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        raise IndexError("Index out of range")

# Usage
v1 = Vector(1, 2)
v2 = Vector(3, 4)
print(v1 + v2)    # Vector(4, 6)
print(v1 == v2)   # False
print(len(v1))    # 2
print(v1[0])      # 1
```

---

## 11. Error Handling

### Try-Except Blocks
```python
# Basic exception handling
try:
    result = 10 / 0
except ZeroDivisionError:
    print("Cannot divide by zero")

# Multiple exceptions
try:
    value = int(input("Enter a number: "))
    result = 10 / value
except ValueError:
    print("Invalid input")
except ZeroDivisionError:
    print("Cannot divide by zero")

# Catch multiple exception types
try:
    # code
    pass
except (ValueError, TypeError) as e:
    print(f"Error: {e}")

# Catch all exceptions (use sparingly)
try:
    # code
    pass
except Exception as e:
    print(f"An error occurred: {e}")

# Else clause (runs if no exception)
try:
    result = 10 / 2
except ZeroDivisionError:
    print("Error")
else:
    print(f"Result: {result}")

# Finally clause (always runs)
try:
    f = open('file.txt')
    data = f.read()
except FileNotFoundError:
    print("File not found")
finally:
    f.close()  # Always close the file
```

### Raising Exceptions
```python
# Raise built-in exception
def divide(a, b):
    if b == 0:
        raise ValueError("Denominator cannot be zero")
    return a / b

# Re-raise exception
try:
    result = divide(10, 0)
except ValueError:
    print("Caught error")
    raise  # Re-raise the same exception

# Custom exceptions
class InvalidAgeError(Exception):
    \"\"\"Custom exception for invalid age\"\"\"
    pass

def set_age(age):
    if age < 0 or age > 120:
        raise InvalidAgeError(f"Age {age} is not valid")
    return age

try:
    set_age(150)
except InvalidAgeError as e:
    print(f"Error: {e}")
```

### Context Managers
```python
# Using 'with' statement (automatic resource cleanup)
with open('file.txt', 'r') as f:
    data = f.read()
# File automatically closed

# Custom context manager
class DatabaseConnection:
    def __enter__(self):
        print("Opening connection")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Closing connection")
        return False  # Don't suppress exceptions
    
    def query(self, sql):
        print(f"Executing: {sql}")

with DatabaseConnection() as db:
    db.query("SELECT * FROM users")

# Using contextlib
from contextlib import contextmanager

@contextmanager
def file_manager(filename, mode):
    f = open(filename, mode)
    try:
        yield f
    finally:
        f.close()

with file_manager('file.txt', 'r') as f:
    data = f.read()
```

### Assertions
```python
# Assert statement (for debugging, disabled with -O flag)
def calculate_average(numbers):
    assert len(numbers) > 0, "List cannot be empty"
    return sum(numbers) / len(numbers)

# AssertionError raised if condition is False
calculate_average([])  # AssertionError: List cannot be empty

# Use assertions for internal checks, not input validation
# Good: assert isinstance(x, int), "x must be integer"
# Bad: Using assertions for user input validation
```

---

## 12. Logging

### Basic Logging
```python
import logging

# Basic configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Log levels (in order of severity)
logging.debug("Debug message")      # Detailed diagnostic info
logging.info("Info message")        # Confirmation things are working
logging.warning("Warning message")  # Something unexpected happened
logging.error("Error message")      # More serious problem
logging.critical("Critical message") # Very serious error

# Log with variables
name = "Alice"
age = 30
logging.info(f"User {name} is {age} years old")
```

### Advanced Logging
```python
import logging

# Configure logging to file
logging.basicConfig(
    filename='app.log',
    filemode='a',  # 'w' to overwrite, 'a' to append
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Create custom logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create handlers
file_handler = logging.FileHandler('app.log')
console_handler = logging.StreamHandler()

# Set level for handlers
file_handler.setLevel(logging.ERROR)
console_handler.setLevel(logging.INFO)

# Create formatters
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Use logger
logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message")

# Log exceptions
try:
    1 / 0
except Exception as e:
    logger.exception("An error occurred")  # Includes traceback
```

### Logging in Production
```python
import logging
from logging.handlers import RotatingFileHandler

# Rotating file handler (creates new file when size limit reached)
handler = RotatingFileHandler(
    'app.log',
    maxBytes=10485760,  # 10MB
    backupCount=5
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# Time-based rotation
from logging.handlers import TimedRotatingFileHandler

handler = TimedRotatingFileHandler(
    'app.log',
    when='midnight',  # Rotate at midnight
    interval=1,
    backupCount=7  # Keep 7 days of logs
)
```

---

## 13. Modules & Packages

### Importing Modules
```python
# Import entire module
import math
print(math.pi)
print(math.sqrt(16))

# Import with alias
import pandas as pd
import numpy as np

# Import specific items
from math import pi, sqrt
from datetime import datetime, timedelta

# Import all (avoid this)
from math import *

# Import from subdirectory
from package.subpackage import module
```

### Creating Modules
```python
# File: my_module.py
def greet(name):
    return f"Hello, {name}!"

PI = 3.14159

class Calculator:
    @staticmethod
    def add(a, b):
        return a + b

# File: main.py
import my_module

print(my_module.greet("Alice"))
print(my_module.PI)
calc = my_module.Calculator()
print(calc.add(3, 4))
```

### Packages
```python
# Directory structure:
# my_package/
#   __init__.py
#   module1.py
#   module2.py
#   subpackage/
#     __init__.py
#     module3.py

# File: my_package/__init__.py
from .module1 import function1
from .module2 import function2

# Usage
from my_package import function1
from my_package.subpackage import module3
```

### Standard Library Modules
```python
# Common standard library modules

# os - Operating system interface
import os
os.getcwd()              # Current directory
os.listdir('.')          # List files
os.environ.get('PATH')   # Environment variables

# sys - System-specific parameters
import sys
sys.argv                 # Command-line arguments
sys.version             # Python version
sys.path                # Module search path

# datetime - Date and time
from datetime import datetime, timedelta
now = datetime.now()
tomorrow = now + timedelta(days=1)
formatted = now.strftime('%Y-%m-%d %H:%M:%S')

# collections - Specialized containers
from collections import Counter, defaultdict, deque
counter = Counter(['a', 'b', 'a', 'c', 'b', 'a'])
# Counter({'a': 3, 'b': 2, 'c': 1})

# itertools - Iterator functions
from itertools import combinations, permutations, product
list(combinations([1, 2, 3], 2))  # [(1, 2), (1, 3), (2, 3)]

# random - Random number generation
import random
random.randint(1, 10)    # Random integer
random.choice([1, 2, 3]) # Random element
random.shuffle(list)     # Shuffle list in-place

# pathlib - Object-oriented paths
from pathlib import Path
path = Path('folder/file.txt')
path.exists()
path.read_text()
```

---

## 14. Testing

### unittest
```python
import unittest

# Function to test
def add(a, b):
    return a + b

# Test class
class TestMathFunctions(unittest.TestCase):
    
    # Setup (runs before each test)
    def setUp(self):
        self.numbers = [1, 2, 3, 4, 5]
    
    # Teardown (runs after each test)
    def tearDown(self):
        pass
    
    # Test methods (must start with 'test_')
    def test_add_positive(self):
        self.assertEqual(add(2, 3), 5)
    
    def test_add_negative(self):
        self.assertEqual(add(-1, -1), -2)
    
    def test_add_zero(self):
        self.assertEqual(add(0, 0), 0)
    
    # Assertion methods
    def test_assertions(self):
        self.assertTrue(True)
        self.assertFalse(False)
        self.assertIsNone(None)
        self.assertIsNotNone(1)
        self.assertIn(1, [1, 2, 3])
        self.assertNotIn(4, [1, 2, 3])
        self.assertIsInstance(1, int)
        self.assertRaises(ValueError, int, 'abc')
        self.assertAlmostEqual(1.0, 1.0001, places=3)

# Run tests
if __name__ == '__main__':
    unittest.main()
```

### pytest (Recommended)
```python
# Install: pip install pytest

# File: test_math.py
def add(a, b):
    return a + b

# Test functions (must start with 'test_')
def test_add_positive():
    assert add(2, 3) == 5

def test_add_negative():
    assert add(-1, -1) == -2

# Fixtures (setup/teardown)
import pytest

@pytest.fixture
def sample_data():
    \"\"\"Fixture that provides test data\"\"\"
    return [1, 2, 3, 4, 5]

def test_with_fixture(sample_data):
    assert len(sample_data) == 5
    assert sum(sample_data) == 15

# Parametrized tests
@pytest.mark.parametrize("a,b,expected", [
    (2, 3, 5),
    (0, 0, 0),
    (-1, 1, 0),
    (10, -5, 5)
])
def test_add_parametrized(a, b, expected):
    assert add(a, b) == expected

# Test exceptions
def test_division_by_zero():
    with pytest.raises(ZeroDivisionError):
        result = 1 / 0

# Run tests from command line:
# pytest                 # Run all tests
# pytest test_math.py    # Run specific file
# pytest -v              # Verbose output
# pytest -k "add"        # Run tests matching pattern
```

### Testing Best Practices
```python
# 1. Test one thing per test
def test_user_creation():
    user = User("Alice", 30)
    assert user.name == "Alice"

def test_user_age():
    user = User("Alice", 30)
    assert user.age == 30

# 2. Use descriptive test names
def test_user_with_negative_age_raises_error():
    with pytest.raises(ValueError):
        user = User("Alice", -1)

# 3. Arrange-Act-Assert pattern
def test_bank_account_deposit():
    # Arrange
    account = BankAccount(100)
    
    # Act
    account.deposit(50)
    
    # Assert
    assert account.balance == 150

# 4. Test edge cases
def test_empty_list():
    assert sum([]) == 0

def test_single_element():
    assert max([42]) == 42

# 5. Use mocking for external dependencies
from unittest.mock import Mock, patch

def test_api_call():
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'data': 'test'}
        
        response = fetch_data()
        assert response['data'] == 'test'
```

---

## 15. Parallel & Distributed Computing

### Threading (I/O-Bound Tasks)
```python
import threading
import time

# Basic thread
def worker(name):
    print(f"Thread {name} starting")
    time.sleep(2)
    print(f"Thread {name} finished")

# Create and start threads
thread1 = threading.Thread(target=worker, args=("A",))
thread2 = threading.Thread(target=worker, args=("B",))

thread1.start()
thread2.start()

# Wait for threads to complete
thread1.join()
thread2.join()

# Thread pool
from concurrent.futures import ThreadPoolExecutor

def download_file(url):
    # Simulate I/O operation
    time.sleep(1)
    return f"Downloaded {url}"

urls = ['url1', 'url2', 'url3', 'url4']

with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(download_file, urls))

# Thread-safe operations
from threading import Lock

counter = 0
lock = Lock()

def increment():
    global counter
    with lock:
        counter += 1

threads = [threading.Thread(target=increment) for _ in range(1000)]
for t in threads:
    t.start()
for t in threads:
    t.join()
```

### Multiprocessing (CPU-Bound Tasks)
```python
import multiprocessing as mp
import time

# Basic process
def worker(name):
    print(f"Process {name} starting")
    time.sleep(2)
    print(f"Process {name} finished")

# Create and start processes
process1 = mp.Process(target=worker, args=("A",))
process2 = mp.Process(target=worker, args=("B",))

process1.start()
process2.start()

process1.join()
process2.join()

# Process pool
from concurrent.futures import ProcessPoolExecutor

def cpu_intensive_task(n):
    # Simulate CPU-bound operation
    result = sum(i**2 for i in range(n))
    return result

numbers = [1000000, 2000000, 3000000, 4000000]

with ProcessPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(cpu_intensive_task, numbers))

# Multiprocessing Pool
from multiprocessing import Pool

def square(x):
    return x ** 2

with Pool(processes=4) as pool:
    results = pool.map(square, range(10))
    # [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
```

### Async/Await (Asynchronous I/O)
```python
import asyncio

# Async function
async def fetch_data(url):
    print(f"Fetching {url}")
    await asyncio.sleep(1)  # Simulate network delay
    print(f"Finished {url}")
    return f"Data from {url}"

# Run async function
async def main():
    result = await fetch_data("http://example.com")
    print(result)

# Run event loop
asyncio.run(main())

# Multiple async tasks
async def main():
    tasks = [
        fetch_data("http://example1.com"),
        fetch_data("http://example2.com"),
        fetch_data("http://example3.com")
    ]
    results = await asyncio.gather(*tasks)
    print(results)

# Async with aiohttp
import aiohttp

async def fetch_url(session, url):
    async with session.get(url) as response:
        return await response.text()

async def main():
    async with aiohttp.ClientSession() as session:
        html = await fetch_url(session, 'http://python.org')
```

### Dask (Parallel Pandas)
```python
import dask.dataframe as dd
import pandas as pd

# Create Dask DataFrame from pandas
df = pd.DataFrame({'x': range(1000), 'y': range(1000)})
ddf = dd.from_pandas(df, npartitions=4)

# Read large CSV in parallel
ddf = dd.read_csv('large_file.csv', blocksize='64MB')

# Operations (lazy evaluation)
ddf['z'] = ddf['x'] + ddf['y']
result = ddf.groupby('x')['y'].mean()

# Compute (trigger execution)
computed_result = result.compute()

# Parallel apply
def complex_function(row):
    # CPU-intensive operation
    return row['x'] ** 2

ddf['result'] = ddf.apply(complex_function, axis=1, meta=('result', 'f8'))
final = ddf.compute()
```

### When to Use What
```python
\"\"\"
Threading:
- I/O-bound tasks (file operations, network requests)
- Tasks that spend time waiting
- Shared memory needed
- GIL limitation for CPU tasks

Multiprocessing:
- CPU-bound tasks (data processing, calculations)
- Tasks that require full CPU cores
- Separate memory space
- No GIL limitation

Async/Await:
- I/O-bound tasks with many concurrent operations
- Network requests, database queries
- Single-threaded but efficient
- Best for thousands of concurrent I/O operations

Dask:
- Large datasets that don't fit in memory
- Parallel pandas operations
- Distributed computing across clusters
- Complex data pipelines
\"\"\"
```

---

## 16. Type Hints

### Basic Type Hints (Python 3.5+)
```python
# Variable annotations
age: int = 30
name: str = "Alice"
is_active: bool = True
salary: float = 50000.0

# Function annotations
def greet(name: str) -> str:
    return f"Hello, {name}!"

def add(a: int, b: int) -> int:
    return a + b

# No return value
def print_message(message: str) -> None:
    print(message)
```

### Advanced Type Hints
```python
from typing import List, Dict, Tuple, Set, Optional, Union, Any

# Collections
numbers: List[int] = [1, 2, 3]
mapping: Dict[str, int] = {"a": 1, "b": 2}
coordinates: Tuple[int, int] = (10, 20)
unique_values: Set[str] = {"a", "b", "c"}

# Optional (value or None)
def find_user(user_id: int) -> Optional[str]:
    if user_id > 0:
        return "User name"
    return None

# Union (multiple possible types)
def process_data(data: Union[int, str, float]) -> str:
    return str(data)

# Any (any type allowed)
def log(message: Any) -> None:
    print(message)

# Callable (function type)
from typing import Callable

def apply_operation(x: int, operation: Callable[[int], int]) -> int:
    return operation(x)

# Generic types
from typing import TypeVar, Generic

T = TypeVar('T')

def first_element(items: List[T]) -> T:
    return items[0]

# Class with generic type
class Stack(Generic[T]):
    def __init__(self) -> None:
        self.items: List[T] = []
    
    def push(self, item: T) -> None:
        self.items.append(item)
    
    def pop(self) -> T:
        return self.items.pop()
```

### Type Checking
```python
# Install mypy: pip install mypy
# Run: mypy script.py

# Type aliases
from typing import List, Dict

Vector = List[float]
Matrix = List[Vector]
JSONDict = Dict[str, Any]

def scale_vector(vector: Vector, scalar: float) -> Vector:
    return [x * scalar for x in vector]

# Literal types (Python 3.8+)
from typing import Literal

def set_mode(mode: Literal["read", "write"]) -> None:
    print(f"Mode: {mode}")

# TypedDict (Python 3.8+)
from typing import TypedDict

class Person(TypedDict):
    name: str
    age: int
    city: str

def process_person(person: Person) -> str:
    return f"{person['name']} from {person['city']}"
```

---

## 17. Real-World Examples from Course Labs

### Lecture 3: Research Paper Management System

#### Global Variables and Query Tracking
```python
# Global counter to track function calls
total_queries = 0

def display_titles(papers, year=None):
    global total_queries
    total_queries += 1
    
    if year is None:
        print("All Paper Titles:")
        for paper in papers:
            print(f"- {paper['title']}")
    else:
        print(f"Papers from {year}:")
        filtered_papers = [paper for paper in papers if paper['year'] == year]
        for paper in filtered_papers:
            print(f"- {paper['title']}")

def get_total_queries():
    return total_queries

def reset_query_counter():
    global total_queries
    total_queries = 0
```

#### Working with Dictionaries and Lists
```python
# Data structure: List of dictionaries
papers = [
    {"title": "Deep Learning for NLP", "citations": 520, "year": 2021, 
     "keywords": ["NLP", "Deep Learning", "Transformer"]},
    {"title": "AI in Healthcare", "citations": 315, "year": 2019, 
     "keywords": ["Healthcare", "AI", "Diagnosis"]},
]

# Filtering with conditions
def filter_papers(papers, min_citations, keyword=None):
    filtered = [paper for paper in papers if paper['citations'] >= min_citations]
    
    if keyword:
        filtered = [paper for paper in filtered 
                   if any(keyword.lower() in kw.lower() for kw in paper['keywords'])]
    return filtered

# Example usage
high_impact_papers = filter_papers(papers, min_citations=500)
ai_papers = filter_papers(papers, min_citations=200, keyword="AI")
```

#### Lambda Functions with Sorting
```python
# Find paper with most citations using lambda
def find_extreme_paper(papers, field, find_max=True):
    if not papers:
        return None
    if find_max:
        return max(papers, key=lambda p: p[field])
    else:
        return min(papers, key=lambda p: p[field])

# Usage
most_cited = find_extreme_paper(papers, 'citations', find_max=True)
oldest_paper = find_extreme_paper(papers, 'year', find_max=False)

# Sort papers by multiple criteria
sorted_papers = sorted(papers, key=lambda p: (p['year'], -p['citations']))
```

#### Nested Functions for Encapsulation
```python
def analyze_keyword(papers, keyword):
    \"\"\"Nested function to check keyword existence\"\"\"
    
    def check_keyword_exists(paper_keywords, target_keyword):
        return any(target_keyword.lower() in kw.lower() 
                  for kw in paper_keywords)
    
    # Use nested function
    relevant_count = sum(1 for paper in papers 
                        if check_keyword_exists(paper['keywords'], keyword))
    return relevant_count

# Example usage
ai_count = analyze_keyword(papers, "AI")
nlp_count = analyze_keyword(papers, "NLP")
```

#### Dictionary Comprehensions for Statistics
```python
# Get keyword frequency across all papers
def get_keyword_stats(papers):
    keyword_counts = {}
    for paper in papers:
        for keyword in paper['keywords']:
            keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
    return keyword_counts

# Using comprehension for year-based analysis
def get_citation_trend(papers):
    trend = {}
    for paper in papers:
        year = paper['year']
        trend[year] = trend.get(year, 0) + paper['citations']
    return trend

# Example usage
keyword_stats = get_keyword_stats(papers)
top_keywords = sorted(keyword_stats.items(), key=lambda x: x[1], reverse=True)[:5]
```

#### Advanced Filtering with Lambda
```python
# Filter papers by complex conditions
def filter_papers_by_condition(papers, condition_func):
    return list(filter(condition_func, papers))

# Usage examples
high_impact = filter_papers_by_condition(
    papers, 
    lambda p: p['citations'] > 600
)

nlp_papers = filter_papers_by_condition(
    papers, 
    lambda p: any('NLP' in kw for kw in p['keywords'])
)

recent_ai = filter_papers_by_condition(
    papers, 
    lambda p: p['year'] >= 2022 and any('AI' in kw for kw in p['keywords'])
)
```

---

### Lecture 4: Medical Appointment System

#### Custom Exception Classes
```python
# Define custom exceptions for specific error cases
class ClinicMismatchError(Exception):
    \"\"\"Raised when doctor is not available at specified clinic\"\"\"
    pass

class DoubleBookingError(Exception):
    \"\"\"Raised when attempting to book an already occupied slot\"\"\"
    pass

class AppointmentNotFoundError(Exception):
    \"\"\"Raised when appointment doesn't exist\"\"\"
    pass

class InvalidEntityError(Exception):
    \"\"\"Raised when patient or doctor ID is invalid\"\"\"
    pass

# Usage in functions
def book_appointment(patient_id, doctor_id, date, time, clinic):
    doctor = next((d for d in doctors if d['id'] == doctor_id), None)
    
    if not doctor:
        raise InvalidEntityError(f"Doctor not found: {doctor_id}")
    
    if clinic not in doctor['clinics']:
        raise ClinicMismatchError(
            f"Dr. {doctor['name']} is not available at {clinic} clinic"
        )
    
    # Check for double booking
    for apt in appointments:
        if (apt['doctor_id'] == doctor_id and 
            apt['date'] == date and 
            apt['time'] == time):
            raise DoubleBookingError(
                f"Dr. {doctor['name']} already has an appointment at {date} {time}"
            )
```

#### Decorators for Input Validation
```python
from functools import wraps

def validate_input(func):
    \"\"\"Decorator to validate patient and doctor IDs\"\"\"
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Extract IDs based on function name
        if func.__name__ == 'book_appointment':
            patient_id, doctor_id = args[0], args[1]
        elif func.__name__ == 'cancel_appointment':
            patient_id = args[0]
            doctor_id = None
        else:
            return func(*args, **kwargs)
        
        # Validate patient ID
        if not any(p['id'] == patient_id for p in patients):
            raise InvalidEntityError(f"Invalid patient ID: {patient_id}")
        
        # Validate doctor ID if provided
        if doctor_id and not any(d['id'] == doctor_id for d in doctors):
            raise InvalidEntityError(f"Invalid doctor ID: {doctor_id}")
        
        return func(*args, **kwargs)
    
    return wrapper

# Apply decorator to functions
@validate_input
def book_appointment(patient_id, doctor_id, date, time, clinic):
    # Function implementation
    pass

@validate_input
def cancel_appointment(patient_id, date, time):
    # Function implementation
    pass
```

#### Comprehensive Error Handling with Logging
```python
import logging
import os

# Setup logging
if not os.path.exists('logs'):
    os.makedirs('logs')

logging.basicConfig(
    filename='logs/system.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='a'
)

def book_appointment(patient_id, doctor_id, date, time, clinic):
    try:
        logging.info(f"Attempting to book: Patient {patient_id}, "
                    f"Doctor {doctor_id}, {date} {time} at {clinic}")
        
        # Validation logic
        doctor = None
        for d in doctors:
            if d['id'] == doctor_id:
                doctor = d
                break
        
        if not doctor:
            raise KeyError(f"Doctor not found: {doctor_id}")
        
        if clinic not in doctor['clinics']:
            raise ClinicMismatchError(
                f"Dr. {doctor['name']} is not available at {clinic} clinic"
            )
        
        # Check double booking
        for apt in appointments:
            if (apt['doctor_id'] == doctor_id and 
                apt['date'] == date and 
                apt['time'] == time):
                raise DoubleBookingError(
                    f"Dr. {doctor['name']} already has an appointment at {date} {time}"
                )
        
        # Book appointment
        new_appointment = {
            'patient_id': patient_id,
            'doctor_id': doctor_id,
            'date': date,
            'time': time,
            'clinic': clinic
        }
        
        appointments.append(new_appointment)
        logging.info(f"Successfully booked appointment for Patient {patient_id}")
        
        return True
        
    except KeyError as e:
        logging.warning(f"KeyError during booking: {e}")
        raise
    except ValueError as e:
        logging.warning(f"ValueError during booking: {e}")
        raise
    except ClinicMismatchError as e:
        logging.warning(f"Clinic mismatch: {e}")
        raise
    except DoubleBookingError as e:
        logging.warning(f"Double booking attempt: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error during booking: {e}")
        raise
    finally:
        logging.info("Booking attempt complete")
```

#### CSV File Operations with Error Handling
```python
import csv
import os

def save_appointments(filename):
    \"\"\"Save appointments to CSV file with proper error handling\"\"\"
    try:
        # Create output directory if it doesn't exist
        output_dir = 'output'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        filepath = os.path.join(output_dir, filename)
        
        # Write to CSV
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['patient_id', 'doctor_id', 'date', 'time', 'clinic']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for appointment in appointments:
                writer.writerow(appointment)
        
        logging.info(f"Appointments saved successfully: {filepath}")
        return True
        
    except FileNotFoundError as e:
        logging.error(f"File not found error: {e}")
        raise
    except PermissionError as e:
        logging.error(f"Permission denied when saving file: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error saving appointments: {e}")
        raise
```

#### Nested Functions for Data Processing
```python
def generate_doctor_summary(doctor_id):
    \"\"\"Generate summary report for a doctor using nested function\"\"\"
    try:
        # Find doctor
        doctor = None
        for d in doctors:
            if d['id'] == doctor_id:
                doctor = d
                break
        
        if not doctor:
            raise DoctorNotFoundError(f"Doctor {doctor_id} not found in system")
        
        # Nested function to count appointments by clinic
        def clinic_counter():
            clinic_counts = {}
            for apt in appointments:
                if apt['doctor_id'] == doctor_id:
                    clinic = apt['clinic']
                    clinic_counts[clinic] = clinic_counts.get(clinic, 0) + 1
            return clinic_counts
        
        # Use nested function
        clinic_appointments = clinic_counter()
        
        # Build summary
        summary = {
            'doctor_id': doctor_id,
            'doctor_name': doctor['name'],
            'specialty': doctor['specialty'],
            'available_clinics': doctor['clinics'],
            'appointment_counts': clinic_appointments,
            'total_appointments': sum(clinic_appointments.values())
        }
        
        logging.info(f"Generated summary for {doctor['name']}: "
                    f"{summary['total_appointments']} appointments")
        
        return summary
        
    except DoctorNotFoundError as e:
        logging.error(f"Doctor summary error: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error generating doctor summary: {e}")
        raise
```

#### List Comprehensions for Filtering
```python
def generate_clinic_report(clinic_name):
    \"\"\"Generate report for a specific clinic\"\"\"
    try:
        # Filter appointments for the clinic
        clinic_appointments = [apt for apt in appointments 
                              if apt['clinic'] == clinic_name]
        
        # Count appointments by doctor
        doctor_counts = {}
        for apt in clinic_appointments:
            doctor_id = apt['doctor_id']
            doctor_counts[doctor_id] = doctor_counts.get(doctor_id, 0) + 1
        
        report = {
            'clinic': clinic_name,
            'total_appointments': len(clinic_appointments),
            'appointments_by_doctor': doctor_counts,
            'appointments': clinic_appointments
        }
        
        logging.info(f"Generated clinic report for {clinic_name}: "
                    f"{len(clinic_appointments)} appointments")
        
        return report
        
    except Exception as e:
        logging.error(f"Error generating clinic report: {e}")
        raise
```

#### Module Organization Pattern
```python
# File: appointment_utils.py
\"\"\"
Module for appointment booking and management.
Demonstrates proper module organization with:
- Global variables
- Custom exceptions
- Decorated functions
- Comprehensive error handling
\"\"\"

import csv
import logging
from functools import wraps

# Module-level data
appointments = []
patients = []
doctors = []

# Custom exceptions
class ClinicMismatchError(Exception):
    pass

class DoubleBookingError(Exception):
    pass

# Decorator for validation
def validate_input(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Validation logic
        return func(*args, **kwargs)
    return wrapper

# Public functions
@validate_input
def book_appointment(patient_id, doctor_id, date, time, clinic):
    \"\"\"Book a new appointment with validation and logging\"\"\"
    pass

@validate_input
def cancel_appointment(patient_id, date, time):
    \"\"\"Cancel an existing appointment\"\"\"
    pass

def save_appointments(filename):
    \"\"\"Save appointments to CSV file\"\"\"
    pass
```

```python
# File: main.py
\"\"\"
Main application file demonstrating module imports and usage
\"\"\"

import logging
from appointment_utils import (
    book_appointment, 
    cancel_appointment, 
    save_appointments,
    appointments,
    patients,
    doctors
)
from report_utils import generate_doctor_summary

# Initialize data
patients = [
    {"id": 101, "name": "Alice", "age": 29, "clinic": "North"},
    {"id": 102, "name": "Bob", "age": 42, "clinic": "West"},
]

doctors = [
    {"id": "D001", "name": "Dr. Smith", "specialty": "Cardiology", 
     "clinics": ["North", "East"]},
]

# Use imported functions
try:
    book_appointment(101, "D001", "2025-08-20", "10:00", "North")
    summary = generate_doctor_summary("D001")
    save_appointments("appointments.csv")
except Exception as e:
    logging.error(f"Error: {e}")
```

---

### Lecture 5: Abstract Base Classes & Polymorphism

#### Abstract Base Class Pattern
```python
from abc import ABC, abstractmethod
from typing import List
import re

# Define abstract interface
class RiskModel(ABC):
    \"\"\"Abstract interface for all risk models.\"\"\"
    
    @abstractmethod
    def predict_proba(self, text: str) -> float:
        \"\"\"Return a risk score in [0, 1].\"\"\"
        raise NotImplementedError
```

#### Concrete Implementations (Polymorphism)
```python
class KeywordModel(RiskModel):
    \"\"\"Simple keyword hit counter for risk detection.\"\"\"
    
    def __init__(self, keywords: List[str]):
        self.keywords = {k.lower() for k in keywords}
    
    def predict_proba(self, text: str) -> float:
        \"\"\"Count keyword hits and return risk score.\"\"\"
        tokens = re.findall(r"[A-Za-z']+", text.lower())
        hits = sum(1 for t in tokens if t in self.keywords)
        # 0 hits -> 0.0, 1 hit -> 0.5, 2+ hits -> 1.0 (capped)
        return min(1.0, 0.5 * hits)


class LengthModel(RiskModel):
    \"\"\"Very long text may be spammy/promotional.\"\"\"
    
    def __init__(self, max_len: int = 120):
        self.max_len = max_len
    
    def predict_proba(self, text: str) -> float:
        \"\"\"Linear ramp: 0 at length 0 → 1.0 at or above max_len.\"\"\"
        return max(0.0, min(1.0, len(text) / float(self.max_len)))


class VowelRatioModel(RiskModel):
    \"\"\"Assume: more vowels -> friendlier tone -> lower risk.\"\"\"
    
    def predict_proba(self, text: str) -> float:
        if not text:
            return 0.5  # Neutral for empty text
        
        total = len(text)
        vowels = sum(ch.lower() in "aeiou" for ch in text)
        ratio = vowels / total
        
        # Map vowel ratio to lower risk (heuristic)
        return max(0.0, min(1.0, 1.0 - ratio * 2))
```

#### Polymorphic Pipeline
```python
def classify(text: str, models: List[RiskModel], threshold: float = 0.5):
    \"\"\"
    Average risk scores from ANY models provided (polymorphism in action).
    
    Args:
        text: Input text to classify
        models: List of RiskModel instances
        threshold: Classification threshold
    
    Returns:
        Tuple of (label, average_score, breakdown_list)
    \"\"\"
    # Polymorphism: Each model responds to predict_proba() uniformly
    scores = [(m.__class__.__name__, m.predict_proba(text)) for m in models]
    
    avg = sum(s for _, s in scores) / len(scores) if scores else 0.0
    label = "FLAG" if avg >= threshold else "OK"
    
    return label, avg, scores


# Usage example
texts = [
    "Have a wonderful day!",
    "You are stupid and awful.",
    "LIMITED OFFER!!! Buy now now now!",
]

# Create polymorphic model instances
models = [
    KeywordModel(["stupid", "awful", "idiot"]),
    LengthModel(max_len=100),
    VowelRatioModel(),
]

# Process all texts with all models
for text in texts:
    label, avg, breakdown = classify(text, models, threshold=0.5)
    
    # Format breakdown
    breakdown_str = ", ".join(f"{name}={score:.2f}" for name, score in breakdown)
    print(f"[{label}] avg={avg:.2f} :: {text}")
    print(f"    -> {breakdown_str}")
```

#### Key Benefits of Abstraction & Polymorphism
```python
\"\"\"
Why Abstraction & Polymorphism?

1. **Extensibility**: Add new models without modifying classify()
   - Just create a new class inheriting from RiskModel
   - Implement predict_proba()
   - Add to models list

2. **Decoupling**: classify() doesn't need to know model details
   - No isinstance() checks
   - No if/elif chains
   - Works with ANY RiskModel

3. **Testability**: Easy to test each model independently
   - Mock models for unit testing
   - Test classify() with dummy models

4. **Maintainability**: Changes to one model don't affect others
   - Each model is self-contained
   - Clear separation of concerns
\"\"\"

# Adding a new model is trivial:
class CapitalizationModel(RiskModel):
    \"\"\"Excessive caps -> aggressive tone -> higher risk.\"\"\"
    
    def predict_proba(self, text: str) -> float:
        if not text:
            return 0.0
        caps_count = sum(1 for ch in text if ch.isupper())
        ratio = caps_count / len(text)
        return min(1.0, ratio * 2)

# Use immediately without changing existing code
models.append(CapitalizationModel())
```

---

### Lecture 6: Advanced OOP - Healthcare Package System

#### Package Structure
```
healthcare/
├── __init__.py
├── demo.py
├── models/
│   ├── __init__.py
│   ├── patient.py
│   └── devices/
│       ├── __init__.py
│       ├── base_device.py
│       ├── heart_rate.py
│       ├── blood_pressure.py
│       └── glucose.py
├── ops/
│   ├── __init__.py
│   ├── hospital_system.py
│   ├── colombo_branch.py
│   └── kandy_branch.py
└── utils/
    ├── __init__.py
    ├── logger.py
    └── errors.py
```

#### Encapsulation with Private Attributes
```python
from typing import Dict, List

class Patient:
    \"\"\"Patient with encapsulated medical history.\"\"\"
    
    def __init__(self, name: str, age: int, contact_details: Dict):
        # Input validation
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Name must be a non-empty string")
        if not isinstance(age, int) or age <= 0:
            raise ValueError("Age must be a positive integer")
        if not isinstance(contact_details, dict):
            raise ValueError("Contact details must be a dictionary")
        
        # Public attributes
        self.name = name
        self.age = age
        self.contact_details = contact_details.copy()  # Defensive copy
        
        # Private attribute (name mangling with _)
        self._medical_history: List[str] = []
    
    def add_medical_record(self, record: str) -> None:
        \"\"\"Add medical record with validation.\"\"\"
        if not isinstance(record, str) or not record.strip():
            raise ValueError("Medical record must be a non-empty string")
        
        self._medical_history.append(record.strip())
        logger.info(f"Medical record added for patient {self.name}")
    
    def get_medical_history(self) -> List[str]:
        \"\"\"Return COPY of medical history (encapsulation).\"\"\"
        return self._medical_history.copy()  # Prevent external modification
    
    def get_summary(self) -> Dict:
        \"\"\"Return patient summary.\"\"\"
        last_condition = self._medical_history[-1] if self._medical_history else None
        return {
            "name": self.name,
            "age": self.age,
            "last_condition": last_condition
        }
    
    def update_contact(self, details: Dict) -> None:
        \"\"\"Update contact details with defensive copy.\"\"\"
        if not isinstance(details, dict):
            raise ValueError("Contact details must be a dictionary")
        
        self.contact_details = details.copy()  # Defensive copy
        logger.info(f"Contact details updated for patient {self.name}")


# Usage demonstrating encapsulation
patient = Patient("Alice", 45, {"phone": "123-456-7890"})
patient.add_medical_record("Hypertension diagnosed")
patient.add_medical_record("Started on ACE inhibitors")

# Get copy of medical history
history_copy = patient.get_medical_history()
original_length = len(history_copy)

# Modifying copy doesn't affect original (encapsulation working!)
history_copy.append("This should not affect the original!")

actual_history = patient.get_medical_history()
print(f"Original protected: {len(actual_history) == original_length}")  # True
```

#### Abstract Base Class for Devices
```python
from abc import ABC, abstractmethod
from typing import Dict

class BaseDevice(ABC):
    \"\"\"Abstract base class for all medical devices.\"\"\"
    
    def __init__(self, device_id: str):
        self.device_id = device_id
        self.status = "offline"
    
    def connect(self) -> None:
        \"\"\"Connect the device.\"\"\"
        if self.status == "online":
            raise AlreadyOnlineError(f"Device {self.device_id} is already online")
        
        self._set_status("online")
        logger.info(f"Device {self.device_id} connected")
    
    def disconnect(self) -> None:
        \"\"\"Disconnect the device.\"\"\"
        if self.status == "offline":
            raise AlreadyOfflineError(f"Device {self.device_id} is already offline")
        
        self._set_status("offline")
        logger.info(f"Device {self.device_id} disconnected")
    
    def is_online(self) -> bool:
        \"\"\"Check if device is online.\"\"\"
        return self.status == "online"
    
    def _set_status(self, new_status: str) -> None:
        \"\"\"Protected method to set status.\"\"\"
        self.status = new_status
    
    @abstractmethod
    def raise_alert(self, measurement: Dict) -> str:
        \"\"\"Abstract method: each device implements its own alert logic.\"\"\"
        pass
```

#### Concrete Device Implementations
```python
class HeartRateMonitor(BaseDevice):
    \"\"\"Monitor heart rate with specific thresholds.\"\"\"
    
    def measure_heart_rate(self) -> Dict:
        \"\"\"Simulate heart rate measurement.\"\"\"
        import random
        bpm = random.randint(60, 100)
        return {"bpm": bpm, "timestamp": time.time()}
    
    def raise_alert(self, measurement: Dict) -> str:
        \"\"\"Check if heart rate is abnormal.\"\"\"
        bpm = measurement.get("bpm", 0)
        
        if bpm < 60:
            return f"ALERT: Low heart rate ({bpm} bpm)"
        elif bpm > 100:
            return f"ALERT: High heart rate ({bpm} bpm)"
        else:
            return "Normal heart rate"


class BloodPressureMonitor(BaseDevice):
    \"\"\"Monitor blood pressure.\"\"\"
    
    def measure_blood_pressure(self) -> Dict:
        \"\"\"Simulate blood pressure measurement.\"\"\"
        import random
        return {
            "systolic": random.randint(90, 140),
            "diastolic": random.randint(60, 90),
            "timestamp": time.time()
        }
    
    def raise_alert(self, measurement: Dict) -> str:
        \"\"\"Check if blood pressure is abnormal.\"\"\"
        sys = measurement.get("systolic", 0)
        dia = measurement.get("diastolic", 0)
        
        if sys > 140 or dia > 90:
            return f"ALERT: High blood pressure ({sys}/{dia})"
        elif sys < 90 or dia < 60:
            return f"ALERT: Low blood pressure ({sys}/{dia})"
        else:
            return "Normal blood pressure"


class GlucoseMonitor(BaseDevice):
    \"\"\"Monitor blood glucose levels.\"\"\"
    
    def measure_glucose(self) -> Dict:
        \"\"\"Simulate glucose measurement.\"\"\"
        import random
        return {"mg_dL": random.randint(70, 180), "timestamp": time.time()}
    
    def raise_alert(self, measurement: Dict) -> str:
        \"\"\"Check if glucose level is abnormal.\"\"\"
        glucose = measurement.get("mg_dL", 0)
        
        if glucose < 70:
            return f"ALERT: Low glucose ({glucose} mg/dL)"
        elif glucose > 140:
            return f"ALERT: High glucose ({glucose} mg/dL)"
        else:
            return "Normal glucose level"
```

#### Polymorphic Device Usage
```python
# Create different device types
devices = [
    HeartRateMonitor("HRM-001"),
    BloodPressureMonitor("BPM-002"),
    GlucoseMonitor("GLU-003")
]

# Polymorphism: Same interface for all devices
for device in devices:
    print(f"\\nTesting {device.device_id}:")
    
    # Common interface methods
    device.connect()
    print(f"  Status: {device.status}")
    
    # Device-specific measurements
    if isinstance(device, HeartRateMonitor):
        measurement = device.measure_heart_rate()
        print(f"  Heart rate: {measurement['bpm']} bpm")
    elif isinstance(device, BloodPressureMonitor):
        measurement = device.measure_blood_pressure()
        print(f"  BP: {measurement['systolic']}/{measurement['diastolic']}")
    elif isinstance(device, GlucoseMonitor):
        measurement = device.measure_glucose()
        print(f"  Glucose: {measurement['mg_dL']} mg/dL")
    
    # Polymorphic alert method
    alert = device.raise_alert(measurement)
    print(f"  {alert}")
    
    device.disconnect()
```

#### Abstract Hospital System
```python
class HospitalSystem(ABC):
    \"\"\"Abstract base class for hospital branch systems.\"\"\"
    
    @abstractmethod
    def admit_patient(self, patient: Patient) -> str:
        \"\"\"Admit a patient and return patient ID.\"\"\"
        pass
    
    @abstractmethod
    def discharge_patient(self, patient_id: str) -> None:
        \"\"\"Discharge a patient.\"\"\"
        pass
    
    @abstractmethod
    def generate_report(self) -> Dict:
        \"\"\"Generate hospital status report.\"\"\"
        pass


class ColomboHospitalBranch(HospitalSystem):
    \"\"\"Colombo branch implementation.\"\"\"
    
    def __init__(self):
        self.patients = {}
        self.devices = []
        self.alert_count = 0
    
    def admit_patient(self, patient: Patient) -> str:
        \"\"\"Admit patient with unique ID.\"\"\"
        patient_id = f"CMB-{len(self.patients) + 1:03d}"
        self.patients[patient_id] = patient
        logger.info(f"Patient {patient.name} admitted with ID {patient_id}")
        return patient_id
    
    def discharge_patient(self, patient_id: str) -> None:
        \"\"\"Discharge patient by ID.\"\"\"
        if patient_id in self.patients:
            patient = self.patients.pop(patient_id)
            logger.info(f"Patient {patient.name} discharged")
        else:
            raise ValueError(f"Patient {patient_id} not found")
    
    def register_device(self, device: BaseDevice) -> None:
        \"\"\"Register a medical device.\"\"\"
        self.devices.append(device)
        logger.info(f"Device {device.device_id} registered")
    
    def increment_alerts(self) -> None:
        \"\"\"Increment alert counter.\"\"\"
        self.alert_count += 1
    
    def generate_report(self) -> Dict:
        \"\"\"Generate branch report.\"\"\"
        return {
            "branch": "Colombo",
            "patients_count": len(self.patients),
            "devices_count": len(self.devices),
            "alert_count": self.alert_count
        }
```

#### Custom Error Classes
```python
# File: utils/errors.py
class AlreadyOnlineError(Exception):
    \"\"\"Raised when trying to connect an already online device.\"\"\"
    pass

class AlreadyOfflineError(Exception):
    \"\"\"Raised when trying to disconnect an already offline device.\"\"\"
    pass

# Usage in BaseDevice
def connect(self) -> None:
    if self.status == "online":
        raise AlreadyOnlineError(f"Device {self.device_id} is already online")
    self._set_status("online")
```

#### Complete Integration Example
```python
# File: demo.py
from models.patient import Patient
from models.devices.heart_rate import HeartRateMonitor
from models.devices.blood_pressure import BloodPressureMonitor
from models.devices.glucose import GlucoseMonitor
from ops.colombo_branch import ColomboHospitalBranch
from ops.kandy_branch import KandyHospitalBranch

def main():
    # Create patients
    patient1 = Patient("Alice", 45, {"phone": "123-456-7890"})
    patient1.add_medical_record("Hypertension diagnosed")
    patient1.add_medical_record("Started on ACE inhibitors")
    
    patient2 = Patient("Bob", 62, {"phone": "987-654-3210"})
    patient2.add_medical_record("Type 2 diabetes")
    
    # Create devices
    devices = [
        HeartRateMonitor("HRM-001"),
        BloodPressureMonitor("BPM-002"),
        GlucoseMonitor("GLU-003")
    ]
    
    # Create hospital branches
    colombo = ColomboHospitalBranch()
    kandy = KandyHospitalBranch()
    
    # Register devices at both branches
    for device in devices:
        colombo.register_device(device)
        kandy.register_device(device.device_id)
    
    # Admit patients
    p1_cmb = colombo.admit_patient(patient1)
    p2_cmb = colombo.admit_patient(patient2)
    p1_knd = kandy.admit_patient(patient1)
    
    # Generate reports
    print(colombo.generate_report())
    print(kandy.generate_report())

if __name__ == "__main__":
    main()
```

---

### Lecture 7: Smart City Data Analysis with Pandas & Visualization

#### Data Loading and Initial Exploration
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# Set visualization style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

# Load sensor data
sensors_df = pd.read_csv('smart_city_sensors.csv')
incidents_df = pd.read_csv('incident_reports.csv')

# Initial exploration
print(sensors_df.head())
print(sensors_df.info())
print(sensors_df.describe())

# Check data types
print(sensors_df.dtypes)

# Dataset structure
print(f"Sensors shape: {sensors_df.shape}")
print(f"Incidents shape: {incidents_df.shape}")
```

#### Data Cleaning and Preprocessing
```python
# Convert timestamp to datetime
sensors_df['timestamp'] = pd.to_datetime(sensors_df['timestamp'])
incidents_df['timestamp'] = pd.to_datetime(incidents_df['timestamp'])

# Set timestamp as index for time series analysis
sensors_df.set_index('timestamp', inplace=True)
incidents_df.set_index('timestamp', inplace=True)

# Check for missing values
print("Missing values in sensors:")
print(sensors_df.isnull().sum())

print("\\nMissing value percentages:")
missing_pct = (sensors_df.isnull().sum() / len(sensors_df)) * 100
print(missing_pct)

# Handle missing values - multiple strategies
# Strategy 1: Drop rows with any missing values
sensors_clean = sensors_df.dropna()

# Strategy 2: Fill with mean (for numeric columns)
sensors_df['pm25'].fillna(sensors_df['pm25'].mean(), inplace=True)
sensors_df['noise_level'].fillna(sensors_df['noise_level'].mean(), inplace=True)

# Strategy 3: Forward fill (for time series)
sensors_df['traffic_flow'].fillna(method='ffill', inplace=True)

# Strategy 4: Fill with median (robust to outliers)
sensors_df['pm25'].fillna(sensors_df['pm25'].median(), inplace=True)

# Drop duplicates
sensors_df.drop_duplicates(inplace=True)
incidents_df.drop_duplicates(inplace=True)
```

#### Grouping and Aggregation
```python
# Group by district and calculate statistics
district_stats = sensors_df.groupby('district').agg({
    'traffic_flow': ['mean', 'min', 'max', 'std'],
    'pm25': ['mean', 'median'],
    'noise_level': ['mean', 'max']
})

print("District-wise statistics:")
print(district_stats)

# Multiple grouping levels
hourly_district = sensors_df.groupby([
    sensors_df.index.hour,
    'district'
])['traffic_flow'].mean()

print("\\nTraffic flow by hour and district:")
print(hourly_district)

# Custom aggregation functions
def pollution_category(pm25_series):
    avg = pm25_series.mean()
    if avg < 50:
        return 'Good'
    elif avg < 100:
        return 'Moderate'
    else:
        return 'Unhealthy'

pollution_status = sensors_df.groupby('district')['pm25'].apply(pollution_category)
print("\\nPollution status by district:")
print(pollution_status)
```

#### Time Series Analysis
```python
# Resample to daily data
daily_sensors = sensors_df.resample('D').agg({
    'traffic_flow': 'mean',
    'pm25': 'mean',
    'noise_level': 'mean'
})

# Calculate rolling averages
sensors_df['pm25_rolling_7d'] = sensors_df['pm25'].rolling(window=7*24).mean()
sensors_df['traffic_rolling_24h'] = sensors_df['traffic_flow'].rolling(window=24).mean()

# Calculate hourly patterns
hourly_pattern = sensors_df.groupby(sensors_df.index.hour).agg({
    'traffic_flow': 'mean',
    'pm25': 'mean',
    'noise_level': 'mean'
})

print("Hourly traffic pattern:")
print(hourly_pattern)

# Day of week analysis
sensors_df['day_of_week'] = sensors_df.index.dayofweek
sensors_df['is_weekend'] = sensors_df['day_of_week'].isin([5, 6])

weekend_vs_weekday = sensors_df.groupby('is_weekend').agg({
    'traffic_flow': 'mean',
    'pm25': 'mean',
    'noise_level': 'mean'
})

print("\\nWeekend vs Weekday comparison:")
print(weekend_vs_weekday)
```

#### Merging and Joining Datasets
```python
# Merge sensor data with incident reports
# Method 1: Merge on timestamp and district
merged_df = pd.merge(
    sensors_df.reset_index(),
    incidents_df.reset_index(),
    on=['timestamp', 'district'],
    how='left'  # Keep all sensor records
)

# Method 2: Merge with time tolerance (within 1 hour)
merged_tolerance = pd.merge_asof(
    sensors_df.reset_index().sort_values('timestamp'),
    incidents_df.reset_index().sort_values('timestamp'),
    on='timestamp',
    by='district',
    tolerance=pd.Timedelta('1 hour'),
    direction='nearest'
)

# Analyze correlation between sensors and incidents
incident_hours = incidents_df.groupby([
    incidents_df.index.floor('H'),
    'district'
]).size().reset_index(name='incident_count')

sensors_with_incidents = pd.merge(
    sensors_df.reset_index(),
    incident_hours,
    left_on=['timestamp', 'district'],
    right_on=['timestamp', 'district'],
    how='left'
)

# Fill missing incident counts with 0
sensors_with_incidents['incident_count'].fillna(0, inplace=True)
```

#### Data Visualization with Matplotlib
```python
# Line plot - Traffic flow over time
plt.figure(figsize=(12, 6))
for district in sensors_df['district'].unique():
    district_data = sensors_df[sensors_df['district'] == district]
    plt.plot(district_data.index, district_data['traffic_flow'], 
             label=district, alpha=0.7)

plt.title('Traffic Flow Over Time by District')
plt.xlabel('Date')
plt.ylabel('Traffic Flow (vehicles/hour)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# Bar plot - Average pollution by district
plt.figure(figsize=(10, 6))
avg_pollution = sensors_df.groupby('district')['pm25'].mean()
avg_pollution.plot(kind='bar', color='skyblue', edgecolor='navy')
plt.title('Average PM2.5 Levels by District')
plt.xlabel('District')
plt.ylabel('PM2.5 (μg/m³)')
plt.xticks(rotation=45)
plt.axhline(y=50, color='orange', linestyle='--', label='Moderate threshold')
plt.axhline(y=100, color='red', linestyle='--', label='Unhealthy threshold')
plt.legend()
plt.tight_layout()
plt.show()

# Histogram - Distribution of noise levels
plt.figure(figsize=(10, 6))
plt.hist(sensors_df['noise_level'].dropna(), bins=30, 
         color='green', alpha=0.7, edgecolor='black')
plt.title('Distribution of Noise Levels')
plt.xlabel('Noise Level (dB)')
plt.ylabel('Frequency')
plt.axvline(x=70, color='red', linestyle='--', label='Safe limit')
plt.legend()
plt.tight_layout()
plt.show()

# Scatter plot - Correlation between traffic and pollution
plt.figure(figsize=(10, 6))
plt.scatter(sensors_df['traffic_flow'], sensors_df['pm25'], 
           alpha=0.5, c=sensors_df.index.hour, cmap='viridis')
plt.colorbar(label='Hour of Day')
plt.title('Traffic Flow vs PM2.5 Pollution')
plt.xlabel('Traffic Flow (vehicles/hour)')
plt.ylabel('PM2.5 (μg/m³)')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# Subplot grid - Multiple metrics
fig, axes = plt.subplots(2, 2, figsize=(15, 10))

# Traffic flow
axes[0, 0].plot(daily_sensors.index, daily_sensors['traffic_flow'])
axes[0, 0].set_title('Daily Average Traffic Flow')
axes[0, 0].set_ylabel('Vehicles/hour')

# PM2.5
axes[0, 1].plot(daily_sensors.index, daily_sensors['pm25'], color='orange')
axes[0, 1].set_title('Daily Average PM2.5')
axes[0, 1].set_ylabel('μg/m³')

# Noise level
axes[1, 0].plot(daily_sensors.index, daily_sensors['noise_level'], color='green')
axes[1, 0].set_title('Daily Average Noise Level')
axes[1, 0].set_ylabel('dB')

# Incidents by type
incident_counts = incidents_df.groupby('incident_type').size()
axes[1, 1].pie(incident_counts.values, labels=incident_counts.index, autopct='%1.1f%%')
axes[1, 1].set_title('Incidents by Type')

plt.tight_layout()
plt.show()
```

#### Advanced Visualization with Seaborn
```python
# Heatmap - Correlation matrix
plt.figure(figsize=(10, 8))
correlation_matrix = sensors_df[['traffic_flow', 'pm25', 'noise_level']].corr()
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', 
            center=0, square=True, linewidths=1)
plt.title('Correlation Matrix: Sensor Measurements')
plt.tight_layout()
plt.show()

# Box plot - Distribution by district
plt.figure(figsize=(12, 6))
sns.boxplot(data=sensors_df, x='district', y='pm25', palette='Set2')
plt.title('PM2.5 Distribution by District')
plt.ylabel('PM2.5 (μg/m³)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Violin plot - Noise levels by district
plt.figure(figsize=(12, 6))
sns.violinplot(data=sensors_df, x='district', y='noise_level', 
               palette='muted', inner='quartile')
plt.title('Noise Level Distribution by District')
plt.ylabel('Noise Level (dB)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Pair plot - Relationships between variables
sample_data = sensors_df.sample(n=1000)  # Sample for performance
sns.pairplot(sample_data[['traffic_flow', 'pm25', 'noise_level']], 
             diag_kind='kde', plot_kws={'alpha': 0.6})
plt.suptitle('Pairwise Relationships', y=1.02)
plt.tight_layout()
plt.show()

# Heatmap - Hourly patterns
hourly_pivot = sensors_df.pivot_table(
    values='traffic_flow',
    index=sensors_df.index.hour,
    columns='district',
    aggfunc='mean'
)

plt.figure(figsize=(10, 8))
sns.heatmap(hourly_pivot, cmap='YlOrRd', annot=False, 
            cbar_kws={'label': 'Vehicles/hour'})
plt.title('Average Traffic Flow by Hour and District')
plt.xlabel('District')
plt.ylabel('Hour of Day')
plt.tight_layout()
plt.show()

# Count plot - Incidents by severity
plt.figure(figsize=(10, 6))
sns.countplot(data=incidents_df, x='severity', hue='incident_type', palette='Set1')
plt.title('Incident Count by Severity and Type')
plt.xlabel('Severity Level')
plt.ylabel('Count')
plt.legend(title='Incident Type', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()
```

#### Advanced Analysis Patterns
```python
# Create pollution alert system
def create_pollution_alert(pm25):
    if pm25 < 50:
        return 'Good'
    elif pm25 < 100:
        return 'Moderate'
    elif pm25 < 150:
        return 'Unhealthy'
    else:
        return 'Hazardous'

sensors_df['pollution_alert'] = sensors_df['pm25'].apply(create_pollution_alert)

# Alert distribution
alert_distribution = sensors_df['pollution_alert'].value_counts()
print("Pollution alert distribution:")
print(alert_distribution)

# Identify peak pollution hours
peak_pollution_hours = sensors_df.groupby(sensors_df.index.hour)['pm25'].mean().nlargest(5)
print("\\nTop 5 peak pollution hours:")
print(peak_pollution_hours)

# Correlation between incidents and sensor readings
incident_impact = sensors_with_incidents.groupby('incident_count').agg({
    'traffic_flow': 'mean',
    'pm25': 'mean',
    'noise_level': 'mean'
})

print("\\nSensor readings by incident count:")
print(incident_impact)

# Find anomalies using IQR method
Q1 = sensors_df['pm25'].quantile(0.25)
Q3 = sensors_df['pm25'].quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

anomalies = sensors_df[
    (sensors_df['pm25'] < lower_bound) | 
    (sensors_df['pm25'] > upper_bound)
]

print(f"\\nFound {len(anomalies)} pollution anomalies")

# Statistical summary by district
summary_report = sensors_df.groupby('district').agg({
    'traffic_flow': ['mean', 'std', 'min', 'max'],
    'pm25': ['mean', 'std', 'min', 'max'],
    'noise_level': ['mean', 'std', 'min', 'max']
}).round(2)

print("\\nComprehensive District Summary:")
print(summary_report)
```

#### Export Results
```python
# Export cleaned data
sensors_df.to_csv('cleaned_sensors.csv')
incidents_df.to_csv('cleaned_incidents.csv')

# Export analysis results
district_stats.to_csv('district_statistics.csv')
hourly_pattern.to_csv('hourly_patterns.csv')

# Export visualizations
plt.figure(figsize=(12, 6))
sensors_df.groupby('district')['pm25'].mean().plot(kind='bar')
plt.title('Average PM2.5 by District')
plt.tight_layout()
plt.savefig('pm25_by_district.png', dpi=300, bbox_inches='tight')
plt.close()

# Create summary report
summary = {
    'total_records': len(sensors_df),
    'districts': sensors_df['district'].unique().tolist(),
    'date_range': f"{sensors_df.index.min()} to {sensors_df.index.max()}",
    'avg_pollution': sensors_df['pm25'].mean(),
    'avg_traffic': sensors_df['traffic_flow'].mean(),
    'total_incidents': len(incidents_df)
}

print("\\nData Summary:")
for key, value in summary.items():
    print(f"{key}: {value}")
```

#### Complete Smart City Analysis Example
```python
def analyze_smart_city_data(sensors_file, incidents_file):
    \"\"\"
    Complete analysis pipeline for smart city data.
    
    Args:
        sensors_file: Path to sensor data CSV
        incidents_file: Path to incident reports CSV
    
    Returns:
        Dictionary with analysis results and visualizations
    \"\"\"
    # Load data
    sensors = pd.read_csv(sensors_file)
    incidents = pd.read_csv(incidents_file)
    
    # Preprocess
    sensors['timestamp'] = pd.to_datetime(sensors['timestamp'])
    incidents['timestamp'] = pd.to_datetime(incidents['timestamp'])
    
    # Clean missing values
    sensors.fillna(sensors.mean(numeric_only=True), inplace=True)
    
    # Analyze by district
    district_analysis = sensors.groupby('district').agg({
        'traffic_flow': 'mean',
        'pm25': 'mean',
        'noise_level': 'mean'
    })
    
    # Time series patterns
    sensors.set_index('timestamp', inplace=True)
    hourly_patterns = sensors.groupby(sensors.index.hour).mean(numeric_only=True)
    
    # Incident analysis
    incident_summary = incidents.groupby('incident_type').agg({
        'severity': ['mean', 'count']
    })
    
    # Visualize results
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # Traffic by district
    district_analysis['traffic_flow'].plot(kind='bar', ax=axes[0, 0])
    axes[0, 0].set_title('Average Traffic Flow by District')
    
    # Pollution by district
    district_analysis['pm25'].plot(kind='bar', ax=axes[0, 1], color='orange')
    axes[0, 1].set_title('Average PM2.5 by District')
    
    # Hourly traffic pattern
    hourly_patterns['traffic_flow'].plot(ax=axes[1, 0])
    axes[1, 0].set_title('Hourly Traffic Pattern')
    
    # Incident types
    incident_summary['severity']['count'].plot(kind='pie', ax=axes[1, 1], autopct='%1.1f%%')
    axes[1, 1].set_title('Incidents by Type')
    
    plt.tight_layout()
    plt.savefig('smart_city_analysis.png', dpi=300)
    
    return {
        'district_stats': district_analysis,
        'hourly_patterns': hourly_patterns,
        'incident_summary': incident_summary
    }

# Run complete analysis
results = analyze_smart_city_data('smart_city_sensors.csv', 'incident_reports.csv')
print("Analysis complete! Results saved to smart_city_analysis.png")
```

---

### Lecture 8: Comprehensions & Generators for IoT Data

#### Functional Programming with map, filter, zip
```python
from typing import Generator, List, Dict
import csv

# Extract data using list comprehensions
soil_moisture_values = [record['soil_moisture'] for record in data]
temperature_values = [record['temperature'] for record in data]
ph_values = [record['ph'] for record in data]

# 1. map() - Transform data
max_moisture = max(soil_moisture_values)
min_moisture = min(soil_moisture_values)

normalized_moisture = list(map(
    lambda x: (x - min_moisture) / (max_moisture - min_moisture) 
              if max_moisture != min_moisture else 0,
    soil_moisture_values
))

print(f"Normalized moisture: {[round(x, 3) for x in normalized_moisture]}")

# 2. filter() - Keep only high temperature records
high_temp_records = list(filter(
    lambda record: record['temperature'] > 35, 
    data
))

print(f"High temp records: {len(high_temp_records)}")

# 3. zip() - Combine multiple sequences
moisture_ph_pairs = list(zip(soil_moisture_values, ph_values))
print(f"Moisture & pH pairs: {moisture_ph_pairs[:3]}")  # First 3 pairs
```

#### Advanced Comprehensions for IoT
```python
# List comprehension: Extract drought risk sensors
drought_risk_sensors = [
    (record['sensor_id'], record['location']) 
    for record in data 
    if record['soil_moisture'] < 30
]

# Dictionary comprehension: Calculate averages by location
location_avg_temp = {
    location: sum(r['temperature'] for r in data if r['location'] == location) /
              len([r for r in data if r['location'] == location])
    for location in set(record['location'] for record in data)
}

print("Average temperature by location:")
for location, avg_temp in location_avg_temp.items():
    print(f"  {location}: {avg_temp:.1f}°C")

# Set comprehension: Find locations with abnormal pH
abnormal_ph_locations = {
    record['location'] 
    for record in data 
    if record['ph'] < 5.5 or record['ph'] > 7.5
}

print(f"Locations with abnormal pH: {abnormal_ph_locations}")

# Nested comprehension: Field-wise analysis
field_analysis = {
    location: {
        'sensor_count': len([r for r in data if r['location'] == location]),
        'avg_moisture': sum(r['soil_moisture'] for r in data if r['location'] == location) / 
                       len([r for r in data if r['location'] == location]),
        'alert_sensors': [r['sensor_id'] for r in data if r['location'] == location and
                         r['soil_moisture'] < 30]
    }
    for location in set(record['location'] for record in data)
}
```

#### Generator Functions for Streaming IoT Data
```python
def read_csv_generator(file_path='sensors_data.csv') -> Generator[Dict, None, None]:
    \"\"\"Generator function to read CSV data with proper type conversion.\"\"\"
    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            row['soil_moisture'] = int(row['soil_moisture'])
            row['temperature'] = int(row['temperature'])
            row['ph'] = float(row['ph'])
            row['timestamp'] = int(row['timestamp'])
            yield row

# Use generator (memory efficient)
data_stream = read_csv_generator()
for i, record in enumerate(data_stream):
    if i < 3:  # Process first 3 records
        print(f"Record {i+1}: {record['sensor_id']} - {record['soil_moisture']}%")
    if i >= 2:
        break

# Generator for real-time streaming simulation
def sensor_data_stream(csv_file: str = 'sensors_data.csv') -> Generator[Dict, None, None]:
    \"\"\"Simulate real-time IoT streaming with delay.\"\"\"
    import time
    for record in read_csv_generator(csv_file):
        time.sleep(0.01)  # Simulate 10ms delay
        yield record

# Generator expression for irrigation decisions
irrigation_data = (
    (record['sensor_id'], record['soil_moisture']) 
    for record in data
)

for sensor_id, moisture in irrigation_data:
    print(f"{sensor_id}: {moisture}% moisture")
```

#### Memory Efficiency: List vs Generator
```python
import sys

# Simulate larger dataset
temps = temperature_values * 1000

# List comprehension (eager - loads all into memory)
temp_squares_list = [temp**2 for temp in temps]
list_size = sys.getsizeof(temp_squares_list)

# Generator expression (lazy - generates on demand)
temp_squares_gen = (temp**2 for temp in temps)
gen_size = sys.getsizeof(temp_squares_gen)

print(f"Memory usage comparison:")
print(f"  List comprehension: {list_size:,} bytes")
print(f"  Generator expression: {gen_size:,} bytes")
print(f"  Memory saved: {list_size - gen_size:,} bytes")
print(f"  Savings: {((list_size - gen_size) / list_size * 100):.1f}%")

# When to use what:
\"\"\"
Use LIST COMPREHENSION when:
- Dataset fits in memory
- Need to access data multiple times
- Need immediate results
- Random access required

Use GENERATOR when:
- Large datasets or streaming data
- Memory-constrained environments
- One-pass processing
- Real-time data pipelines
\"\"\"
```

#### Generator Pipeline for Alert System
```python
THRESHOLDS = {
    'soil_moisture': (20, 80),    # Normal range
    'temperature': (10, 35),
    'ph': (5.5, 7.5)
}

def alert_pipeline(csv_file: str = 'sensors_data.csv', 
                   batch_size: int = 100) -> Generator[List[Dict], None, None]:
    \"\"\"Generator pipeline: stream → filter → batch alerts.\"\"\"
    
    def is_abnormal(record: Dict) -> bool:
        \"\"\"Check if any sensor reading is abnormal.\"\"\"
        return not (
            THRESHOLDS['soil_moisture'][0] <= record['soil_moisture'] <= THRESHOLDS['soil_moisture'][1] and
            THRESHOLDS['temperature'][0] <= record['temperature'] <= THRESHOLDS['temperature'][1] and
            THRESHOLDS['ph'][0] <= record['ph'] <= THRESHOLDS['ph'][1]
        )
    
    alert_batch = []
    
    for record in read_csv_generator(csv_file):
        if is_abnormal(record):
            alert_batch.append({
                'sensor_id': record['sensor_id'],
                'location': record['location'],
                'issue': get_issue_description(record),
                'timestamp': record['timestamp']
            })
            
            if len(alert_batch) >= batch_size:
                yield alert_batch
                alert_batch = []
    
    # Yield remaining alerts
    if alert_batch:
        yield alert_batch


def get_issue_description(record: Dict) -> str:
    \"\"\"Generate human-readable issue description.\"\"\"
    issues = []
    
    if record['soil_moisture'] < THRESHOLDS['soil_moisture'][0]:
        issues.append("Low soil moisture")
    elif record['soil_moisture'] > THRESHOLDS['soil_moisture'][1]:
        issues.append("High soil moisture")
    
    if record['temperature'] < THRESHOLDS['temperature'][0]:
        issues.append("Low temperature")
    elif record['temperature'] > THRESHOLDS['temperature'][1]:
        issues.append("High temperature")
    
    if record['ph'] < THRESHOLDS['ph'][0]:
        issues.append("Low pH (acidic)")
    elif record['ph'] > THRESHOLDS['ph'][1]:
        issues.append("High pH (alkaline)")
    
    return "; ".join(issues)


# Use the pipeline
for batch_num, alert_batch in enumerate(alert_pipeline(batch_size=5), 1):
    print(f"Batch {batch_num}: {len(alert_batch)} alerts")
    for alert in alert_batch[:2]:  # Show first 2
        print(f"  {alert['sensor_id']} at {alert['location']}: {alert['issue']}")
    if batch_num >= 3:
        break
```

#### Streaming Statistics Generator
```python
def streaming_stats() -> Generator[str, None, None]:
    \"\"\"Generator for calculating streaming statistics.\"\"\"
    moisture_sum = 0
    temp_sum = 0
    count = 0
    
    for record in read_csv_generator():
        count += 1
        moisture_sum += record['soil_moisture']
        temp_sum += record['temperature']
        
        if count % 10 == 0:  # Report every 10 records
            avg_moisture = moisture_sum / count
            avg_temp = temp_sum / count
            yield f"After {count} records: Avg moisture={avg_moisture:.1f}%, Avg temp={avg_temp:.1f}°C"

# Use streaming stats
stats_gen = streaming_stats()
for i, stat in enumerate(stats_gen):
    print(stat)
    if i >= 5:  # Limit output
        break
```

---

### Lecture 9: Security & Cryptography

#### Data Integrity with Hashing
```python
import hashlib
import json

class DataTamperDetector:
    \"\"\"Detect data tampering using cryptographic hashes.\"\"\"
    
    def __init__(self, data):
        self.data = data
        self.hash = self.hash_256(data)
        self.hash_blake2b_value = self.hash_blake2b(data)
    
    def hash_256(self, data) -> str:
        \"\"\"Create SHA-256 hash of data.\"\"\"
        data_string = json.dumps(data, sort_keys=True).encode()
        return hashlib.sha256(data_string).hexdigest()
    
    def hash_blake2b(self, data) -> str:
        \"\"\"Create BLAKE2b hash of data (faster than SHA-256).\"\"\"
        data_string = json.dumps(data, sort_keys=True).encode()
        return hashlib.blake2b(data_string).hexdigest()
    
    def is_data_tampered(self) -> bool:
        \"\"\"Check if data has been modified.\"\"\"
        current_hash = self.hash_256(self.data)
        current_blake2b = self.hash_blake2b(self.data)
        return (current_hash != self.hash or 
                current_blake2b != self.hash_blake2b_value)
    
    def verify_data(self, data_to_verify) -> bool:
        \"\"\"Verify if provided data matches original.\"\"\"
        data_string = json.dumps(data_to_verify, sort_keys=True).encode()
        hash_to_verify = hashlib.sha256(data_string).hexdigest()
        return hash_to_verify == self.hash

# Usage
payload = "PatientID=102;HR=88;BP=120/80;Temp=37.2"
detector = DataTamperDetector(payload)

print(f"Original data: {detector.data}")
print(f"SHA-256 hash: {detector.hash}")
print(f"BLAKE2b hash: {detector.hash_blake2b_value}")
print(f"Data tampered: {detector.is_data_tampered()}")  # False

# Tamper with data
detector.data = "PatientID=102;HR=99;BP=120/80;Temp=37.2"  # Changed HR
print(f"Data tampered after modification: {detector.is_data_tampered()}")  # True
```

#### Secure Password Management
```python
import hashlib
import secrets

class SecurePasswordManager:
    \"\"\"Manage passwords with salted hashing.\"\"\"
    
    def __init__(self):
        self.users = {}
    
    def generate_salt(self) -> bytes:
        \"\"\"Generate cryptographically secure random salt.\"\"\"
        return secrets.token_bytes(16)
    
    def hash_password(self, password: str, salt: bytes) -> str:
        \"\"\"Hash password using PBKDF2 with salt.\"\"\"
        # PBKDF2: Password-Based Key Derivation Function 2
        # 200,000 iterations for security
        return hashlib.pbkdf2_hmac(
            'sha256',           # Hash algorithm
            password.encode(),  # Password as bytes
            salt,               # Salt
            200000              # Iterations (computational cost)
        ).hex()
    
    def add_user(self, username: str, password: str) -> bool:
        \"\"\"Add user with securely hashed password.\"\"\"
        salt = self.generate_salt()
        password_hash = self.hash_password(password, salt)
        
        self.users[username] = {
            'salt': salt,
            'password_hash': password_hash
        }
        return True
    
    def verify_user(self, username: str, password: str) -> bool:
        \"\"\"Verify user credentials.\"\"\"
        if username not in self.users:
            return False
        
        salt = self.users[username]['salt']
        password_hash = self.hash_password(password, salt)
        
        return password_hash == self.users[username]['password_hash']
    
    def compare_login_methods(self, username: str, password: str):
        \"\"\"Compare insecure vs secure hashing.\"\"\"
        # INSECURE: Plain SHA-256 (no salt, vulnerable to rainbow tables)
        insecure_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # SECURE: PBKDF2 with salt
        secure_salt = self.users[username]['salt']
        secure_hash = self.hash_password(password, secure_salt)
        
        print(f"Insecure SHA-256: {insecure_hash}")
        print(f"Secure PBKDF2:   {secure_hash}")
        print(f"Different: {insecure_hash != secure_hash}")

# Usage
manager = SecurePasswordManager()
manager.add_user("doctor1", "securepassword123")

print(manager.verify_user("doctor1", "securepassword123"))  # True
print(manager.verify_user("doctor1", "wrongpassword"))      # False

manager.compare_login_methods("doctor1", "securepassword123")
```

#### HMAC for Message Authentication
```python
import hmac
import secrets

class DeviceAuthenticator:
    \"\"\"Authenticate IoT devices using HMAC signatures.\"\"\"
    
    def __init__(self):
        self.devices = {}
    
    def register_device(self, device_id: str) -> bytes:
        \"\"\"Register device and generate secret token.\"\"\"
        token = secrets.token_bytes(16)
        self.devices[device_id] = token
        return token
    
    def sign_message(self, device_id: str, message: str) -> str:
        \"\"\"Sign message with device's secret token.\"\"\"
        if device_id not in self.devices:
            raise ValueError("Device not registered")
        
        token = self.devices[device_id]
        message_bytes = message.encode()
        
        # Create HMAC signature
        signature = hmac.new(token, message_bytes, hashlib.sha256).hexdigest()
        return signature
    
    def verify_message(self, device_id: str, message: str, signature: str) -> bool:
        \"\"\"Verify message signature.\"\"\"
        if device_id not in self.devices:
            return False
        
        token = self.devices[device_id]
        message_bytes = message.encode()
        
        # Calculate expected signature
        expected_signature = hmac.new(token, message_bytes, hashlib.sha256).hexdigest()
        
        # Constant-time comparison (prevents timing attacks)
        return hmac.compare_digest(expected_signature, signature)
    
    def rotate_key(self, device_id: str) -> bytes:
        \"\"\"Rotate device secret key.\"\"\"
        if device_id not in self.devices:
            raise ValueError("Device not registered")
        
        new_token = secrets.token_bytes(16)
        self.devices[device_id] = new_token
        return new_token

# Usage
authenticator = DeviceAuthenticator()

# Register device
device_id = "WearX99"
token = authenticator.register_device(device_id)
print(f"Device registered with token: {token.hex()}")

# Sign message
message = "DeviceID=WearX99;Glucose=5.7"
signature = authenticator.sign_message(device_id, message)
print(f"Message signature: {signature}")

# Verify message
is_valid = authenticator.verify_message(device_id, message, signature)
print(f"Message verified: {is_valid}")  # True

# Tampered message fails verification
tampered = "DeviceID=WearX99;Glucose=9.9"
is_valid = authenticator.verify_message(device_id, tampered, signature)
print(f"Tampered message verified: {is_valid}")  # False

# Key rotation
new_token = authenticator.rotate_key(device_id)
print(f"Key rotated. New token: {new_token.hex()}")

# Old signature no longer valid
is_valid = authenticator.verify_message(device_id, message, signature)
print(f"Old signature after rotation: {is_valid}")  # False
```

#### Token Management with Expiration
```python
import datetime
import secrets
import json

class TokenDB:
    \"\"\"Persistent token storage.\"\"\"
    
    def __init__(self, db_file='tokens.json'):
        self.db_file = db_file
        try:
            with open(db_file, 'r') as f:
                self.tokens = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.tokens = {}
            with open(db_file, 'w') as f:
                json.dump(self.tokens, f)
    
    def save(self):
        \"\"\"Save tokens to file.\"\"\"
        with open(self.db_file, 'w') as f:
            json.dump(self.tokens, f)


class TokenManager:
    \"\"\"Manage authentication tokens with expiration.\"\"\"
    
    def __init__(self):
        token_db = TokenDB()
        self.tokens = token_db.tokens
    
    def generate_token(self, user_id: str) -> str:
        \"\"\"Generate secure token for user.\"\"\"
        # Invalidate old token if exists
        old_token = self.tokens.get(user_id)
        if old_token and old_token in self.tokens:
            del self.tokens[old_token]
        
        # Generate new cryptographically secure token
        token = secrets.token_urlsafe(32)
        
        # Set expiration (30 seconds for demo)
        expire = (datetime.datetime.now() + 
                 datetime.timedelta(seconds=30)).isoformat()
        
        self.tokens[user_id] = token
        self.tokens[token] = {
            'user_id': user_id,
            'expire': expire
        }
        
        # Persist to database
        token_db = TokenDB()
        token_db.tokens = self.tokens
        token_db.save()
        
        return token
    
    def validate_token(self, user_id: str, token: str) -> bool:
        \"\"\"Validate token for user.\"\"\"
        if token not in self.tokens:
            return False
        
        token_data = self.tokens[token]
        
        # Check user ID matches
        if token_data['user_id'] != user_id:
            return False
        
        # Check expiration
        if datetime.datetime.now() > datetime.datetime.fromisoformat(token_data['expire']):
            del self.tokens[token]  # Remove expired token
            return False
        
        return True
    
    def create_reset_token(self, user_id: str) -> str:
        \"\"\"Create password reset link.\"\"\"
        token = self.generate_token(user_id)
        return f"https://ehealth.ai/reset/{token}"

# Usage
token_mgr = TokenManager()

# Generate token
user_id = "patient123"
token = token_mgr.generate_token(user_id)
print(f"Generated token: {token}")

# Validate token
is_valid = token_mgr.validate_token(user_id, token)
print(f"Token valid: {is_valid}")  # True

# Wait for expiration
import time
time.sleep(31)
is_valid = token_mgr.validate_token(user_id, token)
print(f"Token valid after expiration: {is_valid}")  # False

# Create reset link
reset_link = token_mgr.create_reset_token(user_id)
print(f"Password reset link: {reset_link}")
```

#### JWT (JSON Web Token) Implementation
```python
import base64
import hmac
import hashlib
import json
import datetime
import secrets

class JwtManager:
    \"\"\"Manage JWT tokens for authentication.\"\"\"
    
    def __init__(self):
        self.secret_key = secrets.token_bytes(32)
    
    def base64url_encode(self, data: bytes) -> bytes:
        \"\"\"Base64 URL-safe encoding.\"\"\"
        return base64.urlsafe_b64encode(data).rstrip(b'=')
    
    def base64url_decode(self, data: bytes) -> bytes:
        \"\"\"Base64 URL-safe decoding.\"\"\"
        padding = b'=' * (-len(data) % 4)
        return base64.urlsafe_b64decode(data + padding)
    
    def create_jwt(self, payload: dict, algorithm: str = 'HS256', 
                   expire_seconds: int = 15) -> str:
        \"\"\"Create JWT token.\"\"\"
        # Header
        header = {"alg": algorithm, "typ": "JWT"}
        header_json = json.dumps(header, separators=(',', ':')).encode()
        
        # Payload with expiration
        payload['exp'] = (datetime.datetime.now() + 
                         datetime.timedelta(seconds=expire_seconds)).isoformat()
        payload_json = json.dumps(payload, separators=(',', ':')).encode()
        
        # Encode header and payload
        header_b64 = self.base64url_encode(header_json)
        payload_b64 = self.base64url_encode(payload_json)
        
        # Create signature
        if algorithm == 'HS256':
            signature = hmac.new(
                self.secret_key, 
                header_b64 + b'.' + payload_b64, 
                hashlib.sha256
            ).digest()
        elif algorithm == 'HS512':
            signature = hmac.new(
                self.secret_key, 
                header_b64 + b'.' + payload_b64, 
                hashlib.sha512
            ).digest()
        else:
            raise ValueError("Unsupported algorithm")
        
        signature_b64 = self.base64url_encode(signature)
        
        # Combine: header.payload.signature
        jwt_token = header_b64 + b'.' + payload_b64 + b'.' + signature_b64
        return jwt_token.decode()
    
    def verify_jwt(self, token: str) -> bool:
        \"\"\"Verify JWT token signature and expiration.\"\"\"
        try:
            # Split token
            header_b64, payload_b64, signature_b64 = token.encode().split(b'.')
            
            # Decode components
            header_json = self.base64url_decode(header_b64)
            payload_json = self.base64url_decode(payload_b64)
            signature = self.base64url_decode(signature_b64)
            
            # Parse JSON
            header = json.loads(header_json)
            payload = json.loads(payload_json)
            algorithm = header['alg']
            
            # Verify signature
            if algorithm == 'HS256':
                expected_signature = hmac.new(
                    self.secret_key, 
                    header_b64 + b'.' + payload_b64, 
                    hashlib.sha256
                ).digest()
            elif algorithm == 'HS512':
                expected_signature = hmac.new(
                    self.secret_key, 
                    header_b64 + b'.' + payload_b64, 
                    hashlib.sha512
                ).digest()
            else:
                return False
            
            # Constant-time comparison
            if not hmac.compare_digest(expected_signature, signature):
                return False
            
            # Check expiration
            if datetime.datetime.now() > datetime.datetime.fromisoformat(payload['exp']):
                return False
            
            return True
            
        except Exception as e:
            print(f"JWT verification error: {e}")
            return False

# Usage
jwt_mgr = JwtManager()

# Create JWT
payload = {"user_id": "doctor1", "role": "physician"}
jwt_token = jwt_mgr.create_jwt(payload, algorithm='HS256', expire_seconds=15)
print(f"Generated JWT: {jwt_token}")

# Verify JWT
is_valid = jwt_mgr.verify_jwt(jwt_token)
print(f"JWT valid: {is_valid}")  # True

# Wait for expiration
time.sleep(16)
is_valid = jwt_mgr.verify_jwt(jwt_token)
print(f"JWT valid after expiration: {is_valid}")  # False
```

#### Common Hashing Algorithms
```python
import hashlib

data = "Sensitive medical data"

# SHA-256 (most common)
sha256_hash = hashlib.sha256(data.encode()).hexdigest()
print(f"SHA-256: {sha256_hash}")

# SHA-512 (more secure, slower)
sha512_hash = hashlib.sha512(data.encode()).hexdigest()
print(f"SHA-512: {sha512_hash}")

# BLAKE2b (faster than SHA-256, equally secure)
blake2b_hash = hashlib.blake2b(data.encode()).hexdigest()
print(f"BLAKE2b: {blake2b_hash}")

# MD5 (INSECURE - don't use for security!)
md5_hash = hashlib.md5(data.encode()).hexdigest()
print(f"MD5 (INSECURE): {md5_hash}")

# Compare hash speeds
import time

iterations = 100000
start = time.time()
for _ in range(iterations):
    hashlib.sha256(data.encode()).hexdigest()
sha256_time = time.time() - start

start = time.time()
for _ in range(iterations):
    hashlib.blake2b(data.encode()).hexdigest()
blake2b_time = time.time() - start

print(f"\\nPerformance (100k iterations):")
print(f"  SHA-256: {sha256_time:.3f}s")
print(f"  BLAKE2b: {blake2b_time:.3f}s")
print(f"  BLAKE2b is {(sha256_time/blake2b_time):.2f}x faster")
```

#### Secure Random Generation
```python
import secrets
import random

# INSECURE: Don't use random module for security
insecure_token = random.randint(1000, 9999)  # Predictable!

# SECURE: Use secrets module
secure_token = secrets.token_hex(16)        # 32 hex characters
secure_bytes = secrets.token_bytes(16)      # 16 random bytes
secure_url = secrets.token_urlsafe(32)      # URL-safe token

print(f"Secure hex token: {secure_token}")
print(f"Secure bytes: {secure_bytes.hex()}")
print(f"Secure URL-safe: {secure_url}")

# Generate secure random numbers
secure_random_number = secrets.randbelow(1000)  # 0-999
secure_choice = secrets.choice(['A', 'B', 'C', 'D'])

# Compare entropy (randomness)
print(f"\\nRandom module (INSECURE for security):")
print(f"  Token: {random.randint(1000000, 9999999)}")

print(f"\\nSecrets module (SECURE):")
print(f"  Token: {secrets.randbelow(10000000)}")
```

#### Security Best Practices Summary
```python
\"\"\"
Security Best Practices for Healthcare/IoT Applications:

1. PASSWORD STORAGE
   ✕ BAD:  hashlib.sha256(password.encode())
   ✓ GOOD: hashlib.pbkdf2_hmac('sha256', password, salt, 200000)
   
2. RANDOM TOKEN GENERATION
   ✕ BAD:  random.randint()
   ✓ GOOD: secrets.token_urlsafe(32)

3. MESSAGE AUTHENTICATION
   ✕ BAD:  Send data without signature
   ✓ GOOD: Use HMAC with secret key

4. DATA INTEGRITY
   ✕ BAD:  Trust data without verification
   ✓ GOOD: Hash data and verify against stored hash

5. TOKEN VALIDATION
   ✓ ALWAYS: Check expiration time
   ✓ ALWAYS: Use constant-time comparison (hmac.compare_digest)
   ✓ ALWAYS: Rotate keys periodically

6. HASHING ALGORITHMS
   ✓ SHA-256: General purpose, widely supported
   ✓ BLAKE2b: Faster than SHA-256, equally secure
   ✓ PBKDF2: Password hashing with salt and iterations
   ✕ MD5: NEVER use for security (broken)
   ✕ SHA-1: Avoid for security (deprecated)

7. JWT TOKENS
   ✓ Include expiration time
   ✓ Verify signature before trusting payload
   ✓ Use secure secret keys (secrets.token_bytes)
   ✓ Implement token refresh mechanism
\"\"\"
```

---

### Lecture 10: Testing & Debugging for AI Applications

#### unittest with Machine Learning
```python
import unittest
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

def normalize_data(values):
    \"\"\"Normalize data to 0-1 scale.\"\"\"
    max_val = max(values)
    return [v / max_val for v in values]

class TestPreprocessing(unittest.TestCase):
    \"\"\"Test data preprocessing functions.\"\"\"
    
    def setUp(self):
        \"\"\"Run before each test.\"\"\"
        self.sample = [2, 4, 6]
    
    def tearDown(self):
        \"\"\"Run after each test (cleanup).\"\"\"
        pass
    
    def test_normalization(self):
        \"\"\"Test data normalization.\"\"\"
        result = normalize_data(self.sample)
        
        # Test first value normalized correctly
        self.assertAlmostEqual(result[0], 0.333, places=3)
        
        # Test max value is 1.0
        self.assertEqual(max(result), 1.0)
    
    def test_normalization_edge_cases(self):
        \"\"\"Test edge cases.\"\"\"
        # Single value
        self.assertEqual(normalize_data([5]), [1.0])
        
        # All same values
        self.assertEqual(normalize_data([3, 3, 3]), [1.0, 1.0, 1.0])

# Run tests
if __name__ == "__main__":
    unittest.main(argv=[''], exit=False)
```

#### pytest with Fixtures for ML Models
```python
import pytest
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

@pytest.fixture
def iris_dataset():
    \"\"\"Fixture: Load and split iris dataset (runs once per test).\"\"\"
    X, y = load_iris(return_X_y=True)
    return train_test_split(X, y, test_size=0.2, random_state=42)

def test_model_accuracy(iris_dataset):
    \"\"\"Test that model achieves acceptable accuracy.\"\"\"
    X_train, X_test, y_train, y_test = iris_dataset
    
    # Train model
    model = LogisticRegression(max_iter=200)
    model.fit(X_train, y_train)
    
    # Evaluate
    acc = model.score(X_test, y_test)
    
    # Assert minimum accuracy
    assert acc > 0.8, f"Model accuracy {acc:.2f} is below threshold"

def test_model_predictions(iris_dataset):
    \"\"\"Test model predictions are in valid range.\"\"\"
    X_train, X_test, y_train, y_test = iris_dataset
    
    model = LogisticRegression(max_iter=200)
    model.fit(X_train, y_train)
    
    predictions = model.predict(X_test)
    
    # All predictions should be 0, 1, or 2 (iris classes)
    assert all(pred in [0, 1, 2] for pred in predictions)
    
    # Should have same number of predictions as test samples
    assert len(predictions) == len(X_test)

# Run with: pytest -v test_file.py
```

#### Parametrized Testing
```python
import pytest

@pytest.mark.parametrize("a,b,expected", [
    (2, 3, 5),      # Normal case
    (5, 5, 10),     # Same numbers
    (-1, 1, 0),     # Negative number
    (0, 0, 0),      # Zeros
    (100, -50, 50), # Large numbers
])
def test_add(a, b, expected):
    \"\"\"Test addition with multiple parameter sets.\"\"\"
    assert a + b == expected

# Each set of parameters runs as a separate test
# Run with: pytest -v
```

#### Testing with Logging
```python
import logging
import unittest

# Configure logging for tests
logging.basicConfig(
    filename='test.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class TestWithLogging(unittest.TestCase):
    \"\"\"Test class that logs execution.\"\"\"
    
    def setUp(self):
        logging.info(f"Starting test: {self._testMethodName}")
    
    def tearDown(self):
        logging.info(f"Completed test: {self._testMethodName}")
    
    def test_calculation(self):
        \"\"\"Test with logging.\"\"\"
        logging.debug("Performing calculation")
        result = 2 + 2
        logging.debug(f"Result: {result}")
        self.assertEqual(result, 4)
        logging.info("Test passed")
```

#### Debugging Strategies
```python
# 1. Print debugging (quick and simple)
def calculate_average(numbers):
    print(f"DEBUG: Input numbers: {numbers}")
    total = sum(numbers)
    print(f"DEBUG: Total: {total}")
    avg = total / len(numbers)
    print(f"DEBUG: Average: {avg}")
    return avg

# 2. Logging (better for production)
import logging

def process_patient_data(patient_id, data):
    logging.debug(f"Processing patient {patient_id}")
    logging.debug(f"Data: {data}")
    
    try:
        result = perform_calculation(data)
        logging.info(f"Successfully processed patient {patient_id}")
        return result
    except Exception as e:
        logging.error(f"Error processing patient {patient_id}: {e}")
        raise

# 3. Assertions (sanity checks during development)
def divide(a, b):
    assert isinstance(a, (int, float)), f"a must be numeric, got {type(a)}"
    assert isinstance(b, (int, float)), f"b must be numeric, got {type(b)}"
    assert b != 0, "Cannot divide by zero"
    return a / b

# 4. Using pdb (Python debugger)
import pdb

def complex_function(data):
    result = []
    for item in data:
        # pdb.set_trace()  # Debugger stops here
        processed = item * 2
        result.append(processed)
    return result

# pdb commands:
# n - next line
# s - step into function
# c - continue execution
# p variable - print variable
# l - list code around current line
# q - quit debugger
```

---

### Lecture 11: Parallel & Distributed Computing

#### Threading for I/O-Bound Tasks
```python
import time
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import logging

def read_feedback_file(filepath):
    \"\"\"Read JSON file (I/O-bound operation).\"\"\"
    with open(filepath, 'r') as f:
        logging.info(f"Reading: {filepath}")
        data = json.load(f)
    return data

def demonstrate_threading():
    \"\"\"Demonstrate performance improvement with threading.\"\"\"
    feedback_files = list(Path("feedback").glob("*.json"))
    
    thread_counts = [1, 4, 8]
    
    for n_threads in thread_counts:
        start_time = time.time()
        
        # Thread pool executor
        with ThreadPoolExecutor(max_workers=n_threads) as executor:
            results = list(executor.map(read_feedback_file, feedback_files))
        
        elapsed = time.time() - start_time
        print(f"Threads: {n_threads:2d} | Time: {elapsed:6.2f}s | Files: {len(results)}")

# Real results from course:
# Threads:  1 | Time:  10.50s | Files: 60
# Threads:  4 | Time:   3.20s | Files: 60  (3.3x faster!)
# Threads:  8 | Time:   2.10s | Files: 60  (5x faster!)
```

#### Multiprocessing for CPU-Bound Tasks
```python
import numpy as np
import pandas as pd
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
import time

def calculate_rolling_variance(store_data):
    \"\"\"CPU-intensive rolling variance calculation.\"\"\"
    store_id, df = store_data
    
    # Simulate intensive computation
    n_points = 10000
    data = np.random.randn(n_points)
    
    window_size = 100
    rolling_var = []
    
    for i in range(window_size, n_points):
        window = data[i - window_size:i]
        variance = np.var(window)
        rolling_var.append(variance)
    
    # Calculate actual variance from store data
    if not df.empty:
        df['revenue'] = df['qty'] * df['price']
        daily_variance = df.groupby(df['timestamp'].dt.date)['revenue'].var().mean()
    else:
        daily_variance = 0
    
    return {
        'store_id': store_id,
        'simulated_variance': np.mean(rolling_var),
        'actual_variance': daily_variance
    }

def demonstrate_multiprocessing():
    \"\"\"Demonstrate CPU-bound parallel processing.\"\"\"
    # Load sales data
    df = pd.read_csv('sales.csv', parse_dates=['timestamp'])
    
    # Group by store
    store_groups = [(store, group) for store, group in df.groupby('store_id')][:10]
    
    process_counts = [1, multiprocessing.cpu_count()]
    
    for n_processes in process_counts:
        start_time = time.time()
        
        if n_processes == 1:
            # Serial processing
            results = [calculate_rolling_variance(sg) for sg in store_groups]
        else:
            # Parallel processing
            with ProcessPoolExecutor(max_workers=n_processes) as executor:
                results = list(executor.map(calculate_rolling_variance, store_groups))
        
        elapsed = time.time() - start_time
        print(f"Processes: {n_processes:2d} | Time: {elapsed:6.2f}s | Stores: {len(results)}")

# Real results from course:
# Processes:  1 | Time:  45.30s | Stores: 10
# Processes:  8 | Time:   6.80s | Stores: 10  (6.7x faster!)
```

#### Dask for Large-Scale Data Processing
```python
import dask.dataframe as dd
import pandas as pd
from pathlib import Path
import time

def demonstrate_dask():
    \"\"\"Process large datasets with Dask.\"\"\"
    DATA_DIR = Path("islandmarket_data")
    
    # Read multiple CSV files in parallel
    sales_pattern = str(DATA_DIR / "sales" / "sales_*.csv")
    ddf = dd.read_csv(sales_pattern, parse_dates=['timestamp'], blocksize="25MB")
    
    print(f"Partitions: {ddf.npartitions}")  # Data split into chunks
    print(f"Columns: {list(ddf.columns)}")
    
    # Lazy operations (not executed yet)
    ddf['revenue'] = ddf['qty'] * ddf['price']
    revenue_by_store = ddf.groupby('store_id')['revenue'].sum()
    
    # Trigger computation
    start_time = time.time()
    revenue_results = revenue_by_store.compute()
    elapsed = time.time() - start_time
    
    print(f"Computation time: {elapsed:.2f}s")
    print(f"Top 5 stores by revenue:")
    print(revenue_results.nlargest(5))
    
    # Join datasets
    inventory_df = pd.read_csv(DATA_DIR / "inventory_snapshot.csv")
    inventory_ddf = dd.from_pandas(inventory_df, npartitions=4)
    
    # Compute daily demand
    daily_demand = ddf.groupby(['store_id', 'product_id'])['qty'].sum().reset_index()
    
    # Join datasets
    joined = daily_demand.merge(
        inventory_ddf, 
        on=['store_id', 'product_id'], 
        how='inner'
    )
    
    # Calculate metrics
    joined['demand_stock_ratio'] = joined['qty'] / (joined['on_hand'] + 1)
    
    # Find at-risk products
    bottom_10pct_threshold = revenue_results.quantile(0.1)
    bottom_stores = revenue_results[revenue_results <= bottom_10pct_threshold].index
    
    joined_computed = joined.compute()
    risk_analysis = joined_computed[joined_computed['store_id'].isin(bottom_stores)]
    high_risk = risk_analysis[risk_analysis['demand_stock_ratio'] > 0.8]
    
    print(f"Bottom 10% revenue threshold: ${bottom_10pct_threshold:,.2f}")
    print(f"Bottom decile stores: {len(bottom_stores)}")
    print(f"Products at stockout risk: {len(high_risk)}")
    
    if len(high_risk) > 0:
        print(high_risk[['store_id', 'product_id', 'qty', 'on_hand', 'demand_stock_ratio']].head())
```

#### Complete Parallel Computing Example
```python
import logging
import time
import json
import numpy as np
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import dask.dataframe as dd
import multiprocessing
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    \"\"\"Complete parallel computing demonstration.\"\"\"
    DATA_DIR = Path("islandmarket_data")
    
    if not DATA_DIR.exists():
        logger.error(f"{DATA_DIR} not found")
        return
    
    # 1. Threading for I/O-bound tasks
    logger.info("Demonstrating Threading (I/O-bound)")
    demonstrate_threading()
    
    # 2. Multiprocessing for CPU-bound tasks
    logger.info("Demonstrating Multiprocessing (CPU-bound)")
    demonstrate_multiprocessing()
    
    # 3. Dask for large-scale data
    logger.info("Demonstrating Dask (Large datasets)")
    demonstrate_dask()

if __name__ == "__main__":
    main()
```

#### Performance Comparison Guide
```python
\"\"\"
WHEN TO USE WHAT?

THREADING (concurrent.futures.ThreadPoolExecutor):
├─ ✓ I/O-Bound Tasks
│  ├─ Reading/writing files (10-100x faster)
│  ├─ Network requests, API calls
│  ├─ Database queries
│  └─ User input/waiting operations
├─ ✓ Shared memory needed
├─ ✓ Lightweight (low overhead)
└─ ✕ CPU-bound tasks (GIL prevents true parallelism)

MULTIPROCESSING (concurrent.futures.ProcessPoolExecutor):
├─ ✓ CPU-Bound Tasks
│  ├─ Complex calculations (5-10x faster)
│  ├─ Data transformations
│  ├─ Machine learning training
│  └─ Scientific computing
├─ ✓ True parallelism (bypasses GIL)
├─ ✕ I/O-bound tasks (overhead too high)
└─ ✕ Shared memory (requires special handling)

DASK (dask.dataframe):
├─ ✓ Large Datasets (GB-TB scale)
│  ├─ Datasets that don't fit in RAM
│  ├─ Multi-file processing
│  └─ Distributed computing
├─ ✓ Familiar pandas-like API
├─ ✓ Automatic chunking and parallelization
└─ ✕ Small datasets (overhead not worth it)

ASYNC/AWAIT (asyncio):
├─ ✓ High-Concurrency I/O
│  ├─ Thousands of concurrent connections
│  ├─ WebSocket servers
│  ├─ Microservices
│  └─ Real-time data streams
├─ ✓ Single-threaded efficiency
└─ ✕ CPU-bound tasks


REAL PERFORMANCE GAINS FROM COURSE:

I/O Task (Reading 60 JSON files):
  Serial:      10.50s
  Threading:    2.10s  (5.0x faster) ⨁
  Multiproc:    3.80s  (2.8x faster)

CPU Task (10 rolling variance calculations):
  Serial:      45.30s
  Threading:   44.80s  (1.0x - NO GAIN due to GIL)
  Multiproc:    6.80s  (6.7x faster) ⨁

Large Dataset (1GB sales data):
  Pandas:      Out of Memory ✕
  Dask:        Success ✓ (chunked processing)
\"\"\"
```

---

## 18. Lecture Coverage Summary

### ✓ Complete Coverage of All 11 Lectures

| Lecture | Topic | Key Concepts in Cheatsheet |
|---------|-------|----------------------------|
| **1** | Data Loading & Exploration | Pandas basics, DataFrame operations, data inspection |
| **2** | Text Processing & Classification | String methods, sets, tokenization, spam detection |
| **3** | Research Paper Management | Global variables, lambda functions, filtering, nested functions |
| **4** | Medical Appointment System | Custom exceptions, decorators, logging, CSV operations |
| **5** | Risk Scoring | Abstract Base Classes, polymorphism, ABC module |
| **6** | Healthcare OOP Package | Encapsulation, inheritance, package structure, private attributes |
| **7** | Smart City Data Analysis | Pandas visualization, matplotlib, seaborn, time series |
| **8** | IoT Comprehensions & Generators | map/filter/zip, list/dict/set comprehensions, generator functions |
| **9** | Security & Cryptography | Hashing (SHA-256, BLAKE2b), HMAC, JWT, secure tokens, PBKDF2 |
| **10** | Testing & Debugging | unittest, pytest, fixtures, parametrized tests, debugging |
| **11** | Parallel Computing | Threading, multiprocessing, Dask, performance optimization |

###  Section Mapping

- **Sections 1-6**: Fundamentals (Lectures 1-2 concepts)
- **Section 7**: Pandas (Lectures 1, 7)
- **Section 8-9**: Comprehensions & Generators (Lecture 8)
- **Section 10-11**: OOP & Errors (Lectures 5, 6)
- **Section 12**: Logging (Lecture 4)
- **Section 13**: Modules (Lectures 3, 4, 6)
- **Section 14**: Testing (Lecture 10)
- **Section 15**: Parallel Computing (Lecture 11)
- **Section 16**: Type Hints (Lectures 5, 6)
- **Section 17**: Real-World Examples (Lectures 3-11)
- **Section 18**: Best Practices (All lectures)

---

## 19. Best Practices

### Code Style (PEP 8)
```python
# Naming conventions
class MyClass:              # CapWords for classes
    pass

def my_function():          # lowercase_with_underscores for functions
    pass

MY_CONSTANT = 42            # UPPERCASE for constants

my_variable = 10            # lowercase_with_underscores for variables

_internal_use = "private"   # Leading underscore for internal use

# Line length: max 79 characters
long_variable_name = (
    "This is a very long string that needs to be "
    "split across multiple lines"
)

# Imports: one per line
import os
import sys
from typing import List, Dict

# NOT: import os, sys

# Whitespace
spam(ham[1], {eggs: 2})     # YES
spam( ham[ 1 ], { eggs: 2 } )  # NO

x = 1                       # YES
x=1                        # NO

# Comments
# This is a comment
x = x + 1  # Increment x

\"\"\"
This is a 
multi-line comment
or docstring
\"\"\"
```

### Docstrings
```python
def calculate_area(length: float, width: float) -> float:
    \"\"\"
    Calculate the area of a rectangle.
    
    Args:
        length: The length of the rectangle
        width: The width of the rectangle
    
    Returns:
        The area of the rectangle
    
    Raises:
        ValueError: If length or width is negative
    
    Example:
        >>> calculate_area(5, 3)
        15.0
    \"\"\"
    if length < 0 or width < 0:
        raise ValueError("Dimensions must be positive")
    return length * width

class BankAccount:
    \"\"\"
    A class representing a bank account.
    
    Attributes:
        balance: The current balance
        account_number: The account number
    
    Methods:
        deposit: Add money to the account
        withdraw: Remove money from the account
    \"\"\"
    pass
```

### Error Handling Best Practices
```python
# Be specific with exceptions
try:
    result = int(value)
except ValueError:  # Specific exception
    print("Invalid integer")

# Don't catch Exception unless necessary
try:
    risky_operation()
except SpecificException as e:
    handle_error(e)

# Use finally for cleanup
try:
    file = open('data.txt')
    process(file)
finally:
    file.close()

# Or better, use context manager
with open('data.txt') as file:
    process(file)
```

### Performance Tips
```python
# Use list comprehensions (faster than loops)
# SLOW
squares = []
for i in range(1000):
    squares.append(i**2)

# FAST
squares = [i**2 for i in range(1000)]

# Use generators for large datasets
# SLOW (loads all into memory)
def get_squares(n):
    return [i**2 for i in range(n)]

# FAST (lazy evaluation)
def get_squares(n):
    for i in range(n):
        yield i**2

# Use set for membership testing
# SLOW (O(n))
numbers = [1, 2, 3, 4, 5]
if 3 in numbers:
    pass

# FAST (O(1))
numbers = {1, 2, 3, 4, 5}
if 3 in numbers:
    pass

# Use join for string concatenation
# SLOW
result = ""
for s in strings:
    result += s

# FAST
result = "".join(strings)

# Use defaultdict to avoid key checks
from collections import defaultdict

# SLOW
d = {}
for item in items:
    if item not in d:
        d[item] = []
    d[item].append(value)

# FAST
d = defaultdict(list)
for item in items:
    d[item].append(value)
```

### Security Best Practices
```python
# Never use eval() on untrusted input
user_input = "malicious_code()"
# eval(user_input)  # DANGEROUS!

# Use ast.literal_eval for safe evaluation
import ast
safe_data = ast.literal_eval("[1, 2, 3]")

# Don't store sensitive data in code
# BAD
password = "secret123"

# GOOD
import os
password = os.environ.get('PASSWORD')

# Validate user input
def process_age(age_str):
    try:
        age = int(age_str)
        if not 0 <= age <= 120:
            raise ValueError("Invalid age")
        return age
    except ValueError:
        return None

# Use parameterized queries (SQL injection prevention)
# BAD
query = f"SELECT * FROM users WHERE name = '{user_input}'"

# GOOD
query = "SELECT * FROM users WHERE name = ?"
cursor.execute(query, (user_input,))
```

---

## Quick Reference Tables

### Common String Methods
| Method | Description | Example |
|--------|-------------|---------|
| `lower()` | Convert to lowercase | `"HELLO".lower()` → `"hello"` |
| `upper()` | Convert to uppercase | `"hello".upper()` → `"HELLO"` |
| `strip()` | Remove whitespace | `"  hi  ".strip()` → `"hi"` |
| `split()` | Split into list | `"a,b,c".split(',')` → `['a','b','c']` |
| `join()` | Join list into string | `','.join(['a','b'])` → `"a,b"` |
| `replace()` | Replace substring | `"hi".replace('i','o')` → `"ho"` |
| `find()` | Find substring index | `"hello".find('l')` → `2` |
| `startswith()` | Check prefix | `"hello".startswith('he')` → `True` |
| `endswith()` | Check suffix | `"hello".endswith('lo')` → `True` |

### Common List Methods
| Method | Description | Example |
|--------|-------------|---------|
| `append(x)` | Add item to end | `list.append(5)` |
| `extend(iterable)` | Add multiple items | `list.extend([1,2,3])` |
| `insert(i, x)` | Insert at position | `list.insert(0, 'first')` |
| `remove(x)` | Remove first occurrence | `list.remove('item')` |
| `pop([i])` | Remove and return item | `list.pop()` |
| `clear()` | Remove all items | `list.clear()` |
| `sort()` | Sort in place | `list.sort()` |
| `reverse()` | Reverse in place | `list.reverse()` |
| `count(x)` | Count occurrences | `list.count(5)` |
| `index(x)` | Find first index | `list.index('item')` |

### Common Dict Methods
| Method | Description | Example |
|--------|-------------|---------|
| `get(key, default)` | Get value safely | `dict.get('key', 0)` |
| `keys()` | Get all keys | `dict.keys()` |
| `values()` | Get all values | `dict.values()` |
| `items()` | Get key-value pairs | `dict.items()` |
| `pop(key)` | Remove and return | `dict.pop('key')` |
| `update(other)` | Merge dictionaries | `dict.update({'a': 1})` |
| `clear()` | Remove all items | `dict.clear()` |
| `setdefault(k, default)` | Get or set default | `dict.setdefault('key', [])` |

### Pandas Quick Reference
| Operation | Code |
|-----------|------|
| Read CSV | `pd.read_csv('file.csv')` |
| Select column | `df['column']` or `df.column` |
| Select rows | `df.loc[0:5]` or `df.iloc[0:5]` |
| Filter | `df[df['age'] > 25]` |
| Group by | `df.groupby('category')['value'].mean()` |
| Sort | `df.sort_values('column')` |
| Add column | `df['new'] = df['a'] + df['b']` |
| Drop column | `df.drop('column', axis=1)` |
| Drop rows | `df.drop([0, 1, 2])` |
| Handle nulls | `df.fillna(0)` or `df.dropna()` |

---

## Useful Resources

### Official Documentation
- [Python Documentation](https://docs.python.org/3/)
- [PEP 8 Style Guide](https://peps.python.org/pep-0008/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [NumPy Documentation](https://numpy.org/doc/)

### Learning Resources
- [Python Tutorial (official)](https://docs.python.org/3/tutorial/)
- [Real Python](https://realpython.com/)
- [Python.org Beginner's Guide](https://wiki.python.org/moin/BeginnersGuide)

### Tools
- **IDE/Editors**: VS Code, PyCharm, Jupyter Notebook
- **Linters**: pylint, flake8, black (formatter)
- **Type Checking**: mypy
- **Testing**: pytest, unittest
- **Package Management**: pip, conda, poetry

---

## Version Information

This cheatsheet covers Python 3.12+ features and is compatible with:
- Python 3.12
- Python 3.13+

### Python 3.12+ Specific Features
```python
# Type parameter syntax (PEP 695)
def max[T](args: Iterable[T]) -> T:
    ...

# f-string improvements
# Reuse of expressions
value = 10
print(f"{value=}")  # Prints: value=10

# Multi-line f-strings
message = f\"\"\"
Hello {name},
You are {age} years old.
\"\"\"

# Per-interpreter GIL (improved threading)
# Improved error messages with precise locations
```

---

## Summary

This comprehensive Python cheatsheet covers:
- **18 major sections** with practical examples
- **Real-world patterns** from ALL 11 Lectures:
  - **Lecture 1**: Data Loading & Exploration (pandas basics)
  - **Lecture 2**: Text Processing & Classification (string manipulation, sets)
  - **Lecture 3**: Research Paper Management (global state, lambdas, filtering)
  - **Lecture 4**: Medical Appointment System (custom exceptions, decorators, logging)
  - **Lecture 5**: Risk Scoring with Abstract Base Classes & Polymorphism
  - **Lecture 6**: Advanced OOP Healthcare Package (encapsulation, inheritance, package structure)
  - **Lecture 7**: Smart City Data Analysis (pandas, matplotlib, seaborn, time series)
  - **Lecture 8**: IoT Comprehensions & Generators (map/filter/zip, streaming data)
  - **Lecture 9**: Security & Cryptography (hashing, HMAC, JWT, tokens)
  - **Lecture 10**: Testing & Debugging (unittest, pytest, fixtures)
  - **Lecture 11**: Parallel Computing (threading, multiprocessing, Dask)
- **Python 3.12+ features** and best practices
- **Complete coverage** of ALL course topics

**Last Updated**: 2025-10-15  
**Python Version**: 3.12+  
**Course Coverage**: ALL Lectures 1-11 + Lab Materials  
**Total Examples**: 300+ code snippets covering every Python concept  
**License**: Free to use and distribute

---
"""

def get_full_readme():
    """
    Get the embedded full README content.
    
    Returns:
        str: The complete cheatsheet content
    """
    return __readme_full__
