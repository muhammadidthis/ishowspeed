import pandas as pd
from sentence_transformers import SentenceTransformer

# Load dataset
df = pd.read_csv("ishowspeed_yt_dataset_all.csv")

# Use video titles to generate embeddings
titles = df["Title"].astype(str).tolist()

# Load model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Generate embeddings
embeddings = model.encode(titles, show_progress_bar=True)

# Add embedding columns to DataFrame
for i in range(embeddings.shape[1]):
    df[f'embedding_{i}'] = embeddings[:, i]

# Save to new CSV
df.to_csv("ishowspeed_yt_dataset_with_embeddings.csv", index=False)
print("✅ Embeddings saved!")
