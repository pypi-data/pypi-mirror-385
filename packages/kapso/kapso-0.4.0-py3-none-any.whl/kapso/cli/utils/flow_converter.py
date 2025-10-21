"""
Flow JSON to Python code converter.

Converts API flow JSON to executable Python code using the Flow Builder SDK.
"""

from typing import Dict, Any, List, Set
import json


def convert_flow_to_python(flow_data: Dict[str, Any]) -> str:
    """
    Convert flow JSON/dict structure to Python code using Flow Builder SDK.
    
    Args:
        flow_data: Flow data dictionary from API
        
    Returns:
        Python code string
    """
    lines = []
    
    # Add header with flow info
    lines.append('"""')
    flow_name = escape_python_string(flow_data.get("name", "Unnamed Flow"))
    lines.append(f'Flow: {flow_name}')
    
    if flow_data.get('description'):
        description = escape_python_string(flow_data["description"])
        lines.append(f'Description: {description}')
    
    lines.append('"""')
    lines.append('')
    
    # Get nodes and edges for processing
    definition = flow_data.get("definition", {})
    nodes = definition.get("nodes", [])
    edges = definition.get("edges", [])
    
    # Determine required imports
    required_imports = _determine_required_imports(nodes, edges)
    
    # Add imports
    lines.append('from kapso.builder.flows import Flow')
    for import_line in required_imports:
        lines.append(import_line)
    lines.append('')
    lines.append('')
    
    # Create flow
    lines.append('# Create the flow')
    flow_name_code = escape_python_string(flow_data.get("name", "My Flow"))
    lines.append('flow = Flow(')
    
    # Handle parameters with proper comma placement
    has_description = flow_data.get('description')
    name_line = f'    name="{flow_name_code}"'
    if has_description:
        name_line += ','
    lines.append(name_line)
    
    if has_description:
        description_code = escape_python_string(flow_data['description'])
        lines.append(f'    description="{description_code}"')
    
    lines.append(')')
    
    # Add nodes
    if nodes:
        lines.append('')
        lines.append('# Add nodes')
        for node in nodes:
            node_lines = _convert_node(node)
            lines.extend(node_lines)
    
    # Add edges
    if edges:
        lines.append('')
        lines.append('# Add edges') 
        for edge in edges:
            edge_lines = _convert_edge(edge)
            lines.extend(edge_lines)
    
    # Add validation call
    lines.append('')
    lines.append('# Validate the flow')
    lines.append('flow.validate()')
    
    return '\n'.join(lines)


def escape_python_string(s: str) -> str:
    """
    Escape a string for safe inclusion in Python code.
    
    Args:
        s: String to escape
        
    Returns:
        Escaped string safe for Python code
    """
    if not isinstance(s, str):
        s = str(s)
    
    # Escape backslashes first
    s = s.replace('\\', '\\\\')
    # Escape quotes
    s = s.replace('"', '\\"')
    # Escape common escape sequences
    s = s.replace('\n', '\\n')
    s = s.replace('\t', '\\t')
    s = s.replace('\r', '\\r')
    
    return s


