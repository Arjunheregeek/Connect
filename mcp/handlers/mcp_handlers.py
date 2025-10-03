# --- mcp/handlers/mcp_handlers.py ---
import logging
from typing import Dict, Any, List
from mcp.models.mcp_models import (
    MCPRequest, MCPResponse, ListToolsRequest, CallToolRequest,
    create_error_response, create_success_response, create_tool_call_response,
    MCPErrorCodes, ToolDefinition
)
from mcp.schemas.tool_schemas import MCP_TOOLS
from mcp.utils.input_validation import InputValidator
from mcp.utils.caching import cache_manager
from mcp.services.bridge_service import bridge_service

logger = logging.getLogger(__name__)

class MCPHandler:
    """Handles MCP protocol requests and routes them to appropriate handlers"""
    
    def __init__(self):
        self.tool_handlers = {
            "find_person_by_name": self._handle_find_person_by_name,
            "find_people_by_skill": self._handle_find_people_by_skill,
            "find_people_by_company": self._handle_find_people_by_company,
            "find_colleagues_at_company": self._handle_find_colleagues_at_company,
            "find_people_by_institution": self._handle_find_people_by_institution,
            "find_people_by_location": self._handle_find_people_by_location,
            "get_person_skills": self._handle_get_person_skills,
            "find_people_with_multiple_skills": self._handle_find_people_with_multiple_skills,
            "get_person_colleagues": self._handle_get_person_colleagues,
            "find_people_by_experience_level": self._handle_find_people_by_experience_level,
            "get_company_employees": self._handle_get_company_employees,
            "get_skill_popularity": self._handle_get_skill_popularity,
            "get_person_details": self._handle_get_person_details,
            "get_person_job_descriptions": self._handle_get_person_job_descriptions,
            "search_job_descriptions_by_keywords": self._handle_search_job_descriptions_by_keywords,
            "find_technical_skills_in_descriptions": self._handle_find_technical_skills_in_descriptions,
            "find_leadership_indicators": self._handle_find_leadership_indicators,
            "find_achievement_patterns": self._handle_find_achievement_patterns,
            "analyze_career_progression": self._handle_analyze_career_progression,
            "find_domain_experts": self._handle_find_domain_experts,
            "find_similar_career_paths": self._handle_find_similar_career_paths,
            "find_role_transition_patterns": self._handle_find_role_transition_patterns,
            "natural_language_search": self._handle_natural_language_search,
            "health_check": self._handle_health_check
        }
    
    async def handle_request(self, request: MCPRequest) -> MCPResponse:
        """
        Main entry point for handling MCP requests
        
        Args:
            request: The MCP request to handle
            
        Returns:
            MCPResponse with the result or error
        """
        try:
            if request.method == "tools/list":
                return await self._handle_list_tools(request)
            elif request.method == "tools/call":
                return await self._handle_call_tool(request)
            else:
                return create_error_response(
                    request.id,
                    MCPErrorCodes.METHOD_NOT_FOUND,
                    f"Method '{request.method}' not found"
                )
                
        except Exception as e:
            logger.error(f"Error handling MCP request: {e}")
            return create_error_response(
                request.id,
                MCPErrorCodes.INTERNAL_ERROR,
                f"Internal server error: {str(e)}"
            )
    
    async def _handle_list_tools(self, request: MCPRequest) -> MCPResponse:
        """Handle tools/list request"""
        try:
            tools = [
                ToolDefinition(
                    name=tool["name"],
                    description=tool["description"],
                    inputSchema=tool["inputSchema"]
                )
                for tool in MCP_TOOLS
            ]
            
            return create_success_response(
                request.id,
                {"tools": [tool.dict() for tool in tools]}
            )
            
        except Exception as e:
            logger.error(f"Error listing tools: {e}")
            return create_error_response(
                request.id,
                MCPErrorCodes.INTERNAL_ERROR,
                f"Failed to list tools: {str(e)}"
            )
    
    async def _handle_call_tool(self, request: MCPRequest) -> MCPResponse:
        """Handle tools/call request"""
        try:
            if not request.params:
                return create_error_response(
                    request.id,
                    MCPErrorCodes.INVALID_PARAMS,
                    "Missing parameters for tool call"
                )
            
            tool_name = request.params.get("name")
            tool_arguments = request.params.get("arguments", {})
            
            if not tool_name:
                return create_error_response(
                    request.id,
                    MCPErrorCodes.INVALID_PARAMS,
                    "Missing 'name' parameter"
                )
            
            if tool_name not in self.tool_handlers:
                return create_error_response(
                    request.id,
                    MCPErrorCodes.TOOL_NOT_FOUND,
                    f"Tool '{tool_name}' not found"
                )
            
            # Validate input using comprehensive validator
            validation_error = InputValidator.validate_tool_input(tool_name, tool_arguments)
            if validation_error:
                return create_error_response(
                    request.id,
                    validation_error["code"],
                    validation_error["message"],
                    validation_error.get("data")
                )
            
            # Check cache first
            cached_result = await cache_manager.get_cached_result(tool_name, tool_arguments)
            if cached_result is not None:
                logger.info(f"Cache hit for tool: {tool_name}")
                return create_tool_call_response(request.id, cached_result)
            
            # Execute tool with enhanced error handling  
            handler = self.tool_handlers[tool_name]
            result = await self._execute_tool_with_error_handling(tool_name, handler, tool_arguments)
            
            # Cache successful results
            if not (isinstance(result, dict) and "error" in result):
                await cache_manager.cache_result(tool_name, tool_arguments, result)
                logger.debug(f"Cached result for tool: {tool_name}")
            
            if isinstance(result, dict) and "error" in result:
                return create_error_response(
                    request.id,
                    result["error"]["code"],
                    result["error"]["message"],
                    result["error"].get("data")
                )
            
            return create_tool_call_response(request.id, result)
            
        except Exception as e:
            logger.error(f"Tool call failed for {tool_name}: {str(e)}", exc_info=True)
            return create_error_response(
                request.id,
                MCPErrorCodes.INTERNAL_ERROR,
                f"Tool execution failed: {str(e)}"
            )
    
    async def _execute_tool_with_error_handling(
        self, 
        tool_name: str, 
        handler, 
        arguments: Dict[str, Any]
    ) -> Any:
        """Execute a tool handler with comprehensive error handling"""
        try:
            logger.info(f"Executing tool: {tool_name} with arguments: {arguments}")
            result = await handler(arguments)
            logger.info(f"Tool {tool_name} executed successfully")
            return result
            
        except KeyError as e:
            logger.error(f"Missing key in {tool_name}: {str(e)}")
            return {
                "error": {
                    "code": MCPErrorCodes.INVALID_PARAMS,
                    "message": f"Missing required parameter: {str(e)}",
                    "data": {"tool_name": tool_name, "missing_key": str(e)}
                }
            }
        except ValueError as e:
            logger.error(f"Invalid value in {tool_name}: {str(e)}")
            return {
                "error": {
                    "code": MCPErrorCodes.INVALID_PARAMS,
                    "message": f"Invalid parameter value: {str(e)}",
                    "data": {"tool_name": tool_name}
                }
            }
        except ConnectionError as e:
            logger.error(f"Database connection error in {tool_name}: {str(e)}")
            return {
                "error": {
                    "code": MCPErrorCodes.INTERNAL_ERROR,
                    "message": "Database connection failed",
                    "data": {"tool_name": tool_name, "category": "database_error"}
                }
            }
        except Exception as e:
            logger.error(f"Unexpected error in {tool_name}: {str(e)}", exc_info=True)
            return {
                "error": {
                    "code": MCPErrorCodes.INTERNAL_ERROR,
                    "message": f"Tool execution failed: {str(e)}",
                    "data": {"tool_name": tool_name, "error_type": type(e).__name__}
                }
            }
    
    # Tool handler methods
    async def _handle_find_person_by_name(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle find_person_by_name tool"""
        name = arguments["name"]
        results = await bridge_service.find_person_by_name(name)
        
        return [{
            "type": "text",
            "text": f"Found {len(results)} people matching '{name}':" + 
                   "\n" + "\n".join([
                       f"- {person['name']} ({person['headline']})" 
                       for person in results
                   ]) if results else f"No people found matching '{name}'"
        }]
    
    async def _handle_find_people_by_skill(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle find_people_by_skill tool"""
        skill = arguments["skill"]
        results = await bridge_service.find_people_by_skill(skill)
        
        return [{
            "type": "text", 
            "text": f"Found {len(results)} people with '{skill}' skills:" +
                   "\n" + "\n".join([
                       f"- {person['name']} ({person['headline']})"
                       for person in results
                   ]) if results else f"No people found with '{skill}' skills"
        }]
    
    async def _handle_find_people_by_company(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle find_people_by_company tool"""
        company_name = arguments["company_name"]
        results = await bridge_service.find_people_by_company(company_name)
        
        return [{
            "type": "text",
            "text": f"Found {len(results)} people who worked at '{company_name}':" +
                   "\n" + "\n".join([
                       f"- {person['name']} ({person['headline']})"
                       for person in results  
                   ]) if results else f"No people found who worked at '{company_name}'"
        }]
    
    async def _handle_find_colleagues_at_company(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle find_colleagues_at_company tool"""
        person_id = arguments["person_id"]
        company_name = arguments["company_name"]
        results = await bridge_service.find_colleagues_at_company(person_id, company_name)
        
        return [{
            "type": "text",
            "text": f"Found {len(results)} colleagues of person ID {person_id} at '{company_name}':" +
                   "\n" + "\n".join([
                       f"- {colleague['colleague_name']} ({colleague['colleague_headline']})"
                       for colleague in results
                   ]) if results else f"No colleagues found for person ID {person_id} at '{company_name}'"
        }]
    
    async def _handle_natural_language_search(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle natural_language_search tool"""
        question = arguments["question"]
        result = await bridge_service.natural_language_search(question)
        
        return [{
            "type": "text",
            "text": result
        }]
    
    async def _handle_find_people_by_institution(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle find_people_by_institution tool"""
        institution_name = arguments["institution_name"]
        results = await bridge_service.find_people_by_institution(institution_name)
        
        return [{
            "type": "text",
            "text": f"Found {len(results)} people who studied at '{institution_name}':" +
                   "\n" + "\n".join([
                       f"- {person['name']} ({person['headline']})"
                       for person in results
                   ]) if results else f"No people found who studied at '{institution_name}'"
        }]
    
    async def _handle_find_people_by_location(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle find_people_by_location tool"""
        location = arguments["location"]
        results = await bridge_service.find_people_by_location(location)
        
        return [{
            "type": "text",
            "text": f"Found {len(results)} people in '{location}':" +
                   "\n" + "\n".join([
                       f"- {person['name']} ({person['headline']}) - {person.get('location', 'N/A')}"
                       for person in results
                   ]) if results else f"No people found in '{location}'"
        }]
    
    async def _handle_get_person_skills(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle get_person_skills tool"""
        person_name = arguments["person_name"]
        results = await bridge_service.get_person_skills(person_name)
        
        if results:
            person = results[0]
            skills = person.get('skills', [])
            return [{
                "type": "text",
                "text": f"Skills for {person['person_name']}:\n" +
                       "\n".join([f"- {skill}" for skill in skills]) if skills else f"No skills found for {person['person_name']}"
            }]
        else:
            return [{
                "type": "text",
                "text": f"Person '{person_name}' not found"
            }]
    
    async def _handle_find_people_with_multiple_skills(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle find_people_with_multiple_skills tool"""
        skills_list = arguments["skills_list"]
        match_type = arguments.get("match_type", "any")
        results = await bridge_service.find_people_with_multiple_skills(skills_list, match_type)
        
        skills_text = "', '".join(skills_list)
        match_text = "all" if match_type == "all" else "any"
        
        return [{
            "type": "text",
            "text": f"Found {len(results)} people with {match_text} of these skills: '{skills_text}':" +
                   "\n" + "\n".join([
                       f"- {person['name']} ({person['headline']})"
                       for person in results
                   ]) if results else f"No people found with {match_text} of these skills: '{skills_text}'"
        }]
    
    async def _handle_get_person_colleagues(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle get_person_colleagues tool""" 
        person_name = arguments["person_name"]
        results = await bridge_service.get_person_colleagues(person_name)
        
        if results:
            # Group by company
            by_company = {}
            for colleague in results:
                company = colleague['company_name']
                if company not in by_company:
                    by_company[company] = []
                by_company[company].append(f"{colleague['colleague_name']} ({colleague['colleague_headline']})")
            
            text_parts = [f"Colleagues of '{person_name}':"]
            for company, colleagues in by_company.items():
                text_parts.append(f"\nAt {company}:")
                for colleague in colleagues:
                    text_parts.append(f"  - {colleague}")
            
            return [{
                "type": "text",
                "text": "\n".join(text_parts)
            }]
        else:
            return [{
                "type": "text", 
                "text": f"No colleagues found for '{person_name}'"
            }]
    
    async def _handle_find_people_by_experience_level(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle find_people_by_experience_level tool"""
        min_months = arguments.get("min_months")
        max_months = arguments.get("max_months")
        results = await bridge_service.find_people_by_experience_level(min_months, max_months)
        
        # Build description
        desc_parts = []
        if min_months is not None:
            desc_parts.append(f"at least {min_months} months")
        if max_months is not None:
            desc_parts.append(f"at most {max_months} months")
        
        experience_desc = " and ".join(desc_parts) if desc_parts else "any amount"
        
        return [{
            "type": "text",
            "text": f"Found {len(results)} people with {experience_desc} of experience:" +
                   "\n" + "\n".join([
                       f"- {person['name']} ({person['headline']}) - {person.get('experience_months', 'N/A')} months"
                       for person in results
                   ]) if results else f"No people found with {experience_desc} of experience"
        }]
    
    async def _handle_get_company_employees(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle get_company_employees tool"""
        company_name = arguments["company_name"]
        results = await bridge_service.get_company_employees(company_name)
        
        return [{
            "type": "text",
            "text": f"Found {len(results)} employees at '{company_name}':" +
                   "\n" + "\n".join([
                       f"- {person['name']} ({person['headline']})"
                       for person in results
                   ]) if results else f"No employees found at '{company_name}'"
        }]
    
    async def _handle_get_skill_popularity(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle get_skill_popularity tool"""
        limit = arguments.get("limit", 20)
        results = await bridge_service.get_skill_popularity(limit)
        
        return [{
            "type": "text",
            "text": f"Top {len(results)} most popular skills:" +
                   "\n" + "\n".join([
                       f"{i+1}. {skill['skill_name']} ({skill['person_count']} people)"
                       for i, skill in enumerate(results)
                   ]) if results else "No skill data found"
        }]
    
    async def _handle_get_person_details(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle get_person_details tool"""
        person_name = arguments["person_name"]
        results = await bridge_service.get_person_details(person_name)
        
        if results:
            person = results[0]
            details = [f"Details for {person['name']}:"]
            details.append(f"Headline: {person.get('headline', 'N/A')}")
            details.append(f"Location: {person.get('location', 'N/A')}")
            details.append(f"Experience: {person.get('experience_months', 'N/A')} months")
            
            if person.get('skills'):
                skills = [skill for skill in person['skills'] if skill]
                if skills:
                    details.append(f"Skills: {', '.join(skills)}")
            
            if person.get('companies'):
                companies = [company for company in person['companies'] if company]
                if companies:
                    details.append(f"Companies: {', '.join(companies)}")
            
            if person.get('institutions'):
                institutions = [inst for inst in person['institutions'] if inst]
                if institutions:
                    details.append(f"Education: {', '.join(institutions)}")
            
            return [{
                "type": "text",
                "text": "\n".join(details)
            }]
        else:
            return [{
                "type": "text",
                "text": f"Person '{person_name}' not found"
            }]

    async def _handle_get_person_job_descriptions(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle get_person_job_descriptions tool"""
        person_name = arguments["person_name"]
        results = await bridge_service.get_person_job_descriptions(person_name)
        
        if results:
            details = [f"Job descriptions for {results[0]['person_name']}:"]
            details.append("")
            
            for job in results:
                details.append(f"Company: {job['company_name']}")
                details.append(f"Title: {job['job_title']}")
                if job.get('start_date') and job.get('end_date'):
                    details.append(f"Period: {job['start_date']} to {job['end_date']}")
                elif job.get('start_date'):
                    details.append(f"Start Date: {job['start_date']}")
                if job.get('duration_months'):
                    details.append(f"Duration: {job['duration_months']} months")
                if job.get('job_location'):
                    details.append(f"Location: {job['job_location']}")
                if job.get('job_description'):
                    details.append(f"Description: {job['job_description']}")
                details.append("-" * 50)
            
            return [{
                "type": "text",
                "text": "\n".join(details)
            }]
        else:
            return [{
                "type": "text", 
                "text": f"No job descriptions found for '{person_name}'"
            }]

    async def _handle_search_job_descriptions_by_keywords(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle search_job_descriptions_by_keywords tool"""
        keywords = arguments["keywords"]
        match_type = arguments.get("match_type", "any")
        results = await bridge_service.search_job_descriptions_by_keywords(keywords, match_type)
        
        if results:
            details = [f"Found {len(results)} people matching keywords {keywords} ({match_type} match):"]
            details.append("")
            
            for person in results:
                details.append(f"- {person['person_name']} ({person.get('headline', 'N/A')})")
                details.append(f"  Company: {person['company_name']}")
                details.append(f"  Role: {person['job_title']}")
                if person.get('job_description'):
                    desc = person['job_description'][:200] + "..." if len(person['job_description']) > 200 else person['job_description']
                    details.append(f"  Description: {desc}")
                details.append("")
            
            return [{"type": "text", "text": "\n".join(details)}]
        else:
            return [{"type": "text", "text": f"No people found with keywords: {', '.join(keywords)}"}]

    async def _handle_find_technical_skills_in_descriptions(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle find_technical_skills_in_descriptions tool"""
        tech_keywords = arguments["tech_keywords"]
        results = await bridge_service.find_technical_skills_in_descriptions(tech_keywords)
        
        if results:
            details = [f"Found {len(results)} people with technical skills {tech_keywords} in job descriptions:"]
            details.append("")
            
            for person in results:
                details.append(f"- {person['person_name']} ({person.get('headline', 'N/A')})")
                details.append(f"  Company: {person['company_name']} | Role: {person['job_title']}")
                if person.get('start_date') and person.get('end_date'):
                    details.append(f"  Period: {person['start_date']} to {person['end_date']}")
                details.append("")
            
            return [{"type": "text", "text": "\n".join(details)}]
        else:
            return [{"type": "text", "text": f"No people found with technical skills: {', '.join(tech_keywords)}"}]

    async def _handle_find_leadership_indicators(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle find_leadership_indicators tool"""
        results = await bridge_service.find_leadership_indicators()
        
        if results:
            details = [f"Found {len(results)} people with leadership indicators:"]
            details.append("")
            
            for person in results[:20]:  # Limit to top 20
                details.append(f"- {person['person_name']} ({person.get('headline', 'N/A')})")
                details.append(f"  Company: {person['company_name']} | Role: {person['job_title']}")
                if person.get('duration_months'):
                    details.append(f"  Duration: {person['duration_months']} months")
                details.append("")
            
            return [{"type": "text", "text": "\n".join(details)}]
        else:
            return [{"type": "text", "text": "No people found with leadership indicators"}]

    async def _handle_find_achievement_patterns(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle find_achievement_patterns tool"""
        results = await bridge_service.find_achievement_patterns()
        
        if results:
            details = [f"Found {len(results)} people with quantifiable achievements:"]
            details.append("")
            
            for person in results[:20]:  # Limit to top 20
                details.append(f"- {person['person_name']} ({person.get('headline', 'N/A')})")
                details.append(f"  Company: {person['company_name']} | Role: {person['job_title']}")
                if person.get('start_date') and person.get('end_date'):
                    details.append(f"  Period: {person['start_date']} to {person['end_date']}")
                details.append("")
            
            return [{"type": "text", "text": "\n".join(details)}]
        else:
            return [{"type": "text", "text": "No people found with achievement patterns"}]

    async def _handle_analyze_career_progression(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle analyze_career_progression tool"""
        person_name = arguments["person_name"]
        results = await bridge_service.analyze_career_progression(person_name)
        
        if results:
            details = [f"Career progression for {results[0]['person_name']}:"]
            details.append("")
            
            for i, job in enumerate(results, 1):
                details.append(f"{i}. {job['company_name']} - {job['job_title']}")
                if job.get('start_date') and job.get('end_date'):
                    details.append(f"   Period: {job['start_date']} to {job['end_date']}")
                elif job.get('start_date'):
                    details.append(f"   Start: {job['start_date']}")
                if job.get('duration_months'):
                    details.append(f"   Duration: {job['duration_months']} months")
                if job.get('job_location'):
                    details.append(f"   Location: {job['job_location']}")
                details.append("")
            
            return [{"type": "text", "text": "\n".join(details)}]
        else:
            return [{"type": "text", "text": f"No career progression found for '{person_name}'"}]

    async def _handle_find_domain_experts(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle find_domain_experts tool"""
        domain_keywords = arguments["domain_keywords"]
        results = await bridge_service.find_domain_experts(domain_keywords)
        
        if results:
            details = [f"Found {len(results)} domain experts for {domain_keywords}:"]
            details.append("")
            
            for person in results:
                details.append(f"- {person['person_name']} ({person.get('headline', 'N/A')})")
                details.append(f"  Domain Jobs: {person['domain_jobs']} | Total Experience: {person.get('total_experience', 'N/A')} months")
                if person.get('companies'):
                    companies = person['companies'][:5]  # Show first 5 companies
                    details.append(f"  Companies: {', '.join(companies)}")
                details.append("")
            
            return [{"type": "text", "text": "\n".join(details)}]
        else:
            return [{"type": "text", "text": f"No domain experts found for: {', '.join(domain_keywords)}"}]

    async def _handle_find_similar_career_paths(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle find_similar_career_paths tool"""
        reference_person_name = arguments["reference_person_name"]
        similarity_threshold = arguments.get("similarity_threshold", 2)
        results = await bridge_service.find_similar_career_paths(reference_person_name, similarity_threshold)
        
        if results:
            details = [f"Found {len(results)} people with similar career paths to {reference_person_name}:"]
            details.append("")
            
            for person in results:
                details.append(f"- {person['similar_person']} ({person.get('headline', 'N/A')})")
                details.append(f"  Similarity Score: {person['similarity_score']}")
                if person.get('common_companies'):
                    details.append(f"  Common Companies: {', '.join(person['common_companies'])}")
                if person.get('common_titles'):
                    details.append(f"  Common Roles: {', '.join(person['common_titles'])}")
                details.append("")
            
            return [{"type": "text", "text": "\n".join(details)}]
        else:
            return [{"type": "text", "text": f"No similar career paths found for '{reference_person_name}'"}]

    async def _handle_find_role_transition_patterns(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle find_role_transition_patterns tool"""
        from_role_keywords = arguments["from_role_keywords"]
        to_role_keywords = arguments["to_role_keywords"]
        results = await bridge_service.find_role_transition_patterns(from_role_keywords, to_role_keywords)
        
        if results:
            details = [f"Found {len(results)} people who transitioned from {from_role_keywords} to {to_role_keywords}:"]
            details.append("")
            
            for person in results:
                details.append(f"- {person['person_name']} ({person.get('headline', 'N/A')})")
                details.append(f"  FROM: {person['from_role']} at {person['from_company']} ({person.get('from_start', 'N/A')})")
                details.append(f"  TO: {person['to_role']} at {person['to_company']} ({person.get('to_start', 'N/A')})")
                details.append("")
            
            return [{"type": "text", "text": "\n".join(details)}]
        else:
            return [{"type": "text", "text": f"No role transitions found from {from_role_keywords} to {to_role_keywords}"}]

    async def _handle_health_check(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle health_check tool"""
        health_status = await bridge_service.health_check()
        
        return [{
            "type": "text",
            "text": f"Health Status: {health_status['status']}\n" +
                   f"Database Connected: {health_status.get('database_connected', False)}\n" +
                   f"Node Count: {health_status.get('node_count', 'Unknown')}\n" +
                   f"Query Manager Ready: {health_status.get('query_manager_ready', False)}\n" +
                   f"NL Search Ready: {health_status.get('nl_search_ready', False)}"
        }]

# Global handler instance
mcp_handler = MCPHandler()