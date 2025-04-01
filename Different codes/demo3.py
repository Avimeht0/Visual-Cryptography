import random

def generate_random_functions(n, k):
    """Generate a collection of random functions mapping {1..n} -> {1..k}."""
    print(f"Generating {n * k} random functions for n={n}, k={k}...")
    
    # Generate the list of lambda functions
    func_list = [lambda x, k=k: random.randint(0, k - 1) for _ in range(n * k)]
    
    print("Random functions generated successfully!")
    return func_list

# Example usage
if __name__ == "__main__":
    # Define parameters
    n = 2  # Total number of shares
    k = 3  # Minimum number of shares required for reconstruction

    # Generate random functions
    random_funcs = generate_random_functions(n, k)

    # Print the functions and their outputs
    print("\nTesting the random functions:")
    for i, func in enumerate(random_funcs):
        # Test the function with a sample input (e.g., x = 1)
        result = func(1)
        print(f"Function {i + 1}: Called with x=1, returned {result}")