def _determine_required_imports(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> List[str]:
    """
    Determine which imports are needed based on the nodes and edges.
    
    Args:
        nodes: List of node definitions
        edges: List of edge definitions
        
    Returns:
        List of import statements needed
    """
    imports = set()
    node_types = set()
    needs_aifield = False
    
    # Collect node types and check for AIField usage
    for node in nodes:
        node_type = node.get("data", {}).get("node_type", "")
        node_types.add(node_type)
        
        # Check if any field uses AIField marker
        config = node.get("data", {}).get("config", {})
        for value in config.values():
            if isinstance(value, dict) and value == {"$ai": {}}:
                needs_aifield = True
                break
    
    # Always import Edge if there are edges
    if edges:
        imports.add("from kapso.builder.flows.edges import Edge")
    
    # Import AIField if needed
    if needs_aifield:
        imports.add("from kapso.builder.ai.field import AIField")
    
    # Import Condition if DecideNode is used
    if "decide" in node_types:
        imports.add("from kapso.builder.flows.nodes.decide import Condition")
    
    # Import FlowAgent classes if AgentNode is used
    if "agent" in node_types:
        imports.add("from kapso.builder.flows.nodes.agent import FlowAgentWebhook, FlowAgentMcpServer, FlowAgentKnowledgeBase")
    
    # Map node types to imports
    if node_types:
        node_imports = []
        if "start" in node_types:
            node_imports.append("StartNode")
        if "send_text" in node_types:
            node_imports.append("SendTextNode") 
        if "wait_for_response" in node_types:
            node_imports.append("WaitForResponseNode")
        if "decide" in node_types:
            node_imports.append("DecideNode")
        if "agent" in node_types:
            node_imports.append("AgentNode")
        if "send_interactive" in node_types:
            node_imports.append("SendInteractiveNode")
        if "send_template" in node_types:
            node_imports.append("SendTemplateNode")
        if "function" in node_types:
            node_imports.append("FunctionNode")
        if "handoff" in node_types:
            node_imports.append("HandoffNode")
            
        if node_imports:
            imports.add(f"from kapso.builder.flows.nodes import {', '.join(sorted(node_imports))}")
    
    return sorted(list(imports))


def _convert_node(node: Dict[str, Any]) -> List[str]:
    """
    Convert a single node definition to Python code lines.
    
    Args:
        node: Node definition dictionary
        
    Returns:
        List of Python code lines for this node
    """
    lines = []
    node_id = node.get("id", "")
    data = node.get("data", {})
    node_type = data.get("node_type", "")
    config = data.get("config", {})
    
    if node_type == "start":
        lines.append(f'start_node = StartNode(')
        lines.append(f'    id="{escape_python_string(node_id)}"')
        lines.append(')')
        lines.append(f'flow.add_node(start_node)')
    
    elif node_type == "send_text":
        lines.append('send_text_node = SendTextNode(')

        params = [f'    id="{escape_python_string(node_id)}"']

        whatsapp_config_id = config.get("whatsapp_config_id")
        if whatsapp_config_id is not None:
            params.append(f'    whatsapp_config_id="{escape_python_string(whatsapp_config_id)}"')
        else:
            params.append('    whatsapp_config_id=None')

        message_value = config.get("message", "")
        if isinstance(message_value, dict) and message_value == {"$ai": {}}:
            params.append('    message=AIField()')
        else:
            params.append(f'    message="{escape_python_string(str(message_value))}"')

        provider_model_name = config.get("provider_model_name")
        if provider_model_name:
            params.append(
                f'    provider_model_name="{escape_python_string(provider_model_name)}"'
            )

        for idx, param in enumerate(params):
            suffix = ',' if idx < len(params) - 1 else ''
            lines.append(param + suffix)

        lines.append(')')
        lines.append(f'flow.add_node(send_text_node)')
    
    elif node_type == "wait_for_response":
        lines.append(f'wait_for_response_node = WaitForResponseNode(')
        lines.append(f'    id="{escape_python_string(node_id)}"')
        
        # Handle timeout configuration
        timeout_seconds = config.get("timeout_seconds")
        
        # Add timeout parameter if timeout_seconds is provided
        if timeout_seconds is not None:
            lines[-1] += ','  # Add comma to id line
            lines.append(f'    timeout_seconds={timeout_seconds}')
        
        lines.append(')')
        lines.append(f'flow.add_node(wait_for_response_node)')
    
    elif node_type == "decide":
        # First, create the conditions
        conditions_data = config.get("conditions", [])
        if conditions_data:
            lines.append('# Create conditions')
            for i, condition in enumerate(conditions_data):
                label = condition.get("label", "")
                description = condition.get("description", "")
                lines.append(f'condition_{i} = Condition(')
                lines.append(f'    label="{escape_python_string(label)}",')
                lines.append(f'    description="{escape_python_string(description)}"')
                lines.append(')')
            
            lines.append('')
        
        # Create the DecideNode
        lines.append(f'decide_node = DecideNode(')
        node_params = [f'    id="{escape_python_string(node_id)}"']

        decision_type = config.get("decision_type", "ai")
        provider_model_name = config.get("provider_model_name")
        if decision_type != "function" or provider_model_name:
            node_params.append(
                f'    provider_model_name="{escape_python_string(provider_model_name or "")}"'
            )

        if conditions_data:
            condition_refs = [f'condition_{i}' for i in range(len(conditions_data))]
            node_params.append(f'    conditions=[{", ".join(condition_refs)}]')
        else:
            node_params.append('    conditions=[]')

        if decision_type != "ai":
            node_params.append(
                f'    decision_type="{escape_python_string(decision_type)}"'
            )

        if decision_type == "function":
            function_id = config.get("function_id", "")
            node_params.append(f'    function_id="{escape_python_string(function_id)}"')
        else:
            llm_temperature = config.get("llm_temperature", "0.0")
            if str(llm_temperature) != "0.0":
                node_params.append(f'    llm_temperature={float(llm_temperature)}')

            llm_max_tokens = config.get("llm_max_tokens", 10000)
            if llm_max_tokens not in (None, 10000):
                node_params.append(f'    llm_max_tokens={int(llm_max_tokens)}')
        
        for index, param in enumerate(node_params):
            suffix = ',' if index < len(node_params) - 1 else ''
            lines.append(f'{param}{suffix}')

        lines.append(')')
        lines.append(f'flow.add_node(decide_node)')
    
    elif node_type == "send_interactive":
        lines.append('send_interactive_node = SendInteractiveNode(')

        params = [f'    id="{escape_python_string(node_id)}"']

        whatsapp_config_id = config.get("whatsapp_config_id")
        if whatsapp_config_id is not None:
            params.append(f'    whatsapp_config_id="{escape_python_string(whatsapp_config_id)}"')
        else:
            params.append('    whatsapp_config_id=None')

        params.append(
            f'    interactive_type="{escape_python_string(config.get("interactive_type", "button"))}"'
        )

        body_text = config.get("body_text", "")
        if isinstance(body_text, dict) and body_text == {"$ai": {}}:
            params.append('    body_text=AIField()')
        else:
            params.append(f'    body_text="{escape_python_string(str(body_text))}"')

        if config.get("header_type"):
            params.append(f'    header_type="{escape_python_string(config["header_type"])}"')

        header_text = config.get("header_text")
        if header_text is not None:
            if isinstance(header_text, dict) and header_text == {"$ai": {}}:
                params.append('    header_text=AIField()')
            else:
                params.append(f'    header_text="{escape_python_string(str(header_text))}"')

        if config.get("header_media_url"):
            params.append(f'    header_media_url="{escape_python_string(config["header_media_url"])}"')

        footer_text = config.get("footer_text")
        if footer_text is not None:
            if isinstance(footer_text, dict) and footer_text == {"$ai": {}}:
                params.append('    footer_text=AIField()')
            else:
                params.append(f'    footer_text="{escape_python_string(str(footer_text))}"')

        if config.get("buttons"):
            params.append(f'    buttons={repr(config.get("buttons"))}')

        if config.get("list_button_text"):
            params.append(f'    list_button_text="{escape_python_string(config["list_button_text"])}"')

        if config.get("list_sections"):
            params.append(f'    list_sections={repr(config.get("list_sections"))}')

        if config.get("cta_display_text"):
            params.append(f'    cta_display_text="{escape_python_string(config["cta_display_text"])}"')

        if config.get("cta_url"):
            params.append(f'    cta_url="{escape_python_string(config["cta_url"])}"')

        if config.get("flow_id"):
            params.append(f'    flow_id="{escape_python_string(config["flow_id"])}"')

        if config.get("flow_cta"):
            params.append(f'    flow_cta="{escape_python_string(config["flow_cta"])}"')

        if config.get("flow_token"):
            params.append(f'    flow_token="{escape_python_string(config["flow_token"])}"')

        provider_model_name = config.get("provider_model_name")
        if provider_model_name:
            params.append(
                f'    provider_model_name="{escape_python_string(provider_model_name)}"'
            )

        for idx, param in enumerate(params):
            suffix = ',' if idx < len(params) - 1 else ''
            lines.append(param + suffix)

        lines.append(')')
        lines.append(f'flow.add_node(send_interactive_node)')
    
    elif node_type == "agent":
        # Create webhooks first if they exist
        webhooks_data = config.get("flow_agent_webhooks", [])
        if webhooks_data:
            lines.append('# Create webhooks')
            for i, webhook in enumerate(webhooks_data):
                lines.append(f'webhook_{i} = FlowAgentWebhook(')
                lines.append(f'    name="{escape_python_string(webhook.get("name", ""))}",')
                lines.append(f'    url="{escape_python_string(webhook.get("url", ""))}",')
                lines.append(f'    description="{escape_python_string(webhook.get("description", ""))}",')
                lines.append(f'    http_method="{escape_python_string(webhook.get("http_method", "POST"))}",')
                
                # Handle headers - parse JSON string if needed
                headers = webhook.get("headers", "{}")
                if isinstance(headers, str):
                    try:
                        headers_dict = json.loads(headers) if headers else {}
                        lines.append(f'    headers={repr(headers_dict)},')
                    except (json.JSONDecodeError, ValueError):
                        lines.append(f'    headers={{}},')
                else:
                    lines.append(f'    headers={repr(headers)},')
                
                # Handle body - parse JSON string if needed  
                body = webhook.get("body", "{}")
                if isinstance(body, str):
                    try:
                        body_dict = json.loads(body) if body else {}
                        lines.append(f'    body={repr(body_dict)},')
                    except (json.JSONDecodeError, ValueError):
                        lines.append(f'    body={{}},')
                else:
                    lines.append(f'    body={repr(body)},')
                
                # Handle body_schema
                body_schema = webhook.get("body_schema")
                if body_schema:
                    if isinstance(body_schema, dict):
                        lines.append(f'    body_schema={repr(body_schema)},')
                    else:
                        lines.append(f'    body_schema="{escape_python_string(str(body_schema))}",')
                
                # Handle jmespath_query (last parameter, no comma)
                jmespath_query = webhook.get("jmespath_query")
                if jmespath_query:
                    lines.append(f'    jmespath_query="{escape_python_string(jmespath_query)}"')
                else:
                    # Remove comma from last parameter
                    if lines[-1].endswith(','):
                        lines[-1] = lines[-1][:-1]
                
                lines.append(')')
            lines.append('')
        
        # Create MCP servers if they exist
        mcp_servers_data = config.get("flow_agent_mcp_servers", [])
        if mcp_servers_data:
            lines.append('# Create MCP servers')
            for i, mcp_server in enumerate(mcp_servers_data):
                lines.append(f'mcp_server_{i} = FlowAgentMcpServer(')
                lines.append(f'    name="{escape_python_string(mcp_server.get("name", ""))}",')
                lines.append(f'    url="{escape_python_string(mcp_server.get("url", ""))}",')
                lines.append(f'    description="{escape_python_string(mcp_server.get("description", ""))}",')
                
                # Handle headers - parse JSON string if needed
                headers = mcp_server.get("headers", "{}")
                if isinstance(headers, str):
                    try:
                        headers_dict = json.loads(headers) if headers else {}
                        lines.append(f'    headers={repr(headers_dict)}')
                    except (json.JSONDecodeError, ValueError):
                        lines.append(f'    headers={{}}')
                else:
                    lines.append(f'    headers={repr(headers)}')
                
                lines.append(')')
            lines.append('')
        
        # Create knowledge bases if they exist
        knowledge_bases_data = config.get("flow_agent_knowledge_bases", [])
        if knowledge_bases_data:
            lines.append('# Create knowledge bases')
            for i, kb in enumerate(knowledge_bases_data):
                lines.append(f'knowledge_base_{i} = FlowAgentKnowledgeBase(')
                lines.append(f'    name="{escape_python_string(kb.get("name", ""))}",')
                lines.append(f'    knowledge_base_text="{escape_python_string(kb.get("knowledge_base_text", ""))}",')
                lines.append(f'    description="{escape_python_string(kb.get("description", ""))}"')
                lines.append(')')
            lines.append('')
        
        # Create the AgentNode
        lines.append(f'agent_node = AgentNode(')
        lines.append(f'    id="{escape_python_string(node_id)}",')
        lines.append(f'    system_prompt="{escape_python_string(config.get("system_prompt", ""))}",')
        lines.append(f'    provider_model_name="{escape_python_string(config.get("provider_model_name", ""))}",')
        
        # Handle optional parameters
        temperature = config.get("temperature", "0.0")
        if temperature != "0.0":
            # Convert string to float if needed
            temp_value = float(temperature) if isinstance(temperature, str) else temperature
            lines.append(f'    temperature={temp_value},')
        
        max_iterations = config.get("max_iterations", 80)
        if max_iterations != 80:  # SDK default
            lines.append(f'    max_iterations={max_iterations},')
        
        max_tokens = config.get("max_tokens", 8192)
        if max_tokens != 8192:  # SDK default
            lines.append(f'    max_tokens={max_tokens},')
        
        reasoning_effort = config.get("reasoning_effort")
        if reasoning_effort:
            lines.append(f'    reasoning_effort="{escape_python_string(reasoning_effort)}",')
        
        # Add webhooks list if any
        if webhooks_data:
            webhook_refs = [f'webhook_{i}' for i in range(len(webhooks_data))]
            lines.append(f'    webhooks=[{", ".join(webhook_refs)}],')
        
        # Add MCP servers list if any
        if mcp_servers_data:
            mcp_server_refs = [f'mcp_server_{i}' for i in range(len(mcp_servers_data))]
            lines.append(f'    mcp_servers=[{", ".join(mcp_server_refs)}],')
        
        # Add knowledge bases list if any
        if knowledge_bases_data:
            kb_refs = [f'knowledge_base_{i}' for i in range(len(knowledge_bases_data))]
            lines.append(f'    knowledge_bases=[{", ".join(kb_refs)}],')
        
        # Remove trailing comma from last parameter
        if lines[-1].endswith(','):
            lines[-1] = lines[-1][:-1]
        
        lines.append(')')
        lines.append(f'flow.add_node(agent_node)')
    
    elif node_type == "send_template":
        lines.append('send_template_node = SendTemplateNode(')

        params = [f'    id="{escape_python_string(node_id)}"']

        whatsapp_config_id = config.get("whatsapp_config_id")
        if whatsapp_config_id is not None:
            params.append(f'    whatsapp_config_id="{escape_python_string(whatsapp_config_id)}"')
        else:
            params.append('    whatsapp_config_id=None')

        params.append(f'    template_id="{escape_python_string(config.get("template_id", ""))}"')

        parameters_value = config.get("parameters") or config.get("template_params")
        if parameters_value is not None:
            params.append(f'    parameters={repr(parameters_value)}')

        for idx, param in enumerate(params):
            suffix = ',' if idx < len(params) - 1 else ''
            lines.append(param + suffix)

        lines.append(')')
        lines.append(f'flow.add_node(send_template_node)')
    
    elif node_type == "function":
        lines.append(f'function_node = FunctionNode(')
        lines.append(f'    id="{escape_python_string(node_id)}",')
        lines.append(f'    function_id="{escape_python_string(config.get("function_id", ""))}",')
        
        # Handle optional save_response_to
        save_response_to = config.get("save_response_to")
        if save_response_to:
            lines.append(f'    save_response_to="{escape_python_string(save_response_to)}",')
        
        # Remove trailing comma from last parameter
        if lines[-1].endswith(','):
            lines[-1] = lines[-1][:-1]
        
        lines.append(')')
        lines.append(f'flow.add_node(function_node)')
    
    elif node_type == "handoff":
        lines.append(f'handoff_node = HandoffNode(')
        lines.append(f'    id="{escape_python_string(node_id)}"')
        lines.append(')')
        lines.append(f'flow.add_node(handoff_node)')
    
    # TODO: Add other node types
    else:
        lines.append(f'# TODO: Unsupported node type: {node_type}')
        lines.append(f'# Node ID: {node_id}')
    
    return lines


def _convert_edge(edge: Dict[str, Any]) -> List[str]:
    """
    Convert a single edge definition to Python code lines.
    
    Args:
        edge: Edge definition dictionary
        
    Returns:
        List of Python code lines for this edge
    """
    lines = []
    source = edge.get("source", "")
    target = edge.get("target", "")
    label = edge.get("label", "next")
    
    lines.append(f'flow.add_edge(')
    lines.append(f'    source="{escape_python_string(source)}",')
    lines.append(f'    target="{escape_python_string(target)}",')
    lines.append(f'    label="{escape_python_string(label)}"')
    lines.append(')')
    
    return lines
