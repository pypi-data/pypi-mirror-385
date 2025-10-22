# Custom Evaluations

Custom evaluations allow you to reference custom Python evaluation modules for advanced evaluation capabilities beyond built-in types.

## What Custom Evaluations Enable

Custom evaluations provide complete flexibility for specialized testing:

- **Domain-specific logic** - Industry or application-specific evaluation criteria
- **Complex validation** - Multi-step validation that can't be expressed in TOML
- **External integrations** - Connect to external services or databases
- **Advanced algorithms** - Machine learning models, statistical tests, etc.
- **Reusable evaluation logic** - Share evaluation code across multiple test cases

## When to Use Custom Evaluations

Use custom evaluations for specialized needs:

- ✅ **Complex business logic** - Domain-specific rules too complex for built-in types
- ✅ **External validation** - Need to call external APIs or services
- ✅ **Statistical analysis** - Advanced metrics beyond standard evaluations
- ✅ **ML-based validation** - Custom machine learning models for evaluation
- ✅ **Legacy integration** - Integrate with existing testing infrastructure
- ❌ **Simple string matching** - Use accuracy evaluations instead
- ❌ **Standard metrics** - Use built-in evaluation types when possible

## Configuration

### Basic Configuration

```toml
[eval]
description = "Custom evaluation logic"
type = "custom"
targets.agents = ["*"]
targets.tools = []

[eval.custom]
module = "my_evaluations.advanced_logic"  # Python module path
function = "evaluate_response"             # Function name within module

[[eval.cases]]
prompt = "Test input"
parameters = { threshold = 0.8, mode = "strict" }  # Custom parameters
```

### Supported Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `description` | String | Yes | Brief description of the test |
| `type` | String | Yes | Must be `"custom"` |
| `targets.agents` | Array[String] | Yes | Agents to test (`["*"]` for all) |
| `targets.tools` | Array[String] | Yes | Tools to test (`["*"]` for all) |

### Custom Configuration (`[eval.custom]`)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `module` | String | Yes | Python module path (e.g., `"my_pkg.evaluations"`) |
| `function` | String | Yes | Function name within the module |

## Python Evaluation Function

### Function Signature

Your custom evaluation function must accept these parameters:

```python
def evaluate_response(
    output: str,           # Agent/tool output to evaluate
    parameters: dict,      # Custom parameters from TOML
    prompt: str | None = None,      # Input prompt (for agents)
    context: dict | None = None,    # Input context (for tools)
) -> dict:
    """
    Evaluate the response and return results.

    Returns:
        dict with keys:
            - passed (bool): Whether the evaluation passed
            - score (float, optional): Numeric score
            - message (str, optional): Explanation or feedback
            - metadata (dict, optional): Additional data
    """
    # Your evaluation logic here
    return {
        "passed": True,
        "score": 0.95,
        "message": "Response meets quality criteria",
        "metadata": {"confidence": 0.87}
    }
```

### Return Value

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `passed` | bool | Yes | Whether the evaluation passed |
| `score` | float | No | Numeric score (0.0-1.0 recommended) |
| `message` | str | No | Explanation or feedback message |
| `metadata` | dict | No | Additional evaluation data |

## Examples

### Basic Custom Evaluation

**TOML Configuration:**
```toml
[eval]
description = "Validate business-specific rules"
type = "custom"
targets.agents = ["sales-agent"]
targets.tools = []

[eval.custom]
module = "my_company.evaluations"
function = "validate_sales_response"

[[eval.cases]]
prompt = "Create a quote for 100 units"
parameters = {
  max_discount = 0.15,
  require_approval_above = 10000
}

[[eval.cases]]
prompt = "What's our pricing for enterprise customers?"
parameters = {
  require_tier_mention = true
}
```

**Python Module** (`my_company/evaluations.py`):
```python
def validate_sales_response(output: str, parameters: dict, **kwargs) -> dict:
    """Validate sales agent responses against business rules."""

    max_discount = parameters.get("max_discount", 0.1)
    require_approval = parameters.get("require_approval_above")
    require_tier = parameters.get("require_tier_mention", False)

    # Extract discount from response
    import re
    discount_match = re.search(r'(\d+)%\s+discount', output)

    if discount_match:
        discount = float(discount_match.group(1)) / 100
        if discount > max_discount:
            return {
                "passed": False,
                "message": f"Discount {discount:.0%} exceeds maximum {max_discount:.0%}"
            }

    # Check for tier mention
    if require_tier and "tier" not in output.lower():
        return {
            "passed": False,
            "message": "Response must mention pricing tiers"
        }

    return {
        "passed": True,
        "score": 1.0,
        "message": "Response follows business rules"
    }
```

### External API Validation

**TOML Configuration:**
```toml
[eval]
description = "Validate against external fact-checking API"
type = "custom"
targets.agents = ["fact-checker"]
targets.tools = []

[eval.custom]
module = "evaluations.external"
function = "fact_check_response"

[[eval.cases]]
prompt = "When was the first iPhone released?"
parameters = {
  api_endpoint = "https://fact-check-api.example.com/verify",
  min_confidence = 0.8
}
```

