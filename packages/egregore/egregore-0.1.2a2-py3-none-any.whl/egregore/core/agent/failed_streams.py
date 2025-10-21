import json
from pathlib import Path
from typing import Dict, Any, List

class FailedStreamingLog:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.log_file = Path.home() / ".egregore" / agent_id / "failed_streams.jsonl"
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def log_failed_stream(self, session_data: Dict[str, Any]):
        """Log cancelled/error streams only"""
        if session_data.get('status') in ['cancelled', 'error']:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(session_data) + '\n')
    
    def get_failed_streams(self) -> List[Dict[str, Any]]:
        """Get all failed streaming sessions"""
        if not self.log_file.exists():
            return []
        
        failed_streams = []
        with open(self.log_file, 'r') as f:
            for line in f:
                failed_streams.append(json.loads(line.strip()))
        return failed_streams