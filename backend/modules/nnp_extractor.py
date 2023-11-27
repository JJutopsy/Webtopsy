from ratsnlp.nlpbook.ner import NERDeployArguments
from transformers import BertTokenizer
import torch
from transformers import BertConfig
from transformers import BertForTokenClassification
import json
import sqlite3
import time
import re
import string
from dotenv import load_dotenv
import os

load_dotenv()
class NERExtractor:
    def __init__(self, db_name):
        # Database connection
        self.conn = sqlite3.connect(db_name)
        self.korean_pattern = re.compile('[가-힣]+')
        self.MAX_TEXT_LENGTH = 100000

        # NER deployment arguments
        self.args = NERDeployArguments(
            pretrained_model_name="beomi/kcbert-base",
            downstream_model_dir=os.environ.get("NER"),
            max_seq_length=64,
        )

        # Load tokenizer
        self.tokenizer = BertTokenizer.from_pretrained(
            self.args.pretrained_model_name,
            do_lower_case=False,
        )

        # Load fine-tuned model checkpoint
        self.fine_tuned_model_ckpt = torch.load(
            self.args.downstream_model_checkpoint_fpath,
            map_location=torch.device("cpu")
        )

        # Load pretrained model configuration
        self.pretrained_model_config = BertConfig.from_pretrained(
            self.args.pretrained_model_name,
            num_labels=self.fine_tuned_model_ckpt['state_dict']['model.classifier.bias'].shape.numel(),
        )

        # Initialize the model
        self.model = BertForTokenClassification(self.pretrained_model_config)
        self.model.load_state_dict({k.replace("model.", ""): v for k, v in self.fine_tuned_model_ckpt['state_dict'].items()})
        self.model.eval()

        # Load and preprocess labels
        self.labels = [label.strip() for label in open(self.args.downstream_model_labelmap_fpath, "r").readlines()]
        self.id_to_label = self._map_labels()

    def _map_labels(self):
        id_to_label = {}
        for idx, label in enumerate(self.labels):
            if "PER" in label:
                label = "인명"
            elif "LOC" in label:
                label = "지명"
            elif "ORG" in label:
                label = "기관명"
            elif "DAT" in label:
                label = "날짜"
            elif "TIM" in label:
                label = "시간"
            elif "DUR" in label:
                label = "기간"
            elif "MNY" in label:
                label = "통화"
            elif "PNT" in label:
                label = "비율"
            elif "NOH" in label:
                label = "기타 수량표현"
            elif "POH" in label:
                label = "기타"
            else:
                label = label
            id_to_label[idx] = label
        return id_to_label

    def preprocess_text(self, text):
        # Text preprocessing function
        text = text.translate(str.maketrans("", "", string.punctuation))
        return text

    def inference_fn(self, sentence):
        try:
            inputs = self.tokenizer(
                [sentence],
                max_length=self.args.max_seq_length,
                padding="max_length",
                truncation=True,
            )
            with torch.no_grad():
                outputs = self.model(**{k: torch.tensor(v) for k, v in inputs.items()})
                probs = outputs.logits[0].softmax(dim=1)
                top_probs, preds = torch.topk(probs, dim=1, k=1)
                tokens = self.tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
                predicted_tags = [self.id_to_label[pred.item()] for pred in preds]
                result = []
                for token, predicted_tag, top_prob in zip(tokens, predicted_tags, top_probs):
                    if token not in [self.tokenizer.pad_token, self.tokenizer.cls_token, self.tokenizer.sep_token] and predicted_tag != "O":
                        token_result = {
                            "token": token,
                            "predicted_tag": predicted_tag,
                            "top_prob": str(round(top_prob[0].item(), 4)),
                        }
                        result.append(token_result)
            return {
                "result": result,
            }
        except UnicodeDecodeError:
            print(f"UTF-8 decoding error occurred with sentence: {sentence}. Skipping this sentence.")
            return None

    def merge(self, output):
        result_list = output['result']

        # 초기화
        current_tag = None
        current_string = ""
        result_strings = []

        # 문자열 합치기
        for token_info in result_list:
            token = token_info['token']
            predicted_tag = token_info['predicted_tag']

            # "##"이 없는 경우 새로운 문자열 시작
            if "##" not in token:
                if current_string:
                    result_strings.append(f"{current_string}_{current_tag}")
                current_string = token
                current_tag = predicted_tag
            else:
                # "##"이 있는 경우 앞 토큰과 predicted_tag를 비교하여 합치기
                if current_tag == predicted_tag:
                    current_string += token[2:]
                else:
                    result_strings.append(f"{current_string}_{current_tag}")
                    current_string = token[2:]
                    current_tag = predicted_tag

        # 마지막 문자열 추가
        if current_string:
            result_strings.append(f"{current_string}_{current_tag}")

        # "#" 제거 및 하나의 문자열로 합치기
        result_string = ",".join([s.replace("#", "") for s in result_strings])

        # 결과 출력
        return result_string

    def get_nnp(self, text):
        if not text.strip() or len(text) > self.MAX_TEXT_LENGTH:  # 공백 또는 길이가 너무 큰 경우 스킵
            return None
        
        # 한글이 존재하는 경우에만 키워드 추출 실행
        if self.korean_pattern.search(text):
            output = self.inference_fn(text)
            result = self.merge(output)
            return result
        else:
            return None

    def process_texts(self):
        # Process texts from the database
        cursor = self.conn.cursor()
        cursor.execute("SELECT plain_text FROM files")  # Modify table and column names accordingly
        texts = cursor.fetchall()

        total_texts = len(texts)
        MAX_TEXT_LENGTH = 100000

        for i, text in enumerate(texts):
            keywords = self.get_nnp(text[0])
            if keywords is not None:
                cursor.execute("UPDATE files SET NNP = ? WHERE plain_text = ?", (keywords, text[0]))

            progress_percent = (i + 1) / total_texts * 100
            print(f"Processed {i}/{total_texts} texts ({progress_percent:.2f}%)", end='\r')

        self.conn.commit()
        self.conn.close()