# sortlab

**sortlab** is a simple Python package that provides utility functions for temperature conversion and sorting algorithms. It is designed for learning, practice, and quick development tasks.

---

## Features

- Convert temperatures between Celsius and Fahrenheit:
  - `to_celsius(fahrenheit)`  
  - `to_fahrenheit(celsius)`
- Implement common sorting algorithms (future versions will include more):
  - Bubble Sort (and others can be added)
  
---

## Installation

You can install the package directly from PyPI:

```bash
pip install sortlab

from sortlab import to_celsius, to_fahrenheit

# Convert Fahrenheit to Celsius
print(to_celsius(98.6))  # Output: 37.0

# Convert Celsius to Fahrenheit
print(to_fahrenheit(37))  # Output: 98.6


from sortlab import bubble_sort

arr = [5, 3, 1, 4]
sorted_arr = bubble_sort(arr)
print(sorted_arr)  # Output: [1, 3, 4, 5]
