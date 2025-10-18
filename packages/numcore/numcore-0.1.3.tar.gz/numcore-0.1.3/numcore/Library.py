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
