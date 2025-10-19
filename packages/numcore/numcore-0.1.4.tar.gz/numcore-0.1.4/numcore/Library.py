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

def nth_root(num, n):
    """
    Calculate nth root of a number.
    
    Args:
        num (float): The number
        n (int): The root
        
    Returns:
        float: nth root value

    Example:
        >>> nth_root(729,3)
        729 ^ (1/3) = 8.999999999999998
    
    """
    if n == 0:
        raise ValueError("Cannot calculate 0th root")
    if num < 0 and n % 2 == 0:
        raise ValueError("Cannot calculate even root of negative number")
    return num ** (1/n)

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
