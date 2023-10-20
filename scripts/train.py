import pandas as pd
import numpy as np
from sklearn.metrics import f1_score
from transformers import AutoTokenizer
from transformers import AutoModelForSeq2SeqLM, DataCollatorForSeq2Seq, Seq2SeqTrainingArguments, Seq2SeqTrainer
from datasets import load_dataset, load_metric, Dataset
from peft import LoraConfig, get_peft_model, TaskType

############# code changes ###############
import intel_extension_for_pytorch as ipex
############# code changes ###############


def preprocess_function(examples):
    inputs = examples["input"]
    targets = examples["Answer"]

    model_inputs = tokenizer(inputs, max_length=max_input_length, truncation=True)
    labels = tokenizer(text_target=targets, max_length=max_target_length, truncation=True)

    model_inputs["labels"] = labels["input_ids"]
    return model_inputs

def print_number_of_trainable_model_parameters(model):
    trainable_model_params = 0
    all_model_params = 0
    for _, param in model.named_parameters():
        all_model_params += param.numel()
        if param.requires_grad:
            trainable_model_params += param.numel()
    return f"trainable model parameters: {trainable_model_params}\nall model parameters: {all_model_params}\npercentage of trainable model parameters: {100 * trainable_model_params / all_model_params:.2f}%"

def postprocess_text(preds, labels):
    preds = [pred.strip() for pred in preds]
    labels = [label.strip() for label in labels]
    return preds, labels

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


model_checkpoint = "mrm8488/t5-base-finetuned-squadv2"
max_input_length = 1024
max_target_length = 128
batch_size = 8
experiment_name = "T5_qa_model"

train_df = pd.read_csv("../data/train.csv")
test_df = pd.read_csv("../data/test.csv")
train_df = train_df.sample(frac=1).reset_index(drop=True)


train_data = train_df.iloc[:60000].reset_index(drop=True)
valid_data = train_df.iloc[60000:].reset_index(drop=True)

train_data["input"] = train_data.apply(lambda x: f'question: {x["Question"]}  context: {x["Story"]}', axis=1)
valid_data["input"] = valid_data.apply(lambda x: f'question: {x["Question"]}  context: {x["Story"]}', axis=1)

#for getting data for pruning
train_data[["input", "Answer"]].to_csv("../data/train_processed.csv", index=False)
valid_data[["input", "Answer"]].to_csv("../data/valid_processed.csv", index=False)

# Load datasets
train_dataset = Dataset.from_pandas(train_data[["input", "Answer"]])
valid_dataset = Dataset.from_pandas(valid_data[["input", "Answer"]])
    
tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)
model = AutoModelForSeq2SeqLM.from_pretrained(model_checkpoint)
data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)

train_tokenized_datasets = train_dataset.map(preprocess_function, batched=True)
valid_tokenized_datasets = valid_dataset.map(preprocess_function, batched=True)

print(print_number_of_trainable_model_parameters(model))


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

trainer.train()

trainer.save_model(f"../{experiment_name}/final_model")
