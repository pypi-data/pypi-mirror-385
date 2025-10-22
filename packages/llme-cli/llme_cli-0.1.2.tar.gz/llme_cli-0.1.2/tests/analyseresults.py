#!/usr/bin/env python3

import csv
from tabulate import tabulate

def inccell(rowid, colid, mat):
    if rowid not in mat:
        mat[rowid] = {}
    matrow = mat[rowid]
    if colid not in matrow:
        matrow[colid] = 1
    else:
        matrow[colid] += 1

links = []
linksmap = {}
linkstag = {}
def getlink(what, url):
    if url in linksmap:
        tag = linksmap[url]["tag"]
    else:
        tag = url.split('/')[-1][0:2]
        if tag in linkstag:
            n = linkstag[tag] + 1
            linkstag[tag] = n
        else:
            n = linkstag[tag] = 1
        tag = tag + str(n)
        link = {"tag": tag, "what": what, "url": url}
        links.append(link)
        linksmap[url] = link
    return f"[{what}][{tag}]"

def linkmodel(model):
    base = model.split(":")[0]
    if '/' in base:
        return getlink(model, f"https://huggingface.co/{base}")
    else:
        return getlink(model, f"https://ollama.com/library/{base}")

def linksuite(suite):
    return getlink(suite, f"tests/{suite}.sh")

model_results = {}
def inc_model_results(model, result):
    inccell(model, result, model_results)

model_suites = {}
total_model_suites = {}
def inc_model_suites(model, suite):
    inccell(model, suite, model_suites)

suite_results = {}
def inc_suite_results(suite, result):
    inccell(suite, result, suite_results)

test_results = {}
def inc_test_results(test, result):
    inccell(test, result, test_results)

def get(mat, rowid, colid):
    return mat.get(rowid, {}).get(colid, 0)


def color(rate):
    colors = "💀🔴🟠🟡🟢👑"
    if rate == 0:
        return colors[0]
    if rate < 15:
        return colors[1]
    if rate < 50:
        return colors[2]
    if rate < 85:
        return colors[3]
    if rate < 100:
        return colors[4]
    else:
        return colors[5]


def print_mat(mat, f):
    table = []
    headers = {}
    entriees = {}
    for rowid in mat:
        for colid in mat[rowid]:
            v = mat[rowid][colid]
            if colid not in headers:
                headers[colid] = v
            else:
                headers[colid] += v
    for rowid in reversed(sortrow(mat)):
        if mat is model_results:
            title = linkmodel(rowid)
        elif mat is suite_results:
            title = linksuite(rowid)
        elif mat is test_results:
            s, t = rowid.split(' ', 1)
            title = f"{linksuite(s)} {t}"
        else:
            title = rowid
        total=0
        for colid in mat[rowid]:
            total += mat[rowid][colid]
        rate = 100.0 * get(mat, rowid, "PASS") / total
        tablerow = [f"{color(rate)} {title}"]
        table.append(tablerow)
        for colid in ['PASS', 'ALMOST', 'FAIL', 'ERROR', 'TIMEOUT']:
            n = get(mat, rowid, colid)
            if n == 0:
                tablerow.append("0")
            else:
                tablerow.append("%d (%.2f%%)" % (n, 100.0*n/total))
        tablerow.append(total)
    f.write(tabulate(table, headers=['Model', 'PASS', 'ALMOST', 'FAIL', 'ERROR', 'TIMEOUT', 'Total'], tablefmt="pipe"))
    f.write("\n")


def print_model_suites(f):
    table = []
    suites = list(reversed(sortrow(suite_results)))
    for rowid in reversed(sortrow(model_results)):
        tablerow = [linkmodel(rowid)]
        table.append(tablerow)
        for colid in suites:
            n = get(model_suites, rowid, colid)
            t = get(total_model_suites, rowid, colid)
            p = 100.0 * n / t
            if n == 0:
                tablerow.append(f"{color(0)} 0/{t}")
            else:
                tablerow.append("%s %d/%d (%.2f%%)" % (color(p), n, t, p))
    titles = [linksuite(s) for s in suites]
    titles.insert(0, "Models")
    f.write(tabulate(table, headers=(titles), tablefmt="pipe"))
    f.write("\n")


def scorerow(row):
    scores = {"PASS": 1000, "ALMOST": 10, "FAIL": 1, "ERROR": 0, "TIMEOUT": 1}
    score = 0
    for colid in row:
        score += scores.get(colid,0) * row[colid]
    return score


def sortrow(mat):
    res = list(mat)
    return sorted(res, key=lambda x: scorerow(mat[x]))
    return res

def main():
    with open('logs/results.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader) # skip header
        for row in reader:
            inc_model_results(row[3], row[4])
            inc_suite_results(row[0], row[4])
            inc_test_results(row[0]+" "+row[1], row[4])
            inccell(row[3], row[0], total_model_suites)
            if row[4] == "PASS":
                inc_model_suites(row[3], row[0])

    with open("benchmark.md", 'r') as f:
        results = f.read()

    cut = "\n<!-- the contents bellow this line are generated -->\n"
    head = results.split(cut, 1)[0]
    print(len(head),len(results))

    with open("benchmark.md", 'w') as f:

        f.write(head)
        f.write(cut)

        f.write("\n")
        f.write(f"* {len(model_results)} models\n")
        f.write(f"* {len(suite_results)} testsuites\n")
        f.write(f"* {len(test_results)} tests\n")

        f.write("\n## Results by models\n\n")
        print_mat(model_results, f)

        f.write("\n## Testsuites by models\n\n")
        print_model_suites(f)

        f.write("\n## Results by testsuites\n\n")
        print_mat(suite_results, f)

        f.write("\n## Results by tests\n\n")
        print_mat(test_results, f)

        f.write("\n\n")
        for link in links:
            f.write(f"  [{link["tag"]}]: {link["url"]}\n")

if __name__ == "__main__":
    main()
