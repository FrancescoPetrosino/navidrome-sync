import csv

def export_list_to_csv(file_path, data, fieldnames=None):
    """Export a list of dictionaries to a CSV file."""
    try:
        with open(file_path, "w", encoding="utf-8", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames or data[0].keys())
            writer.writeheader()
            writer.writerows(data)
    except Exception as e:
        print("Error exporting to CSV:", e)