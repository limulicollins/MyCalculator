import sys
import ast
import operator
import math
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QLineEdit, QPushButton, QGridLayout,
    QListWidget, QStackedWidget, QHBoxLayout,
    QLabel
)



class Calculator(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Calculator")
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #f0f0f0;
                font-family: 'Segoe UI', sans-serif;
            }

            QLineEdit {
                background-color: #1e1e1e;
                border: 2px solid #555;
                border-radius: 8px;
                padding: 10px;
                font-size: 24px;
                color: #00ffcc;
            }

            QPushButton {
                background-color: #3c3c3c;
                border: 1px solid #555;
                border-radius: 8px;
                font-size: 18px;
            }

            QPushButton:hover {
                background-color: #505050;
            }

            QPushButton:pressed {
                background-color: #606060;
            }

            QListWidget {
                background-color: #1e1e1e;
                border: 1px solid #444;
                border-radius: 5px;
                font-size: 16px;
            }

            QListWidget::item:hover {
                background-color: #333;
            }

            QListWidget::item:selected {
                background-color: #444;
                color: #00ffcc;
            }
        """)

        self.setStyleSheet(self.styleSheet() + """
            QWidget#Calculator {
                border-radius: 10px;
            }
        """)
        self.setObjectName("Calculator")
        self.use_degrees = False  
        self.setGeometry(100, 100, 400, 350)
        self.setFocus()
        self.setFocusPolicy(Qt.StrongFocus)
        self.create_ui()


    def create_ui(self):
        main_layout = QVBoxLayout() # main vertical layout for the calculator

        ## Display (input/output)
        self.display = QLineEdit()
        self.display.setReadOnly(True)
        self.display.setFixedHeight(50)
        self.display.setStyleSheet("font-size: 22px;")
        main_layout.addWidget(self.display)

        ## list widget to show history of calculations
        self.history_list = QListWidget()
        self.history_list.setFixedHeight(100)
        self.history_list.setStyleSheet("font-size: 16px;")
        self.history_list.itemClicked.connect(self.load_from_history)
        main_layout.addWidget(self.history_list)

        # radians/degrees toggle button
        self.angle_mode_button = QPushButton("Mode: Radians")
        self.angle_mode_button.clicked.connect(self.toggle_angle_mode)
        self.angle_mode_button.setStyleSheet("font-size: 14px; padding: 4px;")
        main_layout.addWidget(self.angle_mode_button)

        # Mode switch
        mode_layout = QHBoxLayout()
        self.mode_label = QLabel("Mode: Basic")
        self.mode_label.setStyleSheet("font-size: 14px; color: #aaa;")

        self.mode_button = QPushButton("Switch to Scientific")
        self.mode_button.clicked.connect(self.switch_mode)
        self.mode_button.setStyleSheet("font-size: 14px;")

        # Create stacked widget for switching modes
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)

        # Basic mode layout
        self.basic_widget = QWidget()
        self.basic_layout = QVBoxLayout()
        self.basic_widget.setLayout(self.basic_layout)

        # Scientific mode layout
        self.sci_widget = QWidget()
        self.sci_layout = QVBoxLayout()
        self.sci_widget.setLayout(self.sci_layout)

        # Add to stack
        self.stack.addWidget(self.basic_widget)
        self.stack.addWidget(self.sci_widget)

        mode_layout.addWidget(self.mode_label)
        mode_layout.addStretch()
        mode_layout.addWidget(self.mode_button)
        main_layout.addLayout(mode_layout)

        self.create_basic_buttons()
        self.create_scientific_buttons()
        self.setLayout(main_layout)


    def create_basic_buttons(self):
        grid_layout = QGridLayout()

        buttons = [
            ('C', 0, 0), ('⌫', 0, 1), ('(', 0, 2), (')', 0, 3),
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('/', 1, 3),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('*', 2, 3),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('-', 3, 3),
            ('0', 4, 0), ('.', 4, 1), ('%', 4, 2), ('+', 4, 3),
            ('√', 5, 0), ('^', 5, 1), ('=', 5, 2), ('', 5, 3),
        ]

        for text, row, col in buttons:
            if not text:
                continue

            button = QPushButton(text)
            button.setFixedSize(65, 65)
            button.setStyleSheet("font-size: 18px;")
            grid_layout.addWidget(button, row, col)

            if text == '=':
                button.clicked.connect(self.evaluate_expression)
            elif text == 'C':
                button.clicked.connect(self.clear_display)
            elif text == '⌫':
                button.clicked.connect(self.backspace)
            elif text == '√':
                button.clicked.connect(lambda: self.append_to_display("√("))
            elif text == '^':
                button.clicked.connect(lambda: self.append_to_display("**"))
            else:
                button.clicked.connect(lambda checked, t=text: self.append_to_display(t))

        self.basic_layout.addLayout(grid_layout)

    def create_scientific_buttons(self):
        grid_layout = QGridLayout()

        sci_buttons = [
            ('C', 0, 0), ('⌫', 0, 1), ('(', 0, 2), (')', 0, 3),
            ('sin(', 1, 0), ('cos(', 1, 1), ('tan(', 1, 2), ('log(', 1, 3),
            ('asin(',2, 0), ('acos(', 2, 1), ('atan(', 2, 2), ('ln(', 2, 3),
            ('7', 3, 0), ('8', 3, 1), ('9', 3, 2), ('/', 3, 3),
            ('4', 4, 0), ('5', 4, 1), ('6', 4, 2), ('*', 4, 3),
            ('1', 5, 0), ('2', 5, 1), ('3', 5, 2), ('-', 5, 3),
            ('0', 6, 0), ('.', 6, 1), ('^', 6, 2), ('+', 6, 3),
            ('√', 7, 0), ('pi', 7, 1), ('e', 7, 2), ('=', 7, 3)
        ]

        for text, row, col in sci_buttons:
            button = QPushButton(text)
            button.setFixedSize(65, 65)
            button.setStyleSheet("font-size: 18px;")
            grid_layout.addWidget(button, row, col)

            if text == '=':
                button.clicked.connect(self.evaluate_expression)
            elif text == 'C':
                button.clicked.connect(self.clear_display)
            elif text == '⌫':
                button.clicked.connect(self.backspace)
            elif text == '√':
                button.clicked.connect(lambda: self.append_to_display("√("))
            elif text == '^':
                button.clicked.connect(lambda: self.append_to_display("**"))
            elif text in ['pi', 'e']:
                val = str(getattr(math, text))
                button.clicked.connect(lambda checked, v=val: self.append_to_display(v))
            else:
                button.clicked.connect(lambda checked, t=text: self.append_to_display(t))

        self.sci_layout.addLayout(grid_layout)

    def switch_mode(self):
        current_index = self.stack.currentIndex()
        if current_index == 0:
            self.stack.setCurrentIndex(1)
            self.mode_label.setText("Mode: Scientific")
            self.mode_button.setText("Switch to Basic")
        else:
            self.stack.setCurrentIndex(0)
            self.mode_label.setText("Mode: Basic")
            self.mode_button.setText("Switch to Scientific")


    ## Adds the button text to the display
    def append_to_display(self, text):
        current = self.display.text()
        self.display.setText(current + text)


    ## clears the display
    def clear_display(self):
        self.display.setText("")


    ## removes the last character from the display
    def backspace(self):
        current = self.display.text()
        self.display.setText(current[:-1])


    def safe_eval(self, expr):
        """
        Safely evaluates a math expression using AST.
        Supports +, -, *, /, %, **, (), sqrt, sin, cos, log, etc.
        """

        allowed_operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.Mod: operator.mod,
            ast.USub: operator.neg,
        }

        if self.use_degrees:
            allowed_functions = {
                'sqrt': math.sqrt,
                'log': math.log10,
                'ln': math.log,
                'abs': abs,
                'exp': math.exp,
                'sin': lambda x: math.sin(math.radians(x)),
                'cos': lambda x: math.cos(math.radians(x)),
                'tan': lambda x: math.tan(math.radians(x)),
                'asin': lambda x: math.degrees(math.asin(x)),
                'acos': lambda x: math.degrees(math.acos(x)),
                'atan': lambda x: math.degrees(math.atan(x)),
            }
        else:
            allowed_functions = {
                'sqrt': math.sqrt,
                'log': math.log10,
                'ln': math.log,
                'abs': abs,
                'exp': math.exp,
                'sin': math.sin,
                'cos': math.cos,
                'tan': math.tan,
                'asin': math.asin,
                'acos': math.acos,
                'atan': math.atan,
            }


        allowed_constants = {
            'pi': math.pi,
            'e': math.e
        }

        # Preprocess symbols
        expr = expr.replace("√", "sqrt")
        expr = expr.replace("^", "**")

        def _eval(node):
            if isinstance(node, ast.Expression):
                return _eval(node.body)

            elif isinstance(node, ast.BinOp):
                left = _eval(node.left)
                right = _eval(node.right)
                return allowed_operators[type(node.op)](left, right)

            elif isinstance(node, ast.UnaryOp):
                return allowed_operators[type(node.op)](_eval(node.operand))

            elif isinstance(node, ast.Call):
                func_name = getattr(node.func, 'id', None)
                if func_name in allowed_functions:
                    args = [_eval(arg) for arg in node.args]
                    return allowed_functions[func_name](*args)
                else:
                    raise ValueError(f"Function '{func_name}' is not allowed.")

            elif isinstance(node, ast.Name):
                if node.id in allowed_constants:
                    return allowed_constants[node.id]
                else:
                    raise ValueError(f"Constant '{node.id}' is not allowed.")

            elif isinstance(node, ast.Constant):  # Python 3.8+
                return node.value

            elif isinstance(node, ast.Num):  # < Python 3.8
                return node.n

            else:
                raise TypeError(f"Unsupported expression type: {type(node)}")

        print("Evaluating with use_degrees =", self.use_degrees)
        parsed = ast.parse(expr, mode='eval')
        return _eval(parsed)
    
    ## Uses AST to compute the result of the expression in the display
    def evaluate_expression(self):
        try:
            expr = self.display.text()
            result = str(self.safe_eval(expr))
            self.display.setText(result)
            self.add_to_history(expr + " = " + result)
        except Exception as e:
            print(f"Evaluation error: {e}")
            self.display.setText("Error")

    
    def toggle_angle_mode(self):
        self.use_degrees = not self.use_degrees
        mode = "Degrees" if self.use_degrees else "Radians"
        print("Switched to:", mode)
        self.angle_mode_button.setText(f"Mode: {mode}")

    
    def keyPressEvent(self, event):
        key = event.key()
        text = event.text()

        if key in (Qt.Key_Enter, Qt.Key_Return):
            self.evaluate_expression()

        elif key == Qt.Key_Backspace:
            self.backspace()

        elif key == Qt.Key_Escape:
            self.clear_display()

        elif text in '0123456789+-*/().%^':
            self.append_to_display(text)

        elif text == 'r':  # user types 'r' for square root
            self.append_to_display("√(")

        elif text == '^':
            self.append_to_display("**")

        else:
            # Ignore other keys
            pass

    def load_from_history(self, item):
        expression = item.text().split('=')[0].strip()
        self.display.setText(expression)

    def add_to_history(self, entry):
        self.history_list.addItem(entry)



## Run the application
if __name__ == '__main__':
    app = QApplication(sys.argv)
    calc = Calculator()
    calc.show()
    sys.exit(app.exec_())
