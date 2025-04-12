# SwelCoin
The CryptoCurrency for Swelshin

## Schemes

### Block
this is the block structure



```mermaid

flowchart LR
    block["Block"]
    index["Index"]
    prevhash["Hash of the previous block"]
    timestamp["Time Stamp"]
    transaction["Transaction"]
    hash["Hash of the actual block"]
    block --> hash
    block --> index
    block --> prevhash
    block --> timestamp
    block --> transaction

```

### Transaction
This is the transaction structure

**Transaction Validation System**: The involved nodes need to grant that block, the value of the signatures are the timestamp.


```mermaid
flowchart LR
    block["Transaction"]
    sender["SenderNode"]
    receiver["ReceiverNode"]
    signatures["Signatures"]
    signaturea["Signature of node a"]
    signatureb["Signature of node b"]
    amount["Amount"]
    block --> sender
    block --> receiver
    block --> signatures
    signatures --> signaturea
    signatures --> signatureb
    block --> amount
```