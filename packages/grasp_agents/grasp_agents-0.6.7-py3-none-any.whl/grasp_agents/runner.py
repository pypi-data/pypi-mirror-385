import logging
from collections.abc import AsyncIterator, Sequence
from functools import partial
from typing import Any, Generic
from uuid import uuid4

from grasp_agents.tracing_decorators import workflow

from .errors import RunnerError
from .packet import Packet
from .packet_pool import END_PROC_NAME, START_PROC_NAME, PacketPool
from .processors.base_processor import BaseProcessor
from .run_context import CtxT, RunContext
from .typing.events import Event, ProcPacketOutputEvent, RunResultEvent
from .typing.io import OutT

logger = logging.getLogger(__name__)


class Runner(Generic[OutT, CtxT]):
    def __init__(
        self,
        entry_proc: BaseProcessor[Any, Any, Any, CtxT],
        procs: Sequence[BaseProcessor[Any, Any, Any, CtxT]],
        ctx: RunContext[CtxT] | None = None,
        name: str | None = None,
    ) -> None:
        if entry_proc not in procs:
            raise RunnerError(
                f"Entry processor {entry_proc.name} must be in the list of processors: "
                f"{', '.join(proc.name for proc in procs)}"
            )
        if sum(1 for proc in procs if END_PROC_NAME in (proc.recipients or [])) != 1:
            raise RunnerError(
                "There must be exactly one processor with recipient 'END'."
            )

        self._entry_proc = entry_proc
        self._procs = procs
        self._name = name or str(uuid4())[:6]
        self._ctx = ctx or RunContext[CtxT](state=None)  # type: ignore

    @property
    def name(self) -> str:
        return self._name

    @property
    def ctx(self) -> RunContext[CtxT]:
        return self._ctx

    def _generate_call_id(self, proc: BaseProcessor[Any, Any, Any, CtxT]) -> str | None:
        return self._name + "/" + proc._generate_call_id(call_id=None)  # type: ignore

    def _unpack_packet(
        self, packet: Packet[Any] | None
    ) -> tuple[Packet[Any] | None, Any | None]:
        if packet and packet.sender == START_PROC_NAME:
            return None, packet.payloads[0]
        return packet, None

    async def _packet_handler(
        self,
        packet: Packet[Any],
        *,
        proc: BaseProcessor[Any, Any, Any, CtxT],
        pool: PacketPool,
        **run_kwargs: Any,
    ) -> None:
        _in_packet, _chat_inputs = self._unpack_packet(packet)

        logger.info(f"\n[Running processor {proc.name}]\n")

        out_packet = await proc.run(
            chat_inputs=_chat_inputs,
            in_packet=_in_packet,
            ctx=self._ctx,
            call_id=self._generate_call_id(proc),
            **run_kwargs,
        )

        route = out_packet.uniform_routing or out_packet.routing
        logger.info(
            f"\n[Finished running processor {proc.name}]\n"
            f"Posting output packet to recipients: {route}\n"
        )

        await pool.post(out_packet)

    async def _packet_handler_stream(
        self,
        packet: Packet[Any],
        *,
        proc: BaseProcessor[Any, Any, Any, CtxT],
        pool: PacketPool,
        **run_kwargs: Any,
    ) -> None:
        _in_packet, _chat_inputs = self._unpack_packet(packet)

        logger.info(f"\n[Running processor {proc.name}]\n")

        out_packet: Packet[Any] | None = None
        async for event in proc.run_stream(
            chat_inputs=_chat_inputs,
            in_packet=_in_packet,
            ctx=self._ctx,
            call_id=self._generate_call_id(proc),
            **run_kwargs,
        ):
            if isinstance(event, ProcPacketOutputEvent):
                out_packet = event.data
            await pool.push_event(event)

        assert out_packet is not None

        route = out_packet.uniform_routing or out_packet.routing
        logger.info(
            f"\n[Finished running processor {proc.name}]\n"
            f"Posting output packet to recipients: {route}\n"
        )

        await pool.post(out_packet)

    @workflow(name="runner")  # type: ignore
    async def run(self, chat_inputs: Any = "start", **run_kwargs: Any) -> Packet[OutT]:
        async with PacketPool() as pool:
            for proc in self._procs:
                pool.register_packet_handler(
                    proc_name=proc.name,
                    handler=partial(
                        self._packet_handler,
                        proc=proc,
                        pool=pool,
                        **run_kwargs,
                    ),
                )
            start_packet = Packet[Any](
                sender=START_PROC_NAME,
                routing=[[self._entry_proc.name]],
                payloads=[chat_inputs],
            )
            await pool.post(start_packet)

            return await pool.final_result()

    @workflow(name="runner_run")  # type: ignore
    async def run_stream(
        self, chat_inputs: Any = "start", **run_kwargs: Any
    ) -> AsyncIterator[Event[Any]]:
        async with PacketPool() as pool:
            for proc in self._procs:
                pool.register_packet_handler(
                    proc_name=proc.name,
                    handler=partial(
                        self._packet_handler_stream,
                        proc=proc,
                        pool=pool,
                        **run_kwargs,
                    ),
                )

            start_packet = Packet[Any](
                sender=START_PROC_NAME,
                routing=[[self._entry_proc.name]],
                payloads=[chat_inputs],
            )
            await pool.post(start_packet)

            async for event in pool.stream_events():
                if isinstance(
                    event, ProcPacketOutputEvent
                ) and event.data.uniform_routing == [END_PROC_NAME]:
                    yield RunResultEvent(
                        data=event.data,
                        proc_name=event.proc_name,
                        call_id=event.call_id,
                    )
                else:
                    yield event
