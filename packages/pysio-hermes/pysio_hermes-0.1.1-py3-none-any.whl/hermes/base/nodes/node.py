############
#
# Copyright (c) 2024 Maxim Yudayev and KU Leuven eMedia Lab
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Created 2024-2025 for the KU Leuven AidWear, AidFOG, and RevalExo projects
# by Maxim Yudayev [https://yudayev.com].
#
# ############

from abc import abstractmethod
import zmq

from hermes.utils.zmq_utils import DNS_LOCALHOST, PORT_KILL, PORT_KILL_BTN, PORT_SYNC_HOST, TOPIC_KILL

from hermes.base.nodes.node_interface import NodeInterface
from hermes.base.nodes.node_states import AbstractNodeState, StartState


class Node(NodeInterface):
  def __init__(self,
               host_ip: str = DNS_LOCALHOST,
               port_sync: str = PORT_SYNC_HOST,
               port_killsig: str = PORT_KILL) -> None:
    """Constructor of the Node parent class.

    Args:
        host_ip (str, optional): IP address of the local master Broker. Defaults to DNS_LOCALHOST.
        port_sync (str, optional): Local port to listen to for local master Broker's startup coordination. Defaults to PORT_SYNC_HOST.
        port_killsig (str, optional): Local port to listen to for local master Broker's termination signal. Defaults to PORT_KILL.
    """
    self._host_ip = host_ip
    self._port_sync = port_sync
    self._port_killsig = port_killsig
    self.__is_done = False

    self._state = StartState(self)

    self._ctx: zmq.Context = zmq.Context.instance()
    self._poller: zmq.Poller = zmq.Poller()


  @property
  def _is_done(self) -> bool:
    return self.__is_done
  

  @_is_done.setter
  def _is_done(self, done: bool) -> None:
    self.__is_done = done


  def __call__(self):
    """Node objects are callable to start the FSM as entry-point.
    """
    while self._state.is_continue():
      self._state.run()
    self._cleanup()
    print("%s exited, goodbye <3"%self._log_source_tag(), flush=True)


  def _set_state(self, state: AbstractNodeState) -> None:
    self._state = state


  @abstractmethod
  def _initialize(self):
    # Socket to receive kill signal
    self._killsig: zmq.SyncSocket = self._ctx.socket(zmq.SUB)
    self._killsig.connect("tcp://%s:%s" % (DNS_LOCALHOST, self._port_killsig))
    topics = [TOPIC_KILL]
    for topic in topics: self._killsig.subscribe(topic)

    # Socket to indicate to broker that the subscriber is ready
    self._sync: zmq.SyncSocket = self._ctx.socket(zmq.REQ)
    self._sync.connect("tcp://%s:%s" % (self._host_ip, self._port_sync))
    # Socket to indicate to broker that the Node caught interrupt signal
    self._babykillsig: zmq.SyncSocket = self._ctx.socket(zmq.REQ)
    self._babykillsig.connect("tcp://%s:%s" % (DNS_LOCALHOST, PORT_KILL_BTN))


  def _get_sync_socket(self) -> zmq.SyncSocket:
    return self._sync


  def _activate_kill_poller(self) -> None:
    self._poller.register(self._killsig, zmq.POLLIN)


  @abstractmethod
  def _activate_data_poller(self) -> None:
    pass


  def _deactivate_kill_poller(self) -> None:
    print("%s received KILL signal"%self._log_source_tag(), flush=True)
    # self._killsig.recv_multipart()
    self._poller.unregister(self._killsig)


  def _send_kill_to_broker(self):
    self._babykillsig.send_string(TOPIC_KILL)


  def _poll(self) -> tuple[list[zmq.SyncSocket], list[int]]:
    return tuple(zip(*(self._poller.poll()))) # type: ignore


  @abstractmethod
  def _on_poll(self, poll_res: tuple[list[zmq.SyncSocket], list[int]]) -> None:
    if self._killsig in poll_res[0]:
      self._state.kill()


  @abstractmethod
  def _trigger_stop(self) -> None:
    pass


  @abstractmethod
  def _cleanup(self):
    """Release of generic Node resources, must be done after releasing higher-level resources.
    """
    self._killsig.close()
    self._babykillsig.close()
    self._sync.close()
    # Destroy ZeroMQ context.
    self._ctx.term()
