
import ast
import math
import operator
import re
import tkinter as tk

# ---------- COLORS ----------

BG = "#000000"
DISPLAY_BG = "#000000"
NUMBER_BG = "#d6d6d6"
FUNCTION_BG = "#a5a5a5"
ORANGE = "#ff9f0a"
WHITE = "#ffffff"
BLACK = "#000000"
HISTORY_BG = "#242426"

# ---------- WINDOW ----------

root = tk.Tk()
root.title("Smart Scientific Calculator")
root.geometry("540x790")
root.minsize(470, 680)
root.configure(bg=BG)

expression = tk.StringVar()
status = tk.StringVar(value="")

just_calculated = False
degrees_mode = True
history_items = []

# ---------- SAFE CALCULATION ----------

def safe_calculate(text):
    text = text.replace("×", "*").replace("÷", "/")
    text = text.replace("−", "-").replace("^", "**")

    # Support implicit multiplication:
    # 8(2+3), (2+3)(4+5), and 2pi
    text = re.sub(r"(?<=[0-9)])\s*(?=\()", "*", text)
    text = re.sub(r"(?<=\))\s*(?=[0-9])", "*", text)
    text = re.sub(r"(?<=[0-9])\s*(?=[a-zA-Z])", "*", text)

    functions = {
        "sqrt": math.sqrt,
        "sin": lambda x: math.sin(
            math.radians(x) if degrees_mode else x
        ),
        "cos": lambda x: math.cos(
            math.radians(x) if degrees_mode else x
        ),
        "tan": lambda x: math.tan(
            math.radians(x) if degrees_mode else x
        ),
        "log": math.log10,
        "ln": math.log,
        "abs": abs,
        "exp": math.exp,
        "factorial": math.factorial,
    }

    constants = {"pi": math.pi, "e": math.e}

    binary_ops = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.Mod: operator.mod,
    }

    unary_ops = {
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
    }

    def evaluate(node):
        if isinstance(node, ast.Constant):
            if type(node.value) not in (int, float):
                raise ValueError("Invalid number")
            result = node.value

        elif isinstance(node, ast.Name) and node.id in constants:
            result = constants[node.id]

        elif isinstance(node, ast.BinOp) and type(node.op) in binary_ops:
            left = evaluate(node.left)
            right = evaluate(node.right)

            if isinstance(node.op, ast.Div) and right == 0:
                raise ZeroDivisionError

            if isinstance(node.op, ast.Pow):
                if abs(right) > 100:
                    raise ValueError("Exponent too large")

            result = binary_ops[type(node.op)](left, right)

        elif isinstance(node, ast.UnaryOp) and type(node.op) in unary_ops:
            result = unary_ops[type(node.op)](
                evaluate(node.operand)
            )

        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            name = node.func.id

            if name not in functions or len(node.args) != 1 or node.keywords:
                raise ValueError("Invalid function")

            argument = evaluate(node.args[0])

            if name == "factorial":
                if (
                    argument < 0
                    or not float(argument).is_integer()
                    or argument > 170
                ):
                    raise ValueError("Invalid factorial")

                argument = int(argument)

            result = functions[name](argument)

        else:
            raise ValueError("Invalid expression")

        if isinstance(result, complex) or not math.isfinite(result):
            raise ValueError("Invalid result")

        if abs(result) > 1e100:
            raise ValueError("Result too large")

        return result

    tree = ast.parse(text, mode="eval")
    return evaluate(tree.body)


def fmt(number):
    if isinstance(number, float) and number.is_integer():
        return str(int(number))
    return f"{number:.10g}"


# ---------- HISTORY ----------

def add_history(item):
    history_items.insert(0, item)
    refresh_history()


def refresh_history():
    history_list.delete(0, tk.END)
    for item in history_items:
        history_list.insert(tk.END, item)


def clear_history():
    history_items.clear()
    refresh_history()


def restore_history(event=None):
    selection = history_list.curselection()

    if selection:
        item = history_list.get(selection[0])

        if " = " in item:
            expression.set(item.rsplit(" = ", 1)[1])
            status.set("")
            set_calculated(True)


# ---------- CALCULATOR ACTIONS ----------

def set_calculated(value):
    global just_calculated
    just_calculated = value


def clear_all():
    expression.set("")
    status.set("")
    set_calculated(False)


def backspace():
    expression.set(expression.get()[:-1])
    status.set("")
    set_calculated(False)


