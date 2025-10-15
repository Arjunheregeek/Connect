# 🚀 Quick Start Guide - Connect Agent with Pipeline Logging

## ⚡ TL;DR

```bash
# 1. Start MCP server
python -m mcp.server

# 2. Run agent with full logging
python app/agent_run_instrumented.py "Find Python developers at Google"

# 3. Check logs
cat logs/pipeline_master_*.csv
```

---

## 📊 What You Get

### **Real-time Console Logs**
```
================================================================================
📝 LOG: PLANNER → query_decomposer → decompose_output
================================================================================
🔹 Query ID: 942fb1532ec4
🔹 Timestamp: 2025-10-15T15:36:43.515146

📥 INPUT:
   query: Find Python developers

📤 OUTPUT:
   skill_filters: ["Python"]
   company_filters: []

📊 METADATA:
   - duration_sec: 1.518
   - tokens_used: 1301
================================================================================
```

### **CSV Files**
- `pipeline_master_*.csv` - All stages combined
- `planner_*.csv` - QueryDecomposer + SubQueryGenerator
- `executor_*.csv` - MCP tool calls
- `synthesizer_*.csv` - Profile fetch + GPT-4o

---

## 🎯 Use Cases

### **1. Debug Agent Behavior**
See exactly what the agent is doing at each step:
- What filters were extracted?
- Which tools were selected?
- What parameters were used?
- What results were returned?

### **2. Track Token Usage**
Monitor LLM costs:
- QueryDecomposer: ~1,300 tokens
- SubQueryGenerator: ~2,700 tokens
- GPT-4o Synthesis: ~3,000 tokens
- **Total per query: ~7,000 tokens**

### **3. Performance Analysis**
Identify bottlenecks:
- Planner: ~3-5 seconds
- Executor: ~1-3 seconds per tool
- Synthesizer: ~2-4 seconds
- **Total: ~8-12 seconds per query**

### **4. Quality Assurance**
Validate results:
- Did the right tools get called?
- Were parameters correct?
- Did results match expectations?

---

## 📁 Log File Structure

### **CSV Columns**
```csv
query_id,timestamp,stage,module,operation,input_data,output_data,metadata
```

- **query_id**: Unique identifier for tracking
- **timestamp**: ISO 8601 format
- **stage**: planner / executor / synthesizer
- **module**: query_decomposer / mcp_tool / gpt4o
- **operation**: decompose_input / tool_call_output / etc.
- **input_data**: JSON of inputs
- **output_data**: JSON of outputs
- **metadata**: JSON of extra info (tokens, duration, etc.)

---

## 🔧 Common Tasks

### **View Logs in Excel**
1. Open Excel
2. File → Open
3. Select `logs/pipeline_master_*.csv`
4. Done!

### **Analyze in Python**
```python
import pandas as pd
import json

# Load logs
df = pd.read_csv('logs/pipeline_master_20251015_153641.csv')

# Parse metadata
df['metadata_dict'] = df['metadata'].apply(json.loads)
df['tokens'] = df['metadata_dict'].apply(lambda x: x.get('tokens_used', 0))
df['duration'] = df['metadata_dict'].apply(lambda x: x.get('duration_sec', 0))

# Total tokens by stage
print(df.groupby('stage')['tokens'].sum())

# Average duration by module
print(df.groupby('module')['duration'].mean())

# Count tool calls
executor_df = df[df['stage'] == 'executor']
print(executor_df['module'].value_counts())
```

### **Filter Specific Query**
```python
# Load logs
df = pd.read_csv('logs/pipeline_master_20251015_153641.csv')

# Filter by query ID
query_logs = df[df['query_id'] == '942fb1532ec4']
print(query_logs[['timestamp', 'stage', 'module', 'operation']])
```

---

## 🎓 Understanding the Pipeline

### **Stage 1: Planner** (2 modules)
1. **QueryDecomposer**
   - Input: "Find Python developers at Google"
   - Output: `{"skill_filters": ["Python"], "company_filters": ["Google"]}`

2. **SubQueryGenerator**
   - Input: Extracted filters
   - Output: Sub-queries with tool mappings
   ```json
   {
     "sub_query": "Find people with Python in technical skills",
     "tool": "find_people_by_technical_skill",
     "params": {"skill": "Python"},
     "priority": 1
   }
   ```

### **Stage 2: Executor** (N tool calls)
For each sub-query:
- Input: Tool name + parameters
- Execute via MCP client
- Output: Person IDs + metadata

### **Stage 3: Synthesizer** (2 modules)
1. **Profile Fetching**
   - Input: Person IDs
   - Fetch complete profiles via MCP

2. **GPT-4o Synthesis**
   - Input: Profiles + original query
   - Generate natural language response
   - Output: Formatted response

---

## 💡 Pro Tips

### **1. Use Query ID for Deep Dives**
```bash
# Extract query ID from logs
grep "Query ID:" logs/pipeline_master_*.csv

# Filter by query ID
grep "942fb1532ec4" logs/pipeline_master_*.csv
```

### **2. Track Token Usage Over Time**
```python
import pandas as pd
import glob

# Load all log files
all_logs = []
for file in glob.glob('logs/pipeline_master_*.csv'):
    df = pd.read_csv(file)
    all_logs.append(df)

combined = pd.concat(all_logs)

# Track token usage over time
combined['metadata_dict'] = combined['metadata'].apply(json.loads)
combined['tokens'] = combined['metadata_dict'].apply(lambda x: x.get('tokens_used', 0))

print(combined.groupby('timestamp')['tokens'].sum().plot())
```

### **3. Compare Query Performance**
```python
# Group by query_id
query_summary = combined.groupby('query_id').agg({
    'tokens': 'sum',
    'duration': 'sum'
})

print(query_summary.sort_values('duration', ascending=False).head(10))
```

---

## 🎯 14 Tools Available

1. health_check
2. get_person_complete_profile
3. find_person_by_name
4. find_people_by_skill
5. **find_people_by_technical_skill** ⭐ NEW
6. **find_people_by_secondary_skill** ⭐ NEW
7. **find_people_by_current_company** ⭐ NEW
8. **find_people_by_company_history** 🔄 RENAMED
9. find_people_by_institution
10. find_people_by_location
11. find_people_by_experience_level
12. get_person_job_descriptions
13. search_job_descriptions_by_keywords
14. find_domain_experts

---

## 📚 More Documentation

- **PIPELINE_LOGGING.md** - Complete logging guide
- **IMPLEMENTATION_COMPLETE.md** - Full project summary
- **QUERY_TYPES.md** - Query examples
- **USAGE.md** - Agent usage guide

---

## 🆘 Troubleshooting

### **No logs generated?**
- Check if `logs/` directory exists
- Verify agent completed successfully
- Look for error messages in console

### **Query ID shows "unknown"?**
- This is normal for some internal calls
- Main query ID is still tracked correctly
- Doesn't affect functionality

### **CSV won't open in Excel?**
- Try Google Sheets instead
- Or use pandas in Python
- Check file encoding (should be UTF-8)

---

**Created:** October 15, 2025  
**Version:** 1.0  
**Status:** ✅ Production Ready
