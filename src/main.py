import os
import pandas as pd
import numpy as np

# hnaya bach n'importi  csv ta3i
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "data", "projectAI.csv")

# loadi rules bl pandas
def load_rules():
    df = pd.read_csv(CSV_PATH, delimiter=';', encoding='utf-8')
    # hna bach n effacer les espaces
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    return df

# تقييم شرط واحد
def evaluate_condition(condition, facts):
    condition = condition.strip()
    if "==" in condition:
        key, value = condition.split("==")  #hnaya par exemple ida kant  "age==20"  -> [key:"age" , value:"20"]
        return facts.get(key.strip()) == value.strip()
    if "<=" in condition:
        key, value = condition.split("<=")
        return float(facts.get(key.strip(), 0)) <= float(value)
    if ">" in condition:
        key, value = condition.split(">")
        return float(facts.get(key.strip(), 0)) > float(value)  # exp :age>30 -> False psq age rayh ydi initial value =0
    return False

# la comparaison les condition t3 rule m3a facts
def rule_matches(rule_conditions, facts):
    conditions = rule_conditions.replace("\n", "").split(";")
    return all(evaluate_condition(cond, facts) for cond in conditions)

# ===== 5) محرك الاستدلال مع Trace و Explanation باستخدام pandas =====
def run_expert_system(initial_facts):
    rules_df = load_rules()
    facts = initial_facts.copy()
    fired_rules = set()
    trace = []

    changed = True
    while changed:
        changed = False

        for _, rule in rules_df.iterrows():
            rule_id = rule["id"]
            if rule_id in fired_rules:
                continue

            if rule_matches(rule["conditions"], facts):
                fired_rules.add(rule_id)

                #  Conclusion
                if pd.notna(rule["conclusion"]):
                    key, value = rule["conclusion"].split("=")

                    # 🚫 لا تسمح بإلغاء unsafe=yes
                    if key == "unsafe" and facts.get("unsafe") == "yes" and value == "no":
                        trace.append((rule_id, "Skipped changing unsafe from yes to no", rule["explanation"]))
                    else:
                        if facts.get(key) != value:
                            facts[key] = value
                            changed = True
                            trace.append((rule_id, f"{key} = {value}", rule["explanation"]))

                # ===== Action =====
                if pd.notna(rule.get("action")):
                    facts["action"] = rule["action"]
                    trace.append((rule_id, f"action = {rule['action']}", rule["explanation"]))

    return facts, trace

if __name__ == "__main__":
    user_facts = {
        "perishable": "yes",
        "temp_over_90F": "yes",
        "hours_out": 2,
        "mold_seen": "no",
        "smell_off": "no",
        "reheated": "no"
    }

    final_facts, trace = run_expert_system(user_facts)

    print("\n=== Expert System Trace ===")
    for r_id, result, explanation in trace:
        print(f"✔ Rule {r_id} fired -> {result}")
        print(f"   ℹ Explanation: {explanation}")

    final_action = final_facts.get("action")
    print("\n=== Final Facts ===")
    print(final_facts)
    print("✅ Final Action:", final_action)
