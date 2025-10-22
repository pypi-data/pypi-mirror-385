---
title: "LLM Evaluations"
description: "Use LLM-as-judge methodology for quality assessment. Measure helpfulness, clarity, appropriateness, and completeness with configurable scoring criteria."
---

# LLM Evaluations

LLM evaluations use LLM-as-judge methodology with configurable scoring criteria for quality assessment. They're ideal for subjective quality measures like helpfulness, clarity, and appropriateness that can't be easily measured with rules-based approaches.

## What LLM Evaluations Test

LLM evaluations leverage AI models to assess subjective quality dimensions:

- **Response quality** - Overall helpfulness and usefulness of responses
- **Clarity and coherence** - How well responses communicate information
- **Appropriateness** - Whether responses are suitable for the context
- **Completeness** - How thoroughly responses address user needs
- **Professional tone** - Maintaining appropriate communication style
- **Factual accuracy** - Correctness of information provided
- **User satisfaction** - Predicted user satisfaction with responses

## When to Use LLM Evaluations

Use LLM evaluations for subjective quality assessment:

- ✅ **Content quality** - Assess overall response quality and helpfulness
- ✅ **Subjective criteria** - Evaluate aspects that require judgment
- ✅ **User experience** - Predict user satisfaction with responses
- ✅ **Complex reasoning** - Evaluate multi-step problem-solving
- ✅ **Creative content** - Assess creativity, originality, and engagement
- ✅ **Professional communication** - Evaluate tone, style, and appropriateness
- ❌ **Exact matching** - Use accuracy evaluations instead
- ❌ **Performance metrics** - Use performance evaluations instead
- ❌ **Deterministic checks** - Use accuracy or consistency evaluations

## Configuration

### Basic Configuration

```toml
[eval]
description = "LLM evaluation of response quality"
type = "llm"
targets.agents = ["*"]               # Test all agents
targets.tools = []                   # Skip tools

[eval.llm]
model = "gpt-4"                      # LLM model to use as judge
prompt = "Evaluate the helpfulness and accuracy of this response."
```

### Supported Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `description` | String | Yes | Brief description of the test |
| `type` | String | Yes | Must be `"llm"` |
| `targets.agents` | Array[String] | Yes | Agents to test (`["*"]` for all) |
| `targets.tools` | Array[String] | Yes | Tools to test (`["*"]` for all) |

### LLM Configuration (`[eval.llm]`)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `model` | String | Yes | LLM model to use as judge |
| `prompt` | String | Yes | Evaluation prompt for the LLM judge |
| `output_schema` | Object | No | TOML schema for structured LLM output |
| `temperature` | Number | No | Model temperature (default: 0.1 for consistency) |
| `max_tokens` | Number | No | Maximum tokens for LLM response |

### Available Judge Models

| Model | Best For | Cost | Speed |
|-------|----------|------|-------|
| `gpt-4` | High-quality evaluation | High | Slow |
| `gpt-4-turbo` | Balanced quality and speed | Medium | Medium |
| `gpt-3.5-turbo` | Fast, cost-effective evaluation | Low | Fast |
| `claude-3-opus` | Detailed, nuanced evaluation | High | Medium |
| `claude-3-sonnet` | Balanced evaluation | Medium | Fast |

## Test Cases

### Basic Test Case Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `prompt` | String | No* | Input prompt for agents |
| `context` | Object | No* | Parameters for tools or agent context |
| `score` | Object | Yes | Expected score constraints |
| `criteria` | Array[String] | No | Specific evaluation criteria |
| `reference_response` | String | No | Optional reference for comparison |

*Either `prompt` or `context` (or both) must be provided

### Score Constraints

| Constraint | Description | Example |
|------------|-------------|---------|
| `min` | Minimum acceptable score | `{ min = 7 }` |
| `max` | Maximum acceptable score | `{ max = 9 }` |
| `equal` | Exact score required | `{ equal = 10 }` |
| `range` | Score within range | `{ min = 6, max = 8 }` |

## Examples

### Basic Quality Assessment

