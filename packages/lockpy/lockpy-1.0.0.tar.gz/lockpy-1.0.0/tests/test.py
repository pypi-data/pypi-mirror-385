import pytest
from lockpy import singleton, private

def test_singleton():
    @singleton
    class A:
        pass

    a1 = A()
    a2 = A()
    assert a1 is a2

def test_private():
    class A:
        @private
        def _secret(self):
            return 42

        def call(self):
            return self._secret()

    a = A()
    assert a.call() == 42

    with pytest.raises(RuntimeError):
        a._secret()