def append_value(value):
    current = expression.get()

    if value == "×":
        value = "*"
    elif value == "÷":
        value = "/"
    elif value == "−":
        value = "-"

    if just_calculated:
        if value in ("+", "-", "*", "/", "^", "%"):
            set_calculated(False)
        else:
            current = ""
            expression.set("")
            set_calculated(False)

    expression.set(current + value)
    status.set("")


def calculate():
    text = expression.get().strip()

    if not text:
        status.set("Enter a calculation")
        return

    # Automatically close any unfinished parentheses.
    missing_closures = text.count("(") - text.count(")")

    if missing_closures > 0:
        text += ")" * missing_closures
        expression.set(text)

    try:
        result = safe_calculate(text)
        answer = fmt(result)

        add_history(f"{text} = {answer}")
        expression.set(answer)
        status.set("")
        set_calculated(True)

    except ZeroDivisionError:
        status.set("Cannot divide by zero")

    except (
        ValueError,
        SyntaxError,
        OverflowError,
        TypeError,
        MemoryError,
        RecursionError,
    ):
        status.set("Invalid calculation")


def apply_function(name):
    text = expression.get().strip()

    scientific_functions = (
        "sin", "cos", "tan", "log", "ln", "exp", "√"
    )

    # Allow a scientific function to be entered first.
    if not text:
        if name in scientific_functions:
            function_name = "sqrt" if name == "√" else name
            expression.set(function_name + "(")
            status.set("")
            set_calculated(False)
        else:
            status.set("Enter a number first")
        return

    try:
        # Show scientific functions on the display.
        # Calculation happens only after pressing =.
        if name in scientific_functions:
            function_name = "sqrt" if name == "√" else name
            label = f"{function_name}({text})"
            expression.set(label)
            status.set("")
            set_calculated(False)
            return

        number = safe_calculate(text)

        if name == "±":
            result = -number
            label = f"-({text})"

        elif name == "%":
            result = number / 100
            label = f"{text}%"

        elif name == "x²":
            result = number ** 2
            label = f"({text})^2"

        elif name == "x³":
            result = number ** 3
            label = f"({text})^3"

        elif name == "1/x":
            if number == 0:
                raise ZeroDivisionError

            result = 1 / number
            label = f"1/({text})"

        elif name == "n!":
            if (
                number < 0
                or not float(number).is_integer()
                or number > 170
            ):
                raise ValueError("Invalid factorial")

            result = math.factorial(int(number))
            label = f"{text}!"

        elif name in ("π", "e"):
            append_value("pi" if name == "π" else "e")
            return

        else:
            return

        if not math.isfinite(result) or abs(result) > 1e100:
            raise ValueError("Invalid result")

        answer = fmt(result)
        add_history(f"{label} = {answer}")
        expression.set(answer)
        status.set("")
        set_calculated(True)

    except ZeroDivisionError:
        status.set("Cannot divide by zero")

    except (
        ValueError,
        SyntaxError,
        OverflowError,
        TypeError,
        MemoryError,
        RecursionError,
    ):
        status.set("Invalid operation")


def toggle_angle():
    global degrees_mode
    degrees_mode = not degrees_mode

    angle_button.config(text="DEG" if degrees_mode else "RAD")
    status.set("Degrees mode" if degrees_mode else "Radians mode")


def button_action(label):
    if label == "AC":
        clear_all()

    elif label == "⌫":
        backspace()

    elif label == "=":
        calculate()

    elif label == "DEG":
        toggle_angle()

    elif label in (
        "±", "%", "√", "x²", "x³", "1/x", "n!",
        "sin", "cos", "tan", "log", "ln", "exp", "π", "e"
    ):
        apply_function(label)

    else:
        append_value(label)


# ---------- KEYBOARD ----------

def handle_key(event):
    char = event.char

    if event.keysym in ("Return", "KP_Enter"):
        calculate()
        return "break"

    if event.keysym == "BackSpace":
        backspace()
        return "break"

    if event.keysym in ("Escape", "Delete"):
        clear_all()
        return "break"

    if char in "0123456789.()+-*/%":
        append_value(char)
        return "break"

    if char == "^":
        append_value("^")
        return "break"

    return "break"


# ---------- DISPLAY ----------

header = tk.Frame(root, bg=BG)
header.pack(fill="x", padx=18, pady=(12, 0))

tk.Label(
    header,
    text="Scientific Calculator",
    bg=BG,
    fg=WHITE,
    font=("Arial", 14, "bold")
).pack(side="left")

