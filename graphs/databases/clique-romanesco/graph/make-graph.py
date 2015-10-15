import bson.json_util
from bson.objectid import ObjectId
import sys


def emit_node(label):
    oid = ObjectId()
    print bson.json_util.dumps({"_id": oid,
                                "type": "node",
                                "data": {"label": label}})
    return oid


def emit_link(a, b):
    oid = ObjectId()
    print bson.json_util.dumps({"_id": oid,
                                "type": "link",
                                "source": a,
                                "target": b,
                                "data": {"bidir": True}})

    print bson.json_util.dumps({"_id": ObjectId(),
                                "type": "link",
                                "source": b,
                                "target": a,
                                "data": {"bidir": True,
                                         "reference": oid}})


def main():
    a = emit_node("a")
    b = emit_node("b")
    c = emit_node("c")
    d = emit_node("d")
    e = emit_node("e")

    emit_link(a, b)
    emit_link(b, c)
    emit_link(c, d)
    emit_link(d, e)
    emit_link(e, a)

    emit_link(a, d)

    emit_link(b, d)

    emit_link(c, e)
    emit_link(c, a)

    emit_link(e, b)


if __name__ == "__main__":
    sys.exit(main())
