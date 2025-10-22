def bmi(weight, height):
    return weight / (height**2 / 10000)


def toweight(bmi_value, height):
    return bmi_value * (height**2 / 10000)


if __name__ == "__main__":
    w = toweight(20, 163)
    print(w)
