"""
eVault – Flask backend (DynamoDB + S3, dual‑region)
--------------------------------------------------
Env vars (see .env):
  DDB_REGION   – region for DynamoDB tables
  S3_REGION    – region where the bucket lives
  BUCKET       – S3 bucket name
"""

import os, uuid, hashlib, datetime
from flask import Flask, request, jsonify
import boto3
from boto3.dynamodb.conditions import Key
from dotenv import load_dotenv

load_dotenv()

# ─── configuration ─────────────────────────────────────────────
DDB_REGION = os.getenv("DDB_REGION", "ap-southeast-1")
S3_REGION  = os.getenv("S3_REGION",  "ap-southeast-1")
BUCKET     = os.getenv("BUCKET",     "evault-docs")

# DynamoDB (tables region)
ddb_sess = boto3.session.Session(region_name=DDB_REGION)
dynamodb = ddb_sess.resource("dynamodb")
tbl_docs = dynamodb.Table("Documents")
tbl_logs = dynamodb.Table("AuditLogs")

# S3 (bucket region)
s3 = boto3.session.Session(region_name=S3_REGION).client("s3")

# ─── helpers ───────────────────────────────────────────────────
def put_doc(item): tbl_docs.put_item(Item=item)
def put_log(item): tbl_logs.put_item(Item=item)

# ─── Flask app ─────────────────────────────────────────────────
app = Flask(__name__)

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "no file uploaded"}), 400

    owner = request.form.get("owner", "unknown")
    meta  = request.form.get("meta", "")

    data   = file.read()
    sha256 = hashlib.sha256(data).hexdigest()
    key    = f"{uuid.uuid4()}_{file.filename}"

    # store in S3
    s3.put_object(
        Bucket=BUCKET,
        Key=key,
        Body=data,
        ServerSideEncryption="AES256"
    )

    doc_id = str(uuid.uuid4())
    now    = datetime.datetime.utcnow().isoformat(timespec="seconds")

    put_doc({
        "docId": doc_id,
        "s3key": key,
        "hash": sha256,
        "owner": owner,
        "metadata": meta,
        "timestamp": now
    })
    put_log({
        "docId": doc_id,
        "timestamp": now,
        "action": "UPLOAD",
        "user": owner
    })

    return jsonify({"docId": doc_id}), 201

@app.route("/download/<doc_id>")
def download(doc_id):
    res = tbl_docs.get_item(Key={"docId": doc_id})
    if "Item" not in res:
        return jsonify({"error": "not found"}), 404

    item = res["Item"]
    url  = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": BUCKET, "Key": item["s3key"]},
        ExpiresIn=900)

    put_log({
        "docId": doc_id,
        "timestamp": datetime.datetime.utcnow().isoformat(timespec="seconds"),
        "action": "DOWNLOAD",
        "user": "viewer"
    })

    return jsonify({"url": url, "hash": item["hash"]})

@app.route("/logs/<doc_id>")
def logs(doc_id):
    resp = tbl_logs.query(
        KeyConditionExpression=Key("docId").eq(doc_id),
        ScanIndexForward=False)
    return jsonify(resp.get("Items", []))

# ─── NEW: latest N records without docId ───────────────────────
@app.route("/logs/all")
def logs_all():
    limit = int(request.args.get("limit", "100"))
    resp  = tbl_logs.scan(Limit=limit)
    items = resp.get("Items", [])
    items.sort(key=lambda x: x["timestamp"], reverse=True)
    return jsonify(items)

# ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(port=5000, debug=True)
