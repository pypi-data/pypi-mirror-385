import pytest

from faster_eth_utils.toolz import (
    compose,
)

from faster_web3 import (
    Web3,
)
from faster_web3.method import (
    Method,
)
from faster_web3.module import (
    Module,
)
from faster_web3.providers import (
    BaseProvider,
)


def result_formatter(method, module):
    def formatter(self):
        return "OKAY"

    return compose(formatter)


class DummyProvider(BaseProvider):
    def make_request(method, params):
        raise NotImplementedError


result_for_test = {"method_for_test": "ok"}


class ModuleForTest(Module):
    method = Method("method_for_test", result_formatters=result_formatter)


@pytest.fixture
def dummy_w3():
    w3 = Web3(
        DummyProvider(),
        modules={"module": ModuleForTest},
    )
    return w3


def test_result_formatter(dummy_w3, request_mocker):
    with request_mocker(dummy_w3, mock_results=result_for_test):
        assert dummy_w3.module.method() == "OKAY"
