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
from numcore import mean, median, analyze_list, factorial, is_prime, gcd

# Statistical analysis
data = [23, 45, 67, 45, 89, 34, 78, 98, 54, 55]
print(mean(data))      # 58.8
print(median(data))    # 54.5

# Comprehensive analysis
analysis = analyze_list(data)
print(analysis['mean'])
print(analysis['variance'])

# Number theory
print(factorial(5))           # 120
print(is_prime(17))          # True
print(gcd(48, 18))           # 6
print(prime_factorization(100))  # [2, 2, 5, 5]
```

## ✨ Features

### **Input Functions**
- `n_input()` - Get n integers from user with validation

### **List Utilities**
- `counter()` - Count occurrences of items in a list
- `product()` - Multiply all numbers in a list

### **Statistical Functions**
- `mean()` - Calculate average
- `median()` - Find middle value
- `mode()` - Find most common value(s)
- `variance()` - Calculate variance (population or sample)
- `std()` - Calculate standard deviation
- `analyze_list()` - Comprehensive statistical analysis

### **Number Theory**
- `factorial()` - Calculate n! (factorial)
- `nth_root()` - Calculate nth root of a number
- `divisors()` - Find all divisors of a number
- `common_divisors()` - Find common divisors of two numbers
- `gcd()` - Greatest common divisor (Euclidean algorithm)
- `lcm()` - Least common multiple
- `is_prime()` - Check if a number is prime
- `primes()` - Get all primes up to a number
- `prime_divisors()` - Find prime divisors of a number
- `prime_factorization()` - Prime factorization of a number
- `prime_factors()` - Unique prime factors
- `is_perfect()` - Check if a number is perfect

## 🎯 Roadmap

- [x] Basic input functions (v0.1.0)
- [x] List utilities (v0.1.2)
- [x] Statistical functions (v0.1.3)
- [x] Number theory functions (v0.1.4)
- [ ] Trigonometry functions
- [ ] Algebra functions (equations, matrices)
- [ ] Calculus functions (derivatives, integrals)
- [ ] More advanced statistics
- [ ] **Goal: 250+ functions!**

## 📊 Progress

**Current Functions:** 21/250 (8.4%)

## 👨‍💻 Author

**Ujwal Mantri**
- PyPI: [numcore](https://pypi.org/project/numcore/)
- GitHub: [ujwalmantri](https://github.com/ujwalmantri/numcore)
- Email: ujwalmantrifr@gmail.com

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details

## 🌟 Support

If you find this helpful, please give it a star ⭐ on GitHub!

---

Crafted with Python. Powered by curiosity. Open-sourced for learning. ⚡