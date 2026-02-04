import tkinter as tk
from tkinter import ttk, messagebox
import os
import pandas as pd
from datetime import datetime
import json



class Config:
    APP_NAME = "Food Safety Expert System"
    PRIMARY_COLOR = "#2C3E50"
    SECONDARY_COLOR = "#3498DB"
    SUCCESS_COLOR = "#27AE60"
    WARNING_COLOR = "#F39C12"
    DANGER_COLOR = "#E74C3C"
    LIGHT_BG = "#ECF0F1"
    DARK_BG = "#2C3E50"
    WHITE = "#FFFFFF"

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    CSV_PATH = os.path.join(BASE_DIR, "..", "data", "projectAI.csv")
    LOG_PATH = os.path.join(BASE_DIR, "..", "logs", "safety_checks.json")

    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)



class DataHandler:
    @staticmethod
    def load_rules():
        try:
            df = pd.read_csv(Config.CSV_PATH, delimiter=';')

            for col in df.select_dtypes(include="object").columns:
                df[col] = df[col].str.strip()

            required_cols = ["id", "conditions", "conclusion", "explanation"]
            if not all(col in df.columns for col in required_cols):
                print(f"CSV must contain columns: {required_cols}")

            return df
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load rules file:\n{e}")
            return None

    @staticmethod
    def log_analysis(facts, result, trace):
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "input_facts": facts,
                "result": result,
                "applied_rules": [
                    {"rule_id": str(r_id), "effect": eff, "explanation": exp}
                    for r_id, eff, exp in trace
                ]
            }

            logs = []
            if os.path.exists(Config.LOG_PATH):
                with open(Config.LOG_PATH, 'r') as f:
                    logs = json.load(f)

            logs.append(log_entry)
            logs = logs[-1000:]

            with open(Config.LOG_PATH, 'w') as f:
                json.dump(logs, f, indent=2)

        except Exception as e:
            print("Logging failed:", e)



class ExpertSystem:
    @staticmethod
    def evaluate_condition(condition, facts):
        condition = condition.strip()
        try:
            if "==" in condition:
                key, value = condition.split("==")
                return facts.get(key.strip()) == value.strip()
            if "<=" in condition:
                key, value = condition.split("<=")
                return float(facts.get(key.strip(), 0)) <= float(value)
            if ">" in condition:
                key, value = condition.split(">")
                return float(facts.get(key.strip(), 0)) > float(value)
            return False
        except:
            return False


    @staticmethod
    def rule_matches(rule_conditions, facts):
        if pd.isna(rule_conditions) or str(rule_conditions).strip() == "":
            #ida kant null wla fargha
            return False

        conditions = str(rule_conditions).replace("\n", "").split(";")
        #"perishable == yes; hours_out > 2" -> conditions = ["perishable == yes","hours_out > 2"]

        return all(ExpertSystem.evaluate_condition(cond, facts) for cond in conditions)

    @staticmethod
    def run_inference(initial_facts, rules_df):
        facts = initial_facts.copy()
        fired_rules = set()
        trace = []
        changed = True
        iteration = 0
        max_iterations = 20

        while changed and iteration < max_iterations:
            changed = False
            iteration += 1

            for index, rule in rules_df.iterrows():
                rule_id = rule["id"]
                if rule_id in fired_rules:
                    continue

                if ExpertSystem.rule_matches(rule["conditions"], facts):
                    fired_rules.add(rule_id)

                    if pd.notna(rule["conclusion"]):
                        try:
                            key, value = rule["conclusion"].split("=")
                            key, value = key.strip(), value.strip()

                            if facts.get(key) != value:
                                facts[key] = value
                                changed = True
                                trace.append((rule_id, f"Set {key}={value}", rule["explanation"]))
                        except:
                            continue

        return facts, trace



class ModernButton(tk.Button):
    def __init__(self, parent, **kwargs):
        bg_color = kwargs.pop('bg', Config.SECONDARY_COLOR)
        fg = kwargs.pop('fg', Config.WHITE)
        font = kwargs.pop('font', ("Segoe UI", 10, "bold"))

        self.original_bg = bg_color

        super().__init__(
            parent,
            bg=self.original_bg,
            fg=fg,
            font=font,
            padx=12,
            pady=6,
            relief="flat",
            cursor="hand2",
            **kwargs
        )

        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        self['bg'] = self.lighten_color(self.original_bg)

    def on_leave(self, e):
        self['bg'] = self.original_bg

    @staticmethod
    def lighten_color(color, factor=0.2):
        rgb = tuple(int(color[i:i + 2], 16) for i in (1, 3, 5))
        light = tuple(min(255, int(c + (255 - c) * factor)) for c in rgb)
        return f'#{light[0]:02x}{light[1]:02x}{light[2]:02x}'


class CardFrame(tk.Frame):
    def __init__(self, parent, title="", padding=10, **kwargs):
        super().__init__(parent, bg="white", bd=1, relief="solid", **kwargs)

        if title:
            tk.Label(self, text=title, font=("Segoe UI", 11, "bold"),
                     bg="white", fg="#2C3E50").pack(anchor="w", padx=10, pady=(5, 0))

        self.inner_frame = tk.Frame(self, bg="white") #div background
        self.inner_frame.pack(fill="both", expand=True, padx=padding, pady=padding) #responsive



