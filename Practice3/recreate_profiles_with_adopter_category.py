"""
Recreate user profiles with Rogers' Innovation Diffusion adopter category.
Classification uses age, education level, and time commitment as factors.
"""
import re

def get_education_score(education):
    """Higher education correlates with earlier adoption tendency (1-5)."""
    mapping = {
        "Master's": 5,
        "Bachelor's": 4,
        "Associate": 3,
        "Some College": 2,
    }
    return mapping.get(education, 3)

def get_age_score(age):
    """Younger people tend to adopt innovations earlier (1-5)."""
    if age <= 28:
        return 5
    if age <= 35:
        return 4
    if age <= 45:
        return 3
    if age <= 52:
        return 2
    return 1

def get_time_commitment_score(time_commit):
    """Higher commitment to learning indicates earlier adoption (1-5)."""
    if not time_commit:
        return 2
    s = time_commit.lower()
    if "20+" in s or "15-20" in s:
        return 5
    if "10-15" in s:
        return 4
    if "5-10" in s:
        return 3
    if "3-5" in s or "flexible" in s or "under 5" in s:
        return 2
    return 2

def classify_adopter(total_score):
    """Map total score (3-15) to Rogers' adopter categories."""
    if total_score >= 12:
        return "Innovator"
    if total_score >= 10:
        return "Early Adopter"
    if total_score >= 7:
        return "Early Majority"
    if total_score >= 5:
        return "Late Majority"
    return "Laggard"

def main():
    users = {}
    with open("sample_users.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()
    header = lines[0].strip()
    for line in lines[1:]:
        parts = line.strip().split("\t")
        if len(parts) < 9:
            continue
        uid = parts[0]
        users[uid] = {
            "line": line.strip(),
            "age": int(parts[2]),
            "education": parts[8],
        }

    survey = {}
    with open("survey_responses.txt", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("=") or "Time Commitment" in line:
                continue
            parts = line.split("\t")
            if len(parts) >= 2:
                survey[parts[0]] = parts[1]  # Time Commitment

    output_lines = [
        "ID\tProfile\tAge\tGender\tLocation\tCurrent Role\tDesired Field\tIncome Range\tEducation Level\t"
        "Time Commitment\tAdopter Category",
    ]

    for uid, data in users.items():
        age = data["age"]
        education = data["education"]
        time_commit = survey.get(uid, "")

        age_s = get_age_score(age)
        edu_s = get_education_score(education)
        time_s = get_time_commitment_score(time_commit)
        total = age_s + edu_s + time_s
        category = classify_adopter(total)

        parts = data["line"].split("\t")
        new_line = "\t".join(parts) + "\t" + time_commit + "\t" + category
        output_lines.append(new_line)

    with open("user_profiles_with_adopter_category.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))

    # Summary counts
    from collections import Counter
    cats = Counter()
    for line in output_lines[1:]:
        cat = line.split("\t")[-1]
        cats[cat] += 1

    print(f"Generated {len(output_lines) - 1} user profiles -> user_profiles_with_adopter_category.txt")
    print("\nAdopter category distribution:")
    for c in ["Innovator", "Early Adopter", "Early Majority", "Late Majority", "Laggard"]:
        print(f"  {c}: {cats[c]}")

if __name__ == "__main__":
    main()
