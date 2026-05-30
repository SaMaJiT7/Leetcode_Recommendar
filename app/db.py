from pymongo import MongoClient
from datasets import load_dataset

client = MongoClient("mongodb://localhost:27017/")
db = client["leetcode"]

ds = load_dataset("newfacade/LeetCodeDataset")

for problem in ds['train']:
    doc = {
        "_id":              problem["task_id"],          # "two-sum" # type: ignore
        "question_id":      problem["question_id"], # type: ignore
        "title":            problem["task_id"].replace("-", " ").title(), # type: ignore
        "difficulty":       problem["difficulty"],# type: ignore
        "tags":             problem["tags"],# type: ignore
        "description":      problem["problem_description"],# type: ignore
        "starter_code":     problem["starter_code"],# type: ignore
        "prompt":           problem["prompt"],        # type: ignore   # has all imports + helpers
        "entry_point":      problem["entry_point"],      # "Solution().twoSum" # type: ignore
        "test_cases":       problem["input_output"],    # type: ignore # [{"input": "...", "output": "..."}]
    } #type: ignore
    db.problems.update_one({"_id": doc["_id"]}, {"$set": doc}, upsert=True)

print(f"✅ Ingested {db.problems.count_documents({})} problems")

