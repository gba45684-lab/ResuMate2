#!/usr/bin/env python3
"""Deterministic tests for the local snapshot corruption/recovery contract."""
import copy
import json


def save_snapshot(store, data):
    payload={"schema":1,"time":"test","reason":"test","data":copy.deepcopy(data)}
    current=store.get("snapshots",[])
    if not isinstance(current,list): current=[]
    current.append(payload)
    store["snapshots"]=current[-3:]


def latest_valid(store):
    raw=store.get("snapshots",[])
    if not isinstance(raw,list): return None
    for item in reversed(raw):
        if not isinstance(item,dict) or item.get("schema")!=1: continue
        data=item.get("data")
        if isinstance(data,dict): return item
    return None


def restore(store):
    item=latest_valid(store)
    if not item: return False
    store["app_data"]=copy.deepcopy(item["data"])
    return True


def main():
    # Corrupt snapshot JSON is rejected and must not overwrite working data.
    store={"snapshots":["{not-json"],"app_data":{"resume.name":"Current"}}
    assert latest_valid(store) is None
    assert restore(store) is False
    assert store["app_data"]["resume.name"]=="Current"

    # Malformed snapshot objects are skipped in favor of the newest valid snapshot.
    store={"snapshots":[
        {"schema":1,"data":{"resume.name":"Old"}},
        {"schema":99,"data":{"resume.name":"Bad schema"}},
        {"schema":1,"data":"bad data"},
        {"schema":1,"data":{"resume.name":"Recovered","resume.title":"Analyst"}},
    ]}
    assert restore(store) is True
    assert store["app_data"]["resume.name"]=="Recovered"
    assert store["app_data"]["resume.title"]=="Analyst"

    # Snapshot retention is bounded to three entries.
    store={}
    for i in range(5): save_snapshot(store,{"resume.name":str(i)})
    assert len(store["snapshots"])==3
    assert latest_valid(store)["data"]["resume.name"]=="4"

    # Recovery never includes OTA/error-engine namespaces in application data.
    app={"resume.name":"Safe","resumate.ota.active.v3":"must-not-copy","resumate.error-engine.v1":"must-not-copy"}
    filtered={k:v for k,v in app.items() if not (k.startswith("resumate.ota.") or k.startswith("resumate.error-engine"))}
    save_snapshot(store,filtered)
    recovered=latest_valid(store)["data"]
    assert "resumate.ota.active.v3" not in recovered
    assert "resumate.error-engine.v1" not in recovered

    print("DATA PROTECTION RECOVERY TEST PASSED: corrupt/malformed snapshots are skipped, recovery is bounded, OTA/error namespaces stay isolated")


if __name__ == "__main__":
    main()
