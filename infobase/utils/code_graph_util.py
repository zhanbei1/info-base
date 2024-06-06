#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
=================================================
@Project -> File   ：infobase -> code_graph_util.py
@IDE    ：PyCharm
@Author ：Desmond.zhan
@Date   ：2023/12/10 14:42
@Desc   ：将代码的图形结构保存到图形数据库中
==================================================
"""
import ujson
from py2neo import Graph, Node, Relationship, NodeMatcher


def delete_all():
    graph = Graph("neo4j://114.55.34.219:7687")
    graph.delete_all()


def flatten_dict(d: dict) -> dict:
    result = {}
    for key, value in d.items():
        if isinstance(value, dict):
            flattened_value = flatten_dict(value)
            for sub_key, sub_value in flattened_value.items():
                result[key + '.' + sub_key] = sub_value
        else:
            result[key] = value
    return result


def lsif_to_graph(lsif_file_path: str = None, graph_db_url: str = None, graph_db_name: str = None):
    """
    将lsif文件转换为图结构
    :param lsif_file_path: lsif文件路径
    :param graph_db_url: 数据库连接地址
    :param graph_db_name: 数据库名称
    :return:
    """
    graph = Graph("neo4j://114.55.34.219:7687")
    with open("/Users/zhanbei/PycharmProjects/infobase/sources/doop-server.lsif", "r") as f:
        for line in f:
            code_info_dict: dict = ujson.loads(line)
            tx = graph.begin()
            try:
                # 实体点
                if code_info_dict["type"] == "vertex":
                    label: str = code_info_dict["label"]
                    customer_id: int = code_info_dict["id"]
                    code_info_dict.pop("label")
                    code_info_dict.pop("id")
                    code_info_dict["customer_id"] = customer_id
                    # 将map拍平
                    code_info_dict = flatten_dict(code_info_dict)
                    node: Node = Node(label, **code_info_dict)
                    graph.create(node)
                # 边
                elif code_info_dict["type"] == "edge":
                    in_v = code_info_dict["inV"] if code_info_dict.get("inV") is not None else code_info_dict.get("inVs")
                    ou_v = code_info_dict["outV"] if code_info_dict.get("outV") is not None else code_info_dict.get("outVs")
                    label = code_info_dict.get("label")
                    customer_id: int = code_info_dict["id"]

                    code_info_dict.pop("id")
                    code_info_dict.pop("inV") if code_info_dict.get("inV") is not None else None
                    code_info_dict.pop("inVs") if code_info_dict.get("inVs") is not None else None
                    code_info_dict.pop("outV") if code_info_dict.get("outV") is not None else None
                    code_info_dict.pop("outVs") if code_info_dict.get("outVs") is not None else None
                    code_info_dict.pop("label")

                    code_info_dict["customer_id"] = customer_id
                    node_matcher = NodeMatcher(graph)
                    in_node: Node = node_matcher.match().where(customer_id=in_v).first()
                    out_node: Node = node_matcher.match().where(customer_id=ou_v).first()
                    relation: Relationship = Relationship(in_node, label, out_node, **code_info_dict)
                    graph.create(relation)
                graph.commit(tx)
            except Exception as e:
                print(e)
                print(code_info_dict)
                graph.rollback(tx)


if __name__ == '__main__':
    lsif_to_graph()
    # delete_all()
