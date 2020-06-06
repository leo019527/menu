# -*-coding=UTF-8 -*-
import flask
import json
import codecs
import sys
import random

##############################
#                            #
#                            #
#      global settings       #
#                            #
#                            #
##############################


##############################
#                            #
#                            #
#      global variables      #
#                            #
#                            #
##############################
menuFile = "menu.txt"
server = flask.Flask(__name__)
# 存储菜单 type 0表示蔬菜，1表示荤菜
# 格式为{name:"xxx",type:"0", material:[{"name":"x1","count":1,"unit":"个"},{"name":"x1","count":2,"unit":"个"}],desc:""}
menus = []
# 材料清单 用于选择
materials = []


##############################
#                            #
#                            #
#        server              #
#                            #
#                            #
##############################
@server.route('/favicon.ico', methods=['get'])
def getFavicon():
    return ""


@server.route('/test', methods=['get'])
def test():
    test = flask.request.values.get('test')
    res = {"msg": test}
    return flask.jsonify(res)


@server.route('/addMenu', methods=['get'])
def addMenu():
    name = flask.request.values.get('name')
    materialLine = flask.request.values.get('materialLine')
    desc = flask.request.values.get('desc')
    mtype = flask.request.values.get('type')
    f = addMenua(name, materialLine, desc, mtype)
    if f:
        return flask.jsonify({"msg": "ok"})
    else:
        return flask.jsonify({"msg": u"菜单重复"})


@server.route('/getMenus', methods=['get'])
def getMenus():
    global menus
    return flask.jsonify({"result": menus})


@server.route('/getMaterial', methods=['get'])
def getMaterial():
    global materials
    return flask.jsonify({"result": materials})


@server.route('/getMeals', methods=['get'])
def getMeals():
    return flask.jsonify(randomWeek())


##############################
#                            #
#                            #s
#   data file processor      #
#                            #
#                            #
##############################
def readAll():
    global menuFile, menus, materials
    with codecs.open(menuFile, "r", "utf-8") as f:
        lines = f.readlines()
        for i in range(0, len(lines), 3):
            tmp = lines[i].replace("\n", "").split(" ")
            name = tmp[0]
            mType = tmp[1]
            materialLine = lines[i + 1].replace("\n", "")
            desc = lines[i + 2].replace("\n", "")
            menus.append(createMenu(name, materialLine, desc, mType))


# meterialLine: 鸡蛋,2,个.盐,1,克
def addMenua(name, materialLine, desc, mType):
    global menuFile, menus
    with codecs.open(menuFile, "a", "utf-8") as f:
        flag = False
        for i in menus:
            if i["name"].__eq__(name):
                flag = True
        if not flag:
            menus.append(createMenu(name, materialLine, desc, mType))
            f.write(name + " " + mType + "\n")
            f.write(materialLine + "\n")
            f.write(desc + "\n")
            return True
        return False


##############################
#                            #
#                            #
#          utils             #
#                            #
#                            #
##############################
def getMaterial(materialLine):
    global materials
    result = []
    m = materialLine.split(".")
    for material in m:
        [name, count, unit] = material.split(",")
        if name not in materials:
            materials.append(name)
        tmp = {
            "name": name,
            "count": count,
            "unit": unit,
        }
        result.append(tmp)
    return result


def createMenu(name, materialLine, desc, mType):
    m = getMaterial(materialLine)
    tmp = {
        "name": name,
        "type": mType,
        "material": m,
        "desc": desc,
    }
    return tmp


def randomWeek():
    meals = getAWeek()
    l = [meals["Monday"], meals["Tuesday"], meals["Wednesday"], meals["Thursday"], meals["Friday"]]
    m = getMaterialsFromMeals(l)
    return {
        "meals": meals,
        "material": m,
    }


# 格式为{name:"xxx",type:"0", material:[{"name":"x1","count":1,"unit":"个"},{"name":"x1","count":2,"unit":"个"}],desc:""}
def getMaterialsFromMeals(days):
    l = []
    for day in days:
        l.append(day["noon"]["meat"])
        l.append(day["evening"]["meat"])
        l.append(day["noon"]["vage"])
        l.append(day["evening"]["vage"])
    result = {}
    for i in l:
        for m in i["material"]:
            if m["name"] in result:
                result[m["name"]]["count"] += 1
            else:
                result[m["name"]] = {
                    "count": 1,
                    "unit": m["unit"],
                }
    return result


def getAWeek():
    return {
        "Monday": getADay(),
        "Tuesday": getADay(),
        "Wednesday": getADay(),
        "Thursday": getADay(),
        "Friday": getADay(),
    }


def getADay():
    return {
        "noon": getAMale(),
        "evening": getAMale(),
    }


def getAMale():
    return {
        "meat": getAMenu("1"),
        "vage": getAMenu("0"),
    }


# 0抽个素菜，1抽个荤菜
def getAMenu(mtype):
    global menus
    random.shuffle(menus)
    for m in menus:
        if m["type"].__eq__(mtype):
            return m


if __name__ == '__main__':
    readAll()
    server.run(port=80, host='0.0.0.0', debug=True)
