# 🧮 numcore

A comprehensive mathematics library built from scratch by a first-year student. Currently in active development with a goal of **250+ functions**.

[![PyPI version](https://badge.fury.io/py/numcore.svg)](https://pypi.org/project/numcore/)
[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

## 🚀 Installation

```bash
pip install numcore
```

## 📖 Usage

### **Statistical Analysis**
```python
from numcore import mean, median, mode, std, analyze_list

data = [23, 45, 67, 45, 89, 34, 78, 98, 54, 55]

# Basic statistics
print(mean(data))      # 58.8
print(median(data))    # 54.5
print(mode(data))      # [45]
print(std(data))       # 23.82

# Comprehensive analysis
analysis = analyze_list(data)
print(analysis['mean'])
print(analysis['variance'])
print(analysis['frequency'])
```

### **Number Theory**
```python
from numcore import factorial, is_prime, gcd, lcm, prime_factorization

print(factorial(5))              # 120
print(is_prime(17))             # True
print(gcd(48, 18))              # 6
print(lcm(12, 18))              # 36
print(prime_factorization(100)) # [2, 2, 5, 5]
print(is_armstrong(153))        # True
print(fibonacci(10))            # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

### **Matrix Operations**
```python
from numcore import (create_matrix, matrix_add, matrix_multiply, 
                     scalar_multiply, determinant, matrix_transpose)

# Create matrices
mat1 = create_matrix(2, 2, fill=1)  # [[1, 1], [1, 1]]
mat2 = [[2, 3], [4, 5]]

# Basic operations
sum_mat = matrix_add(mat1, mat2)         # [[3, 4], [5, 6]]
product = matrix_multiply(mat1, mat2)    # [[6, 8], [6, 8]]
scaled = scalar_multiply(mat2, 3)        # [[6, 9], [12, 15]]

# Advanced operations
det = determinant(mat2)                  # -2
transposed = matrix_transpose(mat2)      # [[2, 4], [3, 5]]
identity = matrix_identity(3)            # [[1,0,0], [0,1,0], [0,0,1]]
trace = matrix_trace(mat2)               # 7
```

### **Number Operations**
```python
from numcore import digits, reverse_number, sum_of_digits, is_amicable

print(digits(12345))           # [1, 2, 3, 4, 5]
print(reverse_number(12345))   # 54321
print(sum_of_digits(12345))    # 15
print(is_amicable(220, 284))   # True
```

## ✨ Features

### **Input Functions**
- `n_input(n)` - Get n integers from user with validation

### **List Utilities**
- `counter(lst)` - Count occurrences of items in a list
- `product(lst)` - Multiply all numbers in a list
- `list_power(lst, power)` - Apply power to each element in list

### **Statistical Functions**
- `mean(lst)` - Calculate average
- `median(lst)` - Find middle value
- `mode(lst)` - Find most common value(s)
- `variance(lst, sample=False)` - Calculate variance (population or sample)
- `std(lst, sample=False)` - Calculate standard deviation
- `analyze_list(lst)` - Comprehensive statistical analysis

### **Number Theory**
- `factorial(n)` - Calculate n! (factorial)
- `nth_root(num, n)` - Calculate nth root of a number
- `divisors(num)` - Find all divisors (optimized algorithm)
- `proper_divisors(num)` - Divisors excluding the number itself
- `common_divisors(num1, num2)` - Find common divisors
- `gcd(num1, num2)` - Greatest common divisor (Euclidean algorithm)
- `lcm(num1, num2)` - Least common multiple
- `is_prime(num)` - Check if prime (optimized)
- `primes(num)` - Get all primes up to num
- `prime_divisors(num)` - Prime divisors only
- `prime_factorization(num)` - Prime factorization with repetition
- `prime_factors(num)` - Unique prime factors
- `is_perfect(num)` - Check if perfect number
- `is_armstrong(num)` - Check if Armstrong number
- `is_amicable(a, b)` - Check if amicable pair

### **Sequences**
- `fibonacci(num)` - Generate Fibonacci sequence
- `nth_fibonacci(num)` - Get nth Fibonacci number

### **Digit Operations**
- `digits(num)` - Extract digits as list
- `reverse_number(num)` - Reverse the digits
- `sum_of_digits(num)` - Sum all digits

### **Basic Matrix Operations**
- `create_matrix(rows, cols, fill=0)` - Create matrix with fill value
- `input_matrix()` - Interactive matrix input
- `matrix_shape(matrix)` - Get dimensions and validate
- `matrix_add(mat1, mat2)` - Add matrices element-wise
- `matrix_sub(mat1, mat2)` - Subtract matrices element-wise
- `scalar_multiply(matrix, scalar)` - Multiply by scalar
- `matrix_multiply(mat1, mat2)` - Matrix multiplication

### **Advanced Matrix Operations**
- `matrix_identity(rows)` - Create identity matrix
- `matrix_transpose(matrix)` - Transpose matrix
- `matrix_trace(matrix)` - Sum of diagonal elements
- `determinant(matrix)` - Calculate determinant (recursive)
- `matrix_minor(matrix)` - Matrix of minors
- `matrix_cofactor(matrix)` - Cofactor matrix
- `matrix_power(matrix, power)` - Raise matrix to power
- `is_square(matrix)` - Check if square matrix
- `is_orthogonal(matrix)` - Check if orthogonal matrix

## 🎯 Roadmap

- [x] Basic input functions (v0.1.0)
- [x] List utilities (v0.1.2)
- [x] Statistical functions (v0.1.3)
- [x] Number theory functions (v0.1.4)
- [x] Basic matrix operations (v0.1.5)
- [x] Advanced matrix operations (v0.1.6)
- [x] Sequence generation & digit operations (v0.1.7)
- [ ] Trigonometry functions (sin, cos, tan with degrees)
- [ ] Matrix decomposition (LU, QR, SVD)
- [ ] Algebra functions (solve equations, quadratic formula)
- [ ] Calculus functions (derivatives, integrals)
- [ ] Advanced statistics (correlation, regression)
- [ ] **Goal: 250+ functions!**

## 📊 Progress

**Current Functions:** 47/250 (18.8%)

## 💡 Example Use Cases

### **Finding Armstrong Numbers**
```python
from numcore import is_armstrong

for num in range(1, 1000):
    if is_armstrong(num):
        print(num)  # 1, 153, 370, 371, 407
```

### **Matrix Determinant Calculation**
```python
from numcore import determinant

matrix = [[1, 2, 3],
          [4, 5, 6],
          [7, 8, 9]]

det = determinant(matrix)  # 0 (singular matrix)
```

### **Fibonacci Sequence Generation**
```python
from numcore import fibonacci

fib_seq = fibonacci(10)
print(fib_seq)  # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

### **Checking Amicable Numbers**
```python
from numcore import is_amicable

print(is_amicable(220, 284))  # True
# 220 and 284 are the smallest amicable pair
```

## 🛠️ Development

### **Requirements**
- Python 3.7+
- No external dependencies!

### **Contributing**
This is a learning project, but suggestions and feedback are welcome! Feel free to:
- Report bugs via GitHub Issues
- Suggest new functions
- Share how you're using numcore

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details

## 👨‍💻 Author

**Ujwal Mantri**
- PyPI: [numcore](https://pypi.org/project/numcore/)
- GitHub: [ujwalmantri](https://github.com/ujwalmantri/numcore)
- Email: ujwalmantrifr@gmail.com

## 🌟 Support

If you find this helpful, please:
- ⭐ Star the repository on GitHub
- 📦 Try it out: `pip install numcore`
- 📢 Share with others learning Python

## 🎓 Learning Journey

This library is being built as a learning project by a first-year student. It documents the journey from basic Python concepts to advanced mathematical algorithms. Each function is implemented from scratch to maximize learning.

### **Milestones**
- ✅ Published first version to PyPI
- ✅ Implemented recursive determinant calculation
- ✅ Built complete matrix operations suite
- ✅ Reached 18.8% of 250-function goal
- 🎯 Next: 50 functions (20%)
- 🎯 Goal: 250+ functions

### **Why numcore?**
- ✅ Learn by building
- ✅ No dependencies - pure Python
- ✅ Well-documented with examples
- ✅ Growing collection of useful functions
- ✅ Open source for everyone to learn from

## 📚 Function Categories

| Category | Functions | Status |
|----------|-----------|--------|
| Input/Output | 2 | ✅ Complete |
| Statistics | 6 | ✅ Complete |
| Number Theory | 16 | 🔄 Growing |
| Sequences | 2 | 🔄 Growing |
| Digit Operations | 3 | ✅ Complete |
| Matrix Basic | 7 | ✅ Complete |
| Matrix Advanced | 9 | ✅ Complete |
| List Utilities | 2 | 🔄 Growing |
| **Total** | **47** | **18.8%** |

---

Crafted with Python. Powered by curiosity. Open-sourced for learning. ⚡