import json

# Load structured data
with open('data/ao_report_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Let's inspect all staircase rows from sheet2.xml to get exact values
staircase_rows = [
    {"row": 26, "label_red1": "-49", "green1": "49", "red2": "-167"},
    {"row": 28, "label_red1": "-51", "green1": "51", "red2": "-162"},
    {"row": 30, "label_red1": "-49", "green1": "49", "red2": "-118"},
    {"row": 32, "label_red1": "-51", "green1": "51", "red2": "-111"},
    {"row": 34, "label_red1": "-49", "green1": "49", "red2": "-69"},
    {"row": 36, "label_red1": "-51", "green1": "51", "red2": "-59"},
    {"row": 38, "label_red1": "-24", "green1": "49", "red2": "-21"},
    {"row": 40, "label_red1": "-12", "green1": "51", "red2": "-8"},
]

print("Staircase rows ready:", len(staircase_rows))
