# -------------------------------------------------------------------
# Copyright 2021 Virtex authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied. See the License for the specific language governing
# permissions and limitations under the License.
# -------------------------------------------------------------------
import os

import torch
from transformers.models.bert import BertModel
from transformers.models.bert import BertTokenizer

from virtex import RequestHandler, http_server
from virtex.serial import encode_pickle


max_batch_size = int(os.getenv('MAX_BATCH_SIZE', 128))
max_seq_len = int(os.getenv('MAX_SEQUENCE_LENGTH', 12))
max_time_on_queue = float(os.getenv('MAX_TIME_ON_QUEUE', 0.01))
metrics_interval = float(os.getenv('METRICS_INTERVAL', 0.005))


class BertComputation(RequestHandler):

    """
    Request handler that computes embeddings on english sentences
    """

    enable_cuda = True if torch.cuda.is_available() else False
    CLS = '[CLS]'
    SEP = '[SEP]'
    MSK = '[MASK]'
    pretrained_weights = 'bert-base-uncased'
    tokenizer = BertTokenizer.from_pretrained(pretrained_weights)
    model = BertModel.from_pretrained(pretrained_weights)
    if enable_cuda:
        model.cuda(torch.device('cuda'))

    def process_request(self, data):
        tokens = []
        mask_ids = []
        seg_ids = []
        seq_len = 0
        for txt in data:
            utt = txt.strip().lower()
            toks = self.tokenizer.tokenize(utt)
            if len(toks) > max_seq_len - 2:
                toks = toks[:max_seq_len - 2]
            toks.insert(0, self.CLS)
            toks.insert(-1, self.SEP)
            seq_len = max(len(toks), seq_len)
            mask_ids.append([1] * len(toks) + [0] * (seq_len - len(toks)))
            seg_ids.append([0] * seq_len)
            tokens.append(toks + [self.MSK] * (seq_len - len(toks)))
        input_ids = []
        for i in range(len(tokens)):
            for _ in range(seq_len - len(tokens[i])):
                tokens[i].append(self.MSK)
                mask_ids[i].append(0)
                seg_ids[i].append(0)
            input_ids.append(
                self.tokenizer.convert_tokens_to_ids(tokens[i])
            )
        return (torch.tensor(input_ids),
                torch.tensor(mask_ids),
                torch.tensor(seg_ids))

    def run_inference(self, model_input):
        if self.enable_cuda:
            input_ids, mask_ids, seg_ids = [x.to('cuda') for x in model_input]
        else:
            input_ids, mask_ids, seg_ids = model_input
        cls_emb = self.model.forward(
            input_ids=input_ids,
            attention_mask=mask_ids,
            token_type_ids=seg_ids)[1]
        return cls_emb

    def process_response(self, model_output_item):
        return encode_pickle(model_output_item.cpu().detach().numpy())


# Embed the computation into a Virtex http server
app = http_server(
    name='bert_embedding_service',
    handler=BertComputation(),
    max_batch_size=max_batch_size,
    max_time_on_queue=max_time_on_queue,
    metrics_host='http://0.0.0.0',
    metrics_port=9091,
    metrics_mode='push',
    metrics_interval=metrics_interval
)
