
steps = []

def bubblesort(arr) -> list:
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
        steps.append(arr.copy())
    return arr

def get_steps() -> list:
    return steps    