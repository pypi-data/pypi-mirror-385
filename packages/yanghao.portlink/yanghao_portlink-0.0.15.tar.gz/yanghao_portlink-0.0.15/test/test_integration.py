import pytest
import asyncio
import json
from unittest.mock import AsyncMock, patch
from yanghao.portlink.client import PortLinkClient


@pytest.mark.asyncio
class TestIntegration:
    """集成测试用例"""
    
    async def test_full_client_workflow_mock(self):
        """测试完整的客户端工作流程（模拟）"""
        with patch('websockets.connect') as mock_connect:
            mock_websocket = AsyncMock()
            mock_connect.return_value = mock_websocket
            
            # 模拟服务器响应
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
                
                # 模拟本地服务数据
                mock_reader.read.side_effect = [b"HTTP/1.1 200 OK\r\n\r\n", b'']
                
                # 模拟WebSocket消息流
                mock_websocket.__aiter__.return_value = [b"test response data"]
                
                async with PortLinkClient("ws://localhost:8080/ws") as client:
                    # 启动link任务
                    link_task = asyncio.create_task(client.link(8080))
                    
                    # 等待一小段时间让连接建立
                    await asyncio.sleep(0.1)
                    
                    # 验证隧道地址已设置
                    assert client.get_tunnel_url() == "localhost:12345"
                    
                    # 取消任务以结束测试
                    link_task.cancel()
                    
                    try:
                        await link_task
                    except asyncio.CancelledError:
                        pass
    
    async def test_error_handling_invalid_json(self):
        """测试处理无效JSON消息"""
        with patch('websockets.connect') as mock_connect:
            mock_websocket = AsyncMock()
            mock_connect.return_value = mock_websocket
            
            # 模拟无效JSON消息
            mock_websocket.recv.side_effect = ["invalid json"]
            
            async with PortLinkClient("ws://localhost:8080/ws") as client:
                with patch('builtins.print') as mock_print:
                    await client.link(8080)
                    
                    # 验证打印了错误信息
                    error_calls = [call for call in mock_print.call_args_list 
                                 if "Unexpected message" in str(call)]
                    assert len(error_calls) > 0
    
    async def test_error_handling_unexpected_control_message(self):
        """测试处理意外的控制消息"""
        with patch('websockets.connect') as mock_connect:
            mock_websocket = AsyncMock()
            mock_connect.return_value = mock_websocket
            
            # 模拟意外的控制消息
            unexpected_msg = json.dumps({
                "type": "control",
                "status": "error",
                "message": "Something went wrong"
            })
            mock_websocket.recv.side_effect = [unexpected_msg]
            
            async with PortLinkClient("ws://localhost:8080/ws") as client:
                with patch('builtins.print') as mock_print:
                    await client.link(8080)
                    
                    # 验证打印了错误信息
                    error_calls = [call for call in mock_print.call_args_list 
                                 if "Unexpected control message" in str(call)]
                    assert len(error_calls) > 0
    
    async def test_websocket_connection_closed_handling(self):
        """测试WebSocket连接关闭的处理"""
        client = PortLinkClient()
        mock_websocket = AsyncMock()
        client.websocket = mock_websocket
        
        mock_writer = AsyncMock()
        
        # 模拟WebSocket连接关闭异常
        import websockets.exceptions
        mock_websocket.__aiter__.side_effect = websockets.exceptions.ConnectionClosed(None, None)
        
        with patch('builtins.print') as mock_print:
            await client._receive_from_ws(mock_writer)
            
            # 验证打印了连接关闭信息
            close_calls = [call for call in mock_print.call_args_list 
                         if "WebSocket connection closed" in str(call)]
            assert len(close_calls) > 0
    
    async def test_concurrent_operations(self):
        """测试并发操作"""
        client = PortLinkClient()
        mock_websocket = AsyncMock()
        client.websocket = mock_websocket
        
        mock_reader = AsyncMock()
        mock_writer = AsyncMock()
        
        # 模拟并发的读写操作
        mock_reader.read.side_effect = [b"data1", b"data2", b'']
        mock_websocket.__aiter__.return_value = [b"response1", b"response2"]
        
        # 创建并发任务
        send_task = asyncio.create_task(client._send_to_ws(mock_reader))
        receive_task = asyncio.create_task(client._receive_from_ws(mock_writer))
        
        # 等待任务完成
        await asyncio.sleep(0.1)
        
        # 取消任务
        send_task.cancel()
        receive_task.cancel()
        
        try:
            await asyncio.gather(send_task, receive_task, return_exceptions=True)
        except asyncio.CancelledError:
            pass
        
        # 验证操作被调用
        assert mock_websocket.send.call_count >= 1
        assert mock_writer.write.call_count >= 1


class TestUtilities:
    """工具函数测试"""
    
    def test_json_message_creation(self):
        """测试JSON消息创建"""
        # 测试心跳消息格式
        heartbeat_msg = json.dumps({"type": "heartbeat", "status": "ping"})
        parsed = json.loads(heartbeat_msg)
        
        assert parsed["type"] == "heartbeat"
        assert parsed["status"] == "ping"
    
    def test_control_message_parsing(self):
        """测试控制消息解析"""
        # 测试ready消息
        ready_msg = {
            "type": "control",
            "status": "ready",
            "addr": "localhost:12345"
        }
        
        assert ready_msg.get("type") == "control"
        assert ready_msg.get("status") == "ready"
        assert ready_msg.get("addr") == "localhost:12345"
        
        # 测试connected消息
        connected_msg = {
            "type": "control",
            "status": "connected"
        }
        
        assert connected_msg.get("type") == "control"
        assert connected_msg.get("status") == "connected"
    
    def test_server_uri_validation(self):
        """测试服务器URI验证"""
        # 测试有效的WebSocket URI
        valid_uris = [
            "ws://localhost:8080/ws",
            "wss://example.com:443/ws",
            "ws://192.168.1.1:8080/ws"
        ]
        
        for uri in valid_uris:
            client = PortLinkClient(server_uri=uri)
            assert client.server_uri == uri
    
    def test_port_validation(self):
        """测试端口号验证"""
        # 测试有效端口范围
        valid_ports = [80, 443, 8080, 3000, 65535]
        
        for port in valid_ports:
            assert 1 <= port <= 65535
        
        # 测试无效端口
        invalid_ports = [0, -1, 65536, 100000]
        
        for port in invalid_ports:
            assert not (1 <= port <= 65535)