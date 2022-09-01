import time
from web3 import Web3
import configparser
from flask import Flask, render_template,request
from web3.middleware import geth_poa_middleware
from MyQR import myqr
from flask_basicauth import BasicAuth

app = Flask(__name__)
app.config['BASIC_AUTH_USERNAME']='security'
app.config['BASIC_AUTH_PASSWORD'] = '123456'
app.config['BASIC_AUTH_FORCE'] = True
basic_auth = BasicAuth(app)
@app.route('/')
def index():
    w3 = getweb3Object()
    config = configinit()
    config.read('config.ini')
    network = config.get("NETWORK","network")
    if network == "BNBSmartChain":
        token = "BNB"
    elif network == "Polygon":
        token = "MATIC"
    elif network == "Ethereum":
        token = "ETH"
    elif network == "Fantom":
        token = "FTM"
    elif network == "AVAX-C":
        token = "AVAX"
    elif network == "Optimism":
        token = "ETH"
    elif network == "ArbitrumOne":
        token = "ETH"
    else:
        token = "网络设置错误"
    #rpc = config.get("RPC","rpc")
    privateKey = config.get('ACCOUNT','privateKey')
    privateKey2 = privateKey[:10]+"*"*46+privateKey[-10:]#展示在web界面的私钥，模糊处理
    to = config.get('ACCOUNT','to')
    contractAddr = config.get('CONTRACT','contractAddr')
    contractAbi = config.get('CONTRACT','contractAbi')
    account = w3.eth.account.from_key(privateKey)
    addr = account.address
    addrbalance = w3.fromWei(w3.eth.getBalance(addr),'ether')
    tokenDecimals = getDecimals(contractAddr,contractAbi)
    tokenName = getTokenName(contractAddr,contractAbi)
    tokenBalance = '{:.10f}'.format(getBalance(contractAddr,contractAbi,addr)/10**tokenDecimals)
    myqr.run(words=addr,save_dir='static/image')
    return render_template('index.html',network = network,privateKey2 = privateKey2,to = to,contractAddr = contractAddr,contractAbi=contractAbi,tokenName = tokenName,tokenBalance = tokenBalance,addr = addr,token = token,addrbalance= addrbalance)
@app.route('/edit',methods = ['POST', 'GET'])

def edit():
    if request.method == 'GET':
        return render_template('/edit.html')
    if request.method == 'POST':
        config = configinit()
        config.read('config.ini')
        network = request.form['network']
        privateKey = request.form['privateKey']
        to = request.form['to']
        contractAddr = request.form['contractAddr']
        contractAbi = request.form['contractAbi']
    if network!="":
        if network == "BNBSmartChain":
            config['NETWORK']['network'] = "BNBSmartChain"
        if network == "Polygon":
            config['NETWORK']['network'] = "Polygon"
        if network == "Ethereum":
            config['NETWORK']['network'] = "Ethereum"
        if network == "AVAX-C":
            config['NETWORK']['network'] = "AVAX-C"
        if network == "Fantom":
            config['NETWORK']['network'] = "Fantom"
        if network == "Optimism":
            config['NETWORK']['network'] = "Optimism"
        if network == "ArbitrumOne":
            config['NETWORK']['network'] = "ArbitrumOne"
    else:
        print("rpc不变")

    if privateKey!="":
        config['ACCOUNT']['privateKey'] = privateKey
        with open('config.ini', mode='w') as fp:
            config.write(fp)
    else:
        print("privateKey不变")
    if to!="":
        config['ACCOUNT']['to'] = to
        with open('config.ini', mode='w') as fp:
            config.write(fp)
    else:
        print("to不变")
    if contractAddr!="":
        config['CONTRACT']['contractAddr'] = contractAddr
    else:
        print("contractAddr不变")
    if contractAbi!="":
        config['CONTRACT']['contractAbi'] = contractAbi
    else:
        print("contractAbi不变")
    if network == "":
        temprpc = config.get("RPC",config.get("NETWORK",'network'))
    else:
        temprpc = config.get("RPC", network)
    print(temprpc)
    tempw3 = Web3(Web3.HTTPProvider(temprpc))
    if contractAddr=="":
        tempcontractAddr = config.get("CONTRACT","contractAddr")
    else:
        tempcontractAddr = contractAddr
    if contractAbi=="":
        tempcontractAbi = config.get("CONTRACT","contractAbi")
    else:
        tempcontractAbi = contractAbi

    tempcontractAddr = Web3.toChecksumAddress(tempcontractAddr)
    tempcontractObj = tempw3.eth.contract(address=tempcontractAddr, abi=tempcontractAbi)
    try:
        print(1)
        tempcontractObj.functions.symbol().call()
        with open('config.ini', mode='w') as fp:
            config.write(fp)
    except:
        print(222)
        return '''<html>
        <script>alert("修改失败，请检查网络和合约地址是否匹配！")</script>
        <meta http-equiv="refresh" content="0; url= "edit" />
        </html>
        '''
    return '''
    <script type="text/javascript" src="static/jquery/jquery-3.6.0.min.js"></script>
    <script type="text/javascript">
function moven(){
var success =confirm("修改成功！")
  if(success){
  window.location ="/"
  }
}
setTimeout(moven,1000);
</script>
    '''
