class NumberProperties:
    
    def is_even(self, number):
        remainder = number % 2
        if remainder == 0:
           return True
        else:
            return False
            
            
    def is_odd(self, number):
        remainder = number % 2
        if remainder != 0:
            return True
        else:
            return False


    def is_multiple_of_n(self, number, n):
        remainder = number % n
            if remainder == 0:
                    return True
                else:
                    return False
                    
                    
                    
if __name__ == '__main__':
    np = NumberProperties()
    number = 24
    n = 5
    print('\n{} is even?: {}'.format(number, np.is_even(number)))
    print('{} is odd?: {}'.format(number, np.is_odd(number)))
    property = np.is_multiple_of_n(number, n)
    print('{} is multiple of {}?: {}'.format(number, n, property))
    
    
    number = 25
    n = 5
    print('\n{} is even?: {}'.format(number, np.is_even(number)))
    print('{} is odd?: {}'.format(number, np.is_odd(number)))
    property = np.is_multiple_of_n(number, n)
    print('{} is multiple of {}?: {}'.format(number, n, property))
    
    
    number = 31
    n = 5
    print('\n{} is even?: {}'.format(number, np.is_even(number)))
    print('{} is odd?: {}'.format(number, np.is_odd(number)))
    property = np.is_multiple_of_n(number, n)
    print('{} is multiple of {}?: {}'.format(number, n, property))