"""
LLM Enrichment Pipeline
Uses GPT-4o-mini to extract intelligent attributes requiring domain expertise
"""

import os
import json
import pandas as pd
from openai import OpenAI
import time
from typing import Dict, Any, List

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_person_context(row: pd.Series) -> Dict[str, Any]:
    """
    Extract comprehensive context from LLM input CSV row
    """
    context = {
        "person_id": int(row['person_id']),
        "name": row['name'],
        "headline": row.get('headline', ''),
        "summary": row.get('summary', ''),
        "current_title": row.get('current_title', ''),
        "current_company": row.get('current_company', ''),
        "current_industry": row.get('current_industry', ''),
        "years_of_experience": float(row.get('years_of_experience', 0)),
        "followers_count": int(row.get('followers_count', 0))
    }
    
    # Parse JSON fields
    try:
        context['all_job_descriptions'] = json.loads(row['all_job_descriptions']) if pd.notna(row['all_job_descriptions']) else []
    except:
        context['all_job_descriptions'] = []
    
    try:
        context['education_details'] = json.loads(row['education_details']) if pd.notna(row['education_details']) else []
    except:
        context['education_details'] = []
    
    try:
        context['education_degrees'] = json.loads(row['education_degrees']) if pd.notna(row['education_degrees']) else []
    except:
        context['education_degrees'] = []
    
    try:
        context['all_skills'] = json.loads(row['all_skills']) if pd.notna(row['all_skills']) else []
    except:
        context['all_skills'] = []
    
    return context


def create_llm_prompt(context: Dict[str, Any]) -> str:
    """
    Create structured prompt for LLM with attribute definitions and scoring rubrics
    """
    
    prompt = f"""You are an expert career assessment analyst. Analyze the following professional profile and extract 8 intelligent attributes with objective, evidence-based reasoning.

PROFILE CONTEXT:
{json.dumps(context, indent=2)}

EXTRACT THE FOLLOWING ATTRIBUTES:

1. perceived_expertise_level (0-100): Based on title progression, years of experience, followers, company tier
   - 0-20: Entry level, minimal experience
   - 21-40: Junior with growing skills
   - 41-60: Mid-level with solid expertise
   - 61-80: Senior with deep expertise
   - 81-100: Industry expert/thought leader

2. competence_score (0-100): Based on technical skills depth, education, achievements, company quality
   - Consider: breadth and depth of skills, educational pedigree, notable achievements, company reputation
   - 0-20: Basic competence
   - 21-40: Developing competence
   - 41-60: Solid competence
   - 61-80: High competence
   - 81-100: Exceptional competence

3. seniority_level (categorical): Choose ONE from:
   - "Executive": C-suite, VP, SVP positions
   - "Senior": Senior Manager, Senior Engineer, Lead, Principal
   - "Mid-Level": Manager, Engineer, Specialist (3-8 years exp)
   - "Junior": Entry-level, Intern, Associate (0-3 years exp)
   - "Founder": Startup founder, Co-founder, Entrepreneur

4. primary_expertise (categorical): Choose ONE primary area from:
   - "AI & ML"
   - "Data Science & Analytics"
   - "Cloud & DevOps"
   - "Backend Development"
   - "Frontend Development"
   - "Full Stack Development"
   - "Mobile Development"
   - "Product Management"
   - "Engineering Leadership"
   - "Research & Innovation"
   - "System Architecture"
   - "Cybersecurity"
   - "Embedded Systems"
   - "Hardware Engineering"
   - "Business & Strategy"
   - "Other"

5. technical_skills_refined (array): Extract 10-15 PRIMARY technical skills from job descriptions
   - Focus on skills actually used/mentioned in work experience
   - Prioritize programming languages, frameworks, tools, technologies
   - Example: ["Python", "TensorFlow", "AWS", "Docker", "React", "PostgreSQL"]

6. secondary_skills (array): Extract 8-10 NON-TECHNICAL professional skills
   - Focus on: leadership, communication, project management, strategic thinking
   - Example: ["Team Leadership", "Strategic Planning", "Cross-functional Collaboration"]

7. domain_knowledge (array): Extract up to 5 industry domains based on work history
   - Choose from: FinTech, HealthTech, EdTech, E-Commerce, SaaS, Enterprise Software, 
     Consumer Tech, Gaming, Telecommunications, IoT, Robotics, Autonomous Vehicles, 
     Media & Entertainment, Marketing Tech, HR Tech, LegalTech, Real Estate Tech, etc.

8. industry_refined (categorical): Choose ONE primary industry from:
   - "Technology & Software"
   - "Financial Services"
   - "Healthcare & Biotech"
   - "E-Commerce & Retail"
   - "Telecommunications"
   - "Manufacturing & Industrial"
   - "Media & Entertainment"
   - "Education & EdTech"
   - "Consulting & Professional Services"
   - "Energy & Utilities"
   - "Government & Defense"
   - "Automotive"
   - "Real Estate & Construction"
   - "Agriculture & Food"
   - "Other"

IMPORTANT INSTRUCTIONS:
- Be objective and evidence-based
- Use job descriptions, titles, and company information as primary evidence
- Consider years of experience and career trajectory
- For scores, use the full 0-100 range based on evidence
- For categorical attributes, choose the BEST match
- Provide brief reasoning for your assessments

OUTPUT FORMAT (strict JSON):
{{
  "perceived_expertise_level": <0-100 integer>,
  "competence_score": <0-100 integer>,
  "seniority_level": "<category>",
  "primary_expertise": "<category>",
  "technical_skills_refined": ["skill1", "skill2", ...],
  "secondary_skills": ["skill1", "skill2", ...],
  "domain_knowledge": ["domain1", "domain2", ...],
  "industry_refined": "<category>",
  "reasoning": "Brief explanation of key assessments"
}}
"""
    
    return prompt


