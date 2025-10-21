import pytest
import asyncio
import json
import logging
from unittest.mock import AsyncMock, patch
from yanghao.portlink.client import PortLinkClient


class TestPortLinkClient:
    """PortLinkClient 类的测试用例"""
    
    def test_init_default_server(self):
        """测试默认服务器地址初始化"""
        client = PortLinkClient()
        assert client.server_uri == "ws://106.75.139.203:8080/ws"
        assert client.websocket is None
        assert client.tunnel_addr is None
    
    def test_init_custom_server(self):
        """测试自定义服务器地址初始化"""
        custom_uri = "ws://localhost:8080/ws"
        client = PortLinkClient(server_uri=custom_uri)
        assert client.server_uri == custom_uri
        assert client.websocket is None
        assert client.tunnel_addr is None
    
    def test_get_tunnel_url_none(self):
        """测试未建立隧道时获取URL"""
        client = PortLinkClient()
        assert client.get_tunnel_url() is None
    
    def test_get_tunnel_url_with_address(self):
        """测试已建立隧道时获取URL"""
        client = PortLinkClient()
        client.tunnel_addr = "localhost:12345"
        assert client.get_tunnel_url() == "localhost:12345"
    
    @patch('logging.warning')
    def test_print_tunnel_info_no_tunnel(self, mock_warning):
        """测试打印隧道信息 - 无隧道"""
        client = PortLinkClient()
        client.print_tunnel_info()
        mock_warning.assert_called_once_with("Tunnel not yet established")

    @patch('logging.info')
    def test_print_tunnel_info_with_tunnel(self, mock_info):
        """测试打印隧道信息 - 有隧道"""
        client = PortLinkClient()
        client.tunnel_addr = "localhost:12345"
        client.remote_addr = "test.com:12345"
        client.print_tunnel_info()

        # 验证打印了正确的信息
        assert mock_info.call_count == 4


@pytest.mark.asyncio
class TestPortLinkClientAsync:
    """PortLinkClient 异步方法的测试用例"""
    
    async def test_context_manager_enter_exit(self):
        """测试异步上下文管理器"""
        with patch('websockets.connect') as mock_connect:
            mock_websocket = AsyncMock()
            mock_connect.return_value = mock_websocket
            
            client = PortLinkClient()
            
            # 测试 __aenter__
            result = await client.__aenter__()
            assert result is client
            assert client.websocket is mock_websocket
            mock_connect.assert_called_once_with(client.server_uri)
            
            # 测试 __aexit__
            await client.__aexit__(None, None, None)
            mock_websocket.close.assert_called_once()
    
    async def test_link_no_websocket(self):
        """测试未连接WebSocket时调用link方法"""
        client = PortLinkClient()
        
        with pytest.raises(ConnectionError, match="Client not connected"):
            await client.link(8080)
    
    async def test_link_successful_flow(self):
        """测试成功的link流程"""
        client = PortLinkClient()
        mock_websocket = AsyncMock()
        client.websocket = mock_websocket
        
        # 模拟服务器消息
        ready_msg = json.dumps({
            "type": "control",
            "status": "ready",
            "addr": "localhost:12345"
        })
        connected_msg = json.dumps({
            "type": "control",
            "status": "connected"
        })
        
        mock_websocket.recv.side_effect = [ready_msg, connected_msg]
        
        with patch('asyncio.open_connection') as mock_open_conn:
            mock_reader = AsyncMock()
            mock_writer = AsyncMock()
            mock_open_conn.return_value = (mock_reader, mock_writer)
            
            with patch.object(client, '_handle_local_connection') as mock_handle:
                await client.link(8080)
                
                assert client.tunnel_addr == "localhost:12345"
                mock_open_conn.assert_called_once_with('127.0.0.1', 8080)
                mock_handle.assert_called_once_with(mock_reader, mock_writer)
    
    async def test_link_connection_refused(self):
        """测试本地连接被拒绝的情况"""
        client = PortLinkClient()
        mock_websocket = AsyncMock()
        client.websocket = mock_websocket
        
        # 模拟服务器消息
        ready_msg = json.dumps({
            "type": "control",
            "status": "ready",
            "addr": "localhost:12345"
        })
        connected_msg = json.dumps({
            "type": "control",
            "status": "connected"
        })
        
        mock_websocket.recv.side_effect = [ready_msg, connected_msg]
        
        with patch('asyncio.open_connection') as mock_open_conn:
            mock_open_conn.side_effect = ConnectionRefusedError()

            with patch('logging.error') as mock_error:
                await client.link(8080)
                mock_error.assert_called_once()
    
    async def test_receive_from_ws_binary_data(self):
        """测试接收二进制数据"""
        client = PortLinkClient()
        mock_websocket = AsyncMock()
        client.websocket = mock_websocket
        
        mock_writer = AsyncMock()
        
        # 模拟二进制数据
        binary_data = b"test data"
        mock_websocket.__aiter__.return_value = [binary_data]
        
        await client._receive_from_ws(mock_writer)
        
        # 验证数据被写入
        mock_writer.write.assert_called_once_with(binary_data)
        mock_writer.drain.assert_called_once()
    
    async def test_send_to_ws(self):
        """测试发送数据到WebSocket"""
        client = PortLinkClient()
        mock_websocket = AsyncMock()
        client.websocket = mock_websocket
        
        mock_reader = AsyncMock()
        test_data = b"test data"
        mock_reader.read.side_effect = [test_data, b'']  # 第二次返回空表示结束
        
        await client._send_to_ws(mock_reader)
        
        # 验证数据被发送
        mock_websocket.send.assert_called_once_with(test_data)
        mock_reader.read.assert_called_with(4096)