@app.route('/testFakeDeposit')
def testFakeDeposit():
    config = configinit()
    config.read('config.ini')
    privateKey = config['ACCOUNT']['privateKey']
    to = config['ACCOUNT']['to']
    contractAddr = config['CONTRACT']['contractAddr']
    contractAbi = config['CONTRACT']['contractAbi']
    testResult = fakeDepositTest(contractAddr,contractAbi,privateKey,to)
    return render_template('testFakeDeposit.html',txMsg = txMsg,testResult = testResult)
def configinit():
    config = configparser.RawConfigParser()
    config.optionxform = lambda option: option
    return config
def getweb3Object():
    config = configinit()
    config.read('config.ini')
    network = config['NETWORK']['network']
    rpc = config.get("RPC", network)
    w3 = Web3(Web3.HTTPProvider(rpc))
    return w3
def getDecimals(contractAddr,contractAbi):
    w3 = getweb3Object()
    contractAddr = Web3.toChecksumAddress(contractAddr)
    contractObj = w3.eth.contract(address=contractAddr, abi=contractAbi)
    decimals = contractObj.functions.decimals().call()
    return decimals

def getTokenName(contractAddr,contractAbi):
    w3 = getweb3Object()
    contractAddr = Web3.toChecksumAddress(contractAddr)
    contractObj = w3.eth.contract(address=contractAddr, abi=contractAbi)
    tokenName = contractObj.functions.symbol().call()
    return tokenName

def getBalance(contractAddr,contractAbi,addr):
    w3 = getweb3Object()
    contractAddr = Web3.toChecksumAddress(contractAddr)
    contractObj = w3.eth.contract(address=contractAddr, abi=contractAbi)
    #decimals = getDecimals(contractAddr,contractAbi)
    addr = Web3.toChecksumAddress(addr)
    balance = contractObj.functions.balanceOf(addr).call()
    #print(balance / 10 ** decimals)
    return balance
def transferToken(contractAddr,contractAbi,privateKey,to,value):
    config = configinit()
    config.read('config.ini')
    network = config['NETWORK']['network']

    w3 = getweb3Object()
    account = w3.eth.account.from_key(privateKey)
    addr = account.address
    contractAddr = Web3.toChecksumAddress(contractAddr)
    contractObj = w3.eth.contract(address=contractAddr, abi=contractAbi)
    to = Web3.toChecksumAddress(to)
    gasPrice = w3.eth.gasPrice
    #print(gasprice)
    #print(w3.toWei(10,'gwei'))
    decimal = getDecimals(contractAddr,contractAbi)
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    estimateGaslimit = w3.eth.estimateGas({'to':to,'from':addr,'value':int(value/10**decimal)})

    unsigned_txn = contractObj.functions.transfer(to, int(value)).buildTransaction({'gas': estimateGaslimit*2, 'gasPrice': gasPrice, 'nonce': w3.eth.getTransactionCount(account.address)})
    signed_txn = w3.eth.account.sign_transaction(unsigned_txn, private_key=privateKey)
    txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    txn_receipt = w3.eth.waitForTransactionReceipt(txn_hash)
    global txMsg
    if network == "BNBSmartChain":
        txMsg = "https://bscscan.com/tx/" + str(txn_hash.hex())
    elif network == "Polygon":
        txMsg = "https://polygonscan.com/tx/" + str(txn_hash.hex())
    elif network == "Ethereum":
        txMsg = "https://etherscan.io/tx/" + str(txn_hash.hex())
    elif network == "Fantom":
        txMsg = "https://ftmscan.com/tx/" + str(txn_hash.hex())
    elif network == "AVAX-C":
        txMsg = "https://snowtrace.io/tx/" + str(txn_hash.hex())
    elif network == "Optimism":
        txMsg = "https://optimistic.etherscan.io/tx/" + str(txn_hash.hex())
    elif network == "ArbitrumOne":
        txMsg = "https://arbiscan.io/tx/" + str(txn_hash.hex())
    return txn_receipt['status']

def fakeDepositTest(contractAddr,contractAbi,privateKey,to):
    w3 = getweb3Object()
    account = w3.eth.account.from_key(privateKey)
    addr = account.address
    addr = Web3.toChecksumAddress(addr)
    contractAddr = Web3.toChecksumAddress(contractAddr)
    balance = getBalance(contractAddr,contractAbi,addr)
    decimals = getDecimals(contractAddr,contractAbi)
    print(balance)
    if balance == 0:
        value = 10*(10**decimals)
    else:
        value = 10*balance
    Status = transferToken(contractAddr,contractAbi,privateKey,to,value)
    time.sleep(5)
    if Status == 1:
        testResult = "代币合约存在假充值漏洞"
    elif Status == 0:
        testResult = "代币合约不存在假充值漏洞"
    else:
        testResult = "未知情况，Status为："+Status
    return testResult

if __name__ == '__main__':
    app.run(host='0.0.0.0',port='8889')
