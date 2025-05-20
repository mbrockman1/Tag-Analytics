import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from aqt import mw
from aqt.utils import showInfo, getSaveFile
from aqt.qt import QAction, QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox, QTableWidget, QTableWidgetItem, QColor
import csv

# Configuration and constants
CONFIG_PATH = os.path.join(mw.addonManager.addonsFolder(), "tag_analytics", "config.json")
DAYS_FOR_TREND = 30
MASTERY_LEVELS = {
    "Beginner": (0, 60),
    "Intermediate": (61, 80),
    "Advanced": (81, 100)
}

# Initialize configuration
def load_config():
    default_config = {
        "metrics": {
            "recall_percentage": True,
            "avg_review_time": True,
            "ease_factor": True
        }
    }
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return default_config

def save_config(config):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)

# Database queries
def get_tag_metrics() -> Dict[str, Dict]:
    if not mw.col:
        showInfo("No collection loaded. Please open a profile first.")
        return {}
    
    metrics = {}
    query = """
    SELECT n.tags, c.id, r.ease, r.time, r.type
    FROM cards c
    JOIN notes n ON c.nid = n.id
    JOIN revlog r ON c.id = r.cid
    WHERE r.id > ?
    """
    start_time = int((datetime.now() - timedelta(days=DAYS_FOR_TREND)).timestamp() * 1000)
    try:
        rows = mw.col.db.execute(query, start_time)
        for row in rows:
            tags, card_id, ease, time, rev_type = row
            # Tags are stored as a space-separated string in notes.tags
            tag_list = tags.strip().split() if tags else []
            for tag in tag_list:
                if tag not in metrics:
                    metrics[tag] = {"reviews": [], "times": [], "eases": [], "correct": 0, "total": 0}
                if rev_type in (1, 2, 3):  # Learning, review, relearning
                    metrics[tag]["reviews"].append(rev_type)
                    metrics[tag]["times"].append(time / 1000)  # Convert to seconds
                    metrics[tag]["eases"].append(ease)
                    metrics[tag]["total"] += 1
                    if ease > 1:  # Correct answer
                        metrics[tag]["correct"] += 1
    except Exception as e:
        showInfo(f"Error accessing database: {str(e)}")
        return {}
    return metrics

def calculate_metrics(metrics: Dict[str, Dict]) -> Dict[str, Dict]:
    processed = {}
    for tag, data in metrics.items():
        total_reviews = data["total"]
        if total_reviews == 0:
            continue
        recall = (data["correct"] / total_reviews) * 100 if total_reviews > 0 else 0
        avg_time = sum(data["times"]) / total_reviews if total_reviews > 0 else 0
        avg_ease = sum(data["eases"]) / total_reviews if total_reviews > 0 else 0
        mastery = "Beginner"
        for level, (low, high) in MASTERY_LEVELS.items():
            if low <= recall <= high:
                mastery = level
        processed[tag] = {
            "recall_percentage": round(recall, 2),
            "avg_review_time": round(avg_time, 2),
            "ease_factor": round(avg_ease, 2),
            "mastery": mastery,
            "total_reviews": total_reviews
        }
    return processed

def get_historical_trends(tag: str) -> List[Tuple[str, float]]:
    if not mw.col:
        showInfo("No collection loaded. Please open a profile first.")
        return []
    
    trends = []
    query = """
    SELECT strftime('%Y-%m-%d', r.id / 1000, 'unixepoch') as day, r.ease, n.tags
    FROM cards c
    JOIN notes n ON c.nid = n.id
    JOIN revlog r ON c.id = r.cid
    WHERE r.id > ?
    """
    start_time = int((datetime.now() - timedelta(days=DAYS_FOR_TREND)).timestamp() * 1000)
    try:
        rows = mw.col.db.execute(query, start_time)
        daily = {}
        for day, ease, tags in rows:
            tag_list = tags.strip().split() if tags else []
            if tag not in tag_list:
                continue
            if day not in daily:
                daily[day] = {"correct": 0, "total": 0}
            daily[day]["total"] += 1
            if ease > 1:
                daily[day]["correct"] += 1
        for day in sorted(daily.keys()):
            recall = (daily[day]["correct"] / daily[day]["total"]) * 100
            trends.append((day, round(recall, 2)))
    except Exception as e:
        showInfo(f"Error accessing historical data: {str(e)}")
        return []
    return trends

