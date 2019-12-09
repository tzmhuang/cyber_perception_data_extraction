DTYPE = ['1', 'sbg']

def test_func():
    a = 'sbg1'
    assert a in DTYPE, "Error: %s"%(DTYPE)
    return


if __name__ == "__main__":
    test_func()