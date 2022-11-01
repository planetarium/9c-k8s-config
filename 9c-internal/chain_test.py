import sys
from urllib.parse import urljoin
from requests import post, get

# Instruction: run this script after setting up the 9c-internal cluster.
# mainnet explorer url
explorer = "d131807iozwu1d.cloudfront.net"
# number of blocks to query
limit = sys.argv[1]

# get tip index from internal snapshot
snapshot_latest = get("https://snapshots.nine-chronicles.com/internal/mainnet_latest.json", headers={'content-type': 'application/json'})
data = snapshot_latest.json()
print(data['Index'])
offset = str(data['Index'] + 1)

# get signed txs from mainnet explorer
explorer_url = urljoin("http://{0}".format(explorer), "graphql")
explorer_query = """
query{
  chainQuery{
    blockQuery{
      blocks(offset: """ + offset + " limit: " + limit + """){
        index
        transactions{
          id
          signedTx
        }
      }
    }
  }
}
"""

explorer_res = post(explorer_url, json={'query': explorer_query}, headers={'content-type': 'application/json'})
explorer_result = explorer_res.json()
explorer_data = explorer_result['data']
blocks = explorer_data['chainQuery']['blockQuery']['blocks']

# send signed txs to internal miner
for block in blocks:
  transactions = block['transactions']
  for transaction in transactions:
    signed_tx = transaction['signedTx']
    query = f'mutation{{stageTxV2(payload: "{signed_tx}")}}'
    res = post("http://a778316ca16af4065a02dc2753c1a0fc-1775306312.us-east-2.elb.amazonaws.com/graphql", data=dict(query=query))
    print(res.json())