def call_llm_for_enrichment(context: Dict[str, Any], model: str = "gpt-4o") -> Dict[str, Any]:
    """
    Call OpenAI API to extract attributes
    """
    prompt = create_llm_prompt(context)
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert career assessment analyst. You analyze professional profiles and extract structured attributes with evidence-based reasoning."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=1000,
        )

        # Try multiple common response fields to support different model/SDK shapes
        raw_candidates: List[str] = []

        try:
            # Common newer SDK shape: response.choices[0].message.content
            raw_candidates.append(getattr(response.choices[0].message, 'content', None))
        except Exception:
            pass

        try:
            # Older SDK shape: response.choices[0].message is a dict
            msg = response.choices[0].message if isinstance(response.choices[0].message, dict) else None
            if msg and 'content' in msg:
                raw_candidates.append(msg['content'])
        except Exception:
            pass

        try:
            # Some responses use choices[0].text
            raw_candidates.append(getattr(response.choices[0], 'text', None))
        except Exception:
            pass

        try:
            # Some SDKs return output array
            if hasattr(response, 'output') and response.output:
                # Attempt to join nested text pieces
                parts = []
                for out in response.output:
                    if isinstance(out, dict):
                        # try common places
                        for k in ('content', 'text', 'message'):
                            v = out.get(k)
                            if isinstance(v, str):
                                parts.append(v)
                    elif isinstance(out, str):
                        parts.append(out)
                if parts:
                    raw_candidates.append('\n'.join(parts))
        except Exception:
            pass

        # Fallback: entire response string
        try:
            raw_candidates.append(str(response))
        except Exception:
            pass

        # Try to parse JSON from candidates
        parsed = None
        raw_preview = None
        for cand in raw_candidates:
            if not cand or not isinstance(cand, str):
                continue
            txt = cand.strip()
            if not txt:
                continue
            raw_preview = txt[:1000]
            # First try direct JSON parse
            try:
                parsed = json.loads(txt)
                break
            except Exception:
                # Try to extract JSON object embedded in text
                try:
                    import re
                    m = re.search(r"\{[\s\S]*\}", txt)
                    if m:
                        parsed = json.loads(m.group(0))
                        break
                except Exception:
                    pass

        if parsed is None:
            # Could not parse structured JSON - return helpful debug info
            err_msg = "LLM returned non-JSON or empty response"
            print(f"❌ Error calling LLM for person {context['person_id']}: {err_msg}")
            return {
                "person_id": context['person_id'],
                "name": context['name'],
                "error": err_msg,
                "raw_preview": raw_preview
            }

        # Add metadata
        parsed['person_id'] = context['person_id']
        parsed['name'] = context['name']
        parsed['model_used'] = model
        try:
            parsed['tokens_used'] = getattr(response.usage, 'total_tokens', None) or response.usage.total_tokens
        except Exception:
            parsed['tokens_used'] = None

        return parsed

    except Exception as e:
        print(f"❌ Error calling LLM for person {context['person_id']}: {e}")
        return {
            "person_id": context['person_id'],
            "name": context['name'],
            "error": str(e)
        }


