import logging
import argparse
import os
import pandas as pd
import torch
from sklearn.model_selection import train_test_split
from transformers import (
    GPT2Tokenizer,
    GPT2LMHeadModel,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments,
)
from datasets import Dataset

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s -   %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--parquet_path", type=str, default="data/transcriptions_cleaned.parquet", help="Path to the parquet file")
    parser.add_argument("--output_dir", type=str, default="models/trump_gpt2", help="Directory to save the model")
    parser.add_argument("--model_name", type=str, default="gpt2", help="Pre-trained model name")
    parser.add_argument("--epochs", type=int, default=3, help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=4, help="Batch size (lower for CPU)")
    parser.add_argument("--max_samples", type=int, default=1000, help="Limit number of samples for faster training (0 for all)")
    args = parser.parse_args()

    # 1. Prepare Data
    logger.info(f"Loading data from {args.parquet_path}")
    df = pd.read_parquet(args.parquet_path)
    
    # Filter empty text
    df = df.dropna(subset=["text"])
    df = df[df["text"].str.strip().str.len() > 0]

    # Subsample for speed if requested
    if args.max_samples > 0 and len(df) > args.max_samples:
        logger.info(f"Subsampling dataset from {len(df)} to {args.max_samples} rows for speed.")
        df = df.sample(n=args.max_samples, random_state=42)
    
    # Split data
    train_df, val_df = train_test_split(df, test_size=0.1, random_state=42)
    
    # Convert to Hugging Face Datasets
    train_dataset = Dataset.from_pandas(train_df[["text"]])
    val_dataset = Dataset.from_pandas(val_df[["text"]])

    # 2. Load Tokenizer
    logger.info(f"Loading tokenizer: {args.model_name}")
    tokenizer = GPT2Tokenizer.from_pretrained(args.model_name)
    # GPT2 doesn't have a pad token by default, use EOS
    tokenizer.pad_token = tokenizer.eos_token

    def tokenize_function(examples):
        return tokenizer(examples["text"], truncation=True, padding="max_length", max_length=128)

    logger.info("Tokenizing datasets...")
    # Map applies the tokenizer to all data
    tokenized_train = train_dataset.map(tokenize_function, batched=True, remove_columns=train_dataset.column_names)
    tokenized_val = val_dataset.map(tokenize_function, batched=True, remove_columns=val_dataset.column_names)

    # 3. Load Model
    logger.info(f"Loading model: {args.model_name}")
    model = GPT2LMHeadModel.from_pretrained(args.model_name)

    # 4. Initialize Trainer
    training_args = TrainingArguments(
        output_dir=args.output_dir,
        overwrite_output_dir=True,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        eval_steps=50, # Evaluate more often
        save_steps=100,
        warmup_steps=10,
        prediction_loss_only=True,
        logging_dir=f"{args.output_dir}/logs",
        logging_steps=10,
        save_total_limit=2,
        use_cpu=not torch.cuda.is_available(),
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        data_collator=DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False),
        train_dataset=tokenized_train,
        eval_dataset=tokenized_val,
    )

    # 5. Train
    logger.info("Starting training...")
    trainer.train()
    
    # 6. Save
    logger.info(f"Saving model to {args.output_dir}")
    trainer.save_model(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)
        
    logger.info("Done!")

if __name__ == "__main__":
    main()
