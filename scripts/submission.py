from  transformers  import  AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import torch
import argparse
from tqdm.auto import tqdm
import pandas as pd

############# code changes ###############
import intel_extension_for_pytorch as ipex
############# code changes ###############


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
    size = 128

    tokenizer = AutoTokenizer.from_pretrained(args.model_name_or_path)
    model = AutoModelForSeq2SeqLM.from_pretrained(args.model_name_or_path)

    #################### code changes #################
    model = model.to("xpu")
    model = ipex.optimize(model, dtype=torch.float16)
    #################### code changes #################

    test_data = pd.read_csv("../data/test.csv")
    test_data["input"] = test_data.apply(lambda x: f'question: {x["Question"]}  context: {x["Story"]}', axis=1)

    encoded_inputs = tokenizer.batch_encode_plus(
        test_data["input"].to_list(),
        return_tensors='pt',
        max_length=1024,
        truncation=True,
        padding=True
    )

    results = []
    with torch.no_grad():
        ########################### code changes ########################
        with torch.xpu.amp.autocast(enabled=True, dtype=torch.float16):
        ########################### code changes ########################
            for i in tqdm(range(encoded_inputs["input_ids"].shape[0]//size + 1)):
                payload = encoded_inputs["input_ids"][i*size:(i+1)*size].to("xpu")
                result = tokenizer.batch_decode(model.generate(payload, max_length=128), skip_special_tokens=True)
                results.extend(result)

    submission = pd.read_csv("../data/submission.csv")
    submission["Answer"] = results
    submission["Answer"] = submission["Answer"].apply(lambda x: x.strip())
    submission.to_csv("/tmp/submission.csv", index=False)
    submission = pd.read_csv("/tmp/submission.csv")

    submission["Answer"] = submission["Answer"].fillna("0")
    submission["Answer"] = submission["Answer"].astype(str)
    submission.to_csv("../submission.csv", index=False)

if __name__ == "__main__":
    main()


