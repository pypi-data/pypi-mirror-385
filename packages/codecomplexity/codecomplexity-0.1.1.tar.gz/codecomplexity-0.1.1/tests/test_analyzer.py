def complex_function(x, y, z):
    if x > 0:
        for i in range(y):
            if i % 2 == 0:
                while z > 0:
                    z -= 1
                    return z
    return 0