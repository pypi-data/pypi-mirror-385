# DeepRehab Rules

DeepRehab Rules is a Python package that provides a rules engine for validating rehabilitation exercises based on pose estimation data. It works in conjunction with [deeprehab-pose](../deeprehab-pose) and [deeprehab-angles](../deeprehab-angles) to provide a complete rehabilitation analysis solution.

## Features

- Exercise form validation
- Rule-based feedback system
- Configurable rules engine
- Integration with pose estimation data
- Extensible design

## Installation

```bash
pip install deeprehab-rules
```

## Usage

```python
from deeprehab_rules import DeepRehabRules

# Initialize the rules engine
rules_engine = DeepRehabRules()

# Validate exercise form
result = rules_engine.validate_form(landmarks, "knee_extension")
print(result)
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.