def enrich_profiles_with_llm(
    input_csv: str,
    output_csv: str,
    model: str = "gpt-4o",
    batch_size: int = 10,
    rate_limit_delay: float = 0.5
) -> None:
    """
    Batch process all profiles with LLM enrichment
    """
    
    print("🚀 Starting LLM Enrichment Pipeline")
    print(f"📂 Input: {input_csv}")
    print(f"💾 Output: {output_csv}")
    print(f"🤖 Model: {model}")
    print(f"⏱️  Rate limit delay: {rate_limit_delay}s per request")
    print()
    
    # Load input data
    df = pd.read_csv(input_csv)
    total_profiles = len(df)
    print(f"📊 Total profiles to enrich: {total_profiles}")
    print()
    
    # Process each profile
    enriched_results = []
    failed_profiles = []
    
    start_time = time.time()
    
    for idx, row in df.iterrows():
        profile_num = idx + 1
        
        try:
            # Extract context
            context = extract_person_context(row)
            
            print(f"[{profile_num}/{total_profiles}] Processing: {context['name']} (ID: {context['person_id']})")
            
            # Call LLM
            result = call_llm_for_enrichment(context, model=model)
            
            if 'error' in result:
                failed_profiles.append(context['person_id'])
                print(f"  ❌ Failed")
            else:
                print(f"  ✅ Success (Expertise: {result.get('perceived_expertise_level', 'N/A')}, Competence: {result.get('competence_score', 'N/A')}, Tokens: {result.get('tokens_used', 'N/A')})")
            
            enriched_results.append(result)
            
            # Save progress every batch_size profiles
            if profile_num % batch_size == 0:
                temp_df = pd.DataFrame(enriched_results)
                temp_df.to_csv(output_csv.replace('.csv', '_partial.csv'), index=False)
                print(f"  💾 Progress saved ({profile_num}/{total_profiles})")
            
            # Rate limiting
            time.sleep(rate_limit_delay)
            
        except Exception as e:
            print(f"  ❌ Unexpected error for {row.get('name', 'Unknown')}: {e}")
            failed_profiles.append(row.get('person_id', 'Unknown'))
    
    # Save final results
    enriched_df = pd.DataFrame(enriched_results)
    enriched_df.to_csv(output_csv, index=False)
    
    elapsed_time = time.time() - start_time
    
    # Print summary
    print()
    print("="*70)
    print("🎉 LLM ENRICHMENT COMPLETE!")
    print("="*70)
    print(f"✅ Successfully enriched: {total_profiles - len(failed_profiles)}/{total_profiles}")
    print(f"❌ Failed profiles: {len(failed_profiles)}")
    if failed_profiles:
        print(f"   Failed IDs: {failed_profiles}")
    print(f"⏱️  Total time: {elapsed_time:.1f}s ({elapsed_time/total_profiles:.2f}s per profile)")
    print(f"💾 Output saved to: {output_csv}")
    
    # Calculate cost estimate (rough)
    if enriched_df['tokens_used'].notna().sum() > 0:
        total_tokens = enriched_df['tokens_used'].sum()
        # GPT-4o pricing: $2.50 per 1M input tokens, $10.00 per 1M output tokens
        # Rough estimate assuming 70% input, 30% output
        estimated_cost = (total_tokens * 0.7 * 2.50 / 1_000_000) + (total_tokens * 0.3 * 10.00 / 1_000_000)
        print(f"💰 Total tokens: {total_tokens:,} (estimated cost: ${estimated_cost:.2f})")
    
    print()


if __name__ == "__main__":
    # Paths
    input_csv = "Data/LLM_Input_Profiles.csv"
    output_csv = "Data/LLM_Enriched_People_Knowledge_Graph.csv"
    
    # Check if OPENAI_API_KEY is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("Please set it with: export OPENAI_API_KEY='your-api-key'")
        exit(1)
    
    # Run enrichment
    enrich_profiles_with_llm(
        input_csv=input_csv,
        output_csv=output_csv,
        model="gpt-4o",
        batch_size=10,
        rate_limit_delay=0.5
    )