# GUI
class TagAnalyticsDialog(QDialog):
    def __init__(self):
        super().__init__(mw)
        self.config = load_config()
        self.metrics = calculate_metrics(get_tag_metrics())
        self.setup_ui()
        self.populate_table()

    def setup_ui(self):
        self.setWindowTitle("Tag Analytics")
        self.setMinimumSize(800, 600)
        layout = QVBoxLayout()

        # Metrics toggles
        toggle_layout = QHBoxLayout()
        for metric in self.config["metrics"]:
            checkbox = QCheckBox(metric.replace("_", " ").title())
            checkbox.setChecked(self.config["metrics"][metric])
            checkbox.stateChanged.connect(self.update_config)
            toggle_layout.addWidget(checkbox)
        layout.addLayout(toggle_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Tag", "Recall %", "Avg Time (s)", "Ease Factor", "Raw Recall %", "Mastery"])
        self.table.cellClicked.connect(self.show_trend)
        layout.addWidget(self.table)

        # Export button
        export_btn = QPushButton("Export Report")
        export_btn.clicked.connect(self.export_report)
        layout.addWidget(export_btn)

        self.setLayout(layout)

    def update_config(self):
        for i in range(self.layout().itemAt(0).layout().count()):
            checkbox = self.layout().itemAt(0).layout().itemAt(i).widget()
            metric = checkbox.text().lower().replace(" ", "_")
            self.config["metrics"][metric] = checkbox.isChecked()
        save_config(self.config)
        self.populate_table()

    def populate_table(self):
        self.table.setRowCount(len(self.metrics))
        row = 0
        for tag, data in sorted(self.metrics.items()):
            self.table.setItem(row, 0, QTableWidgetItem(tag))
            if self.config["metrics"]["recall_percentage"]:
                self.table.setItem(row, 1, QTableWidgetItem(str(data["recall_percentage"])))
            if self.config["metrics"]["avg_review_time"]:
                self.table.setItem(row, 2, QTableWidgetItem(str(data["avg_review_time"])))
            if self.config["metrics"]["ease_factor"]:
                self.table.setItem(row, 3, QTableWidgetItem(str(data["ease_factor"])))
            self.table.setItem(row, 4, QTableWidgetItem(str(data["recall_percentage"])))
            mastery_item = QTableWidgetItem(data["mastery"])
            mastery_item.setBackground(QColor("red") if data["mastery"] == "Beginner" else
                                     QColor("yellow") if data["mastery"] == "Intermediate" else
                                     QColor("green"))
            self.table.setItem(row, 5, QTableWidgetItem(mastery_item))
            row += 1
        self.table.resizeColumnsToContents()

    def show_trend(self, row, _):
        tag = self.table.item(row, 0).text()
        trends = get_historical_trends(tag)
        if not trends:
            showInfo("No historical data available for this tag.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Trend for {tag}")
        dialog.setMinimumSize(400, 300)
        layout = QVBoxLayout()

        # Trend table
        trend_table = QTableWidget()
        trend_table.setRowCount(len(trends))
        trend_table.setColumnCount(2)
        trend_table.setHorizontalHeaderLabels(["Date", "Recall %"])
        for i, (day, recall) in enumerate(trends):
            trend_table.setItem(i, 0, QTableWidgetItem(day))
            trend_table.setItem(i, 1, QTableWidgetItem(str(recall)))
        trend_table.resizeColumnsToContents()
        layout.addWidget(trend_table)

        dialog.setLayout(layout)
        dialog.exec()

    def export_report(self):
        filename = getSaveFile(mw, "Export Report", "reports", ".csv", "tag_analytics_report.csv")
        if not filename:
            return
        with open(filename, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            headers = ["Tag", "Recall %", "Avg Time (s)", "Ease Factor", "Raw Recall %", "Mastery", "Total Reviews"]
            writer.writerow(headers)
            for tag, data in sorted(self.metrics.items()):
                row = [
                    tag,
                    data["recall_percentage"],
                    data["avg_review_time"],
                    data["ease_factor"],
                    data["recall_percentage"],
                    data["mastery"],
                    data["total_reviews"]
                ]
                writer.writerow(row)
        showInfo("Report exported successfully!")

# Add-on integration
def show_analytics():
    if not mw.col:
        showInfo("Please open a profile to access Tag Analytics.")
        return
    dialog = TagAnalyticsDialog()
    dialog.exec()

action = QAction("Tag Analytics", mw)
action.triggered.connect(show_analytics)
mw.form.menuTools.addAction(action)