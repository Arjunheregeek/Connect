"""
Test LLM Enrichment on First 3 Profiles
Tests the pipeline and saves results to CSV
"""

import os
import json
import pandas as pd
import time
from llm_enrichment import extract_person_context, call_llm_for_enrichment

def test_first_three_profiles():
    """
    Test LLM enrichment on the first 3 profiles and save results
    """
    
    print("🧪 Testing LLM Enrichment on First 3 Profiles")
    print("="*70)
    print()
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("Please set it with: export OPENAI_API_KEY='your-api-key'")
        return
    
    # Load data
    input_csv = "Data/LLM_Input_Profiles.csv"
    output_csv = "Data/Test_3_Profiles_Results.csv"
    
    if not os.path.exists(input_csv):
        print(f"❌ Error: Input file not found: {input_csv}")
        return
    
    df = pd.read_csv(input_csv)
    
    print(f"📊 Total profiles available: {len(df)}")
    print(f"🎯 Testing first 3 profiles")
    print()
    
    # Process first 3 profiles
    results = []
    total_tokens = 0
    start_time = time.time()
    
    for idx in range(min(3, len(df))):
        row = df.iloc[idx]
        profile_num = idx + 1
        
        print(f"{'='*70}")
        print(f"[{profile_num}/3] Processing: {row['name']}")
        print(f"{'='*70}")
        
        # Extract context
        print("🔍 Extracting context...")
        context = extract_person_context(row)
        
        # Show brief profile info
        print(f"   Name: {context['name']}")
        print(f"   Current: {context['current_title']} at {context['current_company']}")
        print(f"   Experience: {context['years_of_experience']} years")
        print(f"   Education: {len(context['education_details'])} records")
        print(f"   Job History: {len(context['all_job_descriptions'])} positions")
        print()
        
        # Call LLM
        print("🤖 Calling LLM (gpt-4o)...")
        result = call_llm_for_enrichment(context, model="gpt-4o")

        if 'error' in result:
            print(f"   ❌ Failed: {result['error']}")
            result['name'] = context['name']
            result['person_id'] = context['person_id']
        else:
            print(f"   ✅ Success!")
            print(f"   📊 Expertise: {result.get('perceived_expertise_level', 'N/A')}/100")
            print(f"   📊 Competence: {result.get('competence_score', 'N/A')}/100")
            print(f"   👔 Seniority: {result.get('seniority_level', 'N/A')}")
            print(f"   💻 Primary Expertise: {result.get('primary_expertise', 'N/A')}")
            print(f"   🔧 Technical Skills: {len(result.get('technical_skills_refined', []))} skills")
            print(f"   🤝 Secondary Skills: {len(result.get('secondary_skills', []))} skills")
            print(f"   🏢 Domain Knowledge: {', '.join(result.get('domain_knowledge', []))}")
            print(f"   🪙 Tokens: {result.get('tokens_used', 'N/A')}")
            
            total_tokens += result.get('tokens_used', 0)
            
            # Add name for reference
            result['name'] = context['name']
        
        results.append(result)
        print()
        
        # Rate limiting (0.5 sec between requests)
        if idx < 2:  # Don't wait after last one
            time.sleep(0.5)
    
    # Save results to CSV
    results_df = pd.DataFrame(results)
    results_df.to_csv(output_csv, index=False)
    
    elapsed_time = time.time() - start_time
    
    # Print summary
    print()
    print("="*70)
    print("🎉 TEST COMPLETE!")
    print("="*70)
    print(f"✅ Profiles processed: 3/3")
    print(f"⏱️  Total time: {elapsed_time:.1f}s ({elapsed_time/3:.1f}s per profile)")
    print(f"💾 Results saved to: {output_csv}")
    
    if total_tokens > 0:
        # GPT-4o pricing estimate
        # ~$2.50 per 1M input tokens, ~$10.00 per 1M output tokens
        # Rough estimate: 70% input, 30% output
        estimated_cost = (total_tokens * 0.7 * 2.50 / 1_000_000) + (total_tokens * 0.3 * 10.00 / 1_000_000)
        print(f"🪙 Total tokens: {total_tokens:,}")
        print(f"💰 Estimated cost: ${estimated_cost:.4f}")
        print(f"📊 Average tokens per profile: {total_tokens/3:.0f}")
        print(f"📈 Projected cost for 164 profiles: ${estimated_cost * 164/3:.2f}")
    
    print()
    print("📋 Summary of Results:")
    print("-"*70)
    
    # Show summary table
    if not results_df.empty and 'error' not in results_df.columns:
        print(f"{'Name':<25} {'Expertise':<12} {'Competence':<12} {'Seniority':<15}")
        print("-"*70)
        for _, row in results_df.iterrows():
            name = row.get('name', 'Unknown')[:24]
            expertise = row.get('perceived_expertise_level', 'N/A')
            competence = row.get('competence_score', 'N/A')
            seniority = row.get('seniority_level', 'N/A')
            print(f"{name:<25} {expertise:<12} {competence:<12} {seniority:<15}")
    
    print()
    print("💡 Next Steps:")
    print("   1. Review the results in: Data/Test_3_Profiles_Results.csv")
    print("   2. Check if scores and classifications look reasonable")
    print("   3. If satisfied, run: python Pre_processing/llm_enrichment.py")
    print("   4. This will process all 164 profiles")
    print()


if __name__ == "__main__":
    test_first_three_profiles()
