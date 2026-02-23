"""Generate survey responses from user profiles with adopter category."""
import random

random.seed(42)

def parse_income_range(income_str):
    """Map income range to tier for budget logic."""
    if "$120k+" in income_str:
        return 5
    if "$90k–$120k" in income_str or "$90k-$120k" in income_str:
        return 4
    if "$70k–$90k" in income_str or "$70k-$90k" in income_str:
        return 3
    if "$50k–$70k" in income_str or "$50k-$70k" in income_str:
        return 2
    if "$30k–$50k" in income_str or "$30k-$50k" in income_str:
        return 1
    return 2

def get_budget(income_tier):
    """Derive per-semester budget from income."""
    budgets = {
        5: ["$12,000-$15,000", "$10,000-$15,000"],
        4: ["$8,000-$12,000", "$10,000-$12,000"],
        3: ["$6,000-$8,000", "$5,000-$8,000"],
        2: ["$4,000-$6,000", "$3,500-$6,000"],
        1: ["$2,000-$4,000", "$2,500-$4,000"],
    }
    return random.choice(budgets.get(income_tier, budgets[2]))

def get_career_change(profile):
    """Yes/No based on Profile type."""
    if "Career Changer" in profile:
        return "Yes"
    return "No"

def get_timeline(profile, age):
    """Derive target timeline from profile and age."""
    if "Career Changer" in profile:
        if age < 32:
            return "1-2 years"
        if age < 45:
            return "2-3 years"
        return "3-5 years"
    if age < 40:
        return "2-3 years"
    return "3-5 years or flexible"

def main():
    with open("user_profiles_with_adopter_category.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()

    output_lines = [
        "ID\tTime Commitment\tBudget (per semester)\tCareer Change?\tTarget Timeline\tAdopter Category",
        "=" * 120,
    ]

    for line in lines[1:]:
        parts = line.strip().split("\t")
        if len(parts) < 11:
            continue
        uid = parts[0]
        profile = parts[1]
        age = int(parts[2])
        income_str = parts[7]
        time_commit = parts[9]
        adopter_category = parts[10]

        income_tier = parse_income_range(income_str)
        budget = get_budget(income_tier)
        career_change = get_career_change(profile)
        timeline = get_timeline(profile, age)

        output_lines.append(
            f"{uid}\t{time_commit}\t{budget}\t{career_change}\t{timeline}\t{adopter_category}"
        )

    with open("survey_responses.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))

    print(f"Generated {len(output_lines) - 2} survey responses -> survey_responses.txt (with Adopter Category)")

if __name__ == "__main__":
    main()
