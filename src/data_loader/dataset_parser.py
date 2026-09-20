import json
from pathlib import Path

class DataParser:
    def __init__(self, questions_path: str = "", outputs_path: str = ""):
        project_root = Path(__file__).resolve().parent.parent.parent

        default_q = project_root/"data"/"raw"/"LaMP_2"/"dev_questions.json"
        default_o = project_root/"data"/"raw"/"LaMP_2"/"dev_outputs.json"

        if questions_path:
            p = Path(questions_path)
            self.questions_path = p if p.is_absolute() else (project_root / p).resolve()
        else:
            self.questions_path = default_q.resolve()

        if outputs_path:
            p = Path(outputs_path)
            self.outputs_path = p if p.is_absolute() else (project_root / p).resolve()
        else:
            self.outputs_path = default_o.resolve()


    def load(self) -> tuple[list[dict], dict]:
        """Returns:
           - questions: list of all question samples
           - output_map: dict mapping id -> ground truth label
        """
        with open(self.questions_path, "r") as f:
            questions = json.load(f)

        with open(self.outputs_path, "r") as f:
            raw_outputs = json.load(f)

        golds = raw_outputs.get("golds", raw_outputs) if isinstance(raw_outputs, dict) else raw_outputs
        output_map = {item["id"]: item["output"] for item in golds}

        return questions, output_map

    def get_user_profiles(self, questions: list[dict]) -> dict:
        """Returns a dict: { user_id -> list of profile history items }
           Each question sample contains its own profile list.
        """
        profiles = {}
        for sample in questions:
            uid = sample.get("id")  
            profile = sample.get("profile", [])
            profiles[uid] = profile
        return profiles