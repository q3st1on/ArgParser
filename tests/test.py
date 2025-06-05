from ArgParser import ArgParser

class ParentClass:
    def __init__(self):
        pass

class ChildClass(ParentClass):
    def __init__(self):
        pass

class OtherClass:
    def __init__(self):
        pass

class TestClass:
    def __init__(self, *args, **kwargs):
        argParser = ArgParser()
        argParser.addPositionalArg("pos1", dtype = str, default = "value")
        argParser.addKeywordArg("kw1", dtype = ParentClass)
        argParser.addKeywordArg("kw2", subClass = ParentClass)
        argParser.addKeywordArg("kw3", min = 1, max = 1.1, default = 1.05)
        argParser.addKeywordArg("kw4", dtype = str, minLength = 2, maxLength = 4, default = "str")
        argParser.parseArgs(*args, **kwargs)
        
        self.pos1 = argParser.pos1
        self.kw1 = argParser.kw1
        self.kw2 = argParser.kw2
        self.kw3 = argParser.kw3
        self.kw4 = argParser.kw4

    def getParsedVals(self):
        return (self.pos1, self.kw1, self.kw2, self.kw3, self.kw4)    
    
def testDefaults():
    parentInstance = ParentClass()
    childInstance = ChildClass()
    test = TestClass(
        kw1 = parentInstance,
        kw2 = childInstance,
        kw3 = 1.065,
        )
    
    results = test.getParsedVals()

    assert results[0] == "value",           "pos1 parsed incorrectly"
    assert results[1] == parentInstance,    "kw1 parsed incorrectly"
    assert results[2] == childInstance,     "kw2 parsed incorrectly"
    assert results[3] == 1.065,             "kw3 parsed incorrectly"
    assert results[4] == "str",             "kw4 parsed incorrectly"

def testMin():
    parentInstance = ParentClass()
    childInstance = ChildClass()
    try:
        test = TestClass(
            kw1 = parentInstance,
            kw2 = childInstance,
            kw3 = 0.5,
            )
        raise Exception("Min condition not enforced correctly")
    except ValueError:
        pass

def testMax():
    parentInstance = ParentClass()
    childInstance = ChildClass()
    try:
        test = TestClass(
            kw1 = parentInstance,
            kw2 = childInstance,
            kw3 = 2,
            )
        raise Exception("Max condition not enforced correctly")
    except ValueError:
        pass

def testMinLength():
    parentInstance = ParentClass()
    childInstance = ChildClass()
    try:
        test = TestClass(
            kw1 = parentInstance,
            kw2 = childInstance,
            kw4 = "a"
            )
        raise Exception("Min Length condition not enforced correctly")
    except ValueError:
        pass

def testMaxLength():
    parentInstance = ParentClass()
    childInstance = ChildClass()
    try:
        test = TestClass(
            kw1 = parentInstance,
            kw2 = childInstance,
            kw4 = "aaaaa"
            )
        raise Exception("Max Length condition not enforced correctly")
    except ValueError:
        pass

def testDtype():
    parentInstance = ParentClass()
    childInstance = ChildClass()
    try:
        test = TestClass(
            kw1 = parentInstance,
            kw2 = childInstance,
            kw4 = 3
            )
        raise Exception("dtype condition not enforced correctly")
    except TypeError:
        pass

def testSubClass():
    parentInstance = ParentClass()
    otherInstance = OtherClass()
    try:
        test = TestClass(
            kw1 = parentInstance,
            kw2 = otherInstance,
            )
        raise Exception("dtype condition not enforced correctly")
    except TypeError:
        pass

def testKwargOverflow():
    parentInstance = ParentClass()
    childInstance = ChildClass()
    test = TestClass(
        "test",
        parentInstance,
        childInstance,
        1.065,
        "test"
        )
    
    results = test.getParsedVals()
    try:
        assert results[0] == "test",            "pos1 parsed incorrectly"
        assert results[1] == parentInstance,    "kw1 parsed incorrectly"
        assert results[2] == childInstance,     "kw2 parsed incorrectly"
        assert results[3] == 1.065,             "kw3 parsed incorrectly"
        assert results[4] == "test",            "kw4 parsed incorrectly"
    except AssertionError as e:
        print(results)
        raise type(e)(e)

def testPositionalArgCountEnforcement():
    parentInstance = ParentClass()
    childInstance = ChildClass()
    try:
        test = TestClass(
            "test",
            parentInstance,
            childInstance,
            1.065,
            "test",
            "Extra Arg"
            )
        raise Exception("Unexpected positional args not being handled correctly")
    except TypeError:
        pass

def testKeywordArgCountEnforcement():
    parentInstance = ParentClass()
    childInstance = ChildClass()
    try:
        test = TestClass(
            "test",
            kw1 = parentInstance,
            kw2 = childInstance,
            kw3 = 1.065,
            kw4 = "test",
            kw5 = "Extra Arg"
            )
        raise Exception("Unexpected keyword args not being handled correctly")
    except TypeError:
        pass

if __name__=="__main__":
    testDefaults()
    testMin()
    testMax()
    testMinLength()
    testMaxLength()
    testDtype()
    testSubClass()
    testKwargOverflow()
    testPositionalArgCountEnforcement()
    testKeywordArgCountEnforcement()
    print("All tests passed.")