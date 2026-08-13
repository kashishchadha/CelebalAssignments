import os
from pathlib import Path
from config.settings import CRM_INBOUND_DIR, ERP_INBOUND_DIR

class InboundLayer:
    def __init__(self, batch_name: str = "batch_01"):
        self.batch_name = batch_name

    def get_inbound_files(self) -> dict:
        crm_path = CRM_INBOUND_DIR / self.batch_name
        erp_path = ERP_INBOUND_DIR / self.batch_name
        
        files_map = {}
        if crm_path.exists():
            for file_path in crm_path.glob("*.csv"):
                entity = file_path.stem
                files_map[entity] = {
                    "source_system": "CRM",
                    "file_path": str(file_path),
                    "batch_id": self.batch_name
                }

        if erp_path.exists():
            for file_path in erp_path.glob("*.csv"):
                entity = file_path.stem
                files_map[entity] = {
                    "source_system": "ERP",
                    "file_path": str(file_path),
                    "batch_id": self.batch_name
                }

        return files_map
