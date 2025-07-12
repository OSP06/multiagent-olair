import csv
import os

INPUT_PATH = "data/HackathonInternalKnowledgeBase.csv"
OUTPUT_PATH = "data/qa_internal_kb.csv"

def clean_money(value):
    return value.replace(",", "").replace("$", "").strip()

def generate_qa(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        fieldnames = ["question", "answer"]
        qa_pairs = []

        for row in reader:
            address = row.get("Property Address", "").strip()
            suite = row.get("Suite", "").strip()
            rent_sf = clean_money(row.get("Rent/SF/Year", ""))
            monthly_rent = clean_money(row.get("Monthly Rent", ""))
            broker_name = row.get("Associate 1", "").strip()
            broker_email = row.get("BROKER Email ID", "").strip()

            if not address or not suite or not rent_sf or not monthly_rent:
                continue

            question = f"What's the rent at {address}, Suite {suite}?"
            answer = (
                f"${rent_sf}/SF/year. Monthly Rent is ${monthly_rent}. "
                f"Broker: {broker_name} ({broker_email})"
            )

            qa_pairs.append({"question": question, "answer": answer})

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(qa_pairs)

    print(f"✅ Generated {len(qa_pairs)} Q&A pairs to {output_path}")

if __name__ == "__main__":
    generate_qa(INPUT_PATH, OUTPUT_PATH)
