# a = {}
# b = a
# b[1]={}
# b = b[1]
# b[2]=2
# print(a)
# print(b)

class A():
    def __init__(self, a):
        print(a)

    def get_a(self):
        a = A(1)

if __name__ == '__main__':
    c = A(2)
    c.get_a()