angle_button = tk.Button(
    header,
    text="DEG",
    command=toggle_angle,
    bg=FUNCTION_BG,
    fg=BLACK,
    activebackground="#c5c5c5",
    relief="flat",
    font=("Arial", 10, "bold"),
    width=5
)
angle_button.pack(side="right")

display_frame = tk.Frame(root, bg=DISPLAY_BG)
display_frame.pack(fill="x", padx=16, pady=(8, 0))

display = tk.Entry(
    display_frame,
    textvariable=expression,
    bg=DISPLAY_BG,
    fg=WHITE,
    insertbackground=WHITE,
    selectbackground="#555555",
    selectforeground=WHITE,
    font=("Arial", 32),
    justify="right",
    relief="flat",
    bd=0
)
display.pack(fill="x", ipady=15)

tk.Label(
    display_frame,
    textvariable=status,
    bg=DISPLAY_BG,
    fg="#ffb74d",
    font=("Arial", 10),
    anchor="e"
).pack(fill="x", pady=(0, 8))


# ---------- MAC-STYLE BUTTON LAYOUT ----------

main = tk.Frame(root, bg=BG)
main.pack(fill="both", expand=True, padx=12, pady=5)

keypad = tk.Frame(main, bg=BG)
keypad.pack(fill="x")

button_rows = [
    [("AC", "fn"), ("⌫", "fn"), ("(", "fn"), (")", "fn"), ("÷", "op")],
    [("sin", "fn"), ("cos", "fn"), ("tan", "fn"), ("√", "fn"), ("×", "op")],
    [("log", "fn"), ("ln", "fn"), ("π", "fn"), ("e", "fn"), ("−", "op")],
    [("7", "num"), ("8", "num"), ("9", "num"), ("n!", "fn"), ("+", "op")],
    [("4", "num"), ("5", "num"), ("6", "num"), ("x²", "fn"), ("%", "fn")],
    [("1", "num"), ("2", "num"), ("3", "num"), ("1/x", "fn"), ("^", "op")],
    [("±", "fn"), ("0", "num"), (".", "num"), ("x³", "fn"), ("=", "op")],
]


def make_button(parent, label, kind):
    if kind == "num":
        color = NUMBER_BG
        foreground = BLACK

    elif kind == "op":
        color = ORANGE
        foreground = BLACK

    else:
        color = FUNCTION_BG
        foreground = BLACK

    return tk.Button(
        parent,
        text=label,
        command=lambda value=label: button_action(value),
        font=("Arial", 12, "bold"),
        bg=color,
        fg=foreground,
        activebackground="#ffbd55" if kind == "op" else "#c7c7c7",
        activeforeground=BLACK,
        relief="flat",
        bd=0,
        cursor="hand2"
    )


for r, row in enumerate(button_rows):
    keypad.grid_rowconfigure(r, weight=1)

    for c, (label, kind) in enumerate(row):
        keypad.grid_columnconfigure(c, weight=1)

        button = make_button(keypad, label, kind)
        button.grid(
            row=r,
            column=c,
            sticky="nsew",
            padx=3,
            pady=3,
            ipadx=1,
            ipady=8
        )


# ---------- HISTORY ----------

history_panel = tk.Frame(main, bg=HISTORY_BG)
history_panel.pack(fill="both", expand=True, pady=(8, 0))

history_header = tk.Frame(history_panel, bg=HISTORY_BG)
history_header.pack(fill="x", padx=8, pady=(6, 2))

tk.Label(
    history_header,
    text="Calculation History",
    bg=HISTORY_BG,
    fg=WHITE,
    font=("Arial", 11, "bold")
).pack(side="left")

tk.Button(
    history_header,
    text="Clear History",
    command=clear_history,
    bg=HISTORY_BG,
    fg="#ffb74d",
    activebackground=HISTORY_BG,
    activeforeground=WHITE,
    relief="flat",
    bd=0
).pack(side="right")

history_list = tk.Listbox(
    history_panel,
    bg=HISTORY_BG,
    fg=WHITE,
    selectbackground=ORANGE,
    selectforeground=WHITE,
    font=("Arial", 10),
    relief="flat",
    bd=0,
    height=4
)
history_list.pack(fill="both", expand=True, padx=8, pady=(0, 8))
history_list.bind("<Double-Button-1>", restore_history)

root.bind("<Key>", handle_key)
display.focus_set()

root.mainloop()
