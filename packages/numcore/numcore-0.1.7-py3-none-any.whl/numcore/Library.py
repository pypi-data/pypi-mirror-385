# Day 1
def n_input(n):
    """
    Take n integers as input from the user and return them as a list.
    
    Args:
        n (int): Number of integers to input
        
    Returns:
        list: List of n integers entered by user
    """
    numbers = []
    for i in range(1, n + 1):
        while True:
            try:
                value = int(input(f"Enter integer {i}: "))
                numbers.append(value)
                break
            except ValueError:
                print("Invalid input. Please enter an integer.")
    return numbers

# Day 2

def counter(lst):
    """
    Count occurrences of each item in a list.
    
    Args:
        lst (list): Input list
        
    Returns:
        dict: Dictionary with items as keys and their counts as values
        
    Example:
        >>> counter([1, 2, 3, 1, 2, 1])
        {1: 3, 2: 2, 3: 1}
    """
    item_count = {}
    for item in lst:
        if item in item_count:
            item_count[item] += 1
        else:
            item_count[item] = 1
    return item_count

# Day 3

def mean(lst):
    """
    Calculate the average of a list.
    
    Args:
        lst (list): List of numbers
        
    Returns:
        float: Mean value
        
    Example:
        >>> mean([1, 2, 3, 4, 5])
        3.0
    """
    if not lst:
        raise ValueError("Cannot calculate mean of empty list")
    return sum(lst)/len(lst)

