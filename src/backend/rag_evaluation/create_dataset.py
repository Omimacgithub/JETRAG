from ragas import Dataset

# Create a new dataset
dataset = Dataset(name="golden", backend="local/csv", root_dir="./dataset")

cnt = 0

for user_query, reference, referen in parsed_file:
    # Add a sample to the dataset
    dataset.append({
        "id": f"sample_{cnt}",
        "query": user_query,
        "expected_answer": output,
        "metadata": {"complexity": "simple", "language": "en"}
    })
    cnt += 1