# Smart Scientific Calculator

## Project Overview

The Smart Scientific Calculator is a Python-based calculator developed using Tkinter. It provides a simple, user-friendly graphical interface for basic arithmetic and scientific calculations.

It supports mathematical functions, implicit multiplication, keyboard input, error handling, and calculation history.
## Features

- **Basic Arithmetic:** Addition, subtraction, multiplication, and division.
- **Scientific Functions:** Sine, cosine, tangent, logarithm, natural logarithm, square root, and exponential calculations.
- **Powers:** Calculate squares, cubes, and powers using the `^` operator.
- **Implicit Multiplication:** Supports expressions such as `8(6*9)` and `(2+3)(4+5)` without requiring an explicit multiplication symbol.
- **Mathematical Constants:** Use π (pi) and Euler's number (e).
- **Factorial:** Calculate factorials using the `n!` button.
- **Additional Operations:** Percentage, sign change, and reciprocal calculations.
- **Function Display:** Scientific functions appear on the display before the final calculation.
- **Degree and Radian Modes:** Switch between DEG and RAD for trigonometric calculations.
- **Calculation History:** View previous calculations, restore results, and clear history.
- **Keyboard Support:** Enter numbers and operators using the keyboard.
- **Error Handling:** Displays messages for invalid calculations and division by zero.
- **Safe Expression Evaluation:** Uses Python's Abstract Syntax Tree (AST) to evaluate supported mathematical expressions without using `eval()`.
- **User-Friendly GUI:** A Mac-inspired interface built with Tkinter.

## Technologies Used

- Python 3
- Tkinter
- Math module
- AST module
- Operator module
- Regular expressions (`re`)

## Requirements

- Python 3 installed on your computer.
- Tkinter support in your Python installation.

Tkinter is generally included with standard macOS Python installations.

## How to Run the Project

1. Download or clone this repository.
2. Open the project folder in VS Code or Terminal.
3. Run the following command:

```bash
python3 calculator.py
```

If needed, use the full Python path on macOS:

```bash
/usr/local/bin/python3 calculator.py
```

The calculator window will open, and you can start performing calculations.

## Example Calculations

| Expression | Expected Result |
|---|---:|
| `25+15` | `40` |
| `8(6*9)` | `432` |
| `(2+3)(4+5)` | `45` |
| `sin(30)` in DEG mode | `0.5` |
| `cos(60)` in DEG mode | `0.5` |
| `sqrt(81)` | `9` |
| `log(100)` | `2` |
| `5^3` | `125` |
| `5!` | `120` |

## Error Handling

The calculator handles common calculation errors, including:

- Division by zero.
- Invalid mathematical expressions.
- Invalid factorial inputs.
- Negative square roots.
- Results or exponents exceeding configured limits.

## Keyboard Shortcuts

| Key | Action |
|---|---|
| `0–9` | Enter numbers |
| `+`, `-`, `*`, `/` | Arithmetic operations |
| `^` | Power |
| `Enter` | Calculate the result |
| `Backspace` | Delete the last character |
| `Escape` | Clear the display |

## Project Structure

```text
Task 3 Calculator with GUI/
├── calculator.py
├── README.md
└── Screenshots/
    ├── calculator.png
    ├── basic_calculation.png
    ├── scientific_functions.png
    └── calculation_history.png
```

The `Screenshots` folder is optional but recommended for demonstrating the application on GitHub.

## Learning Outcomes

Through this project, I gained practical experience in:

- Developing a graphical user interface using Tkinter.
- Implementing mathematical and scientific functions.
- Handling keyboard and button events.
- Evaluating mathematical expressions safely.
- Managing calculation history.
- Handling invalid inputs and calculation errors.
- Organizing and documenting a Python project.

## Conclusion

This project demonstrates the development of a scientific calculator using Python. It combines basic and scientific calculations with a simple graphical interface and useful features such as implicit multiplication, function display, and calculation history.

**Developed by:** 
Ruhi Farhaz
