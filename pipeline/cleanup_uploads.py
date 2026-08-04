"""每日收尾：清除云端 uploads 集合中「已分析」记录（status=done/rejected_irrelevant），
保留 pending（待处理）与 _init 占位文档。分析结果已写回 Obsidian（唯一事实源），云端仅中转。
用法：python cleanup_uploads.py   （可加 --dry 先看统计不删）
"""
import subprocess, json, sys, argparse

TCB = r"C:/Users/admin/.workbuddy/binaries/node/workspace/node_modules/@cloudbase/cli/bin/tcb"
ENV = "cloud1-d6gvwf6q09e5e6577"

def run(args, timeout=60):
    r = subprocess.run(["node", TCB, *args], capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout, r.stderr

def parse(out):
    i = out.find("{")
    return json.loads(out[i:])

def query_all():
    q = json.dumps([{"TableName": "uploads", "CommandType": "QUERY",
                     "Command": json.dumps({"find": "uploads", "limit": 200,
                                             "projection": {"_id": 1, "status": 1, "subject": 1, "createdAt": 1}})}])
    rc, out, err = run(["db", "nosql", "execute", "-c", q, "-e", ENV, "--json"])
    if rc != 0:
        raise RuntimeError(f"query fail rc={rc} {err[-300:]}")
    return parse(out)["data"]["results"][0]

def delete_docs(qfilter, limit=0):
    # CloudBase NoSQL DELETE: deletes[].limit 只能 0(全部) 或 1(单条)
    cmd = {"delete": "uploads", "deletes": [{"q": qfilter, "limit": limit}]}
    full = json.dumps([{"TableName": "uploads", "CommandType": "DELETE", "Command": json.dumps(cmd)}])
    rc, out, err = run(["db", "nosql", "execute", "-c", full, "-e", ENV, "--json"], timeout=90)
    return rc, out, err

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true", help="只统计不删除")
    args = ap.parse_args()

    docs = query_all()
    from collections import Counter
    c = Counter(d.get("status") for d in docs)
    print(f"uploads 总数: {len(docs)} | 状态分布: {dict(c)}")

    to_del = [d for d in docs if d.get("status") in ("done", "rejected_irrelevant")]
    keep = [d for d in docs if d.get("status") not in ("done", "rejected_irrelevant")]
    print(f"将清除(已分析): {len(to_del)} 条 | 保留: {len(keep)} 条 "
          f"({[ (k.get('_id'), k.get('status')) for k in keep ]})")

    if args.dry or not to_del:
        print("[dry] 未执行删除")
        return

    rc, out, err = delete_docs({"status": {"$in": ["done", "rejected_irrelevant"]}})
    print(f"DELETE rc={rc}")
    print("out:", (out or "")[-300:])
    print("err:", (err or "")[-200:])

    # 验证
    docs2 = query_all()
    c2 = Counter(d.get("status") for d in docs2)
    print(f"删除后 uploads 总数: {len(docs2)} | 状态分布: {dict(c2)}")

if __name__ == "__main__":
    main()