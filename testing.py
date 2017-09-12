from flask import Flask, render_template
from fabric import tasks
from fabric.api import settings,hide,env,run
import time

app = Flask(__name__)

env.hosts = ['bioinfo@10.182.131.21:22']
env.passwords = {'bioinfo@10.182.131.21:22':'b101nf0'}


def test():
        test = run('sleep 5 | echo "hello"').stdout.split("\r\n")
        return test


@app.route("/")
def hello():
    #task = tasks.execute(test,host='bioinfo@10.182.131.21:22')["bioinfo@10.182.131.21:22"]

    return render_template("test.html")

@app.route("/check", methods=['GET','POST'])
def check_status():
    print "hello"
    time.sleep(2)
    print "done"
    return "success"



if __name__ == "__main__":
    app.run(debug=True, host='10.182.131.21', port=5005)

