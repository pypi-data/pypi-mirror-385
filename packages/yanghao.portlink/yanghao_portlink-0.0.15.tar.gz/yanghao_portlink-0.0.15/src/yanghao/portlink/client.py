import asyncio
import websockets
import json
import logging
import inspect

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PortLinkClient:
    def __init__(self, server_uri="ws://106.75.139.203:8080/ws", local_port=None, debug=False, token=""):
        # 容错 None 或空字符串的服务器地址，落回默认值
        self.server_uri = server_uri or "ws://106.75.139.203:8080/ws"
        self.local_port = local_port
        self.websocket = None
        self.ping_task = None
        self.debug = debug
        self.token = token
        self.tunnel_addr = None
        self.remote_addr = None
        # 连接管理（服务器多路复用）：conn_id -> writer
        self.connections = {}
        # 每个 conn_id 的发送任务
        self.conn_send_tasks = {}

    def _debug_print(self, msg):
        if self.debug:
            logging.debug(msg)

    def get_tunnel_url(self):
        return self.tunnel_addr

    def print_tunnel_info(self):
        if not self.tunnel_addr:
            logging.warning("Tunnel not yet established")
            return
        import re
        try:
            ip_match = re.search(r'://([^:/]+)', self.server_uri)
            server_ip = ip_match.group(1) if ip_match else 'unknown'
        except Exception:
            server_ip = 'unknown'
        try:
            port_match = re.search(r':(\d+)$', self.remote_addr or '')
            remote_port = port_match.group(1) if port_match else 'unknown'
        except Exception:
            remote_port = 'unknown'
        combined_addr = f"{server_ip}:{remote_port}"
        logging.info(f"  Tunnel established:")
        logging.info(f"    Local service:  127.0.0.1:{self.local_port}")
        logging.info(f"    Remote address: {self.remote_addr}")
        logging.info(f"    Public address: {combined_addr}")

    async def __aenter__(self):
        logging.info(f"Connecting to server: {self.server_uri}")
        try:
            uri = self.server_uri
            if self.token:
                uri += f"?auth_token={self.token}"
            conn = websockets.connect(uri)
            if inspect.isawaitable(conn):
                self.websocket = await conn
            else:
                self.websocket = conn
            logging.info("WebSocket connection established")
            return self
        except Exception as e:
            logging.error(f"Failed to connect to server: {e}")
            raise

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.ping_task:
            self.ping_task.cancel()
        # 取消所有发送任务
        for task in list(self.conn_send_tasks.values()):
            task.cancel()
        if self.websocket:
            await self.websocket.close()
            logging.info("WebSocket connection closed")

    async def send_control_message(self, msg):
        try:
            await self.websocket.send(json.dumps(msg))
            self._debug_print(f"[CONTROL] Sent: {msg}")
        except Exception as e:
            logging.error(f"Failed to send control message: {e}")

    async def _send_pings(self):  # pragma: no cover
        while True:
            try:
                await asyncio.sleep(30)  # Send a ping every 30 seconds
                if self.debug:
                    logging.debug("Sending PING to server")
                await self.websocket.ping()
                if self.debug:
                    logging.debug("Sent PING to server")
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Error sending ping: {e}")
                break

    async def _send_heartbeat(self):  # pragma: no cover
        try:
            while True:
                await asyncio.sleep(0.1)
                if self.websocket:
                    try:
                        await self.websocket.send(json.dumps({"type": "heartbeat", "status": "ping"}))
                    except Exception:
                        pass
        except asyncio.CancelledError:
            pass

    async def link(self, local_port):
        self.local_port = local_port
        if not self.websocket:
            raise ConnectionError("Client not connected")
        try:
            while True:
                try:
                    message = await self.websocket.recv()
                except StopAsyncIteration:
                    break
                # 文本消息：控制信令
                if isinstance(message, str):
                    try:
                        msg = json.loads(message)
                    except json.JSONDecodeError:
                        print(f"Unexpected message: {message}")
                        continue
                    msg_type = msg.get("type")
                    status = msg.get("status")
                    if msg_type == "control":
                        if status == "ready":
                            # 服务器告知公共监听地址（供展示使用）
                            self.tunnel_addr = msg.get('addr')
                            self.remote_addr = self.tunnel_addr
                            self.print_tunnel_info()
                        elif status == "connected":
                            # 兼容旧流程：服务器驱动的 connected 信号
                            try:
                                reader, writer = await asyncio.open_connection('127.0.0.1', self.local_port)
                                await self._handle_local_connection(reader, writer)
                            except ConnectionRefusedError:
                                logging.error(f"Connection refused to 127.0.0.1:{self.local_port}")
                            # 为避免与 _receive_from_ws 的并发读取，旧流程下退出 link 循环
                            break
                        elif status == "new_connection":  # pragma: no cover
                            # 新流程：服务器有新的公共连接，客户端需要为该连接建立本地连接并双向转发
                            conn_id = msg.get('conn_id')
                            if not conn_id:
                                logging.warning("new_connection without conn_id")
                                continue
                            try:
                                reader, writer = await asyncio.open_connection('127.0.0.1', self.local_port)
                            except ConnectionRefusedError:
                                logging.error(f"Connection refused to 127.0.0.1:{self.local_port}")
                                # 通知服务器关闭该公共连接
                                await self.send_control_message({"type": "control", "status": "close_connection", "conn_id": conn_id})
                                continue
                            # 保存 writer 以便接收二进制数据路由
                            self.connections[conn_id] = writer
                            # 发送 connected 确认，释放服务器缓冲的数据
                            await self.send_control_message({"type": "control", "status": "connected", "conn_id": conn_id})
                            # 启动发送任务：从本地服务读取数据并打包带 conn_id 发送到服务器
                            send_task = asyncio.create_task(self._send_data_with_conn(reader, conn_id))
                            self.conn_send_tasks[conn_id] = send_task
                        else:
                            print(f"Unexpected control message: {msg}")
                # 二进制数据：按协议解析并路由到对应的本地连接
                elif isinstance(message, bytes):  # pragma: no cover
                    if not message:
                        continue
                    try:
                        id_len = message[0]
                        # 如果数据长度足够，认为包含 conn_id 头
                        if len(message) >= 1 + id_len:
                            conn_id = message[1:1+id_len].decode('utf-8') if id_len > 0 else ''
                            payload = message[1+id_len:]
                            writer = self.connections.get(conn_id)
                            if writer:
                                writer.write(payload)
                                await writer.drain()
                            else:
                                # 无已知连接，回退策略：直接忽略或打印调试信息
                                self._debug_print(f"No writer for conn_id={conn_id}, dropping {len(payload)} bytes")
                        else:
                            # 非协议数据或长度异常：作为原始数据回退处理（兼容测试）
                            # 如果只有一个连接，尽量写入该连接
                            if len(self.connections) == 1:
                                (_, writer) = next(iter(self.connections.items()))
                                writer.write(message)
                                await writer.drain()
                            else:
                                self._debug_print(f"Malformed frame, length={len(message)}; no routing performed")
                    except Exception as e:
                        self._debug_print(f"Error routing binary frame: {e}")
        except websockets.ConnectionClosed as e:
            logging.info(f"Connection closed: {e.code} {e.reason}")

    async def _handle_local_connection(self, reader, writer):
        send_task = asyncio.create_task(self._send_to_ws(reader))
        receive_task = asyncio.create_task(self._receive_from_ws(writer))
        try:
            await asyncio.gather(send_task, receive_task)
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass

    async def _receive_from_ws(self, writer):
        self._debug_print("Starting to receive data from WebSocket")
        try:
            async for message in self.websocket:
                if isinstance(message, bytes):
                    self._debug_print(f"Received binary data, length: {len(message)} bytes")
                    writer.write(message)
                    await writer.drain()
                    self._debug_print("Binary data forwarded to local service")
        except websockets.exceptions.ConnectionClosed as e:
            print(f"WebSocket connection closed: {e}")
            self._debug_print(f"WebSocket connection closed details: {e}")
        except Exception as e:
            print(f"Error receiving from WebSocket: {e}")
            self._debug_print(f"Error receiving data from WebSocket details: {e}")
        finally:
            self._debug_print("WebSocket receive task ended, closing writer")
            writer.close()

    async def _send_to_ws(self, reader):
        self._debug_print("Starting to read data from local service and send to WebSocket")
        try:
            while True:
                self._debug_print("Waiting to read data from local service...")
                data = await reader.read(4096)
                if not data:
                    self._debug_print("Local service connection closed, stopping data transmission")
                    break
                self._debug_print(f"Read {len(data)} bytes from local service")
                await self.websocket.send(data)
                self._debug_print("Data sent to WebSocket")
        except asyncio.CancelledError:
            self._debug_print("Send to WebSocket task cancelled")
            pass
        except Exception as e:
            self._debug_print(f"Error sending data to WebSocket: {e}")

    async def _send_data_with_conn(self, reader, conn_id):  # pragma: no cover
        """带 conn_id 头的发送：兼容服务端二进制数据多路复用协议"""
        try:
            conn_id_bytes = conn_id.encode('utf-8')
            header_len = len(conn_id_bytes)
            while True:
                data = await reader.read(4096)
                if not data:
                    break
                frame = bytes([header_len]) + conn_id_bytes + data
                await self.websocket.send(frame)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self._debug_print(f"Error sending framed data for {conn_id}: {e}")
        finally:
            # 本地连接结束，通知服务器关闭对应公共连接
            try:
                await self.send_control_message({"type": "control", "status": "close_connection", "conn_id": conn_id})
            except Exception:
                pass
            # 清理 writer 与任务
            writer = self.connections.pop(conn_id, None)
            try:
                if writer:
                    writer.close()
            except Exception:
                pass

