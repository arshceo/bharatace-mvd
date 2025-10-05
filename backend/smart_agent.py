"""
Super Smart AI Agent Orchestrator
A custom agent that can intelligently route queries and use tools with Gemini LLM
"""

import json
import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from llama_index.core.tools.types import BaseTool

logger = logging.getLogger(__name__)


class SuperSmartAgent:
    """
    Custom AI Agent that can:
    1. Analyze student queries intelligently
    2. Determine which tools to use
    3. Execute tool calls with proper parameters
    4. Synthesize results into natural responses
    5. Handle multi-step reasoning
    """
    
    def __init__(self, llm, query_engine, tools: List[BaseTool]):
        self.llm = llm
        self.query_engine = query_engine
        self.tools = {tool.metadata.name: tool for tool in tools}
        self.tool_descriptions = self._build_tool_descriptions()
        
    def _build_tool_descriptions(self) -> str:
        """Build a description of all available tools"""
        descriptions = []
        for name, tool in self.tools.items():
            desc = f"- {name}: {tool.metadata.description}"
            descriptions.append(desc)
        return "\n".join(descriptions)
    
    async def query(self, query: str, student_context: Optional[Dict] = None) -> str:
        """
        Main query method that orchestrates the entire process
        """
        try:
            # Step 1: Analyze the query and determine intent
            intent_analysis = await self._analyze_intent(query, student_context)
            logger.info(f"🧠 Intent Analysis: {intent_analysis['intent']}")
            
            # Step 2: Execute tools if needed
            tool_results = []
            if intent_analysis.get('requires_tools'):
                for tool_call in intent_analysis['tool_calls']:
                    result = await self._execute_tool(tool_call, student_context)
                    tool_results.append(result)
                    logger.info(f"🔧 Tool executed: {tool_call['tool']} -> {result[:100]}...")
            
            # Step 3: Get RAG response for general knowledge
            rag_response = None
            if intent_analysis.get('requires_rag', True):
                rag_response = await self.query_engine.aquery(query)
                logger.info(f"📚 RAG Response: {str(rag_response)[:100]}...")
            
            # Step 4: Synthesize final response
            final_response = await self._synthesize_response(
                query, 
                intent_analysis, 
                tool_results, 
                rag_response, 
                student_context
            )
            
            return final_response
            
        except Exception as e:
            logger.error(f"Agent error: {str(e)}")
            return f"I apologize, but I encountered an error while processing your question: {str(e)}"
    
    async def _analyze_intent(self, query: str, student_context: Optional[Dict] = None) -> Dict:
        """
        Analyze the user's query to determine intent and required tools
        """
        context_info = ""
        if student_context:
            context_info = f"""
Student Context:
- Name: {student_context.get('full_name', 'Unknown')}
- Roll Number: {student_context.get('roll_number', 'Unknown')}
- Student ID: {student_context.get('id', 'Unknown')}
- Semester: {student_context.get('semester', 'Unknown')}
- Department: {student_context.get('department', 'Unknown')}
- CGPA: {student_context.get('cgpa', 'Unknown')}
"""

        analysis_prompt = f"""
You are an intelligent query analyzer for a student assistant system. Analyze the following query and determine what actions are needed.

{context_info}

Available Tools:
{self.tool_descriptions}

User Query: "{query}"

Analyze this query and respond with a JSON object containing:
1. "intent": Brief description of what the user wants
2. "requires_tools": Boolean - whether any tools need to be called
3. "requires_rag": Boolean - whether general knowledge search is needed
4. "tool_calls": Array of tools to call with their parameters
5. "complexity": "simple" or "complex" based on multi-step requirements

For tool calls, use this format:
{{"tool": "tool_name", "params": {{"param1": "value1", "student_id": "student_id_if_needed"}}}}

Important: If the query is about the student's personal data (attendance, marks, fees, etc.), set requires_tools=true and include appropriate tool calls with the student's ID.

Examples:
- "What's my attendance?" -> Use get_student_attendance tool
- "Show my marks" -> Use get_student_marks tool  
- "What's my CGPA?" -> Use student context + marks analysis
- "Tell me about courses" -> Use RAG only
- "Book a library book" -> Use search_books and reserve_book tools

Respond ONLY with valid JSON.
"""

        try:
            response = await self.llm.acomplete(analysis_prompt)
            response_text = str(response).strip()
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
            else:
                # Fallback analysis
                analysis = {
                    "intent": "General query",
                    "requires_tools": False,
                    "requires_rag": True,
                    "tool_calls": [],
                    "complexity": "simple"
                }
                
            return analysis
            
        except Exception as e:
            logger.error(f"Intent analysis error: {str(e)}")
            return {
                "intent": "General query",
                "requires_tools": False,
                "requires_rag": True,
                "tool_calls": [],
                "complexity": "simple"
            }
    
    async def _execute_tool(self, tool_call: Dict, student_context: Optional[Dict] = None) -> str:
        """
        Execute a specific tool call
        """
        try:
            tool_name = tool_call['tool']
            params = tool_call.get('params', {})
            
            # Inject student_id if needed and available
            if student_context and 'student_id' not in params:
                if any(keyword in tool_name.lower() for keyword in ['student', 'attendance', 'marks', 'fees']):
                    params['student_id'] = student_context['id']
            
            if tool_name not in self.tools:
                return f"Tool '{tool_name}' not available"
            
            tool = self.tools[tool_name]
            result = tool.call(**params)
            
            return str(result)
            
        except Exception as e:
            logger.error(f"Tool execution error: {str(e)}")
            return f"Error executing {tool_call.get('tool', 'unknown')}: {str(e)}"
    
    async def _synthesize_response(
        self, 
        query: str, 
        intent: Dict, 
        tool_results: List[str], 
        rag_response: Any, 
        student_context: Optional[Dict] = None
    ) -> str:
        """
        Synthesize all information into a coherent, natural response
        """
        context_info = ""
        if student_context:
            context_info = f"Student: {student_context.get('full_name')} (Roll: {student_context.get('roll_number')})"
        
        tool_info = ""
        if tool_results:
            tool_info = "Tool Results:\n" + "\n".join([f"- {result}" for result in tool_results])
        
        rag_info = ""
        if rag_response:
            rag_info = f"Knowledge Base: {str(rag_response)}"
        
        synthesis_prompt = f"""
You are a helpful student assistant. Create a natural, personalized response based on the following information:

{context_info}

Original Query: "{query}"
Intent: {intent.get('intent', 'Unknown')}

{tool_info}

{rag_info}

Instructions:
1. Provide a helpful, conversational response
2. Use the student's name when appropriate
3. Be specific and actionable
4. If you have student data, provide detailed analysis
5. If missing information, suggest what the student can do
6. Keep the tone friendly and supportive

Important: If you have specific student data (from tools), USE IT to provide detailed, personalized insights. Don't say you don't have information if the tools provided it.

Response:
"""

        try:
            response = await self.llm.acomplete(synthesis_prompt)
            return str(response).strip()
        except Exception as e:
            logger.error(f"Synthesis error: {str(e)}")
            
            # Fallback response using available data
            if tool_results:
                return f"Based on your query, here's what I found:\n\n" + "\n\n".join(tool_results)
            elif rag_response:
                return str(rag_response)
            else:
                return "I'm sorry, I couldn't process your request at this time."