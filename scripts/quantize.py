import argparse
import pandas as pd
import numpy as np
from sklearn.metrics import f1_score
from transformers import AutoTokenizer
from transformers import AutoModelForSeq2SeqLM, DataCollatorForSeq2Seq, Seq2SeqTrainingArguments, Seq2SeqTrainer
from datasets import load_dataset, load_metric, Dataset
from neural_compressor.config import PostTrainingQuantConfig
from neural_compressor import quantization

############# code changes ###############
import intel_extension_for_pytorch as ipex
############# code changes ###############



def postprocess_text(preds, labels):
    preds = [pred.strip() for pred in preds]
    labels = [label.strip() for label in labels]
    return preds, labels


def parse_args():
    parser = argparse.ArgumentParser(description="Finetune a transformers model on a Translation task")
    
    parser.add_argument(
        "--model_name_or_path",
        type=str,
        help="Path to pretrained model or model identifier from huggingface.co/models.",
        required=False,
    )
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    
    max_input_length = 1024
    max_target_length = 128
    batch_size = 8
    experiment_name = "T5_qa_model"


    train_data = pd.read_csv("../data/train_processed.csv")
    valid_data = pd.read_csv("../data/valid_processed.csv")

    # Load datasets
    train_dataset = Dataset.from_pandas(train_data[["input", "Answer"]])
    valid_dataset = Dataset.from_pandas(valid_data[["input", "Answer"]])
        
    tokenizer = AutoTokenizer.from_pretrained(args.model_name_or_path)
    model = AutoModelForSeq2SeqLM.from_pretrained(args.model_name_or_path)
    data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)

    def preprocess_function(examples):
        inputs = examples["input"]
        targets = examples["Answer"]

        model_inputs = tokenizer(inputs, max_length=max_input_length, truncation=True)
        labels = tokenizer(text_target=targets, max_length=max_target_length, truncation=True)

        model_inputs["labels"] = labels["input_ids"]
        return model_inputs


    def compute_metrics(eval_preds):
        preds, labels = eval_preds
        if isinstance(preds, tuple):
            preds = preds[0]
        decoded_preds = tokenizer.batch_decode(preds, skip_special_tokens=True)
        # Replace -100 in the labels as we can't decode them.
        labels = np.where(labels != -100, labels, tokenizer.pad_token_id)
        decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)

        # Some simple post-processing
        decoded_preds, decoded_labels = postprocess_text(decoded_preds, decoded_labels)

        # Calculate Exact Match (EM) and F1 score
        em_score = 0
        f1_score_value = 0
        for pred, label in zip(decoded_preds, decoded_labels):
            em_score += int(pred == label)
            f1_score_value += f1_score([label], [pred], average='macro')

        em_score = em_score / len(decoded_preds)  # EM is a ratio
        f1_score_value = f1_score_value / len(decoded_preds)  # F1 score is an average

        result = {
            "exact_match": round(em_score, 4),
            "f1_score": round(f1_score_value, 4)
        }

        prediction_lens = [np.count_nonzero(pred != tokenizer.pad_token_id) for pred in preds]
        result["gen_len"] = np.mean(prediction_lens)

        return result

    train_tokenized_datasets = train_dataset.map(preprocess_function, batched=True)
    valid_tokenized_datasets = valid_dataset.map(preprocess_function, batched=True)


    #################### code changes #################
    model = model.to("xpu")
    model = ipex.optimize(model)
    #################### code changes #################

    model.generation_config.max_length = max_target_length

    args = Seq2SeqTrainingArguments(
        f"{experiment_name}",
        evaluation_strategy = "steps",
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        save_total_limit=3,
        num_train_epochs=2,
        predict_with_generate=True,
        fp16=True,
        eval_steps=5000,
        save_steps=5000,
        report_to="none",
        load_best_model_at_end=True
    )

    trainer = Seq2SeqTrainer(
        model,
        args,
        train_dataset=train_tokenized_datasets,
        eval_dataset=valid_tokenized_datasets,
        data_collator=data_collator,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics
    )

    conf = PostTrainingQuantConfig(
        device="gpu",
        backend="itex",
        approach="dynamic"
    )
    
    calib_dataloader = trainer.get_eval_dataloader()
    conf.use_bf16 = False
    q_model = quantization.fit(
        model,
        conf,
        calib_dataloader=calib_dataloader
    )
    q_model.save("../quantized_model")

if __name__ == "__main__":
    main()