```toml
[eval]
description = "Evaluate general response quality"
type = "llm"
targets.agents = ["customer-support"]
targets.tools = []

[eval.llm]
model = "gpt-4"
prompt = """
Evaluate this response on a scale of 1-10 considering:
- Helpfulness: How well does it address the user's question?
- Accuracy: Is the information provided correct?
- Clarity: Is the response easy to understand?
- Completeness: Does it fully answer the question?

Provide a score and brief reasoning.
"""

[eval.llm.output_schema]
score = { type = "int", min = 1, max = 10 }
reasoning = { type = "str" }

[[eval.cases]]
prompt = "I need help with my account login"
score = { min = 7 }

[[eval.cases]]
prompt = "What are your business hours?"
score = { min = 8 }

[[eval.cases]]
prompt = "How do I cancel my subscription?"
score = { min = 7, max = 10 }
```

### Multi-Criteria Evaluation

```toml
[eval]
description = "Multi-dimensional quality assessment"
type = "llm"
targets.agents = ["technical-support"]
targets.tools = []

[eval.llm]
model = "gpt-4"
prompt = """
Evaluate this technical support response across multiple dimensions:

1. Technical Accuracy (1-10): Is the technical information correct?
2. Clarity (1-10): Is the explanation clear and easy to follow?
3. Completeness (1-10): Does it address all aspects of the question?
4. Actionability (1-10): Are the steps concrete and actionable?
5. Professional Tone (1-10): Is the tone appropriate and helpful?

Provide scores for each dimension and overall assessment.
"""

[eval.llm.output_schema]
technical_accuracy = { type = "int", min = 1, max = 10 }
clarity = { type = "int", min = 1, max = 10 }
completeness = { type = "int", min = 1, max = 10 }
actionability = { type = "int", min = 1, max = 10 }
professional_tone = { type = "int", min = 1, max = 10 }
overall_score = { type = "int", min = 1, max = 10 }
feedback = { type = "str" }

[[eval.cases]]
prompt = "My application keeps crashing when I try to upload files. What should I do?"
score = { min = 7 }
criteria = ["technical_accuracy", "actionability", "clarity"]

[[eval.cases]]
prompt = "I'm getting a 500 error on your API. Can you help me debug this?"
score = { min = 8 }
criteria = ["technical_accuracy", "completeness"]
```

### Creative Content Evaluation

```toml
[eval]
description = "Evaluate creative writing quality"
type = "llm"
targets.agents = ["creative-writer"]
targets.tools = []

[eval.llm]
model = "claude-3-opus"
prompt = """
Evaluate this creative content on:
- Creativity and originality (1-10)
- Engagement and readability (1-10)
- Relevance to the prompt (1-10)
- Overall quality (1-10)

Consider the target audience and purpose when scoring.
"""

[eval.llm.output_schema]
creativity = { type = "int", min = 1, max = 10 }
engagement = { type = "int", min = 1, max = 10 }
relevance = { type = "int", min = 1, max = 10 }
overall = { type = "int", min = 1, max = 10 }
commentary = { type = "str" }

[[eval.cases]]
prompt = "Write a compelling product description for a smart home device"
score = { min = 6 }

[[eval.cases]]
prompt = "Create an engaging social media post about our company culture"
score = { min = 7 }

[[eval.cases]]
prompt = "Draft a creative email subject line for our newsletter"
score = { min = 8 }
```

### Educational Content Assessment

```toml
[eval]
description = "Evaluate educational explanations"
type = "llm"
targets.agents = ["tutor-bot"]
targets.tools = []

[eval.llm]
model = "gpt-4"
prompt = """
Assess this educational explanation for:
- Accuracy of information (1-10)
- Clarity of explanation (1-10)
- Appropriate level for audience (1-10)
- Use of examples and analogies (1-10)
- Engagement and motivation (1-10)

Consider pedagogical effectiveness in your evaluation.
"""

[[eval.cases]]
prompt = "Explain how photosynthesis works to a 5th grader"
score = { min = 8 }
criteria = ["clarity", "appropriate_level", "examples"]

[[eval.cases]]
prompt = "What is quantum mechanics?"
score = { min = 6, max = 9 }
criteria = ["accuracy", "clarity"]

[[eval.cases]]
prompt = "How do you solve quadratic equations?"
score = { equal = 10 }        # Math explanations should be perfect
criteria = ["accuracy", "examples"]
```

### Comparative Evaluation

```toml
[eval]
description = "Compare responses against reference answers"
type = "llm"
targets.agents = ["knowledge-expert"]
targets.tools = []

[eval.llm]
model = "gpt-4"
prompt = """
Compare the agent's response to the reference answer:
- How well does it match the reference quality? (1-10)
- Does it provide equivalent or better information? (1-10)
- Is it more or less helpful than the reference? (1-10)

Score based on relative quality, not exact matching.
"""

[[eval.cases]]
prompt = "What is the company's return policy?"
reference_response = "We offer a 30-day return policy for all items in original condition with receipt. Returns can be processed in-store or by mail. Refunds are issued to the original payment method within 5-7 business days."
score = { min = 8 }

[[eval.cases]]
prompt = "How do I reset my password?"
reference_response = "To reset your password: 1) Go to the login page, 2) Click 'Forgot Password', 3) Enter your email address, 4) Check your email for a reset link, 5) Follow the link and create a new password. Contact support if you don't receive the email within 10 minutes."
score = { min = 9 }
```

## Advanced Configuration

### Custom Scoring Rubrics

```toml
[eval.llm]
model = "gpt-4"
prompt = """
Use this scoring rubric:

EXCELLENT (9-10): Response fully addresses the question with accurate, comprehensive information. Clear, professional tone. Actionable guidance provided.

GOOD (7-8): Response addresses most aspects of the question with generally accurate information. Minor gaps in completeness or clarity.

SATISFACTORY (5-6): Response addresses the basic question but may lack detail or have minor inaccuracies. Adequate but not exceptional.

NEEDS IMPROVEMENT (3-4): Response partially addresses the question but has significant gaps or inaccuracies. Unclear or unprofessional tone.

POOR (1-2): Response fails to address the question adequately. Major inaccuracies or inappropriate tone.

Provide score and specific feedback based on this rubric.
"""
```

### Domain-Specific Evaluation

```toml
[eval]
description = "Medical information quality assessment"
type = "llm"
targets.agents = ["health-info-bot"]
targets.tools = []

[eval.llm]
model = "gpt-4"
prompt = """
Evaluate this health information response as a medical professional would:

CRITICAL FACTORS:
- Medical accuracy and evidence-based information
- Appropriate disclaimers about seeking professional medical advice
- Avoidance of specific diagnoses or treatment recommendations
- Clear, accessible language for general public
- Appropriate level of detail without overwhelming

Rate 1-10 and provide detailed medical accuracy assessment.
"""

[[eval.cases]]
prompt = "What are the symptoms of diabetes?"
score = { min = 8 }

[[eval.cases]]
prompt = "Should I take antibiotics for my cold?"
score = { min = 9 }           # Should clearly advise against inappropriate antibiotic use
```

### Multi-Model Consensus

```toml
# Use multiple LLMs for consensus evaluation
[eval]
description = "Multi-model consensus evaluation"
type = "llm"

# Primary evaluation with GPT-4
[eval.llm]
model = "gpt-4"
prompt = "Evaluate this response for overall quality (1-10)..."

# Additional evaluation configurations can be added
# to compare scores across different judge models
```

## Best Practices

### Prompt Engineering for Judges

1. **Be specific about criteria:**
   ```toml
   prompt = """
   Evaluate on these specific criteria:
   1. Factual accuracy - Is the information correct?
   2. Completeness - Does it answer all parts of the question?
   3. Clarity - Is it easy to understand?
   4. Helpfulness - Would this solve the user's problem?
   """
   ```

2. **Include context and examples:**
   ```toml
   prompt = """
   You are evaluating customer support responses.
   Good responses: address the issue, provide clear steps, maintain professional tone.
   Poor responses: are vague, lack actionable advice, or are unprofessional.

   Evaluate this response (1-10):...
   """
   ```

3. **Use structured output:**
   ```toml
   [eval.llm.output_schema]
   score = { type = "int", min = 1, max = 10 }
   strengths = { type = "list[str]" }
   weaknesses = { type = "list[str]" }
   suggestions = { type = "str" }
   ```

### Score Threshold Selection

```toml
# Conservative thresholds for critical content
score = { min = 9 }            # Medical advice, legal information

# Standard thresholds for general content
score = { min = 7 }            # Customer support, general Q&A

# Flexible thresholds for creative content
score = { min = 5, max = 10 }  # Creative writing, brainstorming
```

### Model Selection Strategy

```toml
# Use GPT-4 for highest quality evaluation
model = "gpt-4"               # Best for complex, nuanced evaluation

# Use GPT-4-turbo for balanced quality and speed
model = "gpt-4-turbo"         # Good compromise for most use cases

# Use GPT-3.5-turbo for cost-effective evaluation
model = "gpt-3.5-turbo"       # Suitable for simple quality checks
```

## Advanced Analysis

### Score Distribution Analysis

LLM evaluations provide rich analytics:

- **Score distributions** - Understanding quality patterns
- **Criteria breakdown** - Performance across different dimensions
- **Trend analysis** - Quality improvements or degradations over time
- **Comparative analysis** - Performance across different agents or versions

### Inter-Rater Reliability

```toml
# Use multiple judge models for reliability assessment
[eval]
description = "Multi-judge reliability test"

# Compare scores from different models to ensure consistency
```

## Troubleshooting

### Inconsistent Scores

```toml
# If LLM scores are inconsistent:

# 1. Lower temperature for more consistent judging
[eval.llm]
temperature = 0.0             # Most deterministic

# 2. Use more specific evaluation criteria
prompt = "Evaluate ONLY the factual accuracy of this response (1-10)..."

# 3. Add reference examples to the prompt
prompt = """
Score this response compared to these examples:
Excellent (10): [example of perfect response]
Good (7): [example of good response]
Poor (3): [example of poor response]
"""
```

### Score Inflation/Deflation

```toml
# If scores are consistently too high or low:

# 1. Calibrate with reference responses
[[eval.cases]]
prompt = "Test question"
reference_response = "Known high-quality response"
score = { equal = 9 }         # Calibrate judge expectations

# 2. Adjust scoring prompts
prompt = "Be critical in your evaluation. Score harshly for any deficiencies..."

# 3. Use comparative scoring
prompt = "Rate this response relative to typical customer service quality..."
```

### Judge Model Bias

```toml
# Address potential biases in judge models:

# 1. Use multiple judge models for consensus
model = "gpt-4"               # Primary judge
# Compare with Claude-3-opus, GPT-3.5-turbo

# 2. Test with known good/bad examples
[[eval.cases]]
prompt = "Known poor response example"
score = { max = 3 }           # Should score low

[[eval.cases]]
prompt = "Known excellent response example"
score = { min = 9 }           # Should score high
```

## Production Considerations

### Cost Management

LLM evaluations can be expensive:

```toml
# Use cost-effective models for high-volume testing
model = "gpt-3.5-turbo"       # Lower cost for bulk evaluation

# Reserve premium models for critical evaluations
model = "gpt-4"               # High-stakes content only

# Optimize prompt length
prompt = "Concise evaluation prompt..."  # Shorter prompts reduce costs
```

### Evaluation Frequency

```toml
# Balance thoroughness with cost:

# Critical evaluations: Every deployment
# Standard evaluations: Weekly/monthly
# Experimental evaluations: As needed
```

## Integration with Human Review

```toml
# LLM evaluations complement human review:

# Use LLM for initial screening
score = { min = 6 }           # Flag low-quality responses

# Human review for edge cases
score = { min = 4, max = 6 }  # Borderline cases need human judgment

# LLM for scale, human for quality
# High-volume: LLM evaluation
# High-stakes: Human review
```

## Next Steps

- [Configuration Overview](evaluations.md) - Complete TOML reference
- [Accuracy Evaluations](eval-accuracy.md) - Complement with exact matching