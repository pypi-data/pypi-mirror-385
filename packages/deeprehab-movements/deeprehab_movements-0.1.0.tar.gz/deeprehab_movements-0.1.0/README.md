# DeepRehab Movements

DeepRehab Movements is a Python package that provides movement analysis and scoring capabilities for rehabilitation exercises. It works with [deeprehab-pose](../deeprehab-pose) and [deeprehab-angles](../deeprehab-angles) to provide a complete rehabilitation analysis solution.

## Features

- Exercise movement scoring
- Form evaluation algorithms
- Integration with pose estimation and angle data
- Extensible design for adding new exercises

## Installation

```bash
pip install deeprehab-movements
```

## Usage

```python
from deeprehab_movements import score_deep_squat

# Score a deep squat exercise
result = score_deep_squat(landmarks)
print(f"Score: {result.score}")
print(f"Reason: {result.reason}")
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.