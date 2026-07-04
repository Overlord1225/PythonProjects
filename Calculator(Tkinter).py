import tkinter as tk

class MobileCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculator")
        self.root.geometry("320x500")
        self.root.resizable(False, False)
        self.root.configure(bg='black')

        # Expression storage
        self.expression = ""

        # ------------------- Display -------------------
        self.display = tk.Entry(
            root,
            font=("Helvetica", 32),
            bg='black',
            fg='white',
            justify='right',
            bd=0,
            highlightthickness=0,
            relief='flat'
        )
        self.display.grid(row=0, column=0, columnspan=4, sticky='nsew',
                          padx=10, pady=(20, 10))
        self.display.insert(0, "0")

        # ------------------- Button Definitions -------------------
        # Each button: (text, row, col, colspan, bg, fg, is_operator?)
        # We'll define colours separately for clarity.
        buttons = [
            # Row 1: function buttons
            ('AC', 1, 0, 1, '#a5a5a5', 'black'),
            ('±',  1, 1, 1, '#a5a5a5', 'black'),
            ('%',  1, 2, 1, '#a5a5a5', 'black'),
            ('÷',  1, 3, 1, '#ff9500', 'white'),

            # Row 2: numbers and operator
            ('7', 2, 0, 1, '#333333', 'white'),
            ('8', 2, 1, 1, '#333333', 'white'),
            ('9', 2, 2, 1, '#333333', 'white'),
            ('×', 2, 3, 1, '#ff9500', 'white'),

            # Row 3
            ('4', 3, 0, 1, '#333333', 'white'),
            ('5', 3, 1, 1, '#333333', 'white'),
            ('6', 3, 2, 1, '#333333', 'white'),
            ('−', 3, 3, 1, '#ff9500', 'white'),

            # Row 4
            ('1', 4, 0, 1, '#333333', 'white'),
            ('2', 4, 1, 1, '#333333', 'white'),
            ('3', 4, 2, 1, '#333333', 'white'),
            ('+', 4, 3, 1, '#ff9500', 'white'),

            # Row 5: 0 spans 2 columns, then decimal and equals
            ('0', 5, 0, 2, '#333333', 'white'),
            ('.', 5, 2, 1, '#333333', 'white'),
            ('=', 5, 3, 1, '#ff9500', 'white'),
        ]

        # Create buttons dynamically
        for (text, row, col, colspan, bg, fg) in buttons:
            btn = tk.Button(
                root,
                text=text,
                font=("Helvetica", 18),
                bg=bg,
                fg=fg,
                bd=0,
                highlightthickness=0,
                relief='flat',
                activebackground=self._get_active_bg(bg),
                activeforeground=fg,
                command=lambda t=text: self.on_button_click(t)
            )
            btn.grid(row=row, column=col, columnspan=colspan,
                     sticky='nsew', padx=2, pady=2)

        # Configure grid weights so buttons expand
        for i in range(6):
            root.grid_rowconfigure(i, weight=1)
        for i in range(4):
            root.grid_columnconfigure(i, weight=1)

    def _get_active_bg(self, color):
        """Return a slightly lighter/darker shade for the pressed state."""
        if color == '#a5a5a5':
            return '#8e8e8e'
        elif color == '#333333':
            return '#4a4a4a'
        elif color == '#ff9500':
            return '#e68a00'
        return color

    def on_button_click(self, char):
        """Handle all button presses."""
        if char == 'AC':
            self.clear()
        elif char == '=':
            self.evaluate()
        else:
            # Prevent multiple operators or decimals in a row? We'll keep it simple.
            self.expression += self._convert_symbol(char)
            self.update_display()

    def _convert_symbol(self, char):
        """Map display symbols to Python operators."""
        mapping = {'×': '*', '÷': '/', '−': '-'}
        return mapping.get(char, char)

    def clear(self):
        self.expression = ""
        self.update_display()

    def evaluate(self):
        try:
            # Safe eval with restricted namespace
            result = eval(self.expression, {"__builtins__": None}, {})
            # Format result to avoid long decimals
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            self.expression = str(result)
            self.update_display()
        except Exception:
            self.expression = "Error"
            self.update_display()

    def update_display(self):
        self.display.delete(0, tk.END)
        # Show "0" if expression empty
        if self.expression == "":
            self.display.insert(0, "0")
        else:
            self.display.insert(0, self.expression)


if __name__ == "__main__":
    root = tk.Tk()
    app = MobileCalculator(root)
    root.mainloop()