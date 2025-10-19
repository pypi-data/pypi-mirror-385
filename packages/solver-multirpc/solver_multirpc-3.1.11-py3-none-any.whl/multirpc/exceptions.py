from multirpc.tx_trace import TxTrace

BaseException_ = Exception


class Web3InterfaceException(BaseException_):
    def __str__(self):
        if not self.args:
            return f"{self.__class__.__name__}()"
        return f"{self.__class__.__name__}({self.args[0]})"


class OutOfRangeTransactionFee(Web3InterfaceException):
    pass


class FailedOnAllRPCs(Web3InterfaceException):
    pass


class ViewCallFailed(Web3InterfaceException):
    pass


class TransactionFailedStatus(Web3InterfaceException):
    def __init__(self, hex_tx_hash, func_name=None, func_args=None, func_kwargs=None, trace=None):
        self.hex_tx_hash = hex_tx_hash
        self.func_name = func_name
        self.func_args = func_args
        self.func_kwargs = func_kwargs
        self.trace: TxTrace = trace

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        ret = (f'{self.__class__.__name__}({self.hex_tx_hash}, {self.func_name=}, '
                f'{self.func_args=}, {self.func_kwargs=})')
        if self.trace and self.trace.ok():
            main_error = self.trace.result().first_usable_error()
            ret += f' {main_error=}'

        return ret


class FailedToGetGasPrice(Web3InterfaceException):
    pass


class MaximumRPCInEachBracketReached(Web3InterfaceException):
    pass


class AtLastProvideOneValidRPCInEachBracket(Web3InterfaceException):
    pass

class AllRPCShouldSupportFlashBlockOrNot(Web3InterfaceException):
    pass


class TransactionValueError(Web3InterfaceException):
    pass


class GetBlockFailed(Web3InterfaceException):
    pass


class DontHaveThisRpcType(Web3InterfaceException):
    pass


class NotValidViewPolicy(Web3InterfaceException):
    pass


class TransactionTypeNotSupportedInMultiCall(Web3InterfaceException):
    pass


class KwargsNotSupportedInMultiCall(Web3InterfaceException):
    pass


class FailedToGetGasFromApi(Web3InterfaceException):
    pass
