# Debug Mode Configuration

## Overview
Debug mode automatically pre-selects default answers for all questionnaire questions, making it easier to test the application without manually filling out the entire questionnaire.

## Environment Variables

### DEBUG_MODE
- **Default**: `true`
- **Values**: `true` or `false`
- **Description**: When enabled, all questionnaire questions will be pre-selected with default answers

### DEBUG_DEFAULT_SCORE
- **Default**: `3`
- **Values**: `1`, `2`, `3`, `4`, or `5`
- **Description**: The default score to pre-select for all questions
  - `1` = Strongly disagree
  - `2` = Somewhat disagree
  - `3` = Neither agree nor disagree
  - `4` = Somewhat agree
  - `5` = Strongly agree

## Usage

### For Development (Debug Mode Enabled)
```bash
export DEBUG_MODE=true
export DEBUG_DEFAULT_SCORE=3
python main.py
```

### For Production (Debug Mode Disabled)
```bash
export DEBUG_MODE=false
python main.py
```

### Using .env file
Create a `.env` file in your project root:
```
DEBUG_MODE=true
DEBUG_DEFAULT_SCORE=3
```

## How It Works
When debug mode is enabled:
1. All questionnaire questions will have the default score pre-selected
2. The progress bar will automatically update to show 100% completion
3. You can submit the questionnaire immediately without manually selecting answers
4. You can still change any pre-selected answers if needed

## Deployment Notes
**Important**: Always set `DEBUG_MODE=false` before deploying to production to ensure users must manually answer all questions. 