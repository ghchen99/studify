# Cosmos DB Data Plane RBAC Setup

## The Problem
Custom Azure RBAC roles grant **control plane** permissions (managing the Cosmos DB account), but not **data plane** permissions (accessing the actual data). Applications need data plane access to read/write documents.

## Two Permission Layers

### Control Plane (Azure RBAC)
- Manages the Cosmos DB account as an Azure resource
- Examples: Create/delete account, regenerate keys, change settings
- Your custom role: "Azure Cosmos DB Control Plane Owner"

https://learn.microsoft.com/en-us/azure/cosmos-db/nosql/how-to-connect-role-based-access-control?pivots=azure-portal

### Data Plane (Cosmos DB RBAC)
- Access to data inside Cosmos DB
- Examples: Read/write documents, query data, execute stored procedures
- **Managed separately from Azure RBAC**
- **Cannot be configured in Azure Portal** - CLI/PowerShell only

## Solution: Assign Data Plane Role

### Step 1: Switch to Correct Subscription
```powershell
az account set --subscription <subscription-id>
```

### Step 2: Assign Built-in Data Contributor Role
```powershell
az cosmosdb sql role assignment create \
  --account-name <cosmos-account-name> \
  --resource-group <resource-group> \
  --role-definition-id 00000000-0000-0000-0000-000000000002 \
  --principal-id <user-or-service-principal-object-id> \
  --scope "/"
```

### Built-in Role IDs
- `00000000-0000-0000-0000-000000000001` - **Data Reader** (read-only)
- `00000000-0000-0000-0000-000000000002` - **Data Contributor** (read/write)

## Verification
Wait 2-3 minutes for propagation, then test:

```python
from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential

client = CosmosClient("<endpoint>", DefaultAzureCredential())
# Should connect without permission errors
```

## Key Takeaway
Your custom control plane role enables you to **assign** data plane roles, but you still need to **explicitly grant** data plane access for applications to work with data.