class FoodSafetyExpertSystemApp:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.rules_df = None
        self.load_data()
        self.create_widgets()

    def setup_window(self):
        self.root.title(f"{Config.APP_NAME}")
        self.root.geometry("800x850")
        self.root.configure(bg=Config.LIGHT_BG)

    def load_data(self):
        self.rules_df = DataHandler.load_rules()
        if self.rules_df is None:
            self.root.destroy()

    def create_widgets(self):
        header = tk.Frame(self.root, bg=Config.DARK_BG, height=70)
        header.pack(fill="x")

        tk.Label(header, text=Config.APP_NAME,
                 font=("Segoe UI", 20, "bold"),
                 bg=Config.DARK_BG, fg=Config.WHITE).pack(side="left", padx=20)

        main = tk.Frame(self.root, bg=Config.LIGHT_BG, padx=20, pady=15)
        main.pack(fill="both", expand=True)

        # INPUT CARD
        input_card = CardFrame(main, title="Food Parameters", padding=12)
        input_card.pack(fill="x")

        self.input_vars = {}
        self.create_input_fields(input_card.inner_frame)

        # BUTTONS
        btn_frame = tk.Frame(main, bg=Config.LIGHT_BG)
        btn_frame.pack(pady=10)

        ModernButton(btn_frame, text="ANALYZE", command=self.analyze,
                     bg=Config.PRIMARY_COLOR).pack(side="left", padx=5)

        ModernButton(btn_frame, text="CLEAR", command=self.clear_form,
                     bg="#95A5A6").pack(side="left", padx=5)

        # TRACE BOX
        trace_card = CardFrame(main, title="Inference Trace (Applied Rules)", padding=10)
        trace_card.pack(fill="both", expand=True, pady=(10, 0))

        self.trace_text = tk.Text(trace_card.inner_frame,
                                  height=10,
                                  wrap="word",
                                  font=("Consolas", 9),
                                  bg="#F8F9FA",
                                  fg="#2C3E50")

        scrollbar = ttk.Scrollbar(trace_card.inner_frame, command=self.trace_text.yview)
        self.trace_text.configure(yscrollcommand=scrollbar.set)

        self.trace_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.trace_text.insert(tk.END, "No analysis yet...\n")
        self.trace_text.config(state="disabled")



    def create_input_fields(self, parent):
        fields = [
            ("perishable", "Perishable?", ["yes", "no"], "yes"),
            ("temp_over_90F", "Temp > 90°F?", ["yes", "no"], "no"),
            ("hours_out", "Hours out:", None, "1.5"),
            ("mold_seen", "Mold seen?", ["yes", "no"], "no"),
            ("smell_off", "Bad smell?", ["yes", "no"], "no"),
            ("reheated", "Reheated?", ["yes", "no"], "no"),
        ]

        for i, (key, label, values, default) in enumerate(fields):
            tk.Label(parent, text=label, bg="white").grid(row=i, column=0, sticky="w", pady=5)

            var = tk.StringVar(value=default)
            if values:
                cb = ttk.Combobox(parent, textvariable=var, values=values,
                                  state="readonly", width=10)
                cb.grid(row=i, column=1, padx=10)
            else:
                entry = ttk.Entry(parent, textvariable=var, width=12)
                entry.grid(row=i, column=1, padx=10)

            self.input_vars[key] = var

    def validate_inputs(self):
        try:
            float(self.input_vars["hours_out"].get())
            return True
        except:
            messagebox.showerror("Error", "Invalid hours value!")
            return False

    def analyze(self):
        if not self.validate_inputs():
            return

        facts = {
            k: (float(v.get()) if k == "hours_out" else v.get())
            for k, v in self.input_vars.items()
        }

        final_facts, trace = ExpertSystem.run_inference(facts, self.rules_df)
        result = final_facts.get("action", "No decision")

        DataHandler.log_analysis(facts, result, trace)

        # RESULT POPUP
        messagebox.showinfo("Result", f"Decision:\n{result}")

        # UPDATE TRACE BOX
        self.trace_text.config(state="normal")
        self.trace_text.delete(1.0, tk.END)

        if trace:
            self.trace_text.insert(tk.END, "APPLIED RULES:\n" + "\n\n")
            for r_id, effect, explanation in trace:
                self.trace_text.insert(tk.END, f"Rule {r_id}\n")
                self.trace_text.insert(tk.END, f"→ Effect: {effect}\n")
                self.trace_text.insert(tk.END, f"→ Explanation: {explanation}\n")
                self.trace_text.insert(tk.END, "-" * 35 + "\n")
        else:
            self.trace_text.insert(tk.END, "No rules were triggered.\n")

        self.trace_text.config(state="disabled")


    def clear_form(self):
        self.input_vars["perishable"].set("yes")
        self.input_vars["temp_over_90F"].set("no")
        self.input_vars["hours_out"].set("1.5")
        self.input_vars["mold_seen"].set("no")
        self.input_vars["smell_off"].set("no")
        self.input_vars["reheated"].set("no")

        self.trace_text.config(state="normal")
        self.trace_text.delete(1.0, tk.END)
        self.trace_text.insert(tk.END, "No analysis yet...\n")
        self.trace_text.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk() #ينشئ النافذة الرئيسية للتطبيق
    app = FoodSafetyExpertSystemApp(root)
    root.mainloop()  #خلي النافذة مفتوحة وتستقبل نقرات المستخدم، كتابة، أزرار…
