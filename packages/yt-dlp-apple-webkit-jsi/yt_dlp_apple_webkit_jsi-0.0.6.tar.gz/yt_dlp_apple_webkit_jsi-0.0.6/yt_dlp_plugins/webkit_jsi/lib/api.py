import datetime as dt
import enum

from contextlib import AsyncExitStack, ExitStack
from ctypes import (
    CFUNCTYPE,
    POINTER,
    Structure,
    byref,
    c_bool,
    c_byte,
    c_char_p,
    c_double,
    c_int64,
    c_long,
    c_longlong,
    c_uint64,
    c_ulong,
    c_ulonglong,
    c_void_p,
    cast,
    string_at,
)
from dataclasses import dataclass
from threading import Condition
from types import CoroutineType
from typing import (
    Any,
    Awaitable,
    Callable,
    Coroutine,
    Generator,
    Generic,
    Optional,
    TypeVar,
    Union,
    cast as py_typecast,
    overload
)

from .pyneapple_objc import (
    CRet,
    NotNull_VoidP,
    NULLABLE_VOIDP,
    ObjCBlock,
    PyNeApple,
)
from .consts import SCRIPT_PHOLDER, SCRIPT_TEMPL
from .logging import AbstractLogger


T = TypeVar('T')
U = TypeVar('U')
V = TypeVar('V')


# TODO: support exceptions
class CFRL_Future(Awaitable[T]):
    __slots__ = '_cbs', '_done', '_result'

    def __init__(self):
        self._cbs: list[Callable[['CFRL_Future[T]'], None]] = []
        self._done = False
        self._result: Optional[T] = None

    def result(self) -> T:
        if not self._done:
            raise RuntimeError('result method called upon a future that is not yet resolved')
        return py_typecast(T, self._result)

    def add_done_callback(self, cb: Callable[['CFRL_Future[T]'], None]) -> None:
        if not self._done:
            self._cbs.append(cb)
        else:
            cb(self)

    def set_result(self, res: T) -> None:
        if self._done:
            raise RuntimeError('double resolve')
        self._result = res
        self._done = True
        for cb in self._cbs:
            cb(self)
        self._cbs.clear()

    def done(self) -> bool:
        return self._done

    def __await__(self) -> Generator[Any, Any, T]:
        if self._done:
            return py_typecast(T, self._result)
        else:
            return (yield self)


@dataclass
class CFRL_CoroResult(Generic[T]):
    ret: T
    rexc: Optional[BaseException] = None


class DoubleDouble(Structure):
    _fields_ = (
        ('x', c_double),
        ('y', c_double),
    )
    __slots__ = ()


class CGRect(Structure):
    _fields_ = (
        ('orig', DoubleDouble),
        ('size', DoubleDouble),
    )
    __slots__ = ()


NSUTF8StringEncoding = 4


@overload
def str_from_nsstring(pa: PyNeApple, nsstr: NotNull_VoidP) -> str: ...
@overload
def str_from_nsstring(pa: PyNeApple, nsstr: c_void_p, *, default: T = None) -> Union[str, T]: ...


def str_from_nsstring(pa: PyNeApple, nsstr: Union[c_void_p, NotNull_VoidP], *, default: T = None) -> Union[str, T]:
    if not nsstr.value:
        return default
    length = pa.send_message(nsstr, b'lengthOfBytesUsingEncoding:', NSUTF8StringEncoding, restype=c_ulong, argtypes=(c_ulong, ))
    if not length:
        assert pa.send_message(nsstr, b'canBeConvertedToEncoding:', NSUTF8StringEncoding, restype=c_byte, argtypes=(c_ulong, )), (
            'NSString cannot be losslessly converted to UTF-8 (which is impossible)')
        return ''
    return string_at(py_typecast(int, pa.send_message(nsstr, b'UTF8String', restype=c_void_p)), length).decode()


@dataclass
class _UnknownStructure:
    typename: str


class NullTag:
    ...


_JSResultType = Union[
    T,  # type[None], undefined
    U,  # type[None], null
    str,
    int,
    float,
    dt.datetime,
    dict['_JSResultType', '_JSResultType'],
    list['_JSResultType'],
    V,  # _UnkownStructure
]
DefaultJSResult = _JSResultType[None, type[NullTag], _UnknownStructure]

PyResultType = Union[
    None,
    int,
    float,
    str,
    dt.datetime
]

DarwinMinVer = (20, )

