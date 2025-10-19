import os
import json
import jinja2
import copy
import time
import concurrent.futures
from typing import List, Dict, Any, Optional, Union, Iterator
from functools import partial

from .schema import Endpoint, Response # Import Response
from .tool   import Tool, EndTaskTool
from .event  import Event, EventBroker
from .utils  import model_id
from .service import Service # Import the Service factory
from .schema import Endpoint
from .tool   import Tool, EndTaskTool, Workspace
from .event  import Event, EventBroker
from .utils  import model_id
from .mutilmodal import get_input_processor

# IncrementalXmlParser is no longer needed here as service handles parsing
# from .utils.parser import IncrementalXmlParser

class Agent:
    def __init__(
        self,
        name: str,
        description: str,
        input_parameters: List[Dict[str, Any]] = [],
        tools: List[Tool] = [],
        model_id: str = model_id,
        endpoint: Endpoint = Endpoint(),
        service_type: str = 'openai_compat', # New parameter for service type
        prompt_template_path: Optional[str] = None,
        target_lang:str = 'English',
        max_steps: int = 10,
        optimize_tool_call: bool = False
    ):
        """Initializes the Agent.

        Args:
            name (str): The name of the agent.
            description (str): A description of the agent's purpose.
            input_parameters (List[Dict[str, Any]]): A list of dictionaries describing the agent's input parameters.
            tools (List[Tool]): A list of tools available to the agent.
            endpoint (Endpoint): The API endpoint configuration for the language model.
            service_type (str): The type of service to use for the language model (e.g., 'openai_compat').
            model_id (str): The ID of the language model to use.
            prompt_template_path (Optional[str]): The path to a Jinja2 template for the system prompt.
            target_lang (str): The target language for the agent's responses.
            max_steps (int): The maximum number of steps the agent can take.
            optimize_tool_call (bool): If True, optimizes the tool-calling process by using a custom XML-based prompt mechanism instead of the native API tool-calling feature. This can be useful for models with weaker native tool-calling capabilities.
        """
        self.name = name
        self.description = description
        self.input_parameters = input_parameters
        self.model_id = model_id
        self.target_lang = target_lang
        self.optimize_tool_call = optimize_tool_call
        
        self.endpoint = endpoint
        self.service_type = service_type # Store service type
        self.max_steps = max_steps

        self.original_tools: List[Tool] = tools[:]
        
        # Bind self to workspace tools if they are provided directly
        processed_tools = []
        for tool in self.original_tools:
            # Check if the tool is the read_file method of a Workspace instance
            if tool.name == 'read_file' and hasattr(tool.func, '__self__') and isinstance(tool.func.__self__, Workspace):
                bound_func = partial(tool.func, agent=self)
                
                # Create a new tool with the agent parameter hidden from the LLM
                analysis = tool.func.__globals__['analyze_tool_function'](tool.func)
                new_params = [p for p in analysis['parameters'] if p['name'] != 'agent']
                
                agent_specific_tool = Tool(
                    func=bound_func,
                    name=tool.name,
                    description=tool.description,
                    parameters=new_params
                )
                processed_tools.append(agent_specific_tool)
            else:
                processed_tools.append(tool)

        self.tools: Dict[str, Tool] = {tool.name: tool for tool in processed_tools}
        
        if "end_task" in self.tools:
            print("Warning: A user-provided tool named 'end_task' is being overridden by the built-in final answer tool.")
        # 2. In any case, build in our standard EndTaskTool
        self.tools["end_task"] = EndTaskTool()

        self._api_tools: List[Dict[str, Any]] = [t.info for t in self.tools.values()]
        
        self.system_prompt: str = self._generate_system_prompt_from_template(prompt_template_path)
        
        self.history: List[Dict[str, Any]] = [{"role": "system", "content": self.system_prompt}]

        # Initialize the service using the factory, passing optimize_tool_call
        self.service = Service(
            endpoint=self.endpoint,
            service_type=self.service_type,
            optimize_tool_call=self.optimize_tool_call # Pass optimize_tool_call to the service
        )
        self._client: OpenAI = None
        self._init_client()

    def add_file(self, path: str, chunk_size: int = 4000, overlap: int = 200):
        """Processes a file, splits large text content into chunks, and adds it to history.

        Args:
            path (str): The path to the file.
            chunk_size (int): The size of each text chunk.
            overlap (int): The overlap between consecutive text chunks.
        """
        processor = get_input_processor(path)
        processed_outputs = processor.read_input(chunk_size=chunk_size, overlap=overlap)
        
        for data in processed_outputs:
            filename = data["source"]["filename"]
            content_list = data["content"]
            
            # Check if the content is text
            is_text = len(content_list) == 1 and content_list[0].get("type") == "text"

            if is_text:
                text = content_list[0]["text"]
                message = f"Content from '{filename}':\n\n{text}"
                self.history.append({"role": "user", "content": message})
            else:
                # For non-text content (e.g., images), add the content list directly
                self.history.append({"role": "user", "content": content_list})
    
    def _init_client(self,):
        """Initializes the OpenAI client with the provided API key and base URL."""
        prev = os.environ.get('OPENAI_API_KEY')
        os.environ['OPENAI_API_KEY'] = self.endpoint.api_key
        self._client = OpenAI(api_key=self.endpoint.api_key, base_url=self.endpoint.base_url)
        if prev:
            os.environ['OPENAI_API_KEY'] = prev
        
    def _configure_with_tools(self, tools: List[Tool], extra_context: Optional[Dict[str, Any]] = None):
        """Reconfigures the agent with a given list of tools and extra context.

        Args:
            tools (List[Tool]): The new list of tools to configure the agent with.
            extra_context (Optional[Dict[str, Any]]): Extra data to pass to the prompt template.
        """
        self.tools = {tool.name: tool for tool in tools}
        self.tools["end_task"] = EndTaskTool() # Make sure end_task is always present
        
        # Regenerate API tools and system prompt
        self._api_tools = [t.info for t in self.tools.values()]
        self.system_prompt = self._generate_system_prompt_from_template(
            getattr(self, '_prompt_template_path', None),
            extra_context=extra_context
        )
        self.reset() # Reset history to apply new system prompt


    def _generate_system_prompt_from_template(self, template_path: Optional[str] = None, extra_context: Optional[Dict[str, Any]] = None) -> str:
        """Loads and renders the system prompt from a Jinja2 template file.

        Args:
            template_path (Optional[str]): The path to the Jinja2 template file. 
                                           If None, a default path is used.
            extra_context (Optional[Dict[str, Any]]): Extra data to be injected into the template.

        Returns:
            str: The rendered system prompt.

        Raises:
            FileNotFoundError: If the template file is not found.
        """
        
        # If no template path is provided, use a default hard-coded path
        if template_path is None:
            # Assume the template file is in the prompts/ folder in the same directory as agent.py
            current_dir = os.path.dirname(os.path.abspath(__file__))
            template_path = os.path.join(current_dir, 'prompts', 'default_agent_prompt.md')
        try:
            # Set up Jinja2 environment to load templates from the file system
            template_dir = os.path.dirname(template_path)
            template_filename = os.path.basename(template_path)

            env = jinja2.Environment(
                loader=jinja2.FileSystemLoader(template_dir),
                trim_blocks=True, # Automatically remove the first newline after a template tag
                lstrip_blocks=True # Automatically remove leading spaces before a template tag
            )
            
            template = env.get_template(template_filename)
        except jinja2.TemplateNotFound:
            raise FileNotFoundError(f"Prompt template not found at: {template_path}")
        
        plain_tools = []
        agent_tools = []
        for tool in self.tools.values():
            if getattr(tool, 'is_agent_tool', False):
                agent_tools.append(tool)
            else:
                plain_tools.append(tool)

        # Prepare data to pass to the template
        template_data = {
            "agent_name": self.name,
            "agent_description": self.description,
            "plain_tools": plain_tools, # Pass plain tools
            "agent_tools": agent_tools, # Pass Agent tools
            "tools": list(self.tools.values()), # Still pass the full list of tools for future use
            "target_language": self.target_lang
        }
        
        if extra_context:
            template_data.update(extra_context)
        
        # Render the template
        base_prompt = template.render(template_data)

        if self.optimize_tool_call:
            # If tool call optimization is enabled, append the tool call prompt
            tool_call_prompt_path = os.path.join(os.path.dirname(template_path), 'tool_call.md')
            try:
                with open(tool_call_prompt_path, 'r', encoding='utf-8') as f:
                    tool_call_prompt = f.read()
                return base_prompt + "\n" + tool_call_prompt
            except FileNotFoundError:
                # Handle case where tool_call.md is not found, maybe log a warning
                pass
        
        return base_prompt

    def _execute_tool(self, tool_call: Dict[str, Any]) -> Any:
        """Executes a tool call.

        Args:
            tool_call (Dict[str, Any]): The tool call object from the language model.

        Returns:
            Any: The result of the tool execution, or an error message string.
        """
        tool_name = tool_call.function.name
        tool_to_run = self.tools.get(tool_name)
        
        if not tool_to_run:
            return f"Error: Tool '{tool_name}' not found."
            
        try:
            tool_args = json.loads(tool_call.function.arguments)
            return tool_to_run.execute(**tool_args)
        except Exception as e:
            return f"Error executing tool '{tool_name}': {e}"

    def run(self, stream: bool = True, resume: bool = False, **kwargs) -> Union[str, Iterator[Event]]:
        """Runs the main loop of the Agent.

        Args:
            stream (bool): If True, returns an event generator for real-time output.
                           If False, blocks until the task is complete and returns the final string.
            resume (bool): If True, continues from the existing history instead of resetting.
            **kwargs: Input parameters required to start the Agent.

        Returns:
            Union[str, Iterator[Event]]: The final result or the event stream.
        """
        if stream:
            return self._run_stream(resume=resume, **kwargs)
        else:
            # For non-streaming, we can simulate a simple event handler internally
            final_answer = ""
            for event in self._run_stream(resume=resume, **kwargs):
                if event.type == "end":
                    final_answer = event.payload.get("final_answer", "")
            return final_answer

    def _run_stream(self, resume: bool = False, **kwargs) -> Iterator[Event]:
        """Runs the main loop of the Agent as an event generator.

        This is the core method that drives the agent's think-act cycle. It
        communicates with the language model, executes tools, and yields
        events to report its progress.

        Args:
            resume (bool): If True, continues from the existing history.
            **kwargs: The input parameters for the task.

        Yields:
            Iterator[Event]: A stream of events representing the agent's activity.
        """
        start_time = time.time()
        last_step_time = start_time
        
        # Only reset history if it's a new run
        if not resume:
            self.reset()
            # 1. Construct initial input and yield start event
            initial_prompt = (
                "Task started. Here are your input parameters:\n"
                + json.dumps(kwargs, indent=2)
                + "\nNow, begin your work."
            )
            self.history.append({"role": "user", "content": initial_prompt})
            
            payload = copy.deepcopy(kwargs)
            payload["start_time"] = start_time
            yield Event(f"Agent:{self.name}", "start", payload)
        else:
            # If resuming, just yield a resume event
            yield Event(f"Agent:{self.name}", "resume", {"history_length": len(self.history)})
        
        # 2. "Think-Act" loop
        for step in range(self.max_steps):
            current_time = time.time()
            step_payload = {
                "current_step": step + 1,
                "current_time": current_time,
                "total_elapsed_time": current_time - start_time
            }
            if step > 0:
                step_payload["last_step_elapsed_time"] = current_time - last_step_time
            last_step_time = current_time
            
            yield Event(f"Agent:{self.name}", "step", step_payload)

            # 3. Think: Call LLM
            llm_params = {
                "model": self.model_id,
                "messages": self.history,
                "stream": True
            }
            if not self.optimize_tool_call:
                llm_params["tools"] = self._api_tools
                llm_params["tool_choice"] = "auto"
            
            # Use the service to get the completion stream
            response_stream = self.service.completion(**llm_params)

            # 4. Reassemble response from the stream using standardized Response objects
            full_response_content = ""
            full_reasoning_content = ""
            tool_calls_in_progress = [] # Accumulate tool calls across responses

            # Iterate over the standardized Response objects from the service
            for response_obj in response_stream:
                if response_obj.thinking:
                    full_reasoning_content += response_obj.thinking
                    yield Event(f"Agent:{self.name}", "reasoning_stream", {"content": response_obj.thinking})

                if response_obj.content:
                    full_response_content += response_obj.content
                    yield Event(f"Agent:{self.name}", "content_stream", {"content": response_obj.content})
                
                if response_obj.tool_calls:
                    for tc_info in response_obj.tool_calls:
                        if "delta" in tc_info: # This is a tool call chunk
                            tool_call_chunk = tc_info["delta"]
                            index = tc_info["index"]
                            
                            if index >= len(tool_calls_in_progress):
                                tool_calls_in_progress.append({"id": f"call_{index}", "type": "function", "function": {"name": "", "arguments": ""}})
                            
                            func = tool_calls_in_progress[index]['function']
                            if tool_call_chunk.get('name'):
                                func['name'] += tool_call_chunk['name']
                            if tool_call_chunk.get('arguments'):
                                func['arguments'] += tool_call_chunk['arguments']
                            
                            yield Event(f"Agent:{self.name}", "tool_call_stream", {"index": index, "delta": tool_call_chunk})
                        else: # This is a complete tool call (from the final Response object)
                            tool_calls_in_progress.append(tc_info)

            # Assemble the complete message to add to history
            assembled_message = {"role": "assistant"}
            if full_response_content:
                assembled_message["content"] = full_response_content
            
            # Filter and validate tool calls for history
            valid_tool_calls = []
            for i, tc in enumerate(tool_calls_in_progress):
                func = tc.get('function', {})
                if func.get('name') and func.get('arguments'):
                    try:
                        # Validate JSON arguments
                        json.loads(func['arguments'])
                        valid_tool_calls.append({
                            "id": tc.get("id", f"call_{i}"),
                            "type": "function",
                            "function": func
                        })
                    except json.JSONDecodeError:
                        continue # Skip invalid tool calls
            
            if valid_tool_calls:
                assembled_message["tool_calls"] = valid_tool_calls
                # If there are tool calls, content should be None for native tool calling
                if not self.optimize_tool_call:
                    assembled_message["content"] = None
            
            self.history.append(assembled_message)
            # 5. Decision and Action
            if "tool_calls" in assembled_message:
                tool_calls = assembled_message["tool_calls"]

                # Prioritize 'end_task': if it's present, run it exclusively.
                end_task_call = next((tc for tc in tool_calls if tc['function']['name'] == 'end_task'), None)
                if end_task_call:
                    task_result = json.loads(end_task_call['function']['arguments'])
                    
                    current_time = time.time()
                    task_result["current_time"] = current_time
                    task_result["total_elapsed_time"] = current_time - start_time
                    task_result["total_steps"] = step + 1
                    
                    yield Event(f"Agent:{self.name}", "end", task_result)
                    return

                # If there's only one tool call, execute it sequentially.
                if len(tool_calls) == 1:
                    tool_call_data = tool_calls[0]
                    tool_output = ""
                    tool_name = "unknown_tool"
                    tool_start_time = time.time()
                    try:
                        tool_name = tool_call_data['function']['name']
                        tool_args = json.loads(tool_call_data['function']['arguments'])
                        yield Event(f"Agent:{self.name}", "decision", {"tool_name": tool_name, "tool_args": tool_args})

                        tool_to_run = self.tools.get(tool_name)
                        is_group = getattr(tool_to_run, 'is_group_tool', False)
                        
                        execution_generator = self._execute_tool_from_dict(tool_call_data)
                        
                        if isinstance(execution_generator, Iterator):
                            for sub_event in execution_generator:
                                yield sub_event
                                
                                is_end_event = sub_event.type == 'end'
                                is_correct_source = sub_event.source == f"Group:{tool_name}"
                                
                                if is_group:
                                    if is_end_event and is_correct_source:
                                        tool_output = sub_event.payload.get('result', '')
                                        break
                                elif is_end_event:
                                    tool_output = sub_event.payload.get('final_answer') or sub_event.payload.get('error', '')
                        else:
                            tool_output = execution_generator
                    except Exception as e:
                        tool_output = f"Error during tool execution: {e}"

                    current_time = time.time()
                    tool_result_payload = {
                        "tool_name": tool_name,
                        "output": tool_output,
                        "current_time": current_time,
                        "elapsed_time": current_time - tool_start_time
                    }
                    yield Event(f"Agent:{self.name}", "tool_result", tool_result_payload)
                    
                    self.history.append({
                        "role": "tool",
                        "tool_call_id": tool_call_data['id'],
                        "name": tool_name,
                        "content": str(tool_output)
                    })
                else: # Multiple tool calls: execute in parallel
                    event_broker = EventBroker()
                    tool_results = {} # Store final outputs for history

                    def tool_worker(tool_call_data: Dict, broker: EventBroker):
                        tool_start_time = time.time()
                        tool_name = "unknown_tool"
                        final_output = ""
                        try:
                            tool_name = tool_call_data['function']['name']
                            tool_args = json.loads(tool_call_data['function']['arguments'])
                            broker.emit(f"Agent:{self.name}", "decision", {"tool_name": tool_name, "tool_args": tool_args})

                            tool_to_run = self.tools.get(tool_name)
                            is_group = getattr(tool_to_run, 'is_group_tool', False)
                            
                            execution_generator = self._execute_tool_from_dict(tool_call_data)
                            
                            if isinstance(execution_generator, Iterator):
                                for sub_event in execution_generator:
                                    broker.queue.put(sub_event)
                                    
                                    is_end_event = sub_event.type == 'end'
                                    is_correct_source = sub_event.source == f"Group:{tool_name}"
                                    
                                    if is_group:
                                        if is_end_event and is_correct_source:
                                            final_output = sub_event.payload.get('result', '')
                                            break 
                                    elif is_end_event:
                                        final_output = sub_event.payload.get('final_answer') or sub_event.payload.get('error', '')
                            else:
                                final_output = execution_generator
                        except Exception as e:
                            final_output = f"Error during tool execution: {e}"

                        current_time = time.time()
                        # Emit a special event to signal completion and carry the final result
                        broker.emit(f"Agent:{self.name}", "tool_completed", {
                            "tool_call_id": tool_call_data['id'],
                            "tool_name": tool_name,
                            "output": final_output,
                            "current_time": current_time,
                            "elapsed_time": current_time - tool_start_time
                        })

                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        for tool_call in tool_calls:
                            executor.submit(tool_worker, tool_call, event_broker)
                        
                        completed_tools = 0
                        while completed_tools < len(tool_calls):
                            event = event_broker.queue.get()
                            if event.type == "tool_completed":
                                completed_tools += 1
                                tool_results[event.payload['tool_call_id']] = event.payload
                                
                                tool_result_payload = {
                                    "tool_name": event.payload['tool_name'],
                                    "output": event.payload['output'],
                                    "current_time": event.payload['current_time'],
                                    "elapsed_time": event.payload['elapsed_time']
                                }
                                # Yield the final tool_result event for this tool
                                yield Event(f"Agent:{self.name}", "tool_result", tool_result_payload)
                            else:
                                yield event # Forward sub-agent events in real-time
                    
                    # Append all tool results to history in a stable order
                    for tool_call in tool_calls:
                        result_payload = tool_results[tool_call['id']]
                        self.history.append({
                            "role": "tool",
                            "tool_call_id": result_payload['tool_call_id'],
                            "name": result_payload['tool_name'],
                            "content": str(result_payload['output'])
                        })

                continue
            else: # If the LLM replies directly without calling a tool
                yield Event(f"Agent:{self.name}", "thinking", {"content": full_response_content})
                # If the model responds directly, prompt it to use end_task to formalize the completion.
                self.history.append({
                    "role": "user",
                    "content": "You have provided a direct answer. If this is the final answer, please call the `end_task` tool to properly conclude the task. Do not add any commentary."
                })
                continue
        # If the loop finishes without completion
        final_message = f"Error: Agent '{self.name}' failed to complete the task within {self.max_steps} steps."
        yield Event(f"Agent:{self.name}", "error", {"message": final_message})
        
        current_time = time.time()
        end_payload = {
            "error": final_message,
            "current_time": current_time,
            "total_elapsed_time": current_time - start_time,
            "total_steps": self.max_steps
        }
        yield Event(f"Agent:{self.name}", "end", end_payload)
        return
    
    def _execute_tool_from_dict(self, tool_call_dict: Dict) -> Any:
        """Executes a tool. If the tool is an Agent, returns its event generator.

        Args:
            tool_call_dict (Dict): The tool call dictionary.

        Returns:
            Any: The result of the tool execution. This can be a direct result
                 or an iterator of events if the tool is another agent.
        """
        name = tool_call_dict['function']['name']
        args = json.loads(tool_call_dict['function']['arguments'])
        tool: Optional[Tool] = self.tools.get(name)

        if not tool:
            return f"Error: Tool '{name}' not found."
        
        try:
            # If it's an Agent tool, it will return a generator
            if tool.is_agent_tool:
                # Ensure it's called in streaming mode
                return tool.execute(stream=True, **args)
            else: # Otherwise, it will return a direct result
                return tool.execute(**args)
        except Exception as e:
            return f"Error executing tool '{name}': {e}"

    def as_tool(self) -> Tool:
        """Wraps the entire Agent instance into a Tool.

        This allows the agent to be called by other agents.

        Returns:
            Tool: A Tool instance that encapsulates this agent.
        """
        # Dynamically create a wrapper function
        def agent_runner(stream: bool = False, **kwargs):
            # On each call, create a new Agent instance to ensure state isolation
            agent_instance = Agent(
                name=self.name,
                description=self.description,
                input_parameters=self.input_parameters,
                tools=self.original_tools, # Ensure isolation
                endpoint=self.endpoint,
                service_type=self.service_type, # Pass the service type
                model_id=self.model_id,
                max_steps=self.max_steps,
                optimize_tool_call=self.optimize_tool_call
            )
            return agent_instance.run(stream=stream, **kwargs)

        # Fake a function so the Tool class can parse it
        # This step is a bit hacky, but very effective
        agent_runner.__name__ = self.name
        agent_runner.__doc__ = f'An Agent: {self.description}'
        
        # Dynamically build the function signature
        from inspect import Parameter, Signature
        params = [
            Parameter(name=p['name'], kind=Parameter.POSITIONAL_OR_KEYWORD) 
            for p in self.input_parameters
        ]
        agent_runner.__signature__ = Signature(params)

        tool = Tool(func=agent_runner, is_agent_tool=True)
        setattr(tool, 'source_entity', self)
        return tool
    
    def add_content(self, content: str, role: str = 'user'):
        """Adds content to the agent's history.
        
        Args:
            content: The content to add.
            role: The role of the content ('user' or 'assistant').
        """
        self.history.append({"role": role, "content": content})

    def reset(self):
        """Resets the agent's history.

        This clears the conversation history, preparing the agent for a new run.
        """
        self.history = [{"role": "system", "content": self.system_prompt}]

    def copy(self) -> 'Agent':
        """Creates a deep copy of the agent instance."""
        return Agent(
            name=self.name,
            description=self.description,
            input_parameters=copy.deepcopy(self.input_parameters),
            tools=self.original_tools[:],  # Use a copy of the original tools list
            model_id=self.model_id,
            endpoint=self.endpoint,
            service_type=self.service_type, # Pass the service type
            prompt_template_path=getattr(self, '_prompt_template_path', None),
            target_lang=self.target_lang,
            max_steps=self.max_steps,
            optimize_tool_call=self.optimize_tool_call
        )

    def __mul__(self, other: int) -> List['Agent']:
        """Creates multiple copies of the agent."""
        if not isinstance(other, int):
            raise TypeError("Can only multiply an Agent by an integer.")
        return [self.copy() for _ in range(other)]

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the agent's configuration to a dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "input_parameters": self.input_parameters,
            "tools": [tool.name for tool in self.original_tools],
            "model_id": self.model_id,
            "target_lang": self.target_lang,
            "max_steps": self.max_steps,
            "optimize_tool_call": self.optimize_tool_call,
            "endpoint": self.endpoint.name if self.endpoint else None
        }
