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
    transaction["Transaction"]
    hash["Hash of the actual block"]
    timestamp["TimeStamp"]
    block --> timestamp
    block --> hash
    block --> index
    block --> prevhash
    block --> transaction

```

### Transaction
This is the transaction structure

**Transaction Validation System**: The Transactions is signed by the emisor, this is a centralized net


```mermaid
flowchart LR
    block["Transaction"]
    sender["SenderNode"]
    receiver["ReceiverNode"]
    signatures["Signature"]
    amount["Amount"]
    timestamp["TimeStamp"]
    block --> timestamp
    block --> sender
    block --> receiver
    block --> signatures
    block --> amount
```