def median(lst):
    """
    Calculate the median of a list.
    
    Args:
        lst (list): List of numbers
        
    Returns:
        float: Median value
        
    Example:
        >>> median([1, 2, 3, 4, 5])
        3.0
    """
    if not lst:
        raise ValueError("Cannot calculate median of empty list")
    sorted_list = sorted(lst)
    n = len(lst)
    if n % 2 == 1:  # Odd number of elements
        return sorted_list[n // 2]
    else:  # Even number of elements
        middle1 = sorted_list[n // 2 - 1]
        middle2 = sorted_list[n // 2]
        return (middle1 + middle2) / 2 

def mode(lst):
    """
    Calculate the mode of a list.
    
    Args:
        lst (list): List of numbers
        
    Returns:
        list: List of mode values (can be multiple if there's a tie)
        
    Example:
        >>> mode([1, 2, 3, 4, 5])
        [1,2,3,4,5]
        >>> mode([1, 1, 2, 2, 3])
        [1, 2]
    """
    if not lst:
        raise ValueError("Cannot calculate mode of empty list")
    data = counter(lst)
    mode_counter = max(data.values())
    return [name for name, amount in data.items() if amount == mode_counter]

def variance(lst, sample=False):
    """
    Calculate variance of a list.
    
    Args:
        lst (list): List of numbers
        sample (bool): If True, uses sample variance (n-1). Default is False (population variance)
        
    Returns:
        float: Variance value
        
    Example:
        >>> variance([1, 2, 3, 4, 5])  # Population
        2.0
        >>> variance([1, 2, 3, 4, 5], sample=True)  # Sample
        2.5
    """
    if not lst:
        raise ValueError("Cannot calculate variance of empty list")
    m = mean(lst)
    n = len(lst) - 1 if sample else len(lst)
    return sum((x - m) ** 2 for x in lst) / n

def std(lst,sample=False):
    """
    Calculate standard deviation of a list.
    
    Args:
        lst (list): List of numbers
        sample (bool): If True, uses sample std (n-1). Default is False (population std)
        
    Returns:
        float: Standard Deviation value
        
    Example:
        >>> std([1, 2, 3, 4, 5])  # Population
        2.0
        >>> std([1, 2, 3, 4, 5], sample=True)  # Sample
        2.5
    """
    if not lst:
        raise ValueError("Cannot calculate std of empty list")
    var = variance(lst,sample)
    return var**0.5

def analyze_list(lst):
    """
    Comprehensive statistical analysis of a numerical list.
    
    Args:
        lst (list): List of numbers
        
    Returns:
        dict: Dictionary containing various statistical measures
        
    Example:
        >>> analyze_list([1, 2, 3, 4, 5])
        {
            'count': 5,
            'sum': 15,
            'min': 1,
            'max': 5,
            'mean': 3.0,
            'median': 3,
            'mode': 1,
            'range': 4,
            'variance': 2.0,
            'std': 1.414...,
            'unique_count': 5,
            'frequency': {1: 1, 2: 1, 3: 1, 4: 1, 5: 1}
        }
    """
    if not lst:
        raise ValueError("Cannot analyze empty list")
    return {
        'count': len(lst),
        'sum': sum(lst),
        'min': min(lst),
        'max': max(lst),
        'mean': mean(lst),
        'median': median(lst),
        'mode': mode(lst),
        'range': max(lst) - min(lst),
        'variance': {
            'population variance': variance(lst),
            'sample variance': variance(lst, True)
        },
        'std':{
            'population std': std(lst),
            'sample std': std(lst, True)
        },
        'unique_count': len(set(lst)),
        'frequency': counter(lst)
    }

def product(lst):
    """
    Multiply all numbers in a list.
    
    Args:
        lst (list): List of numbers
        
    Returns:
        float/int: Product of all numbers
        
    Example:
        >>> product([2, 3, 4])
        24
    """
    if not lst:
        raise ValueError("Cannot multiply empty list")
    p = 1
    for i in lst:
        p *= i
    return p

def nth_root(num, n, tol=1e-9):
    """
    Calculate nth root of a number.
    
    Args:
        num (float): The number
        n (int): The root
        tolerence (flaot): Tolerence for floating point precision
        
    Returns:
        float: nth root value

    Example:
        >>> nth_root(729,3)
        729 ^ (1/3) = 9.0
    
    """
    if n == 0:
        raise ValueError("Cannot calculate 0th root")
    if num < 0 and n % 2 == 0:
        raise ValueError("Cannot calculate even root of negative number")
    result = num ** (1/n)
    nearest = round(result)
    if abs(result - nearest) < tol:
        return float(nearest)
    return result

def factorial(num):
    """
    Calculate factorial a number (n!).
    
    Args:
        num (int): The number
        
    Returns:
        int: Factorial of the number. 
    
    Example:
        >>> factorial(6)
        720
    
    """
    if num < 0:
        raise ValueError("Cannot calculate factorial of negative integer")
    f = 1
    for i in range(1, num + 1):
        f *= i
    return f

def divisors(num):
    """
    Find all divisors of a number
    
    Args:
        num (int): The number
        
    Returns:
        lst (List): List of all the divisors.

    Example:
        >>> divisors(100)
        [1, 2, 4, 5, 10, 20, 25, 50, 100]
     
    """
    divisors_list = []
    for i in range (1, int(num**0.5)+1):
        if num % i == 0:
            divisors_list.append(i)
            if i != num//i:
                divisors_list.append(num // i)
    return sorted(divisors_list)

def common_divisors(num1, num2):
    """
    Find all the common divisors of two numbers
    
    Args:
        num1 (int): First number
        num2 (int): Second number
        
    Returns:
        lst (List): List of all the common divisors of num1 and num2. 

    Example:
        >>> common_divisors(48, 18)
        [1,2,3,6]
    """
    common = []
    divisors_1 = divisors(num1)
    divisors_2 = divisors(num2)
    for i in divisors_1:
        if i in divisors_2:
            common.append(i)
    return common

def gcd(num1, num2):
    """
    Calculate Greatest Common Divisor using Euclidean algorithm.
    
    Args:
        num1 (int): First number
        num2 (int): Second number
        
    Returns:
        int: GCD value
        
    Example:
        >>> gcd(48, 18)
        6
    """
    while num2:
        num1, num2 = num2, num1 % num2
    return num1

def lcm(num1, num2):
    """
    Calculate Least Common Multiple.
    
    Args:
        num1 (int): First number
        num2 (int): Second number
        
    Returns:
        int: LCM value
        
    Example:
        >>> lcm(12, 18)
        36
    """
    return int((num1*num2)/gcd(num1, num2))

def is_prime(num):
    """
    Check if a number is prime.
    
    Args:
        num (int): Number to check
        
    Returns:
        bool: True if prime, False otherwise

    Example:
        >>> is_prime(11)
        True
        >>> is_prime(21)
        False
    """
    if num < 2:
        return False
    if num == 2 or num == 3 :
        return True
    for i in range (2, int(num**0.5) + 1):
        if num % i == 0:
            return False
    return True
        
def primes(num):
    """
    Find all the primes till given number.
    
    Args:
        num (int): Number to check
        
    Returns:
        lst (List): List of all the primes till given number

    Example:
        >>> primes(25)
        [2, 3, 5, 7, 11, 13, 17, 19, 23]
    """
    primes_till = []
    for i in range(1,num+1):
        if is_prime(i):
            primes_till.append(i)
    return primes_till

def prime_divisors(num):
    """
    Find all the primes divisors of a number.
    
    Args:
        num (int): Number to check
        
    Returns:
        lst (List): List of all the primes divisors of number.

    Example:
        >>> prime_divisors(30)
        [2, 3, 5]
    """
    prime_div = []
    for i in primes(num):
        if i in divisors(num):
            prime_div.append(i)
    return prime_div

def prime_factorization(num):
    """
    Find prime factorization of a number.
    
    Args:
        num (int): Number to check
        
    Returns:
        lst (List): List of prime factorization method.

    Example:
        >>> prime_factorization(100)
        [2, 2, 5, 5]
    """
    prime_factors = []
    number = num
    for i in primes(num):
        while number % i == 0:
            prime_factors.append(i)
            number //= i
        if number == 1:
            break
    return prime_factors

def prime_factors(num):
    """
    Find all the prime factors of a number.
    
    Args:
        num (int): Number to check
        
    Returns:
        lst (List): List of all prime factors of number.

    Example:
        >>> prime_factors(100)
        [2, 5]
    """
    return list(set(prime_factorization(num)))

def is_perfect(num):
    """
    Check if a number is a perfect number. (sum of divisors = number)
    
    Args:
        num (int): Number to check
        
    Returns:
        bool: True if perfect, False otherwise

    Example:
        >>> is_perfect(6)
        True
        >>> is_perfect(15)
        False
    """
    return sum(divisors(num)) == 2 * num

def input_matrix():
    """
    Get a matrix from user input (interactive).
    
    Returns:
        list: Matrix as 2D list
        
    Example:
        >>> mat = input_matrix()
        Enter number of rows: 2
        Enter number of columns: 2
        Enter element a11: 1
        Enter element a12: 2
        Enter element a21: 3
        Enter element a22: 4
        >>> print(mat)
        [[1, 2], [3, 4]]
    """
    rows = int(input("Enter number of rows: "))
    cols = int(input("Enter number of columns: "))
    
    matrix = []
    print(f"\nEnter elements for {rows} x {cols} matrix:")
    
    for i in range(rows):
        row = []
        for j in range(cols):
            val = float(input(f"Enter element a{i+1}{j+1}: "))
            row.append(val)
        matrix.append(row)
    
    return matrix

def create_matrix(rows, cols, fill=0):
    """
    Create a matrix of given dimensions filled with a value.
    
    Args:
        rows (int): Number of rows
        cols (int): Number of columns
        fill: Value to fill matrix with (default 0)
        
    Returns:
        list: 2D list representing the matrix
        
    Example:
        >>> create_matrix(2, 3)
        [[0, 0, 0], [0, 0, 0]]
        
        >>> create_matrix(2, 2, fill=5)
        [[5, 5], [5, 5]]
    """
    matrix = []
    for i in range(rows):
        row = []
        for j in range(cols):
            row.append(fill)
        matrix.append(row)
    
    return matrix

def matrix_shape(matrix):
    """
    Get the dimensions of a matrix.
    
    Args:
        matrix (list): 2D list representing a matrix
        
    Returns:
        tuple: (rows, cols) dimensions
        
    Example:
        >>> matrix_shape([[1, 2, 3], [4, 5, 6]])
        (2, 3)
    """
    if not matrix:
        raise ValueError("Cannot get shape of empty matrix")
    
    rows = len(matrix)
    cols = len(matrix[0])
    
    for i in range(rows):
        if len(matrix[i]) != cols:
            raise ValueError(f"Invalid matrix: row {i} has {len(matrix[i])} elements, expected {cols}")
    
    return rows, cols

def matrix_add(mat1, mat2):
    """
    Add two matrices element-wise.
    
    Args:
        mat1 (list): First matrix
        mat2 (list): Second matrix
        
    Returns:
        list: Sum of matrices
        
    Example:
        >>> matrix_add([[1,2],[3,4]], [[5,6],[7,8]])
        [[6, 8], [10, 12]]
    """

    if matrix_shape(mat1) != matrix_shape(mat2):
        raise ValueError("Cannot add two matrix with different dimensions.")
    rows = len(mat1)
    cols = len(mat1[0])
    result = create_matrix(rows, cols, 0)

    for i in range(rows):
        for j in range(cols):
            result[i][j] = mat1[i][j] + mat2[i][j]

    return result

def matrix_sub(mat1, mat2):
    """
    Subtract two matrices element-wise.
    
    Args:
        mat1 (list): First matrix
        mat2 (list): Second matrix
        
    Returns:
        list: Difference of matrices
        
    Example:
        >>> matrix_sub([[1,2],[3,4]], [[5,6],[7,8]])
        [[-4, -4], [-4, -4]]
    """
    if matrix_shape(mat1) != matrix_shape(mat2):
        raise ValueError("Cannot subtract two matrix with different dimensions.")
    rows = len(mat1)
    cols = len(mat1[0])
    result = create_matrix(rows, cols, 0)

    for i in range(rows):
        for j in range(cols):
            result[i][j] = mat1[i][j] - mat2[i][j]

    return result

def scalar_multiply(matrix, scalar):
    """
    Multiply a matrix by a scalar (single number).
    
    Args:
        matrix (list): 2D list representing a matrix
        scalar (int/float): Scalar to be multiplied with matrix
        
    Returns:
        list: Multiplication of a scalar with matrix
        
    Example:
        >>> scalar_multiply([[1, 2, 3], [4, 5, 6]], 5)
        [[5, 10, 15], [20, 25, 30]]
    """
    if not matrix:
        raise ValueError("Cannot multiply empty matrix")
    
    rows, cols = matrix_shape(matrix)
    result = create_matrix(rows, cols, 0) 
    
    for i in range(rows):
        for j in range(cols):
            result[i][j] = matrix[i][j] * scalar  
    
    return result

def matrix_multiply(mat1, mat2):
    """
    Multiply two matrices.
    
    Args:
        mat1 (list): First matrix
        mat2 (list): Second matrix
        
    Returns:
        list: Multiplication of matrices
        
    Example:
        >>> matrix_multiply([[1,2],[3,4]], [[5,6],[7,8]])
        [[19, 22], [43, 50]]
    """
    rows1, cols1 = matrix_shape(mat1)
    rows2, cols2 = matrix_shape(mat2)

    if cols1 != rows2:
        raise ValueError("Cannot multiply matrices; number of columns in Matrix 1 must equal the number of rows in Matrix 2.")
    
    result = create_matrix(rows1, cols2, 0)
    for i in range(rows1):
        for j in range(cols2):
            for k in range(cols1):
                result[i][j] += mat1[i][k] * mat2[k][j]\
                
    return result

def matrix_identity(rows):
    """
    Create an identity matrix.
    
    Args:
        rows (int): Size of square identity matrix
        
    Returns:
        list: Identity matrix (1s on diagonal, 0s elsewhere)
        
    Example:
        >>> matrix_identity(3)
        [[1, 0, 0],
         [0, 1, 0],
         [0, 0, 1]]
    """
    identity = create_matrix(rows, rows, 0)
    for i in range(rows):
        identity[i][i] = 1
    return identity

def is_square(matrix):
    """
    Check if matrix is a square matrix (order: n x n).
    
    Args:
        matrix (list): 2D list representing a matrix
        
    Returns:
        Bool: True if matrix is square, else False
        
    Example:
        >>> is_square([[1, 0, 0],[0, 1, 0],[0, 0, 1]])
        True
        >>> is_square([[1,2,3],[4,5,6]])
        False
    """
    rows, cols = matrix_shape(matrix)
    return rows == cols

def matrix_trace(matrix):
    """
    Calculate trace of matrix (Sum of diagonal elements/Sum of Eigen Values).
    
    Args:
        matrix (list): 2D list representing a matrix
        
    Returns:
        int: Trace of matrix
        
    Example:
        >>> matrix_trace([[1, 0, 0],[0, 1, 0],[0, 0, 1]])
        3
    """
    if not is_square(matrix):
        raise ValueError("Trace is only defined for square matrices.")
    trace = 0
    rows, cols = matrix_shape(matrix)
    for i in range(rows):
        trace += matrix[i][i]
    return trace

def matrix_transpose(matrix):
    """
    Calculate transpose of matrix (Interchanging rows with cols).
    
    Args:
        matrix (list): 2D list representing a matrix
        
    Returns:
        list: Transpose of matrix
        
    Example:
        >>> matrix_transpose([[1, 2, 3],[4, 5, 6],[7, 8, 9]])
        [[1, 4, 7], [2, 5, 8], [3, 6, 9]]
        
    """
    rows, cols = matrix_shape(matrix)
    transpose = create_matrix(cols, rows, 0)

    for i in range(cols):
        for j in range(rows):
            transpose[i][j] = matrix[j][i]

    return transpose

def is_orthogonal(matrix, tol=1e-8):
    """
    Check if matrix is orthogonal or not. (A.A^T = I).
    
    Args:
        matrix (list): 2D list representing a matrix
        tol (float): tolerence for floating point precision (default: tol=1e-8)
        
    Returns:
        Bool: True if matrix is orthogonal, else False
        
    Example:
        >>> is_orthogonal([[-2/3,1/3,2/3],[2/3,2/3,1/3],[1/3,-2/3,2/3]])
        True
        >>> is_orthogonal([[1, 2, 3],[4, 5, 6],[7, 8, 9]])
        False
    """
    if tol < 0:
        raise ValueError("Tolerance must be non-negative.")
    
    if not is_square(matrix):
        raise ValueError("Orthogonal Matrices are defined only for square matrices.")
    
    rows, cols = matrix_shape(matrix)
    identity = matrix_identity(rows)
    product = matrix_multiply(matrix, matrix_transpose(matrix))

    for i in range(rows):
        for j in range(cols):
            if abs(product[i][j] - identity[i][j]) > tol:
                return False
    return True

def determinant(matrix):
    """
    Calculate determinant of a matrix
    
    Args:
        matrix (list): 2D list representing a matrix
        
    Returns:
        float: Determinant of a matrix.
        
    Example:
        >>> determinant([[1,0,0],[1,2,3],[9,8,7]])
        -10
    """
    if not is_square(matrix):
        raise ValueError("Determinant is only defined for square matrices.")
    rows, cols = matrix_shape(matrix)

    if rows == 1:
        return matrix[0][0]

    if rows == 2:
        return matrix[0][0]*matrix[1][1]-matrix[0][1]*matrix[1][0]
    
    det = 0
    for c in range(cols):
        mat = []
        for r in range(1,rows):
            row = []
            for j in range(cols):
                if j!=c:
                    row.append(matrix[r][j])
            mat.append(row)
        
        det += ((-1)**c) * (matrix[0][c]) * determinant(mat) 
    
    return round(det,10)

def matrix_minor(matrix):
    """
    Calculate minor matrix of a matrix (formed by replacing elements by minor of that element)
    
    Args:
        matrix (list): 2D list representing a matrix
        
    Returns:
        list: Minor matrix of the matrix
        
    Example:
        >>> matrix_minor([[1,2,3],[4,5,6],[7,8,9]])
        [[-3, -6, -3], [-6, -12, -6], [-3, -6, -3]]
    """
    if not is_square(matrix):
        raise ValueError("Minor of an element is defined only for square matricces.")
    
    rows,cols = matrix_shape(matrix)
    minor = create_matrix(rows, cols, 0)

    for r in range(rows):
        for c in range(cols):
            mat = []
            for i in range(rows):
                if i != r:
                    row = []
                    for j in range(cols):
                        if j != c:
                            row.append(matrix[i][j])
                    mat.append(row)
            minor[r][c] = determinant(mat)

    return minor

def matrix_cofactor(matrix):
    """
    Calculate cofactor matrix of a matrix (formed by replacing elements by cofactor of that element)
    
    Args:
        matrix (list): 2D list representing a matrix
        
    Returns:
        list: Cofactor matrix of the matrix
        
    Example:
        >>> matrix_cofactor([[1,2,3],[4,5,6],[7,8,9]])
        [[-3, 6, -3], [6, -12, 6], [-3, 6, -3]]
    """
    if not is_square(matrix):
        raise ValueError("Cofactor of an element is defined only for square matricces.")
    
    rows,cols = matrix_shape(matrix)
    cofactor = create_matrix(rows, cols, 0)

    for r in range(rows):
        for c in range(cols):
            mat = []
            for i in range(rows):
                if i != r:
                    row = []
                    for j in range(cols):
                        if j != c:
                            row.append(matrix[i][j])
                    mat.append(row)
            cofactor[r][c] = ((-1)**(r+c)) * determinant(mat)

    return cofactor

def matrix_power(matrix, power):
    """
    Calculate higher power of a matrix
    
    Args:
        matrix (list): 2D list representing a matrix
        power (int): Positive Integer 
        
    Returns:
        list: nth (int) power of matrix
        
    Example:
        >>> matrix_power([[1,2,3],[4,5,6],[7,8,9]], 2)
        [[30, 36, 42], [66, 81, 96], [102, 126, 150]]
    """
    if not isinstance(power, int):
        raise ValueError("Power must be an integer.")
    if not is_square(matrix):
        raise ValueError("Cannot calculate higher power of non-square matrices")
    if power < 0:
        raise ValueError("Can only calcualate positive integral powers of matrix.")
    
    i = 0
    product = matrix_identity(len(matrix))
    while i < power:
        product = matrix_multiply(product, matrix)
        i+=1

    return product

def digits(num):
    """
    Extract all digits from a number as a list.
    
    Args:
        num (int): The number to extract digits from
        
    Returns:
        list: List of digits in order
        
    Example:
        >>> digits(12345)
        [1, 2, 3, 4, 5]
        >>> digits(100)
        [1, 0, 0]
    """
    digits = []
    while num > 0:
        digit = num % 10
        digits.append(digit)
        num = num // 10
    digits.reverse()
    return digits

def reverse_number(num):
    """
    Reverse the digits of a number.
    
    Args:
        num (int): Number to reverse
        
    Returns:
        int: Number with reversed digits
        
    Example:
        >>> reverse_number(12345)
        54321
        >>> reverse_number(100)
        1
    """
    digit = digits(num)
    digit.reverse()
    rev = ""
    for i in digit:
        rev += str(i)
    return int(rev)

def sum_of_digits(num):
    """
    Calculate the sum of all digits in a number.
    
    Args:
        num (int): Number to sum digits of
        
    Returns:
        int: Sum of all digits
        
    Example:
        >>> sum_of_digits(12345)
        15  # 1+2+3+4+5
        >>> sum_of_digits(999)
        27  # 9+9+9
    """
    return sum(digits(num))

def power_list(lst, power):
    """
    Apply a power to each element in a list.
    
    Args:
        lst (list): List of numbers
        power (int): Power to raise each element to
        
    Returns:
        list: New list with each element raised to the power
        
    Example:
        >>> power_list([1, 2, 3], 2)
        [1, 4, 9]
        >>> power_list([2, 3, 4], 3)
        [8, 27, 64]
    """
    result = []
    for i in lst:
        result.append(i**power)
    return result

def is_armstrong(num):
    """
    Check if a number is an Armstrong number (narcissistic number).
    An Armstrong number is equal to the sum of its digits each raised 
    to the power of the number of digits.
    
    Args:
        num (int): Number to check
        
    Returns:
        bool: True if Armstrong number, False otherwise
        
    Example:
        >>> is_armstrong(153)
        True  # 1³ + 5³ + 3³ = 1 + 125 + 27 = 153
        >>> is_armstrong(370)
        True  # 3³ + 7³ + 0³ = 27 + 343 + 0 = 370
        >>> is_armstrong(123)
        False
    """
    digit = digits(num)
    power = len(digit)
    return sum(power_list(digit, power)) == num

def proper_divisors(num):
    """
    Find all proper divisors of a number (all divisors except the number itself).
    
    Args:
        num (int): Number to find proper divisors of
        
    Returns:
        list: Sorted list of proper divisors
        
    Example:
        >>> proper_divisors(12)
        [1, 2, 3, 4, 6]
        >>> proper_divisors(28)
        [1, 2, 4, 7, 14]
    """
    divisor = divisors(num)
    divisor.sort()
    divisor.pop(-1)
    return divisor

def is_amicable(a, b):
    """
    Check if two numbers form an amicable pair.
    Two numbers are amicable if the sum of proper divisors of each 
    equals the other number.
    
    Args:
        a (int): First number
        b (int): Second number
        
    Returns:
        bool: True if amicable pair, False otherwise
        
    Example:
        >>> is_amicable(220, 284)
        True  # sum of divisors of 220 = 284, sum of divisors of 284 = 220
        >>> is_amicable(1184, 1210)
        True
        >>> is_amicable(100, 200)
        False
    """
    sum_a, sum_b = sum(proper_divisors(a)), sum(proper_divisors(b))
    return a == sum_b and b == sum_a

def fibonacci(num):
    """
    Generate Fibonacci sequence up to nth number.
    
    Args:
        num (int): How many Fibonacci numbers to generate
        
    Returns:
        list: Fibonacci sequence
        
    Example:
        >>> fibonacci(7)
        [0, 1, 1, 2, 3, 5, 8]
    """
    if num <= 0:
        return []
    if num == 1:
        return [0]
    fibo = [0, 1]
    for i in range(3,num+1):
        fibo.append(fibo[-1] + fibo[-2])
    return fibo

def nth_fibonacci(num):
    """
    Get the nth Fibonacci number.
    
    Args:
        num (int): Position in Fibonacci sequence (1-indexed)
        
    Returns:
        int: The nth Fibonacci number
        
    Example:
        >>> nth_fibonacci(1)
        0
        >>> nth_fibonacci(7)
        8
    """
    if num <= 0:
        raise ValueError("Position must be positive")
    return (fibonacci(num))[-1]
