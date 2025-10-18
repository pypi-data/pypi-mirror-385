# 🧮 numcore

A comprehensive mathematics library built from scratch by a first-year student. Currently in active development with a goal of **250+ functions**.

[![PyPI version](https://badge.fury.io/py/numcore.svg)](https://pypi.org/project/numcore/)
[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

## 🚀 Installation
```bash
pip install numcore
```

## 📖 Usage
```python
from numcore import n_input
from numcore import counter

# Get 5 integers from user
numbers = n_input(5)
print(numbers)
```
```python
from numcore import counter
# Count occurrences in a list
result = counter(['a', 'b', 'c', 'a', 'b', 'a'])
print(result)  # Output: {'a': 3, 'b': 2, 'c': 1}
# List Analysis
```
```python
from numcore import mean, median, mode, std, analyze_list

# Basic statistics
data = [23, 45, 67, 45, 89, 34, 78, 98, 54, 55]
print(mean(data))      # 58.8
print(median(data))    # 54.5
print(mode(data))      # [45]
print(std(data))       # 23.82

# Comprehensive analysis
analysis = analyze_list(data)
print(analysis['mean'])              # 58.8
print(analysis['variance'])          # {'population variance': ..., 'sample variance': ...}
print(analysis['frequency'])         # {23: 1, 45: 2, 67: 1, ...}
```

## ✨ Features

**Input Functions:**
- **n_input()** - Get n integers from user with validation

**List Utilities:**
- **counter()** - Count occurrences of items

**Statistical Functions:**
- **mean()** - Calculate average
- **median()** - Find middle value
- **mode()** - Find most common value(s)
- **variance()** - Calculate variance (population or sample)
- **std()** - Calculate standard deviation
- **analyze_list()** - Comprehensive statistical analysis

## 🎯 Roadmap

- [x] Basic input functions (v0.1.1)
- [x] List utilities - counter (v0.1.2)
- [ ] Arithmetic operations (add, subtract, multiply, divide)
- [ ] Algebra functions
- [ ] Calculus functions
- [ ] Statistics functions
- [ ] **Goal: 250+ functions!**

## 📊 Progress

**Current Functions:** 8/250 (3.2%)

## 👨‍💻 Author

**Ujwal Mantri**
- PyPI: [numcore](https://pypi.org/project/numcore/)
- Email: ujwalmantrifr@gmail.com

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details

## 🌟 Support

If you find this helpful, please give it a star ⭐ on GitHub!

---

> Crafted with Python. Powered by curiosity. Open-sourced for learning. ⚡
```