**Python Module** (`evaluations/external.py`):
```python
import requests

def fact_check_response(output: str, parameters: dict, **kwargs) -> dict:
    """Validate response against external fact-checking API."""

    api_endpoint = parameters["api_endpoint"]
    min_confidence = parameters.get("min_confidence", 0.7)

    # Call external API
    response = requests.post(
        api_endpoint,
        json={"claim": output},
        timeout=10
    )

    result = response.json()
    confidence = result.get("confidence", 0)
    is_accurate = result.get("accurate", False)

    passed = is_accurate and confidence >= min_confidence

    return {
        "passed": passed,
        "score": confidence,
        "message": f"Fact check: {result.get('verdict', 'Unknown')}",
        "metadata": {
            "api_response": result,
            "confidence": confidence
        }
    }
```

### ML Model Evaluation

**TOML Configuration:**
```toml
[eval]
description = "Quality assessment using ML model"
type = "custom"
targets.agents = ["content-generator"]
targets.tools = []

[eval.custom]
module = "evaluations.ml_quality"
function = "assess_content_quality"

[[eval.cases]]
prompt = "Write a product description for a smart watch"
parameters = {
  model_path = "models/quality_classifier.pkl",
  min_score = 0.75,
  aspects = ["clarity", "persuasiveness", "technical_accuracy"]
}
```

**Python Module** (`evaluations/ml_quality.py`):
```python
import pickle
import numpy as np

# Load model once at module level
_model_cache = {}

def load_model(model_path: str):
    """Load and cache ML model."""
    if model_path not in _model_cache:
        with open(model_path, 'rb') as f:
            _model_cache[model_path] = pickle.load(f)
    return _model_cache[model_path]

def assess_content_quality(output: str, parameters: dict, **kwargs) -> dict:
    """Assess content quality using ML model."""

    model_path = parameters["model_path"]
    min_score = parameters.get("min_score", 0.7)
    aspects = parameters.get("aspects", [])

    # Load model
    model = load_model(model_path)

    # Extract features (simplified example)
    features = extract_features(output)

    # Get prediction
    quality_score = model.predict_proba([features])[0][1]

    # Assess individual aspects
    aspect_scores = {}
    for aspect in aspects:
        aspect_scores[aspect] = assess_aspect(output, aspect)

    passed = quality_score >= min_score

    return {
        "passed": passed,
        "score": float(quality_score),
        "message": f"Quality score: {quality_score:.2%}",
        "metadata": {
            "aspect_scores": aspect_scores,
            "feature_importance": get_feature_importance(model, features)
        }
    }

def extract_features(text: str) -> np.ndarray:
    """Extract features from text for ML model."""
    # Simplified feature extraction
    return np.array([
        len(text),                          # Length
        len(text.split()),                  # Word count
        text.count('!') + text.count('?'),  # Excitement markers
        # ... more features
    ])

def assess_aspect(text: str, aspect: str) -> float:
    """Assess individual quality aspect."""
    # Simplified aspect assessment
    aspect_keywords = {
        "clarity": ["clear", "simple", "understand"],
        "persuasiveness": ["benefit", "advantage", "improve"],
        "technical_accuracy": ["specification", "feature", "capability"]
    }

    keywords = aspect_keywords.get(aspect, [])
    score = sum(1 for kw in keywords if kw in text.lower()) / max(len(keywords), 1)
    return min(score, 1.0)

def get_feature_importance(model, features):
    """Get feature importance from model."""
    if hasattr(model, 'feature_importances_'):
        return model.feature_importances_.tolist()
    return []
```

### Statistical Validation

**TOML Configuration:**
```toml
[eval]
description = "Statistical validation of numeric outputs"
type = "custom"
targets.tools = ["data-analyzer"]
targets.agents = []

[eval.custom]
module = "evaluations.statistics"
function = "validate_statistical_output"

[[eval.cases]]
context = { dataset = "sales_data", operation = "mean" }
parameters = {
  expected_range = [1000, 2000],
  confidence_level = 0.95,
  allow_outliers = false
}
```

**Python Module** (`evaluations/statistics.py`):
```python
import json
from scipy import stats
import numpy as np

def validate_statistical_output(
    output: str,
    parameters: dict,
    context: dict | None = None,
    **kwargs
) -> dict:
    """Validate statistical analysis outputs."""

    # Parse JSON output
    try:
        result = json.loads(output)
    except json.JSONDecodeError:
        return {
            "passed": False,
            "message": "Output is not valid JSON"
        }

    expected_range = parameters.get("expected_range")
    confidence_level = parameters.get("confidence_level", 0.95)
    allow_outliers = parameters.get("allow_outliers", False)

    value = result.get("value")
    std_error = result.get("std_error")

    # Check if value is in expected range
    if expected_range:
        if not (expected_range[0] <= value <= expected_range[1]):
            return {
                "passed": False,
                "score": 0.0,
                "message": f"Value {value} outside expected range {expected_range}"
            }

    # Check confidence intervals if available
    if std_error:
        z_score = stats.norm.ppf((1 + confidence_level) / 2)
        ci_lower = value - z_score * std_error
        ci_upper = value + z_score * std_error

        metadata = {
            "confidence_interval": [ci_lower, ci_upper],
            "confidence_level": confidence_level
        }
    else:
        metadata = {}

    # Check for outliers
    if not allow_outliers and "is_outlier" in result:
        if result["is_outlier"]:
            return {
                "passed": False,
                "message": "Value flagged as outlier",
                "metadata": metadata
            }

    return {
        "passed": True,
        "score": 1.0,
        "message": "Statistical validation passed",
        "metadata": metadata
    }
```

