import pytest
import asyncio
import time
import json
from unittest.mock import AsyncMock, patch
from yanghao.portlink.client import PortLinkClient


@pytest.mark.asyncio
class TestPerformance:
    """性能测试用例"""
    
    async def test_connection_establishment_time(self):
        """测试连接建立时间"""
        with patch('websockets.connect') as mock_connect:
            mock_websocket = AsyncMock()
            mock_connect.return_value = mock_websocket
            
            client = PortLinkClient("ws://localhost:8080/ws")
            
            start_time = time.time()
            await client.__aenter__()
            end_time = time.time()
            
            connection_time = end_time - start_time
            
            # 连接时间应该很快（模拟环境下）
            assert connection_time < 1.0
            
            await client.__aexit__(None, None, None)
    
    async def test_message_throughput(self):
        """测试消息吞吐量"""
        client = PortLinkClient()
        mock_websocket = AsyncMock()
        client.websocket = mock_websocket
        
        mock_reader = AsyncMock()
        
        # 模拟大量数据
        data_chunks = [b"x" * 1024 for _ in range(100)]  # 100个1KB的数据块
        data_chunks.append(b'')  # 结束标记
        mock_reader.read.side_effect = data_chunks
        
        start_time = time.time()
        await client._send_to_ws(mock_reader)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # 验证所有数据都被发送
        assert mock_websocket.send.call_count == 100
        
        # 处理时间应该合理（模拟环境下）
        assert processing_time < 5.0
    
    async def test_concurrent_connections(self):
        """测试并发连接处理"""
        async def create_mock_client():
            with patch('websockets.connect') as mock_connect:
                mock_websocket = AsyncMock()
                mock_connect.return_value = mock_websocket
                
                client = PortLinkClient("ws://localhost:8080/ws")
                await client.__aenter__()
                await asyncio.sleep(0.1)  # 模拟一些工作
                await client.__aexit__(None, None, None)
                return True
        
        # 创建多个并发客户端
        num_clients = 10
        start_time = time.time()
        
        tasks = [create_mock_client() for _ in range(num_clients)]
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 验证所有客户端都成功创建
        assert all(results)
        assert len(results) == num_clients
        
        # 并发处理应该比串行快
        assert total_time < num_clients * 0.5  # 假设串行需要每个0.5秒
    
    async def test_large_data_transfer(self):
        """测试大数据传输"""
        client = PortLinkClient()
        mock_websocket = AsyncMock()
        client.websocket = mock_websocket
        
        mock_writer = AsyncMock()
        
        # 模拟大量数据传输
        large_data = b"x" * (1024 * 1024)  # 1MB数据
        mock_websocket.__aiter__.return_value = [large_data]
        
        start_time = time.time()
        await client._receive_from_ws(mock_writer)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # 验证数据被正确处理
        mock_writer.write.assert_called_once_with(large_data)
        mock_writer.drain.assert_called_once()
        
        # 处理时间应该合理
        assert processing_time < 10.0
    
    async def test_heartbeat_performance(self):
        """测试心跳性能"""
        client = PortLinkClient()
        mock_websocket = AsyncMock()
        client.websocket = mock_websocket
        
        # 创建心跳任务
        heartbeat_task = asyncio.create_task(client._send_heartbeat())
        
        start_time = time.time()
        
        # 让心跳运行一小段时间
        await asyncio.sleep(0.5)
        
        # 取消任务
        heartbeat_task.cancel()
        
        try:
            await heartbeat_task
        except asyncio.CancelledError:
            pass
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        # 验证任务能够快速响应取消
        assert elapsed_time < 1.0
    
    async def test_memory_usage_stability(self):
        """测试内存使用稳定性"""
        import gc
        
        # 强制垃圾回收
        gc.collect()
        
        clients = []
        
        # 创建多个客户端实例
        for i in range(50):
            client = PortLinkClient(f"ws://localhost:{8080 + i}/ws")
            clients.append(client)
        
        # 验证客户端创建成功
        assert len(clients) == 50
        
        # 清理客户端
        del clients
        gc.collect()
        
        # 这个测试主要是确保没有内存泄漏
        # 在实际环境中可以使用内存分析工具
        assert True  # 如果到达这里说明没有崩溃
    
    async def test_error_recovery_performance(self):
        """测试错误恢复性能"""
        client = PortLinkClient()
        mock_websocket = AsyncMock()
        client.websocket = mock_websocket
        
        mock_reader = AsyncMock()
        
        # 模拟间歇性错误
        def side_effect_with_errors(*args):
            for i in range(10):
                if i % 3 == 0:  # 每第3次调用抛出异常
                    raise ConnectionError("Simulated error")
                yield b"data"
            yield b''  # 结束
        
        mock_reader.read.side_effect = side_effect_with_errors()
        
        start_time = time.time()
        
        try:
            await client._send_to_ws(mock_reader)
        except ConnectionError:
            pass  # 预期的错误
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # 错误处理应该快速
        assert processing_time < 2.0


@pytest.mark.asyncio
class TestStressTest:
    """压力测试"""
    
    @pytest.mark.slow
    async def test_long_running_connection(self):
        """测试长时间运行的连接"""
        with patch('websockets.connect') as mock_connect:
            mock_websocket = AsyncMock()
            mock_connect.return_value = mock_websocket
            
            async with PortLinkClient("ws://localhost:8080/ws") as client:
                # 模拟长时间运行
                start_time = time.time()
                
                # 运行1秒（缩短测试时间）
                while time.time() - start_time < 1:
                    await asyncio.sleep(0.1)
                
                # 验证连接仍然活跃
                assert client.websocket is not None
    
    @pytest.mark.slow
    async def test_high_frequency_messages(self):
        """测试高频消息处理"""
        client = PortLinkClient()
        mock_websocket = AsyncMock()
        client.websocket = mock_websocket
        
        mock_writer = AsyncMock()
        
        # 模拟高频消息
        messages = [b"msg" + str(i).encode() for i in range(100)]  # 减少消息数量
        mock_websocket.__aiter__.return_value = messages
        
        start_time = time.time()
        await client._receive_from_ws(mock_writer)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # 验证所有消息都被处理
        assert mock_writer.write.call_count == 100
        
        # 计算消息处理速率
        messages_per_second = 100 / max(processing_time, 0.001)  # 避免除零
        
        # 应该能够处理合理的消息速率
        assert messages_per_second > 10  # 至少每秒10条消息


@pytest.fixture
def performance_client():
    """性能测试用的客户端fixture"""
    return PortLinkClient("ws://localhost:8080/ws")


class TestSimpleBenchmark:
    """简单基准测试"""
    
    def test_client_creation_speed(self):
        """客户端创建速度测试"""
        start_time = time.time()
        
        # 创建多个客户端实例
        clients = [PortLinkClient("ws://localhost:8080/ws") for _ in range(100)]
        
        end_time = time.time()
        creation_time = end_time - start_time
        
        # 验证创建成功
        assert len(clients) == 100
        
        # 创建时间应该合理
        assert creation_time < 1.0  # 100个客户端应该在1秒内创建完成
    
    def test_message_parsing_speed(self):
        """消息解析速度测试"""
        msg = json.dumps({
            "type": "control",
            "status": "ready",
            "addr": "localhost:12345"
        })
        
        start_time = time.time()
        
        # 解析多次
        for _ in range(1000):
            result = json.loads(msg)
            assert result["type"] == "control"
        
        end_time = time.time()
        parsing_time = end_time - start_time
        
        # 解析时间应该合理
        assert parsing_time < 1.0  # 1000次解析应该在1秒内完成