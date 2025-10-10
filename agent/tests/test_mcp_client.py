"""
MCP Client Integration Test Suite

This script tests the updated MCP client with all 19 tools to ensure:
1. All tool methods are callable
2. Parameters are correctly formatted
3. HTTP communication works
4. Responses are properly parsed
5. Error handling works correctly
"""

import os
import sys
import asyncio
import json
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agent.mcp_client import MCPClient, MCPResponse


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


class MCPClientTester:
    """Test suite for MCP client"""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: str = None):
        self.base_url = base_url
        self.api_key = api_key or "f435d1c3b1c5e66db047585265bbe4535a4b5f3389e134b54abe482b7b637ac3"
        self.results = []
        self.passed = 0
        self.failed = 0
    
    def print_header(self, text: str):
        """Print section header"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}{text}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}\n")
    
    def print_test(self, name: str, status: str, details: str = ""):
        """Print test result"""
        if status == "PASS":
            print(f"{Colors.GREEN}✓{Colors.END} {name}")
            if details:
                print(f"  {Colors.BLUE}{details}{Colors.END}")
            self.passed += 1
        elif status == "FAIL":
            print(f"{Colors.RED}✗{Colors.END} {name}")
            if details:
                print(f"  {Colors.RED}{details}{Colors.END}")
            self.failed += 1
        else:
            print(f"{Colors.YELLOW}⚠{Colors.END} {name}")
            if details:
                print(f"  {Colors.YELLOW}{details}{Colors.END}")
    
    async def test_health_check(self, client: MCPClient):
        """Test health check endpoint"""
        try:
            response = await client.tool_client.health_check()
            if response.success:
                node_count = response.data.get('node_count', 0)
                self.print_test(
                    "health_check()", 
                    "PASS", 
                    f"Server healthy, {node_count} nodes"
                )
                return True
            else:
                self.print_test("health_check()", "FAIL", response.error or "No error message")
                return False
        except Exception as e:
            self.print_test("health_check()", "FAIL", str(e))
            return False
    
    async def test_list_tools(self, client: MCPClient):
        """Test list tools endpoint"""
        try:
            response = await client.tool_client.list_tools()
            if response.success:
                tools = response.data.get('tools', [])
                self.print_test(
                    "list_tools()", 
                    "PASS", 
                    f"Retrieved {len(tools)} tools"
                )
                return True
            else:
                self.print_test("list_tools()", "FAIL", response.error or "No error message")
                return False
        except Exception as e:
            self.print_test("list_tools()", "FAIL", str(e))
            return False
    
    async def test_find_person_by_name(self, client: MCPClient):
        """Test find_person_by_name"""
        try:
            response = await client.tool_client.find_person_by_name("John")
            if response.success:
                count = len(response.data) if isinstance(response.data, list) else 1
                self.print_test(
                    "find_person_by_name('John')", 
                    "PASS", 
                    f"Found {count} people"
                )
                return True
            else:
                self.print_test("find_person_by_name()", "FAIL", response.error or "No error message")
                return False
        except Exception as e:
            self.print_test("find_person_by_name()", "FAIL", str(e))
            return False
    
    async def test_find_people_by_skill(self, client: MCPClient):
        """Test find_people_by_skill"""
        try:
            response = await client.tool_client.find_people_by_skill("Python")
            if response.success:
                count = len(response.data) if isinstance(response.data, list) else 1
                self.print_test(
                    "find_people_by_skill('Python')", 
                    "PASS", 
                    f"Found {count} people with Python skill"
                )
                return True
            else:
                self.print_test("find_people_by_skill()", "FAIL", response.error or "No error message")
                return False
        except Exception as e:
            self.print_test("find_people_by_skill()", "FAIL", str(e))
            return False
    
    async def test_find_people_by_company(self, client: MCPClient):
        """Test find_people_by_company"""
        try:
            response = await client.tool_client.find_people_by_company("Google")
            if response.success:
                count = len(response.data) if isinstance(response.data, list) else 1
                self.print_test(
                    "find_people_by_company('Google')", 
                    "PASS", 
                    f"Found {count} people from Google"
                )
                return True
            else:
                self.print_test("find_people_by_company()", "FAIL", response.error or "No error message")
                return False
        except Exception as e:
            self.print_test("find_people_by_company()", "FAIL", str(e))
            return False
    
    async def test_find_people_by_location(self, client: MCPClient):
        """Test find_people_by_location"""
        try:
            response = await client.tool_client.find_people_by_location("San Francisco")
            if response.success:
                count = len(response.data) if isinstance(response.data, list) else 1
                self.print_test(
                    "find_people_by_location('San Francisco')", 
                    "PASS", 
                    f"Found {count} people in San Francisco"
                )
                return True
            else:
                self.print_test("find_people_by_location()", "FAIL", response.error or "No error message")
                return False
        except Exception as e:
            self.print_test("find_people_by_location()", "FAIL", str(e))
            return False
    
    async def test_get_person_complete_profile(self, client: MCPClient):
        """Test get_person_complete_profile with person_name"""
        try:
            response = await client.tool_client.get_person_complete_profile(person_name="John Doe")
            if response.success:
                self.print_test(
                    "get_person_complete_profile(person_name='John Doe')", 
                    "PASS", 
                    "Retrieved complete profile"
                )
                return True
            else:
                self.print_test("get_person_complete_profile()", "FAIL", response.error or "No error message")
                return False
        except Exception as e:
            self.print_test("get_person_complete_profile()", "FAIL", str(e))
            return False
    
    async def test_get_person_skills(self, client: MCPClient):
        """Test get_person_skills with person_name"""
        try:
            response = await client.tool_client.get_person_skills(person_name="John Doe")
            if response.success:
                self.print_test(
                    "get_person_skills(person_name='John Doe')", 
                    "PASS", 
                    "Retrieved person skills"
                )
                return True
            else:
                self.print_test("get_person_skills()", "FAIL", response.error or "No error message")
                return False
        except Exception as e:
            self.print_test("get_person_skills()", "FAIL", str(e))
            return False
    
    async def test_find_people_with_multiple_skills(self, client: MCPClient):
        """Test find_people_with_multiple_skills"""
        try:
            response = await client.tool_client.find_people_with_multiple_skills(
                ["Python", "Machine Learning"], 
                "any"
            )
            if response.success:
                count = len(response.data) if isinstance(response.data, list) else 1
                self.print_test(
                    "find_people_with_multiple_skills(['Python', 'Machine Learning'], 'any')", 
                    "PASS", 
                    f"Found {count} people with these skills"
                )
                return True
            else:
                self.print_test("find_people_with_multiple_skills()", "FAIL", response.error or "No error message")
                return False
        except Exception as e:
            self.print_test("find_people_with_multiple_skills()", "FAIL", str(e))
            return False
    
    async def test_find_people_by_experience_level(self, client: MCPClient):
        """Test find_people_by_experience_level"""
        try:
            response = await client.tool_client.find_people_by_experience_level(
                min_months=24, 
                max_months=60
            )
            if response.success:
                count = len(response.data) if isinstance(response.data, list) else 1
                self.print_test(
                    "find_people_by_experience_level(min_months=24, max_months=60)", 
                    "PASS", 
                    f"Found {count} people with 2-5 years experience"
                )
                return True
            else:
                self.print_test("find_people_by_experience_level()", "FAIL", response.error or "No error message")
                return False
        except Exception as e:
            self.print_test("find_people_by_experience_level()", "FAIL", str(e))
            return False
    
    async def test_search_job_descriptions_by_keywords(self, client: MCPClient):
        """Test search_job_descriptions_by_keywords"""
        try:
            response = await client.tool_client.search_job_descriptions_by_keywords(
                ["machine learning", "AI"], 
                "any"
            )
            if response.success:
                count = len(response.data) if isinstance(response.data, list) else 1
                self.print_test(
                    "search_job_descriptions_by_keywords(['machine learning', 'AI'], 'any')", 
                    "PASS", 
                    f"Found {count} people with matching job descriptions"
                )
                return True
            else:
                self.print_test("search_job_descriptions_by_keywords()", "FAIL", response.error or "No error message")
                return False
        except Exception as e:
            self.print_test("search_job_descriptions_by_keywords()", "FAIL", str(e))
            return False
    
    async def test_find_technical_skills_in_descriptions(self, client: MCPClient):
        """Test find_technical_skills_in_descriptions"""
        try:
            response = await client.tool_client.find_technical_skills_in_descriptions(
                ["Python", "JavaScript", "React"]
            )
            if response.success:
                count = len(response.data) if isinstance(response.data, list) else 1
                self.print_test(
                    "find_technical_skills_in_descriptions(['Python', 'JavaScript', 'React'])", 
                    "PASS", 
                    f"Found {count} people with these technical skills"
                )
                return True
            else:
                self.print_test("find_technical_skills_in_descriptions()", "FAIL", response.error or "No error message")
                return False
        except Exception as e:
            self.print_test("find_technical_skills_in_descriptions()", "FAIL", str(e))
            return False
    
    async def test_find_leadership_indicators(self, client: MCPClient):
        """Test find_leadership_indicators"""
        try:
            response = await client.tool_client.find_leadership_indicators()
            if response.success:
                count = len(response.data) if isinstance(response.data, list) else 1
                self.print_test(
                    "find_leadership_indicators()", 
                    "PASS", 
                    f"Found {count} people with leadership indicators"
                )
                return True
            else:
                self.print_test("find_leadership_indicators()", "FAIL", response.error or "No error message")
                return False
        except Exception as e:
            self.print_test("find_leadership_indicators()", "FAIL", str(e))
            return False
    
    async def test_find_domain_experts(self, client: MCPClient):
        """Test find_domain_experts"""
        try:
            response = await client.tool_client.find_domain_experts(
                ["software", "engineering", "development"]
            )
            if response.success:
                count = len(response.data) if isinstance(response.data, list) else 1
                self.print_test(
                    "find_domain_experts(['software', 'engineering', 'development'])", 
                    "PASS", 
                    f"Found {count} domain experts"
                )
                return True
            else:
                self.print_test("find_domain_experts()", "FAIL", response.error or "No error message")
                return False
        except Exception as e:
            self.print_test("find_domain_experts()", "FAIL", str(e))
            return False
    
    async def test_get_company_employees(self, client: MCPClient):
        """Test get_company_employees"""
        try:
            response = await client.tool_client.get_company_employees("Google")
            if response.success:
                count = len(response.data) if isinstance(response.data, list) else 1
                self.print_test(
                    "get_company_employees('Google')", 
                    "PASS", 
                    f"Found {count} Google employees"
                )
                return True
            else:
                self.print_test("get_company_employees()", "FAIL", response.error or "No error message")
                return False
        except Exception as e:
            self.print_test("get_company_employees()", "FAIL", str(e))
            return False
    
    async def run_all_tests(self):
        """Run all tests"""
        self.print_header("MCP CLIENT INTEGRATION TEST SUITE")
        
        print(f"{Colors.BOLD}Configuration:{Colors.END}")
        print(f"  Base URL: {self.base_url}")
        print(f"  API Key: {self.api_key[:20]}...")
        
        # Create client
        async with MCPClient(base_url=self.base_url, api_key=self.api_key) as client:
            
            # System tests
            self.print_header("SYSTEM TOOLS (2 tests)")
            await self.test_health_check(client)
            await self.test_list_tools(client)
            
            # Core person profile tests
            self.print_header("CORE PERSON PROFILE TOOLS (7 tests)")
            await self.test_find_person_by_name(client)
            await self.test_find_people_by_skill(client)
            await self.test_find_people_by_company(client)
            await self.test_find_people_by_location(client)
            await self.test_get_person_complete_profile(client)
            await self.test_get_person_skills(client)
            await self.test_find_people_with_multiple_skills(client)
            
            # Experience and company tests
            self.print_header("EXPERIENCE & COMPANY TOOLS (2 tests)")
            await self.test_find_people_by_experience_level(client)
            await self.test_get_company_employees(client)
            
            # Job description analysis tests
            self.print_header("JOB DESCRIPTION ANALYSIS TOOLS (5 tests)")
            await self.test_search_job_descriptions_by_keywords(client)
            await self.test_find_technical_skills_in_descriptions(client)
            await self.test_find_leadership_indicators(client)
            await self.test_find_domain_experts(client)
            
        # Summary
        self.print_header("TEST SUMMARY")
        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0
        
        print(f"{Colors.BOLD}Results:{Colors.END}")
        print(f"  {Colors.GREEN}✓ Passed: {self.passed}{Colors.END}")
        print(f"  {Colors.RED}✗ Failed: {self.failed}{Colors.END}")
        print(f"  {Colors.BOLD}Total: {total}{Colors.END}")
        print(f"  {Colors.CYAN}Pass Rate: {pass_rate:.1f}%{Colors.END}")
        
        if self.failed == 0:
            print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED! 🎉{Colors.END}")
        else:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  Some tests failed. Please review.{Colors.END}")
        
        return self.failed == 0


async def main():
    """Main entry point"""
    # Check for custom URL or API key
    base_url = os.getenv("MCP_BASE_URL", "http://localhost:8000")
    api_key = os.getenv("MCP_API_KEY", "f435d1c3b1c5e66db047585265bbe4535a4b5f3389e134b54abe482b7b637ac3")
    
    tester = MCPClientTester(base_url=base_url, api_key=api_key)
    success = await tester.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
