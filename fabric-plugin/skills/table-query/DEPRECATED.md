# ⚠️ DEPRECATED: table-query Skill

**Status**: 🔴 DEPRECATED - DO NOT USE

**Reason**: The REST API endpoint used by this skill **does not exist** in the official Microsoft Fabric API.

**Deprecated Date**: 16 Mars 2026

---

## Why is this deprecated?

This skill uses the endpoint:
```
POST /workspaces/{id}/lakehouses/{id}/query
```

**This endpoint DOES NOT EXIST** according to the [official Microsoft Fabric Lakehouse API documentation](https://learn.microsoft.com/en-us/fabric/data-engineering/lakehouse-api).

### Available Endpoints (Official)
- ✅ `GET /lakehouses/{id}/tables` - List tables
- ✅ `POST /lakehouses/{id}/tables/{name}/load` - Load data
- ✅ `POST /lakehouses/{id}/jobs/TableMaintenance/instances` - Table maintenance
- ❌ **NO `/query` endpoint**

### Impact
- ❌ Unpredictable failures (HTTP 404)
- ❌ May work in some regions but not officially supported
- ❌ No guarantee of continued availability
- ❌ No official documentation or support

---

## ✅ Recommended Alternatives

### Option 1: lakehouse-sql-query (RECOMMENDED for SQL)

**Use this for SQL queries with JOIN, GROUP BY, WHERE, etc.**

```bash
# New skill using SQL Analytics Endpoint
/fabric-plugin:\lakehouse:sql-query <workspace-id> <lakehouse-id> \
  "SELECT c.name, COUNT(o.order_id) as orders
   FROM dbo.customers c
   LEFT JOIN dbo.orders o ON c.customer_id = o.customer_id
   GROUP BY c.name
   ORDER BY orders DESC"
```

**Features**:
- ✅ Full T-SQL support
- ✅ Official Microsoft SQL Analytics Endpoint
- ✅ JOIN, GROUP BY, CTEs, Window Functions
- ✅ Fast performance
- ✅ Production-ready

**Requirements**: `pip install pyodbc`

---

### Option 2: table-read (RECOMMENDED for simple reads)

**Use this for simple data extraction without SQL**

```bash
# Read table data via OneLake File API
/fabric-plugin:\lakehouse:read-table <workspace-id> <lakehouse-id> \
  "customers" --limit 100 --schema "dbo"
```

**Features**:
- ✅ Pure REST API (OneLake File API)
- ✅ Direct Delta Lake file access
- ✅ Fast performance
- ✅ Already tested and working

**Requirements**: `pip install deltalake pandas pyarrow`

---

### Option 3: Notebook API (for complex processing)

**Use this for very complex operations or data transformations**

```bash
# Execute parameterized notebook with Spark SQL
/fabric-plugin:\notebook:run-notebook <workspace-id> <notebook-id>
```

**Features**:
- ✅ Pure REST API
- ✅ Full Spark SQL + Python
- ✅ Complex transformations

**Limitations**:
- ⚠️ Slower (Spark session startup ~30-60s)
- ⚠️ More complex setup

---

## Migration Guide

### If you were using table-query for simple SELECT

**Before** (table-query - BROKEN):
```bash
/fabric-plugin:\lakehouse:query-sql <workspace-id> <lakehouse-id> \
  "SELECT * FROM customers LIMIT 100"
```

**After** (table-read - WORKS):
```bash
/fabric-plugin:\lakehouse:read-table <workspace-id> <lakehouse-id> \
  "customers" --limit 100 --schema "dbo"
```

---

### If you were using table-query for complex SQL

**Before** (table-query - BROKEN):
```bash
/fabric-plugin:\lakehouse:query-sql <workspace-id> <lakehouse-id> \
  "SELECT category, COUNT(*) as count, SUM(amount) as total
   FROM sales
   WHERE date >= '2024-01-01'
   GROUP BY category
   ORDER BY total DESC"
```

**After** (lakehouse-sql-query - WORKS):
```bash
/fabric-plugin:\lakehouse:sql-query <workspace-id> <lakehouse-id> \
  "SELECT category, COUNT(*) as count, SUM(amount) as total
   FROM dbo.sales
   WHERE date >= '2024-01-01'
   GROUP BY category
   ORDER BY total DESC"
```

**Note**: Add schema prefix `dbo.` to table names (T-SQL requirement)

---

## Comparison Matrix

| Feature | table-query (DEPRECATED) | lakehouse-sql-query | table-read |
|---------|-------------------------|---------------------|------------|
| **Status** | ❌ Broken | ✅ Works | ✅ Works |
| **API** | ❌ Endpoint missing | ✅ SQL Analytics | ✅ OneLake File |
| **SQL Support** | ❌ N/A | ✅ Full T-SQL | ❌ No SQL |
| **JOIN** | ❌ N/A | ✅ Yes | ❌ No |
| **GROUP BY** | ❌ N/A | ✅ Yes | ❌ No |
| **Performance** | ❌ N/A | ⚡ Fast | ⚡ Fast |
| **Official Support** | ❌ No | ✅ Yes | ✅ Yes |

---

## Timeline

- **Before March 2026**: Skill may have worked intermittently (undocumented endpoint)
- **16 March 2026**: Officially deprecated after API investigation
- **Recommendation**: Migrate immediately to alternatives

---

## Questions?

### Q: Will this skill be fixed?
**A**: No. The endpoint doesn't exist in the official API and cannot be "fixed". Use the recommended alternatives instead.

### Q: Why did this skill exist if the endpoint doesn't work?
**A**: It may have worked in some preview environments or regions, but was never officially documented or supported by Microsoft.

### Q: Which alternative should I use?
**A**:
- **For SQL queries (JOIN, GROUP BY)** → Use `lakehouse-sql-query`
- **For simple data reads** → Use `table-read`
- **For complex transformations** → Use `notebook-run` with Spark

### Q: Do I need to change my existing scripts?
**A**: Yes. Scripts using `table-query` will fail. Migrate to `lakehouse-sql-query` or `table-read` depending on your use case.

---

## References

- [Microsoft Fabric Lakehouse API Documentation](https://learn.microsoft.com/en-us/fabric/data-engineering/lakehouse-api)
- [SQL Analytics Endpoint Documentation](https://learn.microsoft.com/en-us/fabric/data-warehouse/get-started-lakehouse-sql-analytics-endpoint)
- [OneLake File API Documentation](https://learn.microsoft.com/en-us/azure/storage/blobs/data-lake-storage-introduction)
- `QUERY-OPTIONS-COMPARISON.md` - Detailed comparison of all query options
- `QUERY-ENDPOINT-ANALYSIS.md` - Technical analysis of the endpoint issue

---

**For support or questions, see the alternatives documentation:**
- `skills/lakehouse-sql-query/SKILL.md`
- `skills/table-read/SKILL.md`
