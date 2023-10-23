from  transformers  import  AutoTokenizer, AutoModelForSeq2SeqLM
import torch

try:
    ############# code changes ###############
    import intel_extension_for_pytorch as ipex
    ############# code changes ###############
    OPTIMIZATION_AVAILABLE = True
except:
    print("Please install intel extenstion for pytorch if using Intel GPUs")
    OPTIMIZATION_AVAILABLE = False



class Model:
    def __init__(self, model_path=None, tokenizer_path=None) -> None:
        self.model_path = model_path
        self.tokenizer_path = tokenizer_path
        self.model_ready = False

    def prepare_model(self):
        try:
            if torch.xpu.is_available():
                device = "xpu"
        except:
            if torch.cuda.is_available():
                device = "cuda"
            else:
                device = "cpu"
        
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_path)
        self.tokenizer =  AutoTokenizer.from_pretrained(self.tokenizer_path)
        self.model.to(device)
        self.model.eval()

        if device == "xpu" and OPTIMIZATION_AVAILABLE:
            self.model = ipex.optimize(self.model)
        
        self.model_ready = True
        print("Model laoded and is ready to be used")
    
    def __call__(self, context, question, max_length=256) -> str:
        
        if not self.model_ready:
            self.prepare_model()
        
        formatted_string = f'question: {question}  context: {context}'
        input_tokens = self.tokenizer(formatted_string, return_tensors="pt")
        with torch.no_grad():
            if OPTIMIZATION_AVAILABLE:
                ############# code changes ###############
                with torch.xpu.amp.autocast(enabled=True, dtype=torch.float16):
                ############# code changes ###############    
                    ouput_tokens = self.model.generate(**input_tokens, max_length=max_length)
            else:
                ouput_tokens = self.model.generate(**input_tokens, max_length=max_length)
        
        answer = self.tokenizer.decode(ouput_tokens[0], skip_special_tokens=True)
        return answer
        