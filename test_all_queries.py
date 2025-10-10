"""
Comprehensive test suite for all QueryManager methods.
Tests all 23 query types against the live Neo4j database.
"""

import os
import sys
from dotenv import load_dotenv

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.graph_db import GraphDB
from src.query import QueryManager

def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def print_result(query_name, result, limit=2):
    """Print query results in a formatted way."""
    print(f"\n✓ {query_name}")
    if isinstance(result, dict) and 'error' in result:
        print(f"  ❌ Error: {result['error']}")
        return False
    elif isinstance(result, list):
        print(f"  📊 Found {len(result)} results")
        if result:
            for i, record in enumerate(result[:limit], 1):
                print(f"  {i}. {record}")
        else:
            print("  ⚠️  No results found")
        return len(result) > 0
    else:
        print(f"  ⚠️  Unexpected result type: {type(result)}")
        return False

def main():
    # Load environment variables
    load_dotenv()
    
    # Connect to database - use environment variables
    uri = os.getenv("NEO_URI") or os.getenv("NEO4J_URI")
    user = os.getenv("NEO_USERNAME") or os.getenv("NEO4J_USER")
    password = os.getenv("NEO_PASSWORD") or os.getenv("NEO4J_PASSWORD")
    
    if not uri or not user or not password:
        print("❌ Error: NEO4J_URI (or NEO_URI), NEO_USERNAME (or NEO4J_USER), and NEO_PASSWORD (or NEO4J_PASSWORD) environment variables must be set.")
        return
    
    print("\n🔗 Connecting to Neo4j database...")
    db = GraphDB(uri, user, password)
    qm = QueryManager(db)
    
    results = {}
    
    # ========================================================================
    # TEST 1: Get Person Complete Profile
    # ========================================================================
    print_section("TEST 1: Get Person Complete Profile")
    
    # Test with person_id
    result = qm.get_person_complete_profile(person_id=98905076)
    results['get_person_complete_profile_by_id'] = print_result(
        "get_person_complete_profile(person_id=98905076)", result, limit=1
    )
    
    # Test with person_name
    result = qm.get_person_complete_profile(person_name="Ashray")
    results['get_person_complete_profile_by_name'] = print_result(
        "get_person_complete_profile(person_name='Ashray')", result, limit=1
    )
    
    # ========================================================================
    # TEST 2: Find Person by Name
    # ========================================================================
    print_section("TEST 2: Find Person by Name")
    result = qm.find_person_by_name("Sanjay")
    results['find_person_by_name'] = print_result(
        "find_person_by_name('Sanjay')", result
    )
    
    # ========================================================================
    # TEST 3: Find People by Skill
    # ========================================================================
    print_section("TEST 3: Find People by Skill")
    result = qm.find_people_by_skill("Python")
    results['find_people_by_skill'] = print_result(
        "find_people_by_skill('Python')", result
    )
    
    # ========================================================================
    # TEST 4: Find People by Company
    # ========================================================================
    print_section("TEST 4: Find People by Company")
    result = qm.find_people_by_company("Adobe")
    results['find_people_by_company'] = print_result(
        "find_people_by_company('Adobe')", result
    )
    
    # ========================================================================
    # TEST 5: Find Colleagues at Company
    # ========================================================================
    print_section("TEST 5: Find Colleagues at Company")
    result = qm.find_colleagues_at_company(98905076, "Adobe")
    results['find_colleagues_at_company'] = print_result(
        "find_colleagues_at_company(98905076, 'Adobe')", result
    )
    
    # ========================================================================
    # TEST 6: Find People by Institution
    # ========================================================================
    print_section("TEST 6: Find People by Institution")
    result = qm.find_people_by_institution("IIT")
    results['find_people_by_institution'] = print_result(
        "find_people_by_institution('IIT')", result
    )
    
    # ========================================================================
    # TEST 7: Find People by Location
    # ========================================================================
    print_section("TEST 7: Find People by Location")
    result = qm.find_people_by_location("Bengaluru")
    results['find_people_by_location'] = print_result(
        "find_people_by_location('Bengaluru')", result
    )
    
    # ========================================================================
    # TEST 8: Get Person Skills
    # ========================================================================
    print_section("TEST 8: Get Person Skills")
    result = qm.get_person_skills(person_id=98905076)
    results['get_person_skills'] = print_result(
        "get_person_skills(person_id=98905076)", result, limit=1
    )
    
    # ========================================================================
    # TEST 9: Find People with Multiple Skills (ANY)
    # ========================================================================
    print_section("TEST 9: Find People with Multiple Skills (ANY)")
    result = qm.find_people_with_multiple_skills(["Python", "Machine Learning"], match_type="any")
    results['find_people_with_multiple_skills_any'] = print_result(
        "find_people_with_multiple_skills(['Python', 'Machine Learning'], 'any')", result
    )
    
    # ========================================================================
    # TEST 10: Find People with Multiple Skills (ALL)
    # ========================================================================
    print_section("TEST 10: Find People with Multiple Skills (ALL)")
    result = qm.find_people_with_multiple_skills(["Leadership", "Strategic Planning"], match_type="all")
    results['find_people_with_multiple_skills_all'] = print_result(
        "find_people_with_multiple_skills(['Leadership', 'Strategic Planning'], 'all')", result
    )
    
    # ========================================================================
    # TEST 11: Get Person Colleagues
    # ========================================================================
    print_section("TEST 11: Get Person Colleagues")
    result = qm.get_person_colleagues(person_id=98905076)
    results['get_person_colleagues'] = print_result(
        "get_person_colleagues(person_id=98905076)", result
    )
    
    # ========================================================================
    # TEST 12: Find People by Experience Level
    # ========================================================================
    print_section("TEST 12: Find People by Experience Level")
    result = qm.find_people_by_experience_level(min_months=60, max_months=120)
    results['find_people_by_experience_level'] = print_result(
        "find_people_by_experience_level(min_months=60, max_months=120)", result
    )
    
    # ========================================================================
    # TEST 13: Get Company Employees
    # ========================================================================
    print_section("TEST 13: Get Company Employees")
    result = qm.get_company_employees("Qualcomm")
    results['get_company_employees'] = print_result(
        "get_company_employees('Qualcomm')", result
    )
    
    # ========================================================================
    # TEST 14: Get Skill Popularity
    # ========================================================================
    print_section("TEST 14: Get Skill Popularity")
    result = qm.get_skill_popularity(limit=10)
    results['get_skill_popularity'] = print_result(
        "get_skill_popularity(limit=10)", result, limit=10
    )
    
    # ========================================================================
    # TEST 15: Get Person Details
    # ========================================================================
    print_section("TEST 15: Get Person Details")
    result = qm.get_person_details(person_id=98905076)
    results['get_person_details'] = print_result(
        "get_person_details(person_id=98905076)", result, limit=1
    )
    
    # ========================================================================
    # TEST 16: Get Person Job Descriptions
    # ========================================================================
    print_section("TEST 16: Get Person Job Descriptions")
    result = qm.get_person_job_descriptions(person_id=98905076)
    results['get_person_job_descriptions'] = print_result(
        "get_person_job_descriptions(person_id=98905076)", result
    )
    
    # ========================================================================
    # TEST 17: Search Job Descriptions by Keywords (ANY)
    # ========================================================================
    print_section("TEST 17: Search Job Descriptions by Keywords (ANY)")
    result = qm.search_job_descriptions_by_keywords(["software", "engineering"], match_type="any")
    results['search_job_descriptions_any'] = print_result(
        "search_job_descriptions_by_keywords(['software', 'engineering'], 'any')", result
    )
    
    # ========================================================================
    # TEST 18: Find Technical Skills in Descriptions
    # ========================================================================
    print_section("TEST 18: Find Technical Skills in Descriptions")
    result = qm.find_technical_skills_in_descriptions(["python", "machine learning"])
    results['find_technical_skills_in_descriptions'] = print_result(
        "find_technical_skills_in_descriptions(['python', 'machine learning'])", result
    )
    
    # ========================================================================
    # TEST 19: Find Leadership Indicators
    # ========================================================================
    print_section("TEST 19: Find Leadership Indicators")
    result = qm.find_leadership_indicators()
    results['find_leadership_indicators'] = print_result(
        "find_leadership_indicators()", result
    )
    
    # ========================================================================
    # TEST 20: Find Achievement Patterns
    # ========================================================================
    print_section("TEST 20: Find Achievement Patterns")
    result = qm.find_achievement_patterns()
    results['find_achievement_patterns'] = print_result(
        "find_achievement_patterns()", result
    )
    
    # ========================================================================
    # TEST 21: Analyze Career Progression
    # ========================================================================
    print_section("TEST 21: Analyze Career Progression")
    result = qm.analyze_career_progression(person_id=98905076)
    results['analyze_career_progression'] = print_result(
        "analyze_career_progression(person_id=98905076)", result
    )
    
    # ========================================================================
    # TEST 22: Find Domain Experts
    # ========================================================================
    print_section("TEST 22: Find Domain Experts")
    result = qm.find_domain_experts(["software", "development"])
    results['find_domain_experts'] = print_result(
        "find_domain_experts(['software', 'development'])", result
    )
    
    # ========================================================================
    # TEST 23: Find Similar Career Paths
    # ========================================================================
    print_section("TEST 23: Find Similar Career Paths")
    result = qm.find_similar_career_paths(reference_person_id=98905076, similarity_threshold=1)
    results['find_similar_career_paths'] = print_result(
        "find_similar_career_paths(reference_person_id=98905076, similarity_threshold=1)", result
    )
    
    # ========================================================================
    # TEST 24: Find Role Transition Patterns
    # ========================================================================
    print_section("TEST 24: Find Role Transition Patterns")
    result = qm.find_role_transition_patterns(["engineer"], ["director", "manager"])
    results['find_role_transition_patterns'] = print_result(
        "find_role_transition_patterns(['engineer'], ['director', 'manager'])", result
    )
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print_section("TEST SUMMARY")
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    failed_tests = total_tests - passed_tests
    
    print(f"\n✅ Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    
    if failed_tests > 0:
        print("\n❌ Failed Tests:")
        for test_name, passed in results.items():
            if not passed:
                print(f"   • {test_name}")
    
    print("\n" + "=" * 80)
    if failed_tests == 0:
        print("🎉 ALL TESTS PASSED!")
    else:
        print(f"⚠️  {failed_tests} test(s) failed. Review the output above.")
    print("=" * 80 + "\n")
    
    # Close database connection
    db.close()

if __name__ == "__main__":
    main()
