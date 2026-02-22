from pymongo import MongoClient
from datasets import load_dataset

client = MongoClient("mongodb://localhost:27017/")
db = client["leetcode"]

ds = load_dataset("newfacade/LeetCodeDataset")

for problem in ds['train']:
    doc = {
        "_id":              problem["task_id"],          # "two-sum" # type: ignore
        "question_id":      problem["question_id"],
        "title":            problem["task_id"].replace("-", " ").title(),
        "difficulty":       problem["difficulty"],
        "tags":             problem["tags"],
        "description":      problem["problem_description"],
        "starter_code":     problem["starter_code"],
        "prompt":           problem["prompt"],           # has all imports + helpers
        "entry_point":      problem["entry_point"],      # "Solution().twoSum" # type: ignore
        "test_cases":       problem["input_output"],     # [{"input": "...", "output": "..."}]
    } #type: ignore
    db.problems.update_one({"_id": doc["_id"]}, {"$set": doc}, upsert=True)

print(f"✅ Ingested {db.problems.count_documents({})} problems")

