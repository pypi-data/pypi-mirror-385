import sys, os
import json
import jsonlines
import pickle
from typing import List, Any, Dict, Union, Generator

def save_json(data:dict, loc:str) -> None:
    with open(loc, "w") as f0:
        json.dump(data, f0)

def load_json(loc:str) -> dict:
    with open(loc,"r") as f0:
        return json.load(f0)

def load_pickle(loc:str) -> Any:
    with open(loc, "rb") as f0:
        return pickle.load(f0)
    
def save_pickle(obj:Any, loc:str)->None:
    with open(loc, "wb") as f0:
        pickle.dump(obj,f0)
    

def save_text(s:str, loc:str) -> None:
    with open(loc, "w") as f0:
        f0.write(s)

def load_text(loc:str) -> str:
    with open(loc,"r") as f0:
        return f0.read()
    
def save_jsonl(data:Union[List[Dict[str,Any]],Dict[str,Any]], loc:str) -> None:

    if isinstance(data, list):
        with jsonlines.open(loc, 'w') as writer:
            writer.write_all(data)
    elif isinstance(data, dict):
        with open(loc, 'a') as f:
            f.write(json.dumps(data) + '\n')
    else:
        raise NotImplementedError()

def load_jsonl(loc:str) -> List[Dict[str,Any]]:
    with open(loc, 'r', encoding='utf-8') as f:
        records = [json.loads(line) for line in f if line.strip()]

    return records

def load_jsonl_generator(loc:str) -> Generator[Dict[str, Any], None, None]:
    with open(loc, 'r', encoding='utf-8') as f:
        for line in f :
            if line.strip():
                yield json.loads(line)




def file_exist(*args) -> bool:
    return os.path.exists(os.path.join(*args))
    