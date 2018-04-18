import re

c_reg = "u'"


def category(data):
    p = re.compile(c_reg)
    m = p.search(data)
    return m.group

if __name__ == "__main__":
    exp = "u'\n\t\t\t\t\tFact Check '"
    print category(exp)
