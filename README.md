# Algorithm Convergence Visualizer

A Python + HTML project for visualizing convergence of numerical root-finding algorithms.

## Included methods
- Bisection Method
- Regula-Falsi Method
- Newton-Raphson Method
- Secant Method
- Fixed Point Iteration

## Tech stack
- Python (Flask)
- HTML, CSS, JavaScript
- Plotly.js for graphs
- SymPy for function parsing

## How to run

### 1. Open the folder in VS Code
Open the extracted folder in VS Code.

### 2. Create a virtual environment (optional but recommended)
```bash
python -m venv venv
```

### 3. Activate the virtual environment
#### Windows
```bash
venv\Scripts\activate
```

#### Mac/Linux
```bash
source venv/bin/activate
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the Flask app
```bash
python app.py
```

### 6. Open in browser
```text
http://127.0.0.1:5000
```

## Sample input
Use:
```text
x**3 - x - 2
```

- Bisection / Regula-Falsi: `a = 1`, `b = 2`
- Newton-Raphson: `x0 = 1.5`
- Secant: `x0 = 1`, `x1 = 2`
- Fixed Point: `g(x) = (x + 2)**(1/3)`, `x0 = 1.5`

## Notes
- Enter powers using `**`, for example `x**2`.
- Trigonometric functions like `sin(x)` and `cos(x)` also work.
- Fixed Point Iteration uses `g(x)` instead of `f(x)`.
