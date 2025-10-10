import csv
import os
from pathlib import Path
from datetime import datetime
from typing import List, Optional

class InventoryService:
    def __init__(self, base_dir: Path, csv_pattern: str):
        self.base_dir = base_dir
        self.csv_pattern = csv_pattern
    
    def find_csv_file(self) -> Optional[Path]:
        csv_files = list(self.base_dir.glob(self.csv_pattern))
        return max(csv_files, key=os.path.getmtime) if csv_files else None
    
    def get_all_items(self) -> List[dict]:
        csv_file = self.find_csv_file()
        if not csv_file or not csv_file.exists():
            return []
        
        data = []
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cleaned_row = {k: v if v.strip() else None for k, v in row.items()}
                data.append(cleaned_row)
        
        data.sort(key=self._parse_timestamp, reverse=True)
        return data
    
    def _parse_timestamp(self, item: dict) -> Optional[datetime]:
        posted = item.get('posted')
        if not posted:
            return None
        try:
            if posted.endswith(('Z', '+00:00')):
                return datetime.fromisoformat(posted.replace('Z', '+00:00'))
            elif '+' in posted or posted.count('-') > 2:
                return datetime.fromisoformat(posted)
            else:
                return datetime.fromisoformat(posted + '+00:00')
        except (ValueError, TypeError):
            return None

