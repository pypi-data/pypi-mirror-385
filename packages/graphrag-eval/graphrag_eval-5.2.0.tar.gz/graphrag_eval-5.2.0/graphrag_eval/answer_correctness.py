import csv
from pathlib import Path

from openai import OpenAI
from tqdm import tqdm

from graphrag_eval.util import compute_f1


IN_FILE_PATH = "../data/data-1.tsv"
PROMPT_FILE_PATH = Path(__file__).parent / "prompts" / "template.md"
OUT_FILE_PATH = "results/data-1.tsv"
OUT_FIELDS = ["#Reference", "#PTarget", "#Matching", "Reasoning", "Error"]
LLM_MODEL = "gpt-4o-mini"
TEMPERATURE = 0.0



def compute_recall_precision_f1(
    n_pos: int | None,
    n_pred_pos: int | None,
    n_true_pos: int | None,
) -> tuple[float | None, float | None, float | None]:
    recall = None
    precision = None
    if n_true_pos is not None and n_pos:
        recall = n_true_pos / n_pos
    if n_true_pos is not None and n_pred_pos:
        precision = n_true_pos / n_pred_pos
    return recall, precision, compute_f1(recall, precision)


def extract_response_values(
    response: str
) -> tuple[int | None, int | None, int | None, str, str]:
    vals = response.split("\t")
    n = len(vals)
    if n < 4:
        msg = f"Expected 4 tab-separated values: {response}"
        return None, None, None, "", msg
    vals = vals[:4]
    try:
        n_ref, n_actual, n_matching = map(int, vals[:3])
    except ValueError:
        msg = f"Claims counts should be ints: {vals}"
        return None, None, None, vals[3], msg
    if any([
        n_ref < 1,
        n_actual < 1,
        n_matching < 0,
        n_matching > n_ref,
        n_matching > n_actual
    ]):
        msg = f"Invalid claims counts combination: {n_ref}\t{n_actual}\t{n_matching}"
        return None, None, None, vals[3], msg
    return n_ref, n_actual, n_matching, vals[3], ""


class AnswerCorrectnessEvaluator:
    def __init__(
        self,
        prompt_file_path: str | Path = PROMPT_FILE_PATH,
        temperature : float = TEMPERATURE
    ):
        with open(prompt_file_path, encoding="utf-8") as f:
            self.prompt_template = f.read()
        self.openai_client = OpenAI()
        self.temperature = temperature

    def call_llm(self, prompt: str) -> str:
        try:
            response = self.openai_client.chat.completions.create(
                model=LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature
            )
            return response.choices[0].message.content.strip("\n")
        except Exception as e:
            return str(e).replace("\n", "    ")

    def evaluate_answer(
        self,
        question: str,
        reference_answer: str,
        actual_answer: str
    ):
        prompt = self.prompt_template.format(
            question=question,
            reference_answer=reference_answer,
            candidate_answer=actual_answer,
        )
        response_str = self.call_llm(prompt)
        return extract_response_values(response_str)

    def get_correctness_dict(
        self,
        reference: dict,
        actual: dict,
    ):
        result = {}
        result["reference_answer"] = reference["reference_answer"]
        num_ref_claims, num_actual_claims, num_matching_claims, reason, error = \
        self.evaluate_answer(
            reference["question_text"],
            reference["reference_answer"],
            actual["actual_answer"],
        )
        if error:
            result["answer_eval_error"] = error
        else:
            result.update({
                "answer_reference_claims_count": num_ref_claims,
                "answer_actual_claims_count": num_actual_claims,
                "answer_matching_claims_count": num_matching_claims,
                "answer_correctness_reason": reason,
            })
            recall, precision, f1 = compute_recall_precision_f1(
                num_ref_claims, num_actual_claims, num_matching_claims
            )
            if recall is not None:
                result["answer_recall"] = recall
            if precision is not None:
                result["answer_precision"] = precision
            if f1 is not None:
                result["answer_f1"] = f1
        return result


def evaluate_and_write(
    in_file_path: str | Path,
    out_file_path: str | Path,
) -> None:
    evaluator = AnswerCorrectnessEvaluator(PROMPT_FILE_PATH)
    with open(in_file_path, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        rows = [row for row in reader]
    print(f"Writing results to {out_file_path}")
    Path(out_file_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_file_path, "w", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(OUT_FIELDS)
        for row in tqdm(rows):
            vals = evaluator.evaluate_answer(
                row["Question"],
                row["Reference answer"],
                row["Actual answer"]
            )
            writer.writerow(vals)
            f.flush()


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--in-file", type=str, default=IN_FILE_PATH)
    parser.add_argument("-o", "--out-file", type=str, default=OUT_FILE_PATH)
    args = parser.parse_args()
    evaluate_and_write(
        in_file_path=args.in_file,
        out_file_path=args.out_file,
    )
