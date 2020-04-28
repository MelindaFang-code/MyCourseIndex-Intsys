from sklearn.feature_extraction.text import TfidfVectorizer
from app.utils import toke
import boto3
import os
import json
import numpy as np
from flask import Flask
app = Flask(__name__)

if os.environ.get("deployment", False):
    app.config.from_pyfile('/etc/cs4300-volume-cfg/cs4300app.cfg')
else:
    app.config.from_pyfile(os.path.join(
        os.path.join(os.getcwd(), "secrets"), "cs4300app.cfg"))

tokenizer = toke.tokenized_already
key = app.config["AWS_ACCESS"]
secret = app.config["AWS_SECRET"]

# P03Data.json
s3 = boto3.client('s3', aws_access_key_id=key, aws_secret_access_key=secret)
s3.download_file('cs4300-data-models', 'P03Data_mod.json', 'P03Data.json')

# S3 JSON Format:
# { "CS4300": {"Piazza": {PostID: content, PostID2: content2}, "Textbook": {DocId: content, DocID2: content2} } }
with open("P03Data.json") as f:
    fromS3 = json.load(f)

docVecDictionary = {}
courseDocDictionary = {}
sourceDictionary = {}
# courseRawDataDictionary = {}
# courseURLDictionary = {}
# courseTypeOfDocDictionary = {}
# courseDocIDNameDictionary = {}

for course in fromS3:
    vec = TfidfVectorizer(tokenizer=tokenizer, lowercase=False)
    piazza_documents = []
    other_documents = []
    src = []
    piazza_rawDocs = []
    other_rawDocs = []
    for source in fromS3[course]:
        for content in fromS3[course][source]:
            # for final in fromS3[course][source][content]:
                #pre is type, first is text, second is tokenized, third is url
            if source == "Piazza":
                src.append(1)
                piazza_documents.append(fromS3[course][source][content].pop("tokenized"))
                piazza_rawDocs.append(fromS3[course][source][content])

            else:
                src.append(0.2) # Warning, magic number
                other_documents.append(fromS3[course][source][content].pop("tokenized"))
                other_rawDocs.append(fromS3[course][source][content])


    # elif course == "INFO 1998"
    sourceDictionary[course] = np.array(src)
    docVecDictionary[course] = (vec, vec.fit_transform(piazza_documents).toarray(), vec.fit_transform(other_documents).toarray())
    courseDocDictionary[course] = {}
    courseDocDictionary[course]["Piazza"] = np.array(piazza_rawDocs)
    courseDocDictionary[course]["Resource"] = np.array(other_rawDocs)