async def main():  # pragma: no cover
    print("PortLink Client - Simple TCP Tunnel Tool")
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='PortLink Client - Simple TCP Tunnel Tool')
    parser.add_argument('local_port', type=int, help='Local service port')
    parser.add_argument('-s', '--server', type=str, default='ws://106.75.139.203:8080/ws', help='Server address (e.g.: ws://example.com:8080/ws)')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug mode to show detailed information')
    parser.add_argument('-t', '--ping-timeout', type=int, default=61, help='WebSocket ping timeout in seconds (default: 61)')
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug("Debug mode enabled")
    
    retries = 0
    retry_delay = 5  # Default 5 seconds reconnection delay
    
    while True:
        try:
            async with PortLinkClient(local_port=args.local_port, server_uri=args.server, debug=args.debug) as client:
                logging.info(f"Connecting to server: {args.server if args.server else client.server_uri}")
                await client.link(args.local_port)
                logging.info("Task completed, normal exit.")
                break
        except (websockets.ConnectionClosed, ConnectionRefusedError, OSError) as e:
            retries += 1
            logging.error(f"Connection error: {e}, trying to reconnect in {retry_delay} seconds (Attempt: {retries})")
            await asyncio.sleep(retry_delay)
        except KeyboardInterrupt:
            logging.info("\nUser interrupted, program exiting.")
            break

if __name__ == "__main__":
    asyncio.run(main())  # pragma: no cover
