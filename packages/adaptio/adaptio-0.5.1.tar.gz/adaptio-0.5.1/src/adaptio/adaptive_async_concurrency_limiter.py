import asyncio
from collections.abc import Coroutine
from typing import Any

from .adjustable_semaphore import AdjustableSemaphore
from .log_utils import setup_colored_logger


class ServiceOverloadError(BaseException):
    pass


class AdaptiveAsyncConcurrencyLimiter:
    """自适应并发限制器，用于动态控制并发任务数量。

    使用类似 TCP 拥塞控制的算法来动态调整并发数：
    - 当系统正常运行时，逐步增加并发数
    - 当检测到过载时，快速降低并发数
    - 通过动态信号量（DynamicSemaphore）来控制并发度

    Args:
        max_concurrency: 最大允许的并发数
        min_concurrency: 最小允许的并发数
        initial_concurrency: 初始并发数
        adjust_overload_rate: 触发并发度调整的过载率阈值
            意思是在最近一轮并发调用中，若触发过载错误的调用数量超过这个比例，才会进行降低并发数操作
        overload_exception: 用于标识过载的异常类型
        log_level: 日志级别
        log_prefix: 日志前缀
        ignore_loop_bound_exception: 是否忽略事件循环绑定异常
            如果你获取了一个在另一个asyncio循环中初始化的信号量，实际上它没有任何限制并发的能力！
            默认情况下，这个库在这种情况下会引发RuntimeError异常。
            但是，如果你将此选项设置为True，它将忽略异常，并且除了打印一条 warning 外没有其他动作。
            通常情况下很难在实际应用中出发这个错误，除非刻意写出在同步函数中使用多线程调用异步函数的代码。
            https://github.com/python/cpython/blob/v3.13.3/Lib/asyncio/mixins.py#L20
    """

    def __init__(
        self,
        max_concurrency=256,
        min_concurrency=1,
        initial_concurrency=1,
        adjust_overload_rate: float = 0.1,
        overload_exception: type[BaseException] = ServiceOverloadError,
        log_level: str = "INFO",
        log_prefix: str = "",
        ignore_loop_bound_exception: bool = False,
    ):
        if initial_concurrency < min_concurrency:
            raise ValueError(
                f"{log_prefix} -- {initial_concurrency=} 不能小于 {min_concurrency=}"
            )
        if initial_concurrency > max_concurrency:
            raise ValueError(
                f"{log_prefix} -- {initial_concurrency=} 不能大于 {max_concurrency=}"
            )
        if min_concurrency > max_concurrency:
            raise ValueError(
                f"{log_prefix} -- {min_concurrency=} 不能大于 {max_concurrency=}"
            )

        self.max_concurrency = max_concurrency
        self.min_concurrency = min_concurrency
        self.adjust_overload_rate = adjust_overload_rate
        self.overload_exception = overload_exception
        self.log_prefix = log_prefix

        self.logger = setup_colored_logger(
            logger_name=f"scheduler_{id(self)}",
            log_level=log_level,
        )

        self.submitted_tasks: set[asyncio.Future[Any]] = set()

        self.current_failed_count = 0
        self.current_overload_count = 0
        self.current_succeed_count = 0
        self.current_finished_count = 0
        self.current_running_count = 0

        self.workers_lock = AdjustableSemaphore(
            initial_concurrency,
            ignore_loop_bound_exception=ignore_loop_bound_exception,
        )
        # 添加新的变量来跟踪调整状态
        self.increase_step = 1  # 初始增长步长
        self.decrease_factor = 0.75  # 遇到过载时的下降因子

    def reset_counters(self):
        self.current_failed_count = 0
        self.current_overload_count = 0
        self.current_succeed_count = 0
        self.current_finished_count = 0

    async def adjust_concurrency(self):
        """借鉴TCP的拥塞控制算法调整 workers 数量"""
        if self.current_finished_count == 0:
            self.logger.debug(f"{self.log_prefix} -- 没有完成的任务，跳过调整")
            return

        overload_rate = self.current_overload_count / self.current_finished_count
        self.logger.debug(
            f"{self.log_prefix} -- 当前过载率: {overload_rate:.2%}, 调整阈值: {self.adjust_overload_rate:.2%}"
        )

        if overload_rate > self.adjust_overload_rate:
            # 遇到过载时，乘以下降因子快速降低并发数
            new_concurrency = max(
                self.min_concurrency,
                int(self.workers_lock.initial_value * self.decrease_factor),
            )
            self.increase_step = 1  # 重置增长步长
            self.logger.info(
                f"{self.log_prefix} -- 检测到过载，降低并发数至 {new_concurrency}"
            )
        else:
            # 未过载时，采用渐进式增长
            new_concurrency = min(
                self.max_concurrency,
                self.workers_lock.initial_value + self.increase_step,
            )
            self.increase_step = min(
                self.increase_step * 2, 16
            )  # 指数增长步长，但设置上限
            self.logger.info(
                f"{self.log_prefix} -- 系统运行正常，提升并发数从 {self.workers_lock.initial_value} 到 {new_concurrency}，下次增长步长: {self.increase_step}"
            )

        await self.workers_lock.set_value(new_concurrency)

    def submit(self, coro: Coroutine[Any, Any, Any]) -> asyncio.Task[Any]:
        if not self.workers_lock.initial_value:
            raise RuntimeError("并发限制器已关闭")

        async def _task_wrapper():
            async with self.workers_lock:
                self.current_running_count += 1
                try:
                    result = await coro
                    self.current_succeed_count += 1
                    return result
                except self.overload_exception:
                    self.current_overload_count += 1
                    self.logger.debug(
                        f"{self.log_prefix} -- "
                        f"服务过载，当前触发过载任务数: {self.current_overload_count} "
                        f"任务状态 - 已完成: {self.current_finished_count}, "
                        f"成功数: {self.current_succeed_count}, "
                        f"运行中: {self.current_running_count}, "
                        f"过载数: {self.current_overload_count}, "
                        f"失败数: {self.current_failed_count}, "
                        f"当前并发度: {self.workers_lock.get_value()}, "
                        f"基准并发度: {self.workers_lock.initial_value}",
                    )
                    raise
                except Exception:
                    self.current_failed_count += 1
                    raise
                finally:
                    self.current_finished_count += 1
                    self.current_running_count -= 1
                    self.logger.debug(
                        f"{self.log_prefix} -- "
                        f"任务状态 - 已完成: {self.current_finished_count}, "
                        f"成功数: {self.current_succeed_count}, "
                        f"运行中: {self.current_running_count}, "
                        f"过载数: {self.current_overload_count}, "
                        f"失败数: {self.current_failed_count}, "
                        f"当前并发度: {self.workers_lock.get_value()}, "
                        f"基准并发度: {self.workers_lock.initial_value}"
                    )
                    if self.workers_lock.get_value() < 0:
                        self.reset_counters()

                    if self.current_finished_count > self.workers_lock.initial_value:
                        await self.adjust_concurrency()
                        self.reset_counters()

        def _on_done(task: asyncio.Task[Any]) -> None:
            # self.finished_tasks.put_nowait(task)
            self.submitted_tasks.remove(task)

        task = asyncio.create_task(_task_wrapper())
        task.add_done_callback(_on_done)
        self.submitted_tasks.add(task)
        return task

    async def shutdown(self):
        """关闭并发限制器，等待所有任务完成"""
        await self.workers_lock.set_value(0)
        if self.submitted_tasks:
            await asyncio.gather(*self.submitted_tasks, return_exceptions=True)
        self.submitted_tasks.clear()
