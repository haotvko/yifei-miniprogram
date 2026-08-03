# -*- coding: utf-8 -*-
"""本地管道 <-> 微信云开发 的同步层。
依赖：pip install requests pyyaml
凭证：pipeline/config.json（已被 .gitignore 忽略，绝不入 git），字段 appid / secret / env。
所有云数据库操作走微信云开发 HTTP API（databasequery / databaseupdate / batchdownloadfile / batchdeletefile）。
"""
import json
import time
import requests

TOKEN_URL = "https://api.weixin.qq.com/cgi-bin/token"
API = "https://api.weixin.qq.com/tcb"


class CloudSync:
    def __init__(self, appid, secret, env, dry_run=False):
        self.appid = appid
        self.secret = secret
        self.env = env
        self.dry_run = dry_run
        self._token = None
        self._exp = 0

    # ---------- 基础 ----------
    def _access_token(self):
        if self._token and time.time() < self._exp:
            return self._token
        r = requests.get(TOKEN_URL, params={
            "grant_type": "client_credential",
            "appid": self.appid,
            "secret": self.secret
        }, timeout=10).json()
        if "access_token" not in r:
            raise RuntimeError("获取 access_token 失败: " + str(r))
        self._token = r["access_token"]
        self._exp = time.time() + r.get("expires_in", 7200) - 300
        return self._token

    def _post(self, endpoint, query=None, payload=None):
        token = self._access_token()
        body = {"env": self.env}
        if query is not None:
            body["query"] = query
        if payload is not None:
            body.update(payload)
        return requests.post(f"{API}/{endpoint}?access_token={token}",
                             json=body, timeout=15).json()

    # ---------- 快照 ----------
    def push_snapshot(self, snap):
        query = "db.collection('snapshot').doc('current').set({data:%s})" % json.dumps(snap, ensure_ascii=False)
        if self.dry_run:
            with open("snapshot.push.json", "w", encoding="utf-8") as f:
                json.dump(snap, f, ensure_ascii=False, indent=2)
            return {"dry_run": True}
        return self._post("databaseupdate", query=query)

    # ---------- uploads 表 ----------
    def pull_pending(self):
        query = "db.collection('uploads').where({status:'pending'}).limit(100).get()"
        if self.dry_run:
            return {"data": []}
        return self._post("databasequery", query=query)

    def set_upload_status(self, doc_id, status, extra=None):
        extra = extra or {}
        inner = "status:'%s', analyzedAt:new Date()" % status
        if extra:
            inner += "," + ",".join("%s:%s" % (k, json.dumps(v, ensure_ascii=False)) for k, v in extra.items())
        query = "db.collection('uploads').doc('%s').update({data:{%s}})" % (doc_id, inner)
        if self.dry_run:
            return {"dry_run": True, "doc_id": doc_id, "status": status}
        return self._post("databaseupdate", query=query)

    # ---------- 云存储（原图清理用） ----------
    def download_file(self, fileID):
        if self.dry_run:
            return None
        r = self._post("batchdownloadfile", payload={"file_list": [{"fileid": fileID, "max_age": 7200}]})
        fl = (r.get("file_list") or [])
        if not fl or not fl[0].get("download_url"):
            return None
        return requests.get(fl[0]["download_url"], timeout=20).content

    def delete_file(self, fileID):
        if self.dry_run or not fileID:
            return {"dry_run": True}
        return self._post("batchdeletefile", payload={"fileid_list": [fileID]})
