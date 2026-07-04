import tkinter as tk
from tkinter import messagebox
import calendar
from datetime import datetime

class CalendarApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Calendar")
        self.root.geometry("400x400")

        # Current date
        self.now = datetime.now()
        self.current_year = self.now.year
        self.current_month = self.now.month
        self.selected_date = None

        # Widgets for navigation and display
        self.header_frame = tk.Frame(root)
        self.header_frame.pack(pady=10)

        # Navigation buttons and month/year label
        self.prev_year_btn = tk.Button(self.header_frame, text="<<", command=self.prev_year)
        self.prev_year_btn.grid(row=0, column=0, padx=5)

        self.prev_month_btn = tk.Button(self.header_frame, text="<", command=self.prev_month)
        self.prev_month_btn.grid(row=0, column=1, padx=5)

        self.month_year_label = tk.Label(self.header_frame, text="", font=("Arial", 16, "bold"))
        self.month_year_label.grid(row=0, column=2, padx=20)

        self.next_month_btn = tk.Button(self.header_frame, text=">", command=self.next_month)
        self.next_month_btn.grid(row=0, column=3, padx=5)

        self.next_year_btn = tk.Button(self.header_frame, text=">>", command=self.next_year)
        self.next_year_btn.grid(row=0, column=4, padx=5)

        # Calendar grid frame
        self.calendar_frame = tk.Frame(root)
        self.calendar_frame.pack(pady=10)

        # Day names
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i, day in enumerate(days):
            lbl = tk.Label(self.calendar_frame, text=day, font=("Arial", 10, "bold"), width=5, anchor="center")
            lbl.grid(row=0, column=i, padx=2, pady=2)

        # We'll update the calendar grid dynamically
        self.day_buttons = {}  # Store button references for updating

        self.update_calendar()

    def update_calendar(self):
        """Clear and redraw the calendar grid for the current month/year."""
        # Clear existing day buttons
        for widget in self.calendar_frame.winfo_children():
            # Keep the day name labels (row 0)
            if int(widget.grid_info()["row"]) > 0:
                widget.destroy()

        # Update month/year label
        month_name = calendar.month_name[self.current_month]
        self.month_year_label.config(text=f"{month_name} {self.current_year}")

        # Get the calendar as a list of weeks (each week is a list of day numbers or 0 for empty)
        cal = calendar.monthcalendar(self.current_year, self.current_month)

        # Determine today's date for highlighting
        today = datetime.now()
        today_day = today.day if (today.year == self.current_year and today.month == self.current_month) else None

        # Populate grid rows
        for row, week in enumerate(cal, start=1):
            for col, day in enumerate(week):
                if day == 0:
                    # Empty cell
                    lbl = tk.Label(self.calendar_frame, text="", width=5, height=2, anchor="center")
                    lbl.grid(row=row, column=col, padx=2, pady=2)
                else:
                    # Day button
                    btn = tk.Button(
                        self.calendar_frame,
                        text=str(day),
                        width=5,
                        height=2,
                        anchor="center",
                        command=lambda d=day: self.on_day_click(d)
                    )
                    # Highlight current day
                    if day == today_day:
                        btn.config(bg="lightblue", relief="sunken")
                    # Highlight selected day if any
                    if self.selected_date and self.selected_date[0] == self.current_year and self.selected_date[1] == self.current_month and self.selected_date[2] == day:
                        btn.config(bg="yellow")
                    btn.grid(row=row, column=col, padx=2, pady=2)
                    # Store reference (optional)
                    self.day_buttons[(row, col)] = btn

    def on_day_click(self, day):
        """Handle day selection."""
        self.selected_date = (self.current_year, self.current_month, day)
        messagebox.showinfo("Date Selected", f"Selected: {day}-{self.current_month}-{self.current_year}")
        self.update_calendar()  # Refresh to show highlight

    def prev_month(self):
        """Go to previous month."""
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.update_calendar()

    def next_month(self):
        """Go to next month."""
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.update_calendar()

    def prev_year(self):
        """Go to previous year."""
        self.current_year -= 1
        self.update_calendar()

    def next_year(self):
        """Go to next year."""
        self.current_year += 1
        self.update_calendar()

if __name__ == "__main__":
    root = tk.Tk()
    app = CalendarApp(root)
    root.mainloop()