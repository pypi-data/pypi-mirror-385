from dataclasses import dataclass
from parsesafe import combinators as c
from parsesafe.err import iserr
from parsesafe.advancer import Advancer
import operator as op

def test_string():
    assert c.string("bob").parse("bob") == "bob"
    assert c.string("yghuijfs324").parse("yghuijfs324") == "yghuijfs324"
    assert iserr(c.string("bob").parse("bob bob"))


def test_regex():
    assert c.regex(r"\w+ \d.\d\d").parse("abcdefg 3.14") == "abcdefg 3.14"
    assert c.regex(r"\w\d").parse("a1") == "a1"
    assert iserr(c.regex(r"\w\d").parse(" a1"))
    assert iserr(c.regex(r"\w\d").parse("a1a1"))

def test_otherwise():
    assert (c.regex(r"\d.\d\d") | c.string("bob")).parse("3.14") == "3.14"
    assert (c.regex(r"\d.\d\d") | c.string("bob")).parse("bob") == "bob"
    assert iserr((c.regex(r"\d.\d\d") | c.string("bob")).parse("3.145"))

def test_postignore():
    assert iserr(c.regex(r"d.\d\d").parse("3.14    "))
    assert c.regex(r"\d.\d\d").postignore(c.regex(r"\s+")).parse("3.14   ") == "3.14"
    assert c.regex(r"\w\d").postignore(c.string("\n")).parse("a1\n") == "a1"
def test_preignore():
    assert iserr(c.regex(r"d.\d\d").parse("    3.14"))
    assert c.regex(r"\d.\d\d").preignore(c.regex(r"\s+")).parse("     3.14") == "3.14"

def test_as_token():
    string = "hello good\n   friend  "
    result = c.regex(r"\w+").as_token().postignore(c.regex(r"[\s\n\r]+")).times().parse(string)
    assert not iserr(result)
    assert result == [
        c.Token("hello", c.Span(0,5)),
        c.Token("good", c.Span(6,10)),
        c.Token("friend", c.Span(string.find("friend"),string.find("friend") + len("friend")))]

def test_as_token_with_postignore_first():
    string = "hello good\n   friend  "
    result = c.regex(r"\w+").postignore(c.regex(r"[\s\n\r]+")).as_token().times().parse(string)
    assert not iserr(result)
    assert result == [
        c.Token("hello", c.Span(0,6)),
        c.Token("good", c.Span(6, string.find("friend"))),
        c.Token("friend", c.Span(string.find("friend"), len(string)))]

def test_seq():
    @c.combinator
    def number(seq: Advancer[int]):
        return seq.advance(1), seq[0]
    
    assert number.parse([1]) == 1
    assert number.seq(number).parse([1,2]) == 3

    comb = c.regex(r"\d+") + c.string(".")
    assert comb.parse("123.") == "123."
    assert iserr(comb.parse("123"))
    assert iserr(comb.parse("."))
    
    comb = comb + c.regex(r"\d+")
    assert comb.parse("123.8") == "123.8"
    assert iserr(comb.parse("123. 8"))
    

def test_cons():
    comb = c.string("d").cons(c.regex(r"\d+").map(int))
    assert comb.parse("d198") == ("d", 198)
    assert iserr(comb.parse("dd"))
    assert iserr(comb.parse("198"))

def test_append():
    comb = c.string("d").cons(c.regex(r"\d+").map(int)).append(c.string("d"))
    assert comb.parse("d654d") == ("d", 654, "d")
    assert iserr(comb.parse("d"))
    assert iserr(comb.parse("198"))
    assert iserr(comb.parse("d198"))
    assert iserr(comb.parse("198"))

def test_and():
    comb = c.regex(r"\d+").map(int) & c.regex(r"[a-g]+")

    assert comb.parse("123dadgad") == (123, "dadgad")

    comb = c.regex(r"\d+").map(int) & c.regex(r"[a-g]+") & c.regex(r"True|False").map(lambda x: x == "True")
    assert comb.parse("123dadgadTrue") == (123, "dadgad", True)
    assert comb.parse("123dadgadFalse") == (123, "dadgad", False)

def test_build():
    @dataclass
    class User:
        name: str
        height: float
        age: int

    comb = c.build(User, str,
                   c.regex_groups(r"\s*(\w+)\s+").map(lambda g: g[0]).lie,
                   age=c.regex(r"\d+\s+").map(int).lie,
                   height=c.regex(r"(\d*\.)?\d+\s*").map(float).lie)

    assert comb.parse("Fredrick 28 6.5") == User("Fredrick", 6.5, 28)

def test_expression():
    space = c.regex(r"\s*")
    expr = c.forward(str, float, "Expression")
    term = c.forward(str, float, "Term")
    fac = c.forward(str, float, "Factor")
    num = c.regex(r"(\d*\.)?\d+").map(float)

    expr.define(
        term.postignore(space)
        .cons(c.string("+").map(lambda x: op.add) | c.string("-").map(lambda x: op.sub))
        .postignore(space)
        .append(expr)
        .map(lambda x: x[1](x[0],x[2]))
        | term
    )
    term.define(
        fac.postignore(space)
        .cons(c.string("*").map(lambda x: op.mul) | c.string("/").map(lambda x: op.truediv))
        .postignore(space)
        .append(term)
        .map(lambda x: x[1](x[0],x[2]))
        | fac
        )
    fac.define(
        c.string("(")
        .postignore(space)
        .cons(expr)
        .postignore(space)
        .after(c.string(")"))
        .map(lambda x: x[1])
        | num
    )
    assert num.parse("12") == 12
    assert expr.parse("12") == 12
    assert expr.parse("12 +8/2") == 16




    
