from flask import Flask, request, g, Response, send_from_directory
from flask_cors import CORS
from src.graph import GraphDB
from src import question_solve
import json
from json import dumps
from src.mysql import SqlDB

url = 'bolt://127.0.0.1:7687'
username = 'neo4j'
password = '123456'

sql = '''
    SELECT * FROM login WHERE name=%s
'''

app = Flask(__name__, template_folder='../CSKG-frontend', static_folder='../CSKG-frontend', static_url_path='')
# app = Flask(__name__, static_folder='./static',static_url_path='')
CORS(app)
apiPrefix = '/api/v1/'


@app.route('/')
def get_index():
    # return 'hello'
    return app.send_static_file('index.html')


# entity search  知识图谱搜索
@app.route(apiPrefix + 'search', methods=['POST'])
def get_search():
    data = request.get_data(as_text=True)
    new_data = data.replace('"', '')
    print('获取数据:', new_data)
    # res = {
    #     'code': 0,
    #     'data': data,
    #     'message': '测试数据'
    # }
    db = GraphDB(url, username, password)
    links, nodes = db.search_graph(new_data)
    db.close()
    # return res
    return Response(dumps({"nodes": nodes, 'links': links}),
                    mimetype="application/json")


# get whole graph
@app.route(apiPrefix + 'graph')
def get_graph():
    entitycls = ['Subject', 'Concept', 'Operation', 'Method']

    db = GraphDB(url, username, password)
    res, rel, test = db.get_graph()
    temp = []
    node = []
    count = 0
    for record in test:
        for path in record:
            # print(type(path))
            for node in path:
                # print(type(node))
                # print(node.nodes)
                source = db.serialize_node(node.nodes[0])
                target = db.serialize_node(node.nodes[1])
                # for item in node.nodes[0].labels:
                # print(tuple(node.nodes[0].labels)[0])
                temp.append({'source': source, 'target': target})
    print(temp)

    nodes = []
    rels = []
    # test = []
    i = 0
    for record in res:
        nodes.append({'id': record['id'], 'title': record[entitycls[0]], 'label': 'subj'})
        source = i
        i += 1
        for item in record['conc']:
            # print(item.id)         
            oper = {'id': item.id, 'title': item['title'], "label": "conc"}
            try:
                #    target = int(item['id'])
                target = nodes.index(oper)
            #    nodes.append(oper)
            except ValueError:
                nodes.append(oper)
                target = i
                i += 1
            # rels.append({'source':source, 'target':target})    

    # for r in rel:
    #     source = r['rel'].nodes[0]
    #     target = r['rel'].nodes[1]
    #     test.append({'source':source.id, 'target':target.id})
    # print(source)
    # print(test)

    db.close()
    return Response(dumps({"nodes": nodes, "links": temp}),
                    mimetype="application/json")


@app.route(apiPrefix + '/question', methods=['POST'])
def query():
    data = request.get_data(as_text=True)
    print(data)
    # question = request.form.to_dict().get("question", "")
    # question = '进程包含线程吗？'
    if data:
        answer, node = question_solve.Solve().query(data)
        # print(answer)
        # s = '包含'
        # for data in answer:
        #     s = s+str(data)+'，'
    else:
        answer = "Sorry, I can't understand what you say."

    print(answer)
    print(node)
    return Response(dumps({"answer": answer, 'node': node}),
                    mimetype="application/json")


# 读取json文件
@app.route(apiPrefix + '/whole')
def get_whole():
    # path = './src/records.json'
    # with open('./src/records.json','r',encoding='utf_8_sig')as f:
    # json_data = json.load(f)
    # print(json_data)
    return send_from_directory('./src', 'records_path.json')


@app.route(apiPrefix + '/sql_login', methods=['POST'])
def login():
    db = SqlDB()
    cursor = db.cursor
    username = (request.args['username'])
    password = (request.args['password'])
    cursor.execute(sql, username)
    a = cursor.fetchone()
    cursor.close()
    if a is None:
        print("用户不存在！")
        return Response(dumps({"code": "204"}),
                        mimetype="application/json")
    elif a[2] != password:
        print("密码错误！")
        return Response(dumps({"code": "203"}),
                        mimetype="application/json")
    else:
        print("成功登录！")
        return Response(dumps({"code": "200", "power": a[3]}),
                        mimetype="application/json")


@app.route(apiPrefix + '/sql_que')
def get_question():
    db = SqlDB()
    result = db.getdata()
    print(result)
    return Response(dumps({"result": result}),
                    mimetype="application/json")


@app.route(apiPrefix + '/node', methods=['POST'])
def get_node():
    data = request.get_data(as_text=True)
    id = data.replace('"', '')
    print('获取数据:', data)
    db = GraphDB(url, username, password)
    res = db.search_node(int(id))
    return Response(dumps({"node": res[0]}),
                    mimetype="application/json")


if __name__ == '__main__':
    app.run(debug=True, port=8080)
