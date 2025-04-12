# SwelCoin
The CryptoCurrency for Swelshin

## Schemes

### Block
this is the block structure

**Blocks Validation System**: The involved nodes need to grant that block

```mermaid
---
title: Block
---

flowchart LR
    block["Block"]
    index["index (position of the block in the chain)"]
    prevhash["Hash of the previous block"]
    signaturea["Signature of node a"]
    signatureb["Signature of node b"]
```