## Best Practices

### Module Organization

1. **Keep evaluation functions focused:**
   ```python
   # Good: Single responsibility
   def validate_pricing(output: str, parameters: dict, **kwargs) -> dict:
       """Validate pricing rules."""
       pass

   # Avoid: Multiple concerns
   def validate_everything(output: str, parameters: dict, **kwargs) -> dict:
       """Validate pricing, formatting, and content quality."""
       pass
   ```

2. **Use helper functions:**
   ```python
   def evaluate_response(output: str, parameters: dict, **kwargs) -> dict:
       """Main evaluation function."""
       score = calculate_quality_score(output)
       passed = check_requirements(output, parameters)
       message = generate_feedback(score, passed)

       return {"passed": passed, "score": score, "message": message}

   def calculate_quality_score(text: str) -> float:
       """Calculate quality score."""
       # ...

   def check_requirements(text: str, params: dict) -> bool:
       """Check if requirements are met."""
       # ...
   ```

### Error Handling

```python
def evaluate_response(output: str, parameters: dict, **kwargs) -> dict:
    """Evaluate with proper error handling."""

    try:
        # Your evaluation logic
        result = perform_evaluation(output, parameters)

        return {
            "passed": result["success"],
            "score": result["score"],
            "message": result["message"]
        }

    except ValueError as e:
        return {
            "passed": False,
            "message": f"Validation error: {str(e)}"
        }

    except Exception as e:
        return {
            "passed": False,
            "message": f"Evaluation failed: {str(e)}",
            "metadata": {"error_type": type(e).__name__}
        }
```

### Performance Considerations

```python
# Cache expensive resources at module level
import functools

@functools.lru_cache(maxsize=1)
def load_expensive_model(path: str):
    """Load model once and cache."""
    return load_model_from_disk(path)

def evaluate_response(output: str, parameters: dict, **kwargs) -> dict:
    """Use cached resources."""
    model = load_expensive_model(parameters["model_path"])
    # Use model for evaluation
    pass
```

### Testability

```python
# Make evaluation logic testable
def evaluate_response(output: str, parameters: dict, **kwargs) -> dict:
    """Main evaluation function."""
    return _evaluate_impl(output, parameters, kwargs.get("prompt"))

def _evaluate_impl(output: str, parameters: dict, prompt: str | None) -> dict:
    """Implementation that's easy to unit test."""
    # Evaluation logic without I/O dependencies
    pass

# Unit tests
def test_evaluation_logic():
    result = _evaluate_impl("test output", {"threshold": 0.5}, "test prompt")
    assert result["passed"] is True
    assert result["score"] >= 0.5
```

## Troubleshooting

### Import Errors

```toml
# Ensure module is in Python path
[eval.custom]
module = "evaluations.my_eval"  # Must be importable
function = "evaluate"
```

```python
# In your evaluation module, use absolute imports
from evaluations.helpers import parse_output
from evaluations.validators import check_format
```

### Parameter Validation

```python
def evaluate_response(output: str, parameters: dict, **kwargs) -> dict:
    """Validate parameters before use."""

    # Check required parameters
    required = ["threshold", "mode"]
    missing = [p for p in required if p not in parameters]
    if missing:
        return {
            "passed": False,
            "message": f"Missing required parameters: {missing}"
        }

    # Validate parameter values
    threshold = parameters["threshold"]
    if not (0 <= threshold <= 1):
        return {
            "passed": False,
            "message": f"threshold must be between 0 and 1, got {threshold}"
        }

    # Continue with evaluation
    # ...
```

### Debugging

```python
import logging

logger = logging.getLogger(__name__)

def evaluate_response(output: str, parameters: dict, **kwargs) -> dict:
    """Evaluation with debug logging."""

    logger.debug(f"Evaluating output: {output[:100]}...")
    logger.debug(f"Parameters: {parameters}")

    result = perform_evaluation(output, parameters)

    logger.info(f"Evaluation result: passed={result['passed']}, score={result.get('score')}")

    return result
```

## Next Steps

- [Evaluations Overview](evaluations.md) - Complete TOML reference
- [Accuracy Evaluations](eval-accuracy.md) - Built-in exact matching and validation
- [LLM Evaluations](eval-llm.md) - AI-powered quality assessment
