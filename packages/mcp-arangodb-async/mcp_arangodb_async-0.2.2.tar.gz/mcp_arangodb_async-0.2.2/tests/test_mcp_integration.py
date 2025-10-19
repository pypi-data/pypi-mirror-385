"""Integration tests for MCP server functionality."""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
from mcp_arangodb_async.entry import server, _json_content
from mcp_arangodb_async.models import QueryArgs, InsertArgs, BackupArgs
import mcp.types as types


class TestMCPIntegration:
    """Test MCP server integration and tool execution."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_db = Mock()
        self.mock_client = Mock()

    def test_json_content_helper(self):
        """Test JSON content conversion helper."""
        data = {"test": "value", "number": 42}
        result = _json_content(data)
        
        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        assert result[0].type == "text"
        
        parsed_data = json.loads(result[0].text)
        assert parsed_data == {"test": "value", "number": 42}

    @pytest.mark.asyncio
    async def test_list_tools(self):
        """Test MCP tool listing."""
        tools = await server._handlers["list_tools"]()

        assert len(tools) == 7
        tool_names = [tool.name for tool in tools]

        expected_tools = [
            "arango_query",
            "arango_list_collections",
            "arango_insert",
            "arango_update",
            "arango_remove",
            "arango_create_collection",
            "arango_backup"
        ]

        for expected in expected_tools:
            assert expected in tool_names

    @pytest.mark.asyncio
    async def test_list_tools_full_set(self):
        """Test MCP tool listing with full tool set including new graph management tools."""
        with patch.dict('os.environ', {'MCP_COMPAT_TOOLSET': 'full'}):
            tools = await server._handlers["list_tools"]()

            tool_names = [tool.name for tool in tools]

            # Test that new graph management tools are included
            new_graph_tools = [
                "arango_backup_graph",
                "arango_restore_graph",
                "arango_backup_named_graphs",
                "arango_validate_graph_integrity",
                "arango_graph_statistics"
            ]

            for tool in new_graph_tools:
                assert tool in tool_names, f"New graph tool {tool} not found in tool list"

            # Verify we have significantly more tools now
            assert len(tools) >= 24  # Original + new graph tools

    @pytest.mark.asyncio
    async def test_call_tool_validation_error(self):
        """Test tool call with validation error."""
        # Mock server context
        with patch.object(server, 'request_context') as mock_ctx:
            mock_ctx.lifespan_context = {"db": self.mock_db, "client": self.mock_client}
            
            # Call with invalid arguments (missing required query)
            result = await server._handlers["call_tool"]("arango_query", {})
            
            assert len(result) == 1
            response_data = json.loads(result[0].text)
            assert "error" in response_data
            assert response_data["error"] == "ValidationError"

    @pytest.mark.asyncio
    async def test_call_tool_database_unavailable(self):
        """Test tool call when database is unavailable."""
        with patch.object(server, 'request_context') as mock_ctx:
            mock_ctx.lifespan_context = {"db": None, "client": None}
            
            result = await server._handlers["call_tool"]("arango_query", {"query": "RETURN 1"})
            
            assert len(result) == 1
            response_data = json.loads(result[0].text)
            assert response_data["error"] == "Database unavailable"

    @pytest.mark.asyncio
    @patch('mcp_arangodb_async.entry.handle_arango_query')
    async def test_call_tool_query_success(self, mock_handler):
        """Test successful query tool call."""
        # Setup
        mock_handler.return_value = [{"result": "success"}]
        
        with patch.object(server, 'request_context') as mock_ctx:
            mock_ctx.lifespan_context = {"db": self.mock_db, "client": self.mock_client}
            
            result = await server._handlers["call_tool"]("arango_query", {
                "query": "RETURN 1",
                "bind_vars": {"test": "value"}
            })
            
            assert len(result) == 1
            response_data = json.loads(result[0].text)
            assert response_data == [{"result": "success"}]
            
            # Verify handler was called with validated args
            mock_handler.assert_called_once()
            call_args = mock_handler.call_args[1]  # Get the args dict
            assert call_args["query"] == "RETURN 1"
            assert call_args["bind_vars"] == {"test": "value"}

    @pytest.mark.asyncio
    @patch('mcp_arangodb_async.entry.handle_list_collections')
    async def test_call_tool_list_collections_success(self, mock_handler):
        """Test successful list collections tool call."""
        mock_handler.return_value = ["users", "products"]
        
        with patch.object(server, 'request_context') as mock_ctx:
            mock_ctx.lifespan_context = {"db": self.mock_db, "client": self.mock_client}
            
            result = await server._handlers["call_tool"]("arango_list_collections", {})
            
            assert len(result) == 1
            response_data = json.loads(result[0].text)
            assert response_data == ["users", "products"]

    @pytest.mark.asyncio
    @patch('mcp_arangodb_async.entry.handle_insert')
    async def test_call_tool_insert_success(self, mock_handler):
        """Test successful insert tool call."""
        mock_handler.return_value = {"_id": "users/123", "_key": "123", "_rev": "_abc"}
        
        with patch.object(server, 'request_context') as mock_ctx:
            mock_ctx.lifespan_context = {"db": self.mock_db, "client": self.mock_client}
            
            result = await server._handlers["call_tool"]("arango_insert", {
                "collection": "users",
                "document": {"name": "John", "age": 30}
            })
            
            assert len(result) == 1
            response_data = json.loads(result[0].text)
            assert response_data["_id"] == "users/123"

    @pytest.mark.asyncio
    async def test_call_tool_unknown_tool(self):
        """Test call to unknown tool."""
        with patch.object(server, 'request_context') as mock_ctx:
            mock_ctx.lifespan_context = {"db": self.mock_db, "client": self.mock_client}
            
            result = await server._handlers["call_tool"]("unknown_tool", {})
            
            assert len(result) == 1
            response_data = json.loads(result[0].text)
            assert "Unknown tool" in response_data["error"]

    @pytest.mark.asyncio
    @patch('mcp_arangodb_async.entry.handle_arango_query')
    async def test_call_tool_handler_exception(self, mock_handler):
        """Test tool call when handler raises exception."""
        mock_handler.side_effect = Exception("Handler error")
        
        with patch.object(server, 'request_context') as mock_ctx:
            mock_ctx.lifespan_context = {"db": self.mock_db, "client": self.mock_client}
            
            result = await server._handlers["call_tool"]("arango_query", {"query": "RETURN 1"})
            
            assert len(result) == 1
            response_data = json.loads(result[0].text)
            assert response_data["error"] == "Handler error"
            assert response_data["tool"] == "arango_query"

    @pytest.mark.asyncio
    @patch('mcp_arangodb_async.entry.handle_backup_graph')
    async def test_call_tool_backup_graph_success(self, mock_handler):
        """Test successful backup graph tool call."""
        mock_handler.return_value = {
            "graph_name": "test_graph",
            "output_dir": "/tmp/backup",
            "total_documents": 100,
            "metadata_included": True
        }

        with patch.object(server, 'request_context') as mock_ctx:
            mock_ctx.lifespan_context = {"db": self.mock_db, "client": self.mock_client}

            result = await server._handlers["call_tool"](
                "arango_backup_graph",
                {"graph_name": "test_graph", "output_dir": "/tmp/backup"}
            )

            assert len(result) == 1
            response_data = json.loads(result[0].text)
            assert response_data["graph_name"] == "test_graph"
            assert response_data["total_documents"] == 100
            mock_handler.assert_called_once()

    @pytest.mark.asyncio
    async def test_call_tool_backup_graph_validation_error(self):
        """Test backup graph tool call with validation error."""
        with patch.object(server, 'request_context') as mock_ctx:
            mock_ctx.lifespan_context = {"db": self.mock_db, "client": self.mock_client}

            # Missing required graph_name field
            result = await server._handlers["call_tool"]("arango_backup_graph", {})

            assert len(result) == 1
            response_data = json.loads(result[0].text)
            assert "error" in response_data
            assert response_data["error"] == "ValidationError"
            assert "details" in response_data

    @pytest.mark.asyncio
    @patch('mcp_arangodb_async.entry.handle_graph_statistics')
    async def test_call_tool_graph_statistics_with_aliases(self, mock_handler):
        """Test graph statistics tool call with field aliases."""
        mock_handler.return_value = {
            "graphs_analyzed": 1,
            "statistics": [{"graph_name": "test", "total_vertices": 50}]
        }

        with patch.object(server, 'request_context') as mock_ctx:
            mock_ctx.lifespan_context = {"db": self.mock_db, "client": self.mock_client}

            # Use aliases (camelCase)
            result = await server._handlers["call_tool"](
                "arango_graph_statistics",
                {
                    "graphName": "test_graph",  # alias for graph_name
                    "includeDegreeDistribution": False,  # alias for include_degree_distribution
                    "sampleSize": 200  # alias for sample_size
                }
            )

            assert len(result) == 1
            response_data = json.loads(result[0].text)
            assert response_data["graphs_analyzed"] == 1

            # Verify handler was called with correct arguments
            mock_handler.assert_called_once()
            call_args = mock_handler.call_args[1]  # Get the args dict
            assert call_args["graph_name"] == "test_graph"
            assert call_args["include_degree_distribution"] is False
            assert call_args["sample_size"] == 200


class TestServerLifespan:
    """Test server lifespan management."""

    @pytest.mark.asyncio
    @patch('mcp_arangodb_async.entry.load_config')
    @patch('mcp_arangodb_async.entry.get_client_and_db')
    async def test_server_lifespan_success(self, mock_get_client, mock_load_config):
        """Test successful server lifespan initialization."""
        from mcp_arangodb_async.entry import server_lifespan
        
        # Setup mocks
        mock_config = Mock()
        mock_load_config.return_value = mock_config
        mock_client = Mock()
        mock_db = Mock()
        mock_get_client.return_value = (mock_client, mock_db)
        
        # Test lifespan context manager
        async with server_lifespan(server) as context:
            assert context["db"] == mock_db
            assert context["client"] == mock_client
        
        # Verify cleanup
        mock_client.close.assert_called_once()

    @pytest.mark.asyncio
    @patch('mcp_arangodb_async.entry.load_config')
    @patch('mcp_arangodb_async.entry.get_client_and_db')
    async def test_server_lifespan_connection_failure(self, mock_get_client, mock_load_config):
        """Test server lifespan with connection failure."""
        from mcp_arangodb_async.entry import server_lifespan
        
        # Setup mocks
        mock_config = Mock()
        mock_load_config.return_value = mock_config
        mock_get_client.side_effect = Exception("Connection failed")
        
        # Test lifespan context manager with connection failure
        async with server_lifespan(server) as context:
            assert context["db"] is None
            assert context["client"] is None

    @pytest.mark.asyncio
    @patch('mcp_arangodb_async.entry.load_config')
    @patch('mcp_arangodb_async.entry.get_client_and_db')
    async def test_server_lifespan_retry_logic(self, mock_get_client, mock_load_config):
        """Test server lifespan retry logic."""
        from mcp_arangodb_async.entry import server_lifespan
        
        # Setup mocks
        mock_config = Mock()
        mock_load_config.return_value = mock_config
        mock_client = Mock()
        mock_db = Mock()
        
        # First call fails, second succeeds
        mock_get_client.side_effect = [
            Exception("First attempt failed"),
            (mock_client, mock_db)
        ]
        
        with patch.dict('os.environ', {'ARANGO_CONNECT_RETRIES': '2', 'ARANGO_CONNECT_DELAY_SEC': '0.01'}):
            async with server_lifespan(server) as context:
                assert context["db"] == mock_db
                assert context["client"] == mock_client
        
        # Verify retry happened
        assert mock_get_client.call_count == 2