class WKJS_Task:
    NAVIGATE_TO = 0
    EXECUTE_JS = 1
    SHUTDOWN = 2
    NEW_WEBVIEW2 = 3
    FREE_WEBVIEW = 4
    ON_SCRIPTLOG2 = 5
    ON_SCRIPTCOMM2 = 6
    SET_LOGGER = 7


class WKJS_UncaughtException(Exception):
    DOMAIN_DEFAULT = '<unknown>'
    UINFO_DEFAULT = '<no description provided>'

    __slots__ = 'err_at', 'code', 'domain', 'user_info'
    def __init__(self, *, err_at: int, code: int, domain: Optional[str], user_info: Optional[str]):
        self.err_at = err_at
        self.code = code
        self.domain = domain
        self.user_info = user_info

    def __str__(self):
        return (
            f'JS Uncaught Exception: Error at {self.err_at}, code: {self.code}, '
            f'domain: {self.domain or WKJS_UncaughtException.DOMAIN_DEFAULT}, '
            f'user info: {self.user_info or WKJS_UncaughtException.UINFO_DEFAULT}')

    def __repr__(self) -> str:
        slst = [f'err_at={self.err_at}, code={self.code}']
        if self.domain is not None:
            slst.append(f'domain={self.domain}')
        if self.user_info is not None:
            slst.append(f'user_info={self.user_info}')
        s = ', '.join(slst)
        return f'WKJS_UncaughtException({s})'


class WKJS_SELNoSupportError(RuntimeError):
    ...


class WKJS_LogType(enum.Enum):
    TRACE = 0
    DIAG = 1
    INFO = 2
    WARN = 3
    ASSERT = 4
    ERR = 5


SENDMSG_CBTYPE = Callable[[int, tuple], any]
LOG_CBTYPE = Callable[[DefaultJSResult], None]
COMM_CBTYPE = Callable[
    [DefaultJSResult, Callable[[PyResultType, Optional[str]], None]],
    None,
]


def get_gen(_logger: AbstractLogger) -> Generator[SENDMSG_CBTYPE, None, None]:
    with PyNeApple(logger=_logger) as pa:
        pa.load_framework_from_path('Foundation')
        cf = pa.load_framework_from_path('CoreFoundation')
        pa.load_framework_from_path('WebKit')

        # NSAutoreleasePool = pa.safe_objc_getClass(b'NSAutoreleasePool')
        # pool = pa.safe_alloc_init(NSAutoreleasePool)
        # print(f'the pool is at {pool.value}')
        # pa.call_on_exit(lambda: pa.send_message(pool, b'drain'))

        NSArray = pa.safe_objc_getClass(b'NSArray')
        NSDate = pa.safe_objc_getClass(b'NSDate')
        NSDictionary = pa.safe_objc_getClass(b'NSDictionary')
        NSString = pa.safe_objc_getClass(b'NSString')
        NSNull = pa.safe_objc_getClass(b'NSNull')
        inst_NSNull = py_typecast(NotNull_VoidP, c_void_p(pa.send_message(NSNull, b'null', restype=c_void_p)))
        if inst_NSNull.value is None:
            raise RuntimeError('[NSNull null] really is NULL')
        NSNumber = pa.safe_objc_getClass(b'NSNumber')
        NSObject = pa.safe_objc_getClass(b'NSObject')
        NSURL = pa.safe_objc_getClass(b'NSURL')
        WKContentWorld = pa.safe_objc_getClass(b'WKContentWorld')
        WKWebView = pa.safe_objc_getClass(b'WKWebView')
        WKWebViewConfiguration = pa.safe_objc_getClass(b'WKWebViewConfiguration')
        WKUserContentController = pa.safe_objc_getClass(b'WKUserContentController')

        if not pa.send_message(
            WKUserContentController, b'instancesRespondToSelector:',
            pa.sel_registerName(b'addScriptMessageHandlerWithReply:contentWorld:name:'),
            restype=c_byte, argtypes=(c_void_p, )):
                raise WKJS_SELNoSupportError('-[WKUserContentController addScriptMessageHandlerWithReply:contentWorld:name:]')
        if not pa.send_message(
            WKWebView, b'instancesRespondToSelector:',
            pa.sel_registerName(b'callAsyncJavaScript:arguments:inFrame:inContentWorld:completionHandler:'),
            restype=c_byte, argtypes=(c_void_p, )):
                raise WKJS_SELNoSupportError('-[WKWebView callAsyncJavaScript:arguments:inFrame:inContentWorld:completionHandler:]')

        CFRunLoopStop = pa.cfn_at(cf(b'CFRunLoopStop').value, None, c_void_p)
        CFRunLoopRun = pa.cfn_at(cf(b'CFRunLoopRun').value, None)
        CFRunLoopGetMain = pa.cfn_at(cf(b'CFRunLoopGetMain').value, c_void_p)
        kCFRunLoopDefaultMode = c_void_p.from_address(cf(b'kCFRunLoopDefaultMode').value)
        CFRunLoopPerformBlock = pa.cfn_at(cf(b'CFRunLoopPerformBlock').value, None, c_void_p, c_void_p, POINTER(ObjCBlock))
        CFRunLoopWakeUp = pa.cfn_at(cf(b'CFRunLoopWakeUp').value, None, c_void_p)
        currloop = c_void_p(pa.cfn_at(cf(b'CFRunLoopGetCurrent').value, c_void_p)())
        mainloop = c_void_p(CFRunLoopGetMain())
        if currloop.value != mainloop.value:
            pa.logger.warning('running code on another loop is an experimental feature')
        CFDateGetAbsoluteTime = pa.cfn_at(cf(b'CFDateGetAbsoluteTime').value, c_double, c_void_p)
        CFNumberGetValue = pa.cfn_at(cf(b'CFNumberGetValue').value, c_bool, c_void_p, c_long, c_void_p)
        kCFNumberFloat64Type = c_long(6)
        kCFNumberLongLongType = c_long(11)
        CFDictionaryApplyFunction = pa.cfn_at(cf(b'CFDictionaryApplyFunction').value, None, c_void_p, c_void_p, c_void_p)
        CFArrayGetCount = pa.cfn_at(cf(b'CFArrayGetCount').value, c_long, c_void_p)
        CFArrayGetValueAtIndex = pa.cfn_at(cf(b'CFArrayGetValueAtIndex').value, c_void_p, c_void_p, c_long)

        type_to_largest: dict[bytes, tuple[c_long, Union[type[c_int64], type[c_uint64], type[c_double]]]] = {
            b'c': (kCFNumberLongLongType, c_int64),
            b'C': (kCFNumberLongLongType, c_uint64),
            b's': (kCFNumberLongLongType, c_int64),
            b'S': (kCFNumberLongLongType, c_uint64),
            b'i': (kCFNumberLongLongType, c_int64),
            b'I': (kCFNumberLongLongType, c_uint64),
            b'l': (kCFNumberLongLongType, c_int64),
            b'L': (kCFNumberLongLongType, c_uint64),
            b'q': (kCFNumberLongLongType, c_int64),
            b'Q': (kCFNumberLongLongType, c_uint64),
            b'f': (kCFNumberFloat64Type, c_double),
            b'd': (kCFNumberFloat64Type, c_double),
        }

        kCFBooleanTrue = c_void_p.from_address(cf(b'kCFBooleanTrue').value)

        # pa.send_message(NSAutoreleasePool, b'showPools')

        # RELEASE IT!!!
        def alloc_nsstring_from_str(pystr: str):
            # DO NOT USE b'initWithCharacters:length:'!
            str_utf8 = pystr.encode()
            p_str = pa.safe_new_object(
                NSString, b'initWithBytes:length:encoding:', str_utf8, len(str_utf8), NSUTF8StringEncoding,
                    argtypes=(c_char_p, c_ulong, c_ulong))
            return p_str

        def pyobj_from_nsobj_jsresult(
            pa: PyNeApple,
            jsobj: NULLABLE_VOIDP,
            *,
            visited: dict[int, _JSResultType[T, U, V]],
            undefined: T = None,
            null: U = None,
            on_unknown_st: Callable[[str], V] = _UnknownStructure,
        ) -> _JSResultType[T, U, V]:
            if not jsobj.value:
                return undefined
            elif visitedobj := visited.get(jsobj.value):
                return visitedobj
            elif pa.instanceof(jsobj, NSNull):
                visited[jsobj.value] = null
                return null
            elif pa.instanceof(jsobj, NSString):
                s_res = str_from_nsstring(pa, py_typecast(NotNull_VoidP, jsobj))
                visited[jsobj.value] = s_res
                return s_res
            elif pa.instanceof(jsobj, NSNumber):
                kcf_numtyp, restyp = type_to_largest[py_typecast(bytes, pa.send_message(
                    jsobj, b'objCType', restype=c_char_p))]
                n_res = restyp()
                if not CFNumberGetValue(jsobj, kcf_numtyp, byref(n_res)):
                    sval = str_from_nsstring(pa, py_typecast(NotNull_VoidP, c_void_p(
                        pa.send_message(jsobj, b'stringValue', restype=c_void_p))))
                    raise RuntimeError(f'CFNumberGetValue failed on CFNumberRef@{jsobj.value}, stringValue: {sval}')
                n_resv = n_res.value
                visited[jsobj.value] = n_resv
                return n_resv
            elif pa.instanceof(jsobj, NSDate):
                dte1970 = py_typecast(float, CFDateGetAbsoluteTime(jsobj)) + 978307200.0
                py_dte = dt.datetime.fromtimestamp(dte1970, dt.timezone.utc)
                visited[jsobj.value] = py_dte
                return py_dte
            elif pa.instanceof(jsobj, NSDictionary):
                d = {}
                visited[jsobj.value] = d

                @CFUNCTYPE(None, c_void_p, c_void_p, c_void_p)
                def visitor(k: CRet.Py_PVoid, v: CRet.Py_PVoid, userarg: CRet.Py_PVoid):
                    nonlocal d
                    # pa.logger.trace(f'visit s dict@{userarg=}; {k=}; {v=}')
                    k_ = pyobj_from_nsobj_jsresult(pa, c_void_p(k), visited=visited, undefined=undefined, null=null, on_unknown_st=on_unknown_st)
                    v_ = pyobj_from_nsobj_jsresult(pa, c_void_p(v), visited=visited, undefined=undefined, null=null, on_unknown_st=on_unknown_st)
                    # pa.logger.trace(f'visit e dict@{userarg=}; {k_=}; {v_=}')
                    d[k_] = v_

                CFDictionaryApplyFunction(jsobj, visitor, jsobj)
                return d
            elif pa.instanceof(jsobj, NSArray):
                larr = CFArrayGetCount(jsobj)
                arr = []
                visited[jsobj.value] = arr
                for i in range(larr):
                    v = CFArrayGetValueAtIndex(jsobj, i)
                    # pa.logger.trace(f'visit s arr@{jsobj.value}; {v=}')
                    v_ = pyobj_from_nsobj_jsresult(pa, c_void_p(v), visited=visited, undefined=undefined, null=null, on_unknown_st=on_unknown_st)
                    # pa.logger.trace(f'visit e arr@{jsobj.value}; {v_=}')
                    arr.append(v_)
                return arr
            else:
                tn = py_typecast(bytes, pa.class_getName(pa.object_getClass(jsobj))).decode()
                pa.logger.trace(f'unk@{jsobj.value=}; {tn=}')
                unk_res = on_unknown_st(tn)
                visited[jsobj.value] = unk_res
                return unk_res

        def ns_jsobj_from_pyres(
            pyres: PyResultType,
            *,
            pending_free: list[NotNull_VoidP],
        ) -> NotNull_VoidP:
            if pyres is None:
                return inst_NSNull
            elif isinstance(pyres, str):
                p_str = alloc_nsstring_from_str(pyres)
                pending_free.append(p_str)
                return p_str
            elif isinstance(pyres, int):
                if pyres >= 0:  # use ULL
                    if pyres > 18446744073709551615:
                        raise OverflowError('Number does not fit in NSNumber (greater than ULLONG_MAX)')
                    ull = pa.safe_new_object(NSNumber, b'initWithUnsignedLongLong:', pyres, argtypes=(c_ulonglong, ))
                    pending_free.append(ull)
                    return ull
                else:  # use LL
                    if pyres < -9223372036854775807:
                        raise OverflowError('Number does not fit in NSNumber (less than LLONG_MIN)')
                    ll = pa.safe_new_object(NSNumber, b'initWithLongLong:', pyres, argtypes=(c_longlong, ))
                    pending_free.append(ll)
                    return ll
            elif isinstance(pyres, float):
                fpnum = pa.safe_new_object(NSNumber, b'initWithDouble:', pyres, argtypes=(c_double, ))
                pending_free.append(fpnum)
                return fpnum
            elif isinstance(pyres, dt.datetime):
                nsdt = pa.safe_new_object(
                    NSDate, b'initWithTimeIntervalSince1970:', pyres.timestamp(),
                    argtypes=(c_double, ))
                pending_free.append(nsdt)
                return nsdt
            else:
                raise RuntimeError(f'Type {type(pyres)} is not (yet) supported')

        def schedule_on(loop: c_void_p, pycb: Callable[[], None], *, var_keepalive: set, mode=kCFRunLoopDefaultMode):
            block: ObjCBlock

            def _pycb_real():
                pycb()
                var_keepalive.remove(block)
            block = pa.make_block(_pycb_real)
            var_keepalive.add(block)
            CFRunLoopPerformBlock(loop, mode, byref(block))
            CFRunLoopWakeUp(loop)

        def _runcoro_on_loop_base(
            coro: Coroutine[Any, Any, T],
            *,
            var_keepalive: set,
            loop: c_void_p,
            finish: Callable[[BaseException], None],
            default: U = None,
        ) -> CFRL_CoroResult[Union[T, U]]:
            # Default is returned when the coroutine wrongly calls CFRunLoopStop(loop) or its equivalent
            res = CFRL_CoroResult[Union[T, U]](default)
            pa.logger.trace(f'_runcoro_on_loop_base: starting coroutine: {coro=}')

            def _coro_step(v: Any = None, *, exc: Optional[BaseException] = None):
                nonlocal res
                pa.logger.trace(f'coro step: {v=}; {exc=}')
                fut: CFRL_Future
                try:
                    if exc is not None:
                        fut = coro.throw(exc)
                    else:
                        fut = coro.send(v)
                    # TODO: support awaitables that aren't futures, e.g. coro
                except StopIteration as si:
                    pa.logger.trace(f'stopping with return value: {si.value=}')
                    res.ret = si.value
                    finish(si)
                    return
                except BaseException as e:
                    pa.logger.trace(f'will throw exc raised from coro: {e=}')
                    res.rexc = e
                    finish(e)
                    return

                def _on_fut_done(f: CFRL_Future):
                    pa.logger.trace(f'fut done: {f=}')
                    try:
                        fut_res = f.result()
                    except BaseException as fut_err:
                        pa.logger.trace(f'fut exc: {fut_err=}, scheduling exc callback')

                        def _exc_cb(fut_err=fut_err):
                            pa.logger.trace(f'fut exc cb: calling _coro_step with {fut_err=}')
                            _coro_step(exc=fut_err)
                        scheduled = _exc_cb
                    else:
                        pa.logger.trace(f'fut res: {fut_res=}, scheduling done callback')

                        def _normal_cb():
                            pa.logger.trace(f'fut cb, calling _coro_step with {fut_res=}')
                            _coro_step(fut_res)
                        scheduled = _normal_cb
                    schedule_on(loop, scheduled, var_keepalive=var_keepalive)
                fut.add_done_callback(_on_fut_done)
                pa.logger.trace(f'added done callback {_on_fut_done=} to fut {fut=}')

            schedule_on(loop, _coro_step, var_keepalive=var_keepalive)
            return res

        def runcoro_on_current(coro: Coroutine[Any, Any, T], *, default: U = None) -> Union[T, U]:
            var_keepalive = set()
            res = _runcoro_on_loop_base(coro, var_keepalive=var_keepalive, loop=currloop, default=default, finish=lambda exc: CFRunLoopStop(currloop))
            CFRunLoopRun()
            pa.logger.trace(f'runcoro_on_current done: {res.rexc=}; {res.ret=}')
            if res.rexc is not None:
                raise res.rexc from None
            return res.ret

        def runcoro_on_loop(coro: Coroutine[Any, Any, T], *, loop=mainloop, default: U = None) -> Union[T, U]:
            if loop.value == currloop.value:
                return runcoro_on_current(coro, default=default)
            finished = False
            cv = Condition()
            var_keepalive = set()

            def finish(e: BaseException):
                nonlocal finished
                with cv:
                    finished = True
                    cv.notify()
            res = _runcoro_on_loop_base(coro, var_keepalive=var_keepalive, loop=loop, default=default, finish=finish)
            with cv:
                while not finished:
                    cv.wait()

            pa.logger.trace(f'runcoro_on_loop done: {res.rexc=}; {res.ret=}')
            if res.rexc is not None:
                raise res.rexc from None
            return res.ret

        navi_cbdct: dict[int, Callable[[], None]] = {}
        usrcontctlr_cbdct: dict[int, LOG_CBTYPE] = {}
        usrcontctlr_commcbdct: dict[int, COMM_CBTYPE] = {}
        class PFC_WVHandler:
            @staticmethod
            def webView0_didFinishNavigation1(this: CRet.Py_PVoid, sel: CRet.Py_PVoid, rp_webview: CRet.Py_PVoid, rp_navi: CRet.Py_PVoid) -> None:
                pa.logger.trace(f'Callback: [(PyForeignClass_WebViewHandler){this} webView: {rp_webview} didFinishNavigation: {rp_navi}]')
                if cb := navi_cbdct.get(rp_navi or 0):
                    cb()

            @staticmethod
            def userContentController0_didReceiveScriptMessage1(this: CRet.Py_PVoid, sel: CRet.Py_PVoid, rp_usrcontctlr: CRet.Py_PVoid, rp_sm: CRet.Py_PVoid) -> None:
                pa.logger.trace(f'Callback: [(PyForeignClass_WebViewHandler){this} userContentController: {rp_usrcontctlr} didReceiveScriptMessage: {rp_sm}]')
                rp_msgbody = c_void_p(pa.send_message(c_void_p(rp_sm), b'body', restype=c_void_p))
                pyobj = pyobj_from_nsobj_jsresult(pa, rp_msgbody, visited={}, null=NullTag)
                if cb := usrcontctlr_cbdct.get(rp_usrcontctlr or 0):
                    cb(pyobj)

            @staticmethod
            def userContentController0_didReceiveScriptMessage1_replyHandler2(
                this: CRet.Py_PVoid, sel: CRet.Py_PVoid,
                rp_usrcontctlr: CRet.Py_PVoid, rp_sm: CRet.Py_PVoid, rp_replyhandler: CRet.Py_PVoid
            ):
                replyhandler = cast(rp_replyhandler or 0, POINTER(ObjCBlock)).contents
                pa.logger.trace(
                        f'Callback: [(PyForeignClass_WebViewHandler){this} userContentController: {rp_usrcontctlr} '
                    f'didReceiveScriptMessage: {rp_sm} replyHandler: &({replyhandler!r})]')
                res_or_exc = replyhandler.as_pycb(None, c_void_p, c_void_p)
                def return_result(result: PyResultType, err: Optional[str]) -> None:
                    try:
                        if err is not None:
                            p_errstr = alloc_nsstring_from_str(err)
                            res_or_exc(None, p_errstr)
                            pa.release_obj(p_errstr)
                        else:
                            pending_free = []
                            nsobj = ns_jsobj_from_pyres(result, pending_free=pending_free)
                            assert nsobj
                            res_or_exc(nsobj, None)
                            list(map(pa.release_obj, pending_free))
                    except Exception as e:
                        pa.logger.warning(f'Error sending script message, did the conversion fail? {e!r}')
                        return_result(None, repr(e))

                # TODO(?): expose some CFRL utils to the callback?
                try:
                    rp_msgbody = c_void_p(pa.send_message(c_void_p(rp_sm), b'body', restype=c_void_p))
                    pyobj = pyobj_from_nsobj_jsresult(pa, rp_msgbody, visited={}, null=NullTag)
                    usrcontctlr_commcbdct[rp_usrcontctlr or 0](pyobj, return_result)
                except BaseException as e:
                    pa.logger.warning(f'Error while handling script message: {e!r}')
                    return_result(None, repr(e))

        meth_list: PyNeApple.METH_LIST_TYPE = (
            (
                pa.sel_registerName(b'webView:didFinishNavigation:'),
                CFUNCTYPE(
                    None,
                    c_void_p, c_void_p, c_void_p, c_void_p)(
                        PFC_WVHandler.webView0_didFinishNavigation1),
                b'v@:@@',
            ), (
                pa.sel_registerName(b'userContentController:didReceiveScriptMessage:'),
                CFUNCTYPE(
                    None,
                    c_void_p, c_void_p, c_void_p, c_void_p)(
                        PFC_WVHandler.userContentController0_didReceiveScriptMessage1),
                b'v@:@@',
            ),
            (
                pa.sel_registerName(b'userContentController:didReceiveScriptMessage:replyHandler:'),
                CFUNCTYPE(
                    None,
                    c_void_p, c_void_p, c_void_p, c_void_p, c_void_p)(
                        PFC_WVHandler.userContentController0_didReceiveScriptMessage1_replyHandler2),
                b'v@:@@@?',
            ),
        )
        if i_Py_WVHandler := pa.objc_allocateClassPair(NSObject, b'PyForeignClass_WebViewHandler', 0):
            Py_WVHandler = py_typecast(NotNull_VoidP, c_void_p(i_Py_WVHandler))
            try:
                pa.safe_add_meths(Py_WVHandler, meth_list)
            except RuntimeError:
                pa.objc_disposeClassPair(Py_WVHandler)
                raise
            pa.objc_registerClassPair(Py_WVHandler)
            pa.logger.trace('Registered PyForeignClass_WebViewHandler')
        else:
            Py_WVHandler = pa.safe_objc_getClass(b'PyForeignClass_WebViewHandler')
            pa.logger.trace('Failed to allocate class PyForeignClass_WebViewHandler, testing if it is what we previously registered')
            pa.safe_upd_or_add_meths(Py_WVHandler, meth_list)
        pa.logger.trace(f'PyForeignClass_WebViewHandler@{Py_WVHandler.value}')

        def run() -> Generator[Any, Optional[tuple[int, tuple]], None]:
            with ExitStack() as exsk_out:
                p_wvhandler = pa.safe_alloc_init(Py_WVHandler)
                exsk_out.callback(pa.release_obj, p_wvhandler)
                active = True

                async def new_webview() -> tuple[int, int]:
                    async with AsyncExitStack() as exsk:
                        p_cfg = pa.safe_alloc_init(WKWebViewConfiguration)
                        exsk.callback(pa.release_obj, p_cfg)

                        rp_pref = c_void_p(pa.send_message(p_cfg, b'preferences', restype=c_void_p))
                        if not rp_pref.value:
                            raise RuntimeError('Failed to get preferences from WKWebViewConfiguration')
                        pa.send_message(
                            rp_pref, b'setJavaScriptCanOpenWindowsAutomatically:',
                            c_byte(1), argtypes=(c_byte,))
                        p_setkey0 = pa.safe_new_object(
                            NSString, b'initWithUTF8String:', b'allowFileAccessFromFileURLs',
                            argtypes=(c_char_p, ))
                        exsk.callback(pa.release_obj, p_setkey0)
                        pa.send_message(
                            rp_pref, b'setValue:forKey:',
                            kCFBooleanTrue, p_setkey0,
                            argtypes=(c_void_p, c_void_p))
                        rp_pref = None

                        p_setkey1 = pa.safe_new_object(
                            NSString, b'initWithUTF8String:', b'allowUniversalAccessFromFileURLs',
                            argtypes=(c_char_p, ))
                        exsk.callback(pa.release_obj, p_setkey1)
                        pa.send_message(
                            p_cfg, b'setValue:forKey:',
                            kCFBooleanTrue, p_setkey1,
                            argtypes=(c_void_p, c_void_p))

                        p_usrcontctlr = pa.safe_alloc_init(WKUserContentController)
                        exsk.callback(pa.release_obj, p_usrcontctlr)

                        p_handler_name = pa.safe_new_object(
                            NSString, b'initWithUTF8String:', b'wkjs_log',
                            argtypes=(c_char_p, ))
                        exsk.callback(pa.release_obj, p_handler_name)

                        pa.send_message(
                            p_usrcontctlr, b'addScriptMessageHandler:name:',
                            p_wvhandler, p_handler_name,
                            argtypes=(c_void_p, c_void_p))

                        rp_pageworld = c_void_p(pa.send_message(
                            WKContentWorld, b'pageWorld',
                            restype=c_void_p))

                        p_comhandler_name = pa.safe_new_object(
                            NSString, b'initWithUTF8String:', b'wkjs_com',
                            argtypes=(c_char_p, ))
                        exsk.callback(pa.release_obj, p_comhandler_name)

                        pa.send_message(
                            p_usrcontctlr, b'addScriptMessageHandlerWithReply:contentWorld:name:',
                            p_wvhandler,rp_pageworld, p_comhandler_name,
                            argtypes=(c_void_p, c_void_p, c_void_p))

                        pa.send_message(
                            p_cfg, b'setUserContentController:', p_usrcontctlr,
                            argtypes=(c_void_p, ))

                        p_webview = pa.safe_new_object(
                            WKWebView, b'initWithFrame:configuration:',
                            CGRect(), p_cfg,
                            argtypes=(CGRect, c_void_p))

                    pa.send_message(
                        p_webview, b'setNavigationDelegate:',
                        p_wvhandler, argtypes=(c_void_p, ))
                    pa.logger.trace('webview full init')
                    return p_webview.value, p_usrcontctlr.value

                async def free_webview(wv: int) -> None:
                    if wv:
                        pa.release_obj(c_void_p(wv))

                def on_script_log(usrcontctlr: int, cb_new: LOG_CBTYPE) -> Optional[LOG_CBTYPE]:
                    ret = usrcontctlr_cbdct.get(usrcontctlr)
                    usrcontctlr_cbdct[usrcontctlr] = cb_new
                    return ret

                def on_script_comm(usrcontctlr: int, cb_new: COMM_CBTYPE) -> Optional[COMM_CBTYPE]:
                    ret = usrcontctlr_commcbdct.get(usrcontctlr or 0)
                    usrcontctlr_commcbdct[usrcontctlr] = cb_new
                    return ret

                async def navigate_to(webview: int, host: str, html: str) -> None:
                    fut_navidone: CFRL_Future[None] = CFRL_Future()
                    async with AsyncExitStack() as exsk:
                        ps_html = alloc_nsstring_from_str(html)
                        exsk.callback(pa.release_obj, ps_html)
                        ps_base_url = alloc_nsstring_from_str(host)
                        exsk.callback(pa.release_obj, ps_base_url)
                        purl_base = pa.safe_new_object(
                            NSURL, b'initWithString:', ps_base_url,
                            argtypes=(c_void_p, ))
                        exsk.callback(pa.release_obj, purl_base)

                        rp_navi = py_typecast(NotNull_VoidP, c_void_p(pa.send_message(
                            c_void_p(webview), b'loadHTMLString:baseURL:', ps_html, purl_base,
                            restype=c_void_p, argtypes=(c_void_p, c_void_p))))

                        def cb_navi_done():
                            pa.logger.trace('navigation done, resolving future')
                            fut_navidone.set_result(None)

                        navi_cbdct[rp_navi.value] = cb_navi_done
                        pa.logger.trace(f'Navigation started on {host}')

                        await fut_navidone
                    pa.logger.trace('navigation done')

                async def execute_js(webview: int, script: str) -> tuple[DefaultJSResult, Optional[WKJS_UncaughtException]]:
                    fut_jsdone: CFRL_Future[bool] = CFRL_Future()
                    result_exc: Optional[WKJS_UncaughtException] = None
                    result_pyobj: Optional[DefaultJSResult] = None
                    real_script = SCRIPT_TEMPL.replace(SCRIPT_PHOLDER, script)
                    async with AsyncExitStack() as exsk:
                        ps_script = alloc_nsstring_from_str(real_script)
                        exsk.callback(pa.release_obj, ps_script)

                        pd_jsargs = pa.safe_alloc_init(NSDictionary)
                        exsk.callback(pa.release_obj, pd_jsargs)

                        rp_pageworld = c_void_p(pa.send_message(
                            WKContentWorld, b'pageWorld',
                            restype=c_void_p))

                        def completion_handler(self: CRet.Py_PVoid, id_result: CRet.Py_PVoid, err: CRet.Py_PVoid):
                            nonlocal result_exc, result_pyobj
                            if err:
                                nserr = c_void_p(err)
                                code = pa.send_message(nserr, b'code', restype=c_long)
                                s_domain = str_from_nsstring(pa, c_void_p(pa.send_message(
                                    nserr, b'domain', restype=c_void_p)), default=WKJS_UncaughtException.DOMAIN_DEFAULT)
                                s_uinfo = str_from_nsstring(pa, c_void_p(pa.send_message(
                                    c_void_p(pa.send_message(nserr, b'userInfo', restype=c_void_p)),
                                    b'description', restype=c_void_p)), default=WKJS_UncaughtException.UINFO_DEFAULT)
                                result_exc = WKJS_UncaughtException(err_at=err, code=code, domain=s_domain, user_info=s_uinfo)
                                fut_jsdone.set_result(False)
                                return
                            result_pyobj = pyobj_from_nsobj_jsresult(pa, c_void_p(id_result), visited={}, null=NullTag)
                            pa.logger.trace(f'JS done, resolving future; {id_result=}, {err=}')
                            fut_jsdone.set_result(True)

                        chblock = pa.make_block(completion_handler, None, POINTER(ObjCBlock), c_void_p, c_void_p)
                        pa.send_message(
                            # Requires iOS 14.0+, maybe test its availability first
                            # TODO: respondsToSelector:@selector(callAsyncJavaScript:arguments:inFrame:inContentWorld:completionHandler:)
                            c_void_p(webview), b'callAsyncJavaScript:arguments:inFrame:inContentWorld:completionHandler:',
                            ps_script, pd_jsargs, c_void_p(None), rp_pageworld, byref(chblock),
                            argtypes=(c_void_p, c_void_p, c_void_p, c_void_p, POINTER(ObjCBlock)))

                        await fut_jsdone

                        pa.logger.trace('JS execution completed')
                        return result_pyobj, result_exc

                def shutdown():
                    nonlocal active
                    active = False

                fn_tup = navigate_to, execute_js, shutdown, new_webview, free_webview, on_script_log, on_script_comm, pa.set_logger
                fn_iscoro = True, True, False, True, True, False, False, False, False
                last_res = 0
                while active:
                    task = yield last_res
                    assert task
                    fn_id, args = task
                    res_or_coro = fn_tup[fn_id](*args)
                    last_res = runcoro_on_loop(py_typecast(CoroutineType, res_or_coro)) if fn_iscoro[fn_id] else res_or_coro

        gen_run = run()
        assert gen_run.send(None) == 0
        yield lambda *args: gen_run.send(args)
        # pa.send_message(NSAutoreleasePool, b